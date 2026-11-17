"""Build the app's continent-scale map icons: a sprite sheet and their world placements.

Writes assets/world/map-icons.png (icons from scripts/art/sprites.py) and src/data/map-icons.json:
  names:  icon kind for each frame (e.g. "acacia", "elephant");
  frames: [x, y, w, h] rectangles in the sheet; icons are anchored at their bottom centre;
  icons:  [frame, longitude, latitude, dx, dy], sorted north to south (back to front on a
          north-up globe). dx/dy are offsets in icon pixels, so groups keep their shape on screen.

Placements (ART_CONTRACT.md):
  - mountains: 1-4 per Natural Earth range (scalerank <= 4), about one per 220,000 km2,
    peaks at least 550 km apart across all ranges; Antarctic ranges use the glacier icon;
  - each continent's flora and landforms: the curated habitat regions in
    scripts/geography/scenery.json (oak, olive, acacia, baobab, bamboo, eucalyptus, cactus...);
  - animals: that file's sourced anchors (deer, elephant, panda, bison, jaguar, kangaroo,
    penguin...). These are representative illustrations, not wildlife observations or exact ranges.
Deterministic. Run after `npm run assets:prepare`:

    .venv/bin/python scripts/art/build_map_icons.py
"""

from hashlib import sha256
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw

import sprites

