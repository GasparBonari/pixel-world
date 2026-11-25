"""Rebuild world textures and display labels from pinned Natural Earth inputs."""

from base64 import b64encode
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
from io import BytesIO
import json
import math
from pathlib import Path
from struct import pack
from tempfile import TemporaryDirectory
import urllib.request

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / '.cache' / 'geography'
OUTPUT = ROOT / 'assets' / 'world'
REVISION = 'ca96624a56bd078437bca8184e78163e5039ad19'
SOURCES = {
    'land-10m': f'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/{REVISION}/geojson/ne_10m_land.geojson',
    'countries-50m': f'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/{REVISION}/geojson/ne_50m_admin_0_countries.geojson',
    'lakes-10m': f'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/{REVISION}/geojson/ne_10m_lakes.geojson',
    'regions-10m': f'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/{REVISION}/geojson/ne_10m_geography_regions_polys.geojson',
    'places-10m': f'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/{REVISION}/geojson/ne_10m_populated_places_simple.geojson',
    # Ocean depth contours: each layer is the sea deeper than its depth in metres.
    **{f'bathymetry-{depth}': f'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/{REVISION}/geojson/ne_10m_bathymetry_{layer}.geojson'
       for depth, layer in ((200, 'K_200'), (1000, 'J_1000'), (2000, 'I_2000'), (4000, 'G_4000'))},
}
# Depth levels in the depth texture: 0 shelf (< 200 m), then deeper than 200, 1000, 2000 and 4000 m.
DEPTHS = (200, 1000, 2000, 4000)


def fetch(item):
    name, url = item
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / f'{name}.source'
    if not path.exists():
        request = urllib.request.Request(url, headers={'User-Agent': 'PixelWorld/0.1 asset preparation'})
        with urllib.request.urlopen(request, timeout=60) as response:
            data = response.read(20_000_001)
        if len(data) > 20_000_000:
            raise ValueError(f'{name}: source exceeded the 20 MB limit')
        path.write_bytes(data)
    data = path.read_bytes()
    return name, data


def write_atomic(destination, data):
    # Metro can be running while assets are regenerated. Publish complete files.
    with TemporaryDirectory(dir=destination.parent, prefix='.geography-') as directory:
        temporary = Path(directory) / destination.name
        temporary.write_bytes(data)
        temporary.replace(destination)


def generate_globe(sources):
    width, height = 4096, 2048

    def point(position):
        return ((position[0]+180)/360*width, (90-position[1])/180*height)

    def mask(data):
        image = Image.new('L', (width, height))
        draw = ImageDraw.Draw(image)
        for feature in data['features']:
            geometry = feature['geometry']
            polygons = [geometry['coordinates']] if geometry['type'] == 'Polygon' else geometry['coordinates']
            for polygon in polygons:
                draw.polygon([point(p) for p in polygon[0]], fill=255)
                for hole in polygon[1:]:
                    draw.polygon([point(p) for p in hole], fill=0)
        return image

    land = mask(json.loads(sources['land-10m']))
    lakes = mask(json.loads(sources['lakes-10m']))
    borders = Image.new('L', (width, height))
    draw = ImageDraw.Draw(borders)
    labels = []
    for feature in json.loads(sources['countries-50m'])['features']:
        geometry = feature['geometry']
        polygons = [geometry['coordinates']] if geometry['type'] == 'Polygon' else geometry['coordinates']
        for polygon in polygons:
            draw.line([point(p) for p in polygon[0]], fill=255, width=1)
        properties = feature['properties']
        labels.append({'id': properties['ADM0_A3'], 'name': properties['NAME'],
                       'longitude': properties['LABEL_X'], 'latitude': properties['LABEL_Y'],
                       'rank': properties['LABELRANK'], 'population': properties['POP_EST']})
    labels.sort(key=lambda label: (label['rank'], -label['population'], label['id']))
    write_atomic(ROOT/'src/data/country-labels.json', (json.dumps(labels, separators=(',', ':'))+'\n').encode())
    # One 32 MiB decoded texture carries three geographic masks, avoiding duplicate full-size images.
    texture = OUTPUT/'globe.png'
    encoded = BytesIO()
    Image.merge('RGB', (land, borders, lakes)).save(encoded, format='PNG', optimize=True)
    write_atomic(texture, encoded.getvalue())
    return {'width': width, 'height': height, 'bytes': texture.stat().st_size,
            'decodedBytes': width*height*4, 'projection': 'equirectangular',
            'channels': {'red': 'land', 'green': 'country borders', 'blue': 'lakes'},
            'decorative': ['clouds', 'terrain colors', 'lighting', 'stars'], 'countryLabelCount': len(labels)}


