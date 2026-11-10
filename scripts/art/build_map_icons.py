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
SHEET = ROOT / "assets" / "world" / "map-icons.png"
DATA = ROOT / "src" / "data" / "map-icons.json"
GRID = 0.25  # degrees per placement-grid cell
KM_PER_DEGREE = 111.2

# Sprite variants per kind (seeds). Kinds placed in groups use several variants.
VARIANTS = {
    "mountain": 3, "hill": 2, "oak": 3, "pine": 2, "olive": 2, "acacia": 2, "baobab": 1,
    "palm": 2, "bamboo": 1, "eucalyptus": 2, "fern": 1, "grass": 2, "cactus": 1, "dune": 1,
    "red-rock": 1, "volcano": 1, "glacier": 2, "iceberg": 2,
    **{animal: 1 for animal in sprites.FAUNA},
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
    continents = [f["properties"]["CONTINENT"] for f in json.loads(COUNTRIES.read_bytes())["features"]]
    country = Image.open(BOARD).getchannel("R").resize((width, height), Image.NEAREST).load()

    def continent_at(x, y):
        index = country[x % width, y]
        return continents[index - 1] if index else None

    def cell_center(x, y):
        return -180 + (x + 0.5) * GRID, 90 - (y + 0.5) * GRID

    def is_land(x, y):
        return land[x % width, y] >= 128

    def near_land(x, y, radius=6):
        return any(is_land(x + dx, y + dy) for dx in range(-radius, radius + 1, 2)
                   for dy in range(-radius, radius + 1, 2) if 0 <= y + dy < height)

    icons, placed = [], []

    def add(kind, lon, lat, seed, group=None):
        offsets = GROUPS[group] if group else ((0, 0),)
        for i, (dx, dy) in enumerate(offsets):
            icons.append([frame_index(kind, seed + i), round(lon, 4), round(lat, 4), dx, dy])
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