ROOT = Path(__file__).resolve().parents[2]
REGIONS = ROOT / ".cache" / "geography" / "regions-10m.source"
REGIONS_SHA256 = "b7b26e50ea917d3696aec87f932def2bf5f890f5770e441d59c162c6f4c92a77"
SCENERY = ROOT / "scripts" / "geography" / "scenery.json"
GLOBE = ROOT / "assets" / "world" / "globe.png"
BOARD = ROOT / "assets" / "world" / "board.png"
COUNTRIES = ROOT / ".cache" / "geography" / "countries-50m.source"
PLACES = ROOT / ".cache" / "geography" / "places-10m.source"
PLACES_LOCK = ROOT / "scripts" / "art" / "phase3-sources.lock.json"
# Countries with a country tier: their mainland bounds (west, south, east, north) and capital.
# Must match COVERAGE in src/features/world/globe-camera.ts.
COUNTRY_TIER = [
    {"adm0": "PRT", "bounds": (-10.0, 36.8, -6.0, 42.2), "capital": "Lisbon", "cities": 9},
    {"adm0": "ESP", "bounds": (-9.4, 35.9, 3.4, 43.8), "capital": "Madrid", "cities": 12,
     # The windmills of La Mancha at Consuegra and Campo de Criptana.
     "landmarks": [("windmill", -3.6085, 39.4566), ("windmill", -3.1235, 39.4049)]},
    {"adm0": "FRA", "bounds": (-5.2, 41.3, 9.6, 51.1), "capital": "Paris", "cities": 12,
     # Mont-Saint-Michel on its tidal island, and the vineyards of Saint-Émilion near Bordeaux.
     "landmarks": [("mont-saint-michel", -1.5115, 48.6361), ("vineyard", -0.155, 44.894)]},
    {"adm0": "DEU", "bounds": (5.8, 47.2, 15.1, 55.1), "capital": "Berlin", "cities": 9,
     "trees": 7,
     # Neuschwanstein, above Hohenschwangau in the Bavarian Alps.
     "landmarks": [("neuschwanstein", 10.7492, 47.5576)]},
    {"adm0": "NLD", "bounds": (3.2, 50.7, 7.3, 53.6), "capital": "Amsterdam", "cities": 9,
     "trees": 7,
     # Kinderdijk's Nederwaard mill network, at its actual polder site near Rotterdam.
     "landmarks": [("kinderdijk", 4.64, 51.8833)]},
    {"adm0": "BEL", "bounds": (2.5, 49.45, 6.4, 51.6), "capital": "Brussels", "cities": 9,
     "trees": 7,
     # Gravensteen, the medieval Counts' castle beside the Leie in Ghent.
     "landmarks": [("gravensteen", 3.7206, 51.0572)]},
    {"adm0": "GBR", "bounds": (-8.3, 49.8, 2.0, 60.9), "capital": "London", "cities": 9,
     "trees": 7,
     # Stonehenge's surviving sarsen ring, on Salisbury Plain.
     "landmarks": [("stonehenge", -1.8262, 51.1789)]},
    {"adm0": "IRL", "bounds": (-10.8, 51.35, -5.9, 55.5), "capital": "Dublin", "cities": 9,
     "trees": 7,
     # The medieval ecclesiastical complex on its limestone outcrop in Tipperary.
     "landmarks": [("rock-of-cashel", -7.8902, 52.5200)]},
    {"adm0": "ITA", "bounds": (6.6, 35.4, 18.6, 47.1), "capital": "Rome", "cities": 9,
     "trees": 7,
     "landmarks": [("leaning-tower-pisa", 10.3966, 43.7230)]},
    {"adm0": "DNK", "bounds": (8.0, 54.5, 15.3, 57.8), "capital": "København", "cities": 9,
     "trees": 7,
     # Kronborg at Helsingør, on the Danish side of the Øresund.
     "landmarks": [("kronborg", 12.6218, 56.0388)]},
    {"adm0": "SWE", "bounds": (11.0, 55.3, 24.2, 69.2), "capital": "Stockholm", "cities": 9,
     "trees": 7,
     # Gripsholm's Renaissance castle on Lake Mälaren at Mariefred.
     "landmarks": [("gripsholm", 17.2192, 59.2561)]},
    {"adm0": "NOR", "bounds": (4.5, 57.8, 31.3, 71.3), "capital": "Oslo", "cities": 9,
     "trees": 7,
     # Borgund Stave Church in Lærdal, not the modern neighbouring parish church.
     "landmarks": [("borgund", 7.8124, 61.0473)]},
    {"adm0": "FIN", "bounds": (19.0, 59.7, 31.6, 70.2), "capital": "Helsinki", "cities": 9,
     "trees": 7,
     # Olavinlinna on its rocky island in Kyrönsalmi, Savonlinna.
     "landmarks": [("olavinlinna", 28.9013, 61.8638)]},
    {"adm0": "ISL", "bounds": (-24.6, 63.2, -13.4, 66.6), "capital": "Reykjavík", "cities": 9,
     "trees": 7,
     # Gullfoss's two cascades on the Hvítá, northeast of Reykjavík.
     "landmarks": [("gullfoss", -20.1225, 64.3271)]},
    {"adm0": "CHE", "bounds": (5.95, 45.8, 10.55, 47.85), "capital": "Bern", "cities": 9,
     "trees": 7,
     # Chillon's island castle on Lake Geneva, south of Montreux.
     "landmarks": [("chillon", 6.9275, 46.4142)]},
    {"adm0": "AUT", "bounds": (9.5, 46.35, 17.2, 49.05), "capital": "Vienna", "cities": 9,
     "trees": 7,
     # The abbey church and monastery on the rocky terrace above Melk.
     "landmarks": [("melk-abbey", 15.3315, 48.2286)]},
    {"adm0": "MLT", "bounds": (14.05, 35.75, 14.65, 36.12), "capital": "Valletta", "cities": 9,
     # The whole archipelago is smaller than the standard city/decoration spacings.
     # City spacing stays 75 km; only decoration samples use the native source pixels.
     "trees": 2, "decoration_grid": 0.025, "decoration_km": 9,
     "landmarks": [("gozo-citadel", 14.2394, 36.0464)]},
    {"adm0": "CZE", "bounds": (12.05, 48.5, 18.9, 51.1), "capital": "Prague", "cities": 9,
     "trees": 7,
     # Karlštejn Castle, southwest of Prague, at the castle rather than the village.
     "landmarks": [("karlstejn", 14.18806, 49.93944)]},
    {"adm0": "POL", "bounds": (14.05, 49.0, 24.2, 55.1), "capital": "Warsaw", "cities": 9,
     "trees": 7,
     # The Teutonic brick castle on the east bank of the Nogat at Malbork.
     "landmarks": [("malbork", 19.02778, 54.03972)]},
    {"adm0": "LUX", "bounds": (5.7, 49.4, 6.55, 50.2), "capital": "Luxembourg", "cities": 9,
     # The populated places are within 75 km of the capital. Keep that rule;
     # sample a few broadleaf trees at native country-index resolution.
     "trees": 3, "decoration_grid": .025, "decoration_km": 12,
     "landmarks": [("vianden", 6.20222, 49.935)]},
    {"adm0": "SVK", "bounds": (16.8, 47.7, 22.6, 49.65), "capital": "Bratislava", "cities": 9,
     "trees": 7,
     "landmarks": [("spis-castle", 20.7683, 49.0006)]},
    {"adm0": "HUN", "bounds": (16.05, 45.7, 22.95, 48.65), "capital": "Budapest", "cities": 9,
     "trees": 7,
     # Benedictine abbey on the Tihany peninsula above Lake Balaton.
     "landmarks": [("tihany-abbey", 17.8894, 46.9139)]},
    {"adm0": "EST", "bounds": (21.7, 57.45, 28.25, 59.85), "capital": "Tallinn", "cities": 9,
     "trees": 7,
     # Saaremaa's episcopal castle, at the castle rather than the town centre.
     "landmarks": [("kuressaare", 22.4792, 58.2470)]},
    {"adm0": "LVA", "bounds": (20.9, 55.65, 28.25, 58.1), "capital": "Riga", "cities": 9,
     "trees": 7,
     # Rastrelli's palace at Pilsrundāle; museum-published entrance GPS.
     "landmarks": [("rundale", 24.026048, 56.414819)]},
    {"adm0": "LTU", "bounds": (20.85, 53.85, 26.85, 56.5), "capital": "Vilnius", "cities": 9,
     "trees": 7,
     # Island Castle in Lake Galvė, rather than Trakai town or its tourism office.
     "landmarks": [("trakai", 24.93306, 54.6525)]},
    {"adm0": "SVN", "bounds": (13.35, 45.4, 16.65, 46.9), "capital": "Ljubljana", "cities": 9,
     # Small and heavily forested: decorations keep 40 km apart instead of 70 km.
     "trees": 5, "decoration_km": 40,
     # The pilgrimage church on Bled Island, rather than the lake's centre or Bled town.
     "landmarks": [("bled", 14.09004, 46.36223)]},
    {"adm0": "HRV", "bounds": (13.45, 42.4, 19.45, 46.6), "capital": "Zagreb", "cities": 9,
     "trees": 7,
     # Veliki slap, the great waterfall at the end of Plitvice's Lower Lakes.
     "landmarks": [("plitvice", 15.6079, 44.9025)]},
    {"adm0": "BIH", "bounds": (15.7, 42.5, 19.65, 45.3), "capital": "Sarajevo", "cities": 9,
     "trees": 7,
     # The overlapping country box includes Croatian waters. Keep boats by Bosnia's Neum coast.
     "boat_bounds": (17.45, 42.85, 17.7, 43.0),
     # Stari Most itself, rather than Mostar's city centre or a bridge museum.
     "landmarks": [("stari-most", 17.81503, 43.33728)]},
    {"adm0": "SRB", "bounds": (18.8, 42.2, 23.1, 46.2), "capital": "Belgrade", "cities": 9,
     "trees": 7,
     # Golubac Fortress itself on the Danube, not Golubac town.
     "landmarks": [("golubac", 21.6784847, 44.6611873)]},
    {"adm0": "MNE", "bounds": (18.4, 41.8, 20.4, 43.6), "capital": "Podgorica", "cities": 9,
     "trees": 7, "decoration_grid": .05, "decoration_km": 20,
     "boat_bounds": (18.4, 41.8, 19.4, 42.4),
     # Upper Ostrog itself in its cliff, not the lower monastery or Danilovgrad.
     "landmarks": [("ostrog", 19.02917, 42.67500)]},
    {"adm0": "ALB", "bounds": (19.2, 39.6, 21.1, 42.7), "capital": "Tirana", "cities": 9,
     "trees": 7, "decoration_grid": .1, "decoration_km": 35,
     "boat_bounds": (19.2, 39.6, 19.7, 41.8),
     # Krujë's fortress itself, not Krujë town or the museum entrance.
     "landmarks": [("kruje", 19.794087, 41.507026)]},
]
SHEET = ROOT / "assets" / "world" / "map-icons.png"
DATA = ROOT / "src" / "data" / "map-icons.json"
GRID = 0.25  # degrees per placement-grid cell
KM_PER_DEGREE = 111.2