def generate_country_lookup(countries, features):
    width, height = countries.size
    runs = bytearray()
    row_offsets = [0]
    pixels = countries.tobytes()
    for y in range(height):
        row = pixels[y * width:(y + 1) * width]
        for x, index in enumerate(row):
            if x == 0 or index != row[x - 1]:
                runs.extend(pack('<HB', x, index))
        row_offsets.append(len(runs) // 3)

    data = pack(f'<{len(row_offsets)}H', *row_offsets) + runs
    path = 'src/data/board-country-lookup.json'
    lookup = {
        'generatedBy': 'scripts/geography/prepare_assets.py',
        'width': width, 'height': height,
        'countryIds': [None] + [feature['properties']['ADM0_A3'] for feature in features],
        'rows': b64encode(data).decode('ascii'),
    }
    write_atomic(ROOT/path, (json.dumps(lookup, separators=(',', ':'))+'\n').encode())
    return {'path': path, 'decodedBytes': len(data),
            'source': 'countries-50m, board.png red channel', 'license': 'Natural Earth, public domain'}


def generate_board(sources):
    """Continent-scale 'game board' data (ART_CONTRACT.md), equirectangular 2048x1024:

    red   = country index + 1 (order of ne_50m_admin_0_countries; 0 = none), for puzzle tones
            and borders;
    green = distance from water to the nearest land in units of 3 km (capped at 255), for the
            night-sea bands, which the shader converts to screen pixels at every zoom;
    blue  = mountain ranges (255: scalerank <= 3, 160: scalerank 4), for a relief tint.
    """
    width, height = 2048, 1024

    def point(position):
        return ((position[0]+180)/360*width, (90-position[1])/180*height)

    def fill(image, features, value):
        draw = ImageDraw.Draw(image)
        for feature, level in features:
            geometry = feature['geometry']
            polygons = [geometry['coordinates']] if geometry['type'] == 'Polygon' else geometry['coordinates']
            for polygon in polygons:
                draw.polygon([point(p) for p in polygon[0]], fill=value(level))
                for hole in polygon[1:]:
                    draw.polygon([point(p) for p in hole], fill=0)

    land = Image.new('L', (width, height))
    fill(land, [(f, 0) for f in json.loads(sources['land-10m'])['features']], lambda _: 255)
    countries = Image.new('L', (width, height))
    country_features = json.loads(sources['countries-50m'])['features']
    fill(countries, [(f, i + 1) for i, f in enumerate(country_features)], lambda index: index)
    ranges = Image.new('L', (width, height))
    regions = [f for f in json.loads(sources['regions-10m'])['features']
               if f['properties']['FEATURECLA'] == 'Range/mtn' and f['properties']['SCALERANK'] <= 4]
    fill(ranges, [(f, f['properties']['SCALERANK']) for f in regions], lambda rank: 255 if rank <= 3 else 160)

    # Chamfer distance in kilometres. East-west steps shrink with cos(latitude), so bands keep
    # their true shape at high latitudes instead of stretching like a plain pixel distance.
    row_km = 180 / height * 111.2
    far = 1e9
    mask = land.load()
    dist = [[0.0 if mask[x, y] else far for x in range(width)] for y in range(height)]
    for forward in (True, False):
        rows = range(height) if forward else range(height - 1, -1, -1)
        cols = range(width) if forward else range(width - 1, -1, -1)
        step = -1 if forward else 1
        for y in rows:
            col_km = max(0.5, math.cos(math.radians(90 - (y + 0.5) * 180 / height)) * 360 / width * 111.2)
            diagonal = math.hypot(col_km, row_km)
            row, previous = dist[y], dist[y + step] if 0 <= y + step < height else None
            for x in cols:
                value = row[x]
                if value == 0.0:
                    continue
                if 0 <= x + step < width:
                    value = min(value, row[x + step] + col_km)
                if previous is not None:
                    value = min(value, previous[x] + row_km)
                    if 0 <= x - 1 < width:
                        value = min(value, previous[x - 1] + diagonal)
                    if x + 1 < width:
                        value = min(value, previous[x + 1] + diagonal)
                row[x] = value
    distance = Image.new('L', (width, height))
    distance.putdata([min(255, int(v / 3 + 0.5)) for row in dist for v in row])

    texture = OUTPUT/'board.png'
    encoded = BytesIO()
    Image.merge('RGB', (countries, distance, ranges)).save(encoded, format='PNG', optimize=True)
    write_atomic(texture, encoded.getvalue())
    lookup = generate_country_lookup(countries, country_features)
    return {'width': width, 'height': height, 'bytes': texture.stat().st_size,
            'decodedBytes': width*height*4, 'projection': 'equirectangular',
            'countryLookup': lookup,
            'channels': {'red': 'country index + 1 (ne_50m_admin_0_countries order)',
                         'green': 'water distance to land, 3 km units, capped at 255',
                         'blue': 'mountain ranges: 255 scalerank<=3, 160 scalerank 4'},
            'countryCount': len(country_features), 'rangeCount': len(regions)}


def generate_depth(sources):
    """Ocean depth for the sea's colours (ART_CONTRACT.md section 2), equirectangular 1024x512, one
    grey channel: 0 on the continental shelf (and on land and lakes), then 64, 128, 191 and 255 for
    water deeper than 200, 1000, 2000 and 4000 m. The shader samples it smoothly, so contours blend.

    Each Natural Earth layer outlines the sea deeper than its depth. Its holes (islands, seamounts,
    shallower banks) belong to the shallower levels, so each level is drawn as its own mask and
    every pixel keeps the deepest level that covers it.
    """
    width, height = 1024, 512

    def point(position):
        return ((position[0]+180)/360*width, (90-position[1])/180*height)

    depth = Image.new('L', (width, height))
    for level, metres in enumerate(DEPTHS, start=1):
        mask = Image.new('L', (width, height))
        draw = ImageDraw.Draw(mask)
        for feature in json.loads(sources[f'bathymetry-{metres}'])['features']:
            geometry = feature['geometry']
            polygons = [geometry['coordinates']] if geometry['type'] == 'Polygon' else geometry['coordinates']
            for polygon in polygons:
                draw.polygon([point(p) for p in polygon[0]], fill=255)
                for hole in polygon[1:]:
                    draw.polygon([point(p) for p in hole], fill=0)
        depth.paste(round(level * 255 / len(DEPTHS)), mask=mask)
    texture = OUTPUT/'depth.png'
    encoded = BytesIO()
    depth.save(encoded, format='PNG', optimize=True)
    write_atomic(texture, encoded.getvalue())
    return {'width': width, 'height': height, 'bytes': texture.stat().st_size,
            'decodedBytes': width*height*4, 'projection': 'equirectangular',
            'channels': {'grey': '0 shelf/land, then 64/128/191/255 deeper than ' + '/'.join(f'{d} m' for d in DEPTHS)}}


def generate_city_lights(sources):
    """Illustrative night lights at major Natural Earth populated places."""
    width, height = 512, 256
    lights = Image.new('L', (width, height))
    pixels = lights.load()
    cities = [f for f in json.loads(sources['places-10m'])['features']
              if f['properties']['pop_max'] >= 500_000]
    for city in cities:
        longitude, latitude = city['geometry']['coordinates']
        center_x = (longitude + 180) / 360 * width
        center_y = (90 - latitude) / 180 * height
        size = min(1, math.log10(city['properties']['pop_max'] / 500_000) / 1.6)
        radius = 1.65 + size * 2.25
        latitude_scale = max(0.35, math.cos(math.radians(latitude)))
        radius_x = radius / latitude_scale
        peak = 125 + 130 * size
        for y in range(max(0, math.floor(center_y - radius)), min(height, math.ceil(center_y + radius))):
            for x in range(math.floor(center_x - radius_x), math.ceil(center_x + radius_x)):
                distance = math.hypot((x + 0.5 - center_x) / radius_x, (y + 0.5 - center_y) / radius)
                glow = round(peak * min(1, max(0, (1 - distance) * 1.55)))
                pixels[x % width, y] = max(pixels[x % width, y], glow)

    texture = OUTPUT/'city-lights.png'
    encoded = BytesIO()
    lights.save(encoded, format='PNG', optimize=True)
    write_atomic(texture, encoded.getvalue())
    return {'width': width, 'height': height, 'bytes': texture.stat().st_size,
            'decodedBytes': width*height*4, 'projection': 'equirectangular',
            'channels': {'grey': 'illustrative light intensity from populated places and population'},
            'placeCount': len(cities)}


def main():
    with ThreadPoolExecutor(max_workers=4) as pool:
        sources = dict(pool.map(fetch, SOURCES.items()))
    checksums = {name: sha256(data).hexdigest() for name, data in sources.items()}
    lock_path = Path(__file__).with_name('sources.lock.json')
    if lock_path.exists():
        expected = json.loads(lock_path.read_text())
        if expected != checksums:
            raise ValueError('Source checksum mismatch. Review source changes before updating sources.lock.json.')
    else:
        lock_path.write_text(json.dumps(checksums, indent=2) + '\n')
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (ROOT/'src/data').mkdir(parents=True, exist_ok=True)
    manifest = {
        'sources': {name: {'url': url, 'sha256': checksums[name]} for name, url in SOURCES.items()},
        'globe': generate_globe(sources),
        'board': generate_board(sources),
        'depth': generate_depth(sources),
        'cityLights': generate_city_lights(sources),
    }
    write_atomic(OUTPUT/'manifest.json', (json.dumps(manifest, indent=2)+'\n').encode())
    write_atomic(OUTPUT/'LICENSE.txt', (
        'Geography: Natural Earth, public-domain map data.\n'
        'Terms: https://www.naturalearthdata.com/about/terms-of-use/\n'
        f'Source revision: {REVISION}\n'
        'Pixel projection, terrain coloring, clouds, lighting, and stars: Pixel World.\n'
        'Terrain colors and cloud patterns are decorative, not measured land cover or weather.\n'
    ).encode())
    print(json.dumps(manifest['globe'], indent=2))



if __name__ == '__main__':
    main()