# Sprite variants per kind (seeds). Kinds placed in groups use several variants.
VARIANTS = {
    "mountain": 3, "hill": 2, "oak": 3, "pine": 2, "olive": 2, "acacia": 2, "baobab": 1,
    "palm": 2, "bamboo": 1, "eucalyptus": 2, "fern": 1, "grass": 2, "cactus": 1, "dune": 1,
    "red-rock": 1, "volcano": 1, "glacier": 2, "iceberg": 2,
    "castle": 1, "church": 1, "house": 2, "boat": 1, "windmill": 1, "mont-saint-michel": 1, "vineyard": 1,
    **{animal: 1 for animal in sprites.FAUNA},
    "neuschwanstein": 1,
    "kinderdijk": 1,
    "gravensteen": 1,
    "stonehenge": 1,
    "rock-of-cashel": 1,
    "leaning-tower-pisa": 1,
    "kronborg": 1,
    "gripsholm": 1,
    "borgund": 1,
    "olavinlinna": 1,
    "gullfoss": 1,
    "chillon": 1,
    "melk-abbey": 1,
    "gozo-citadel": 1,
    "karlstejn": 1,
    "malbork": 1,
    "vianden": 1,
    "spis-castle": 1,
    "tihany-abbey": 1,
    "kuressaare": 1,
    "rundale": 1,
    "trakai": 1,
    "bled": 1,
    "plitvice": 1,
    "stari-most": 1,
    "golubac": 1,
    "ostrog": 1,
    "kruje": 1,
}
FRAMES = [(kind, seed) for kind, count in VARIANTS.items() for seed in range(count)]
# Icon-pixel offsets for groups, so a stand of trees keeps its shape at every zoom.
GROUPS = {
    "pair": ((-5, -1), (5, 1)),
    "triple": ((-6, -1), (6, -1), (0, 2)),
}
GROUPING = {
    "oak": "pair", "pine": "pair", "olive": "pair", "acacia": "pair", "palm": "pair",
    "eucalyptus": "pair", "bamboo": "pair", "fern": "pair", "grass": "triple",
}
LANDFORMS = {"dune", "red-rock", "volcano", "glacier", "iceberg"}
# Extra animals per species beyond the curated anchors: (count, search radius in degrees around
# the anchors). Tight radii keep island and mountain species (kiwi, panda) in their small ranges.
EXTRA_WILDLIFE = {"panda": (1, 3.0), "kiwi": (1, 2.5), "orangutan": (1, 3.0)}


def frame_index(kind, seed):
    options = [i for i, (k, _) in enumerate(FRAMES) if k == kind]
    return options[seed % len(options)]


def h01(*values):
    return sprites.h01(*values)


def great_circle_km(a, b):
    la1, la2 = math.radians(a[1]), math.radians(b[1])
    dl = math.radians(b[0] - a[0])
    c = math.sin(la1) * math.sin(la2) + math.cos(la1) * math.cos(la2) * math.cos(dl)
    return 6371 * math.acos(max(-1.0, min(1.0, c)))


def spread(candidates, count, spacing_km, seed, taken=(), taken_km=None):
    """Deterministic, evenly spaced picks; keeps taken_km away from already placed icons."""
    chosen = []
    for lon, lat in sorted(candidates, key=lambda c: h01(seed, round(c[0] * 40), round(c[1] * 40))):
        if len(chosen) >= count:
            break
        if all(great_circle_km((lon, lat), other) >= spacing_km for other in chosen) and all(
            great_circle_km((lon, lat), other) >= (taken_km or spacing_km) for other in taken
        ):
            chosen.append((lon, lat))
    return chosen


def main():
    raw = REGIONS.read_bytes()
    if sha256(raw).hexdigest() != REGIONS_SHA256:
        raise ValueError("regions-10m checksum mismatch; run npm run assets:prepare first")
    regions = json.loads(raw)["features"]
    scenery = json.loads(SCENERY.read_text())
    width, height = int(360 / GRID), int(180 / GRID)
    land = Image.open(GLOBE).getchannel("R").resize((width, height), Image.BOX).load()
    # Continent of each cell, from the board texture's country index (Natural Earth CONTINENT).
    country_features = json.loads(COUNTRIES.read_bytes())["features"]
    continents = [f["properties"]["CONTINENT"] for f in country_features]
    codes = [f["properties"]["ADM0_A3"] for f in country_features]
    country = Image.open(BOARD).getchannel("R").resize((width, height), Image.NEAREST).load()
    native_board = Image.open(BOARD).getchannel("R")
    native_land = Image.open(GLOBE).getchannel("R")

    def native_country(lon, lat):
        index = native_board.getpixel((int((lon+180)/360*native_board.width) % native_board.width,
                                       min(native_board.height-1, max(0, int((90-lat)/180*native_board.height)))))
        return codes[index-1] if index else None

    def native_is_land(lon, lat):
        return native_land.getpixel((int((lon+180)/360*native_land.width) % native_land.width,
                                     min(native_land.height-1, max(0, int((90-lat)/180*native_land.height))))) >= 128

    def continent_at(x, y):
        index = country[x % width, y]
        return continents[index - 1] if index else None

    def country_code(x, y):
        if not 0 <= y < height:
            return None
        index = country[x % width, y]
        return codes[index - 1] if index else None

    def cell_center(x, y):
        return -180 + (x + 0.5) * GRID, 90 - (y + 0.5) * GRID

    def is_land(x, y):
        return land[x % width, y] >= 128

    def near_land(x, y, radius=6):
        return any(is_land(x + dx, y + dy) for dx in range(-radius, radius + 1, 2)
                   for dy in range(-radius, radius + 1, 2) if 0 <= y + dy < height)

    icons, placed = [], []

    def add(kind, lon, lat, seed, group=None, tier=0):
        offsets = GROUPS[group] if group else ((0, 0),)
        for i, (dx, dy) in enumerate(offsets):
            icons.append([frame_index(kind, seed + i), round(lon, 4), round(lat, 4), dx, dy, tier])
        if tier == 0:
            placed.append((lon, lat))

    # 1. Animals, first, so plants keep clear of them: the curated anchors, then a few more of
    #    each species near those anchors, on suitable ground and spread apart.
    anchors = {}
    for animal in scenery["animals"]:
        lon, lat = animal["anchor"]
        add(animal["kind"], lon, lat, 0)
        anchors.setdefault(animal["kind"], []).append((lon, lat, animal["habitat"], animal["continent"]))
    animals = list(placed)
    for kind, points in anchors.items():
        extra, radius = EXTRA_WILDLIFE.get(kind, (2, 6.0))
        candidates = []
        for ax, ay, habitat, home in points:
            for y in range(int((90 - ay - radius) / GRID), int((90 - ay + radius) / GRID) + 1, 2):
                for x in range(int((ax - radius + 180) / GRID), int((ax + radius + 180) / GRID) + 1, 2):
                    if not 0 <= y < height:
                        continue
                    lon, lat = cell_center(x % width, y)
                    if math.hypot(((lon - ax + 180) % 360) - 180, lat - ay) > radius:
                        continue
                    if habitat == "coastal-ice":
                        ok = lat < -62 and near_land(x, y, 2)
                    elif habitat == "coastal-sea":
                        ok = lat < -62 and not is_land(x, y) and near_land(x, y, 4)
                    else:  # extra animals never cross onto another continent
                        ok = is_land(x, y) and continent_at(x, y) == home
                    if ok:
                        candidates.append((lon, lat))
        for lon, lat in spread(candidates, extra, 320, sum(map(ord, kind)), animals, 260):
            add(kind, lon, lat, 0)
            animals.append((lon, lat))

    # 2. Mountains on Natural Earth ranges.
    range_cells, peaks = set(), []
    for feature in regions:
        props = feature["properties"]
        if props["FEATURECLA"] != "Range/mtn" or props["SCALERANK"] > 4:
            continue
        mask = Image.new("L", (width, height))
        draw = ImageDraw.Draw(mask)
        geometry = feature["geometry"]
        polygons = [geometry["coordinates"]] if geometry["type"] == "Polygon" else geometry["coordinates"]
        for polygon in polygons:
            draw.polygon([((lon + 180) / GRID, (90 - lat) / GRID) for lon, lat, *_ in polygon[0]], fill=255)
        pixels, bbox = mask.load(), mask.getbbox()
        if not bbox:
            continue
        cells, area = [], 0.0
        for y in range(bbox[1], bbox[3]):
            for x in range(bbox[0], bbox[2]):
                if pixels[x, y] and is_land(x, y):
                    lon, lat = cell_center(x, y)
                    cells.append((lon, lat))
                    range_cells.add((x, y))
                    area += (GRID * KM_PER_DEGREE) ** 2 * math.cos(math.radians(lat))
        count = max(1, min(4, int(area / 220000)))
        cells = [c for c in cells if all(great_circle_km(c, a) >= 200 for a in animals)]
        # Peaks keep 550 km from each other, across neighbouring ranges too.
        for lon, lat in spread(cells, count, 550, 31, peaks, 550):
            peaks.append((lon, lat))
            # Polar ranges are ice, not rock.
            kind = "glacier" if lat < -60 else "mountain" if props["SCALERANK"] <= 3 else "hill"
            add(kind, lon, lat, int(h01(lon * 7, lat * 7) * 9))

    # 3. Each continent's flora and landforms from the curated habitat regions.
    for region in scenery["regions"]:
        kind = region["kind"]
        if kind == "mountain":
            continue  # ranges come from Natural Earth (step 2)
        (ax, ay), (rx, ry) = region["anchor"], region["radius"]
        candidates = []
        for y in range(max(0, int((90 - ay - ry) / GRID)), min(height, int((90 - ay + ry) / GRID) + 1), 2):
            for x in range(int((ax - rx + 180) / GRID), int((ax + rx + 180) / GRID) + 1, 2):
                lon, lat = cell_center(x % width, y)
                dlon = ((lon - ax + 180) % 360) - 180
                if (dlon / rx) ** 2 + ((lat - ay) / ry) ** 2 > 1:
                    continue
                if region["habitat"] == "coastal-ice":
                    ok = not is_land(x, y) and near_land(x, y)
                else:
                    ok = is_land(x, y) and ((x % width, y) not in range_cells or kind in LANDFORMS)
                if ok:
                    candidates.append((lon, lat))
        count = max(2, round(region["count"] * 0.45))
        spacing = 420 if kind in LANDFORMS else 300
        for lon, lat in spread(candidates, count, spacing, sum(map(ord, region["id"])), placed, 170):
            add(kind, lon, lat, int(h01(lon * 5, lat * 5) * 9), GROUPING.get(kind))

    # 4. Country tier (fades in at country zoom): the capital as a castle among houses, towns as
    #    churches with houses, smaller cities as churches or house pairs, a few trees and boats.
    places_raw = PLACES.read_bytes()
    if sha256(places_raw).hexdigest() != json.loads(PLACES_LOCK.read_text())["places-10m"]:
        raise ValueError("places-10m checksum mismatch")
    places = [f["properties"] for f in json.loads(places_raw)["features"]]

    def building(kind, lon, lat, dx, dy, seed=0):
        icons.append([frame_index(kind, seed), round(lon, 4), round(lat, 4), dx, dy, 1])

    for spec in COUNTRY_TIER:
        w, s_, e, n = spec["bounds"]
        cities = sorted(
            (p for p in places if p["adm0_a3"] == spec["adm0"] and w <= p["longitude"] <= e
             and s_ <= p["latitude"] <= n),
            # A capital can rank below a nearby metro area (The Hague above Amsterdam).
            # Anchor it first so the 75 km spacing filter cannot discard the capital itself.
            key=lambda p: (p["name"] != spec["capital"], -p["pop_max"]))
        towns = []
        for city in cities:
            here = (city["longitude"], city["latitude"])
            if any(great_circle_km(here, t) < 75 for t in towns) or len(towns) >= spec["cities"]:
                continue
            towns.append(here)
            lon, lat = here
            rank = len(towns) - 1
            if city["name"] == spec["capital"]:
                building("house", lon, lat, -9, -2, 0)
                building("house", lon, lat, 10, -1, 1)
                building("castle", lon, lat, 0, 0)
            elif rank <= 2:
                building("house", lon, lat, -8, 1, rank)
                building("church", lon, lat, 0, 0)
                building("house", lon, lat, 8, 2, rank + 1)
            elif rank % 2:
                building("church", lon, lat, 0, 0)
            else:
                building("house", lon, lat, -5, -1, rank)
                building("house", lon, lat, 5, 1, rank + 1)
        for kind, lon, lat in spec.get("landmarks", []):
            building(kind, lon, lat, 0, 0)
            towns.append((lon, lat))
        trees, boats = [], []
        step = spec.get("decoration_grid", GRID)
        for y in range(int((90 - n) / step), int((90 - s_) / step)):
            for x in range(int((w + 180) / step), int((e + 180) / step)):
                lon, lat = -180+(x+.5)*step, 90-(y+.5)*step
                if not (w <= lon <= e and s_ <= lat <= n):
                    continue  # grid rounding can reach half a cell outside the bounds
                if step != GRID:
                    # Tiny islands disappear in the averaged 0.25° land mask. Keep
                    # the same country-index and land filters at source resolution.
                    if native_is_land(lon, lat) and native_country(lon, lat) == spec["adm0"]:
                        trees.append((lon, lat))
                    elif not native_is_land(lon, lat) and any(
                        native_country(lon+dx*step, lat+dy*step) == spec["adm0"]
                        for dx in (-3, 0, 3) for dy in (-3, 0, 3)
                    ):
                        boats.append((lon, lat))
                    continue
                if is_land(x, y) and country_code(x, y) == spec["adm0"]:
                    trees.append((lon, lat))
                elif not is_land(x, y) and any(country_code(x + dx, y + dy) == spec["adm0"]
                                               for dx in (-3, 0, 3) for dy in (-3, 0, 3)):
                    boats.append((lon, lat))
        # Italy spans Alpine forests and Mediterranean islands: distribute its seven trees
        # across three latitude bands rather than letting one seeded cluster fill the north.
        tree_sites = spread(trees, spec.get("trees", 7 if spec["adm0"] == "PRT" else 12),
                            spec.get("decoration_km", 70), 51, towns, spec.get("decoration_km", 45))
        if spec["adm0"] == "ITA":
            tree_sites = []
            for south, north, count in ((44, 48, 2), (40, 44, 2), (35, 40, 3)):
                candidates = [t for t in trees if south <= t[1] < north
                              and all(great_circle_km(t, other) >= 70 for other in tree_sites)]
                tree_sites += spread(candidates, count, 70, 51, towns, 45)
        for lon, lat in tree_sites:
            if spec["adm0"] in ("SWE", "NOR", "FIN", "EST", "LVA", "LTU"):
                kind = "pine" if lat > 60 or spec["adm0"] in ("EST", "LVA", "LTU") else "oak"
                building(kind, lon, lat, 0, 0, int(h01(lon * 9, lat * 9) * 9))
                continue
            if spec["adm0"] == "ITA":
                kind = "pine" if lat >= 44 else "oak" if lat >= 40 else "olive"
                building(kind, lon, lat, 0, 0, int(h01(lon * 9, lat * 9) * 9))
                continue
            if spec["adm0"] in ("DEU", "NLD", "BEL", "GBR", "IRL", "DNK", "CZE", "POL", "LUX", "SVK", "HUN", "SVN"):
                kind = "pine" if (spec["adm0"] in ("DEU", "POL") and lat > 53 or spec["adm0"] in ("GBR", "DNK") and lat > 56
                                  or spec["adm0"] == "SVN" and lat > 46.2) else "oak"
                building(kind, lon, lat, 0, 0, int(h01(lon * 9, lat * 9) * 9))
                continue
            if spec["adm0"] == "HRV":
                # Olives on the Dalmatian coast and islands, pines in Istria, Gorski kotar and Lika, oaks inland.
                kind = "olive" if lat < 44.3 else "pine" if lon < 15.8 and lat < 45.5 else "oak"
                building(kind, lon, lat, 0, 0, int(h01(lon * 9, lat * 9) * 9))
                continue
            if spec["adm0"] == "MNE":
                kind = "olive" if lat < 42.4 else "pine"
                building(kind, lon, lat, 0, 0, int(h01(lon * 9, lat * 9) * 9))
                continue
            if spec["adm0"] == "ALB":
                kind = "pine" if lat > 41.5 or lon > 20.3 else "olive"
                building(kind, lon, lat, 0, 0, int(h01(lon * 9, lat * 9) * 9))
                continue
            if spec["adm0"] in ("BIH", "SRB"):
                kind = "pine" if lat < 44.5 and lon > 17 else "oak"
                building(kind, lon, lat, 0, 0, int(h01(lon * 9, lat * 9) * 9))
                continue
            if lat > 47.5 and spec["adm0"] == "FRA":
                kind = "oak"  # northern France: broadleaf woods
                building(kind, lon, lat, 0, 0, int(h01(lon * 9, lat * 9) * 9))
                continue
            kind = "pine" if lat > 40.5 else "olive" if lat < 38.8 else "oak"
            building(kind, lon, lat, 0, 0, int(h01(lon * 9, lat * 9) * 9))
        if "boat_bounds" in spec:
            bw, bs, be, bn = spec["boat_bounds"]
            boats = [(lon, lat) for lon, lat in boats if bw <= lon <= be and bs <= lat <= bn]
        for lon, lat in spread(boats, 2, spec.get("decoration_km", 75)*2, 53):
            building("boat", lon, lat, 0, 0)

    icons.sort(key=lambda i: (-i[2] + i[4] * 0.01, i[1]))

    images = [sprites.ICONS[kind](seed) for kind, seed in FRAMES]
    sheet = Image.new("RGBA", (sum(img.width + 1 for img in images), max(img.height for img in images)))
    frames, x = [], 0
    for img in images:
        sheet.alpha_composite(img, (x, 0))
        frames.append([x, 0, img.width, img.height])
        x += img.width + 1
    sheet.save(SHEET, optimize=True)
    DATA.write_text(json.dumps(
        {"names": [kind for kind, _ in FRAMES], "frames": frames, "icons": icons},
        separators=(",", ":"),
    ) + "\n")
    kinds = {}
    for frame, *_ in icons:
        kinds[FRAMES[frame][0]] = kinds.get(FRAMES[frame][0], 0) + 1
    print(f"{len(icons)} icons, sheet {sheet.size} {SHEET.stat().st_size} bytes:", kinds)


if __name__ == "__main__":
    main()
