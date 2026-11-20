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
    {"adm0": "MKD", "bounds": (20.4, 40.8, 23.1, 42.4), "capital": "Skopje", "cities": 9,
     "trees": 7, "decoration_grid": .1, "decoration_km": 30,
     # St John at Kaneo itself on the cliff above Lake Ohrid. Landlocked: no offshore boats.
     "landmarks": [("kaneo", 20.7887653, 41.1111244)]},
    {"adm0": "GRC", "bounds": (19.3, 34.7, 29.7, 41.8), "capital": "Athens", "cities": 9,
     "trees": 7,
     # Holy Trinity Monastery itself on its sandstone pillar at Meteora, above Kalambaka.
     "landmarks": [("meteora", 21.6358, 39.7132)]},
    {"adm0": "ROU", "bounds": (20.2, 43.6, 29.8, 48.3), "capital": "Bucharest", "cities": 9,
     "trees": 7,
     # Offshore boats stay off Romania's own Black Sea coast, outside the Danube delta.
     "boat_bounds": (28.7, 43.7, 29.7, 44.8),
     "landmarks": [("bran", 25.36722, 45.51500)]},
    {"adm0": "TUR", "bounds": (25.6, 35.8, 44.9, 42.2), "capital": "Ankara", "cities": 9,
     "trees": 7,
     # Pamukkale's travertine terraces, rather than the modern town or Hierapolis theatre.
     "landmarks": [("pamukkale", 29.12333, 37.92389)]},
    {"adm0": "AND", "bounds": (1.4, 42.42, 1.79, 42.66), "capital": "Andorra", "cities": 9,
     # The pinned Natural Earth name is Andorra; all other towns are within 75 km.
     "trees": 3, "decoration_grid": .01, "decoration_km": 5,
     "landmarks": [("meritxell", 1.59088, 42.55463)]},
    {"adm0": "BGR", "bounds": (22.3, 41.2, 28.7, 44.3), "capital": "Sofia", "cities": 9,
     "trees": 7,
     # Rila Monastery complex in the Rilska valley, south of Sofia.
     "boat_bounds": (27.8, 42.0, 28.7, 43.8),
     "landmarks": [("rila", 23.3401159, 42.1333100)]},
    {"adm0": "MDA", "bounds": (26.6, 45.4, 30.2, 48.5), "capital": "Chișinău", "cities": 9,
     "trees": 7, "decoration_km": 40, "boats": 0,
     # Soroca's fortress itself on the Moldovan bank of the Dniester. Moldova is landlocked.
     "landmarks": [("soroca", 28.3054778, 48.1612167)]},
    {"adm0": "BLR", "bounds": (23.1, 51.2, 32.8, 56.2), "capital": "Minsk", "cities": 9,
     "trees": 7, "boats": 0,
     # Mir Castle itself, southwest of Minsk; Belarus is landlocked.
     "landmarks": [("mir-castle", 26.473, 53.4512389)]},
    {"adm0": "KOS", "bounds": (20.0, 41.8, 21.9, 43.3), "capital": "Pristina", "cities": 9,
     # All pinned cities are within 75 km of Pristina. Keep city spacing;
     # the smaller country only needs closer, country-index-filtered decoration.
     "trees": 7, "decoration_grid": .05, "decoration_km": 20, "boats": 0, "landmarks": []},
    {"adm0": "UKR", "bounds": (22.0, 44.2, 40.3, 52.4), "capital": "Kyiv", "cities": 9,
     "trees": 7, "boats": 2,
     # Keep Ukraine's offshore decoration east of the existing Romanian coastal boat.
     "boat_bounds": (30.2, 44.2, 40.3, 48.0),
     # Khotyn's citadel itself, on the western/right bank of the Dniester.
     "landmarks": [("khotyn", 26.49833, 48.52194)]},
    {"adm0": "RUS", "bounds": (19.0, 41.0, -169.0, 82.0), "capital": "Moscow", "cities": 9,
     "trees": 7, "boats": 2,
     "boat_bounds": (130.0, 42.0, 180.0, 64.0),
     # Western summit of Elbrus; east < west preserves Russia across the date line.
     "landmarks": [("elbrus", 42.4378432, 43.3524103)]},
    {"adm0": "CYP", "bounds": (32.15, 34.48, 34.65, 35.78), "capital": "Nicosia", "cities": 9,
     "trees": 7, "boats": 2, "decoration_grid": 0.05, "decoration_km": 23,
     "boat_bounds": (32.15, 34.48, 34.65, 34.95),
     # Centre of the excavated Neolithic settlement, above the Maroni valley.
     "landmarks": [("choirokoitia", 33.34398, 34.79712)]},
    {"adm0": "LIE", "bounds": (9.47, 47.04, 9.64, 47.28), "capital": "Vaduz", "cities": 9,
     # Restrict the coarse native board cell to its strip inside the Natural Earth outline.
     "trees": 2, "tree_bounds": (9.48, 47.07, 9.49, 47.17),
     "decoration_grid": .01, "decoration_km": 4, "boats": 0, "landmarks": []},
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
    "kaneo": 1,
    "meteora": 1,
    "bran": 1,
    "pamukkale": 1,
    "meritxell": 1,
    "rila": 1,
    "soroca": 1,
    "mir-castle": 1,
    "khotyn": 1,
    "elbrus": 1,
    "choirokoitia": 1,
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


# Country-tier icons appear in zoom steps, each once it no longer overlaps an icon already shown.
# Icons have a fixed screen size while the globe grows with 2**zoom, so the zoom at which two
# icons stop overlapping can be computed here, once, instead of every frame on the device.
# An icon's appearance zoom is where it is fully visible; it fades in over the 0.6 zoom before it
# (MapIcons), and may touch its neighbours only while still faint.
ICON_PX_PER_RADIAN = 0.41 * 130 * 1.5  # globe radius in icon pixels at zoom 0: globeRadius / iconScale
APPEAR_FIRST = 5.0  # COUNTRY_ZOOM.full
APPEAR_STEP = 0.2
APPEAR_LAST = 6.2  # icons that only fit later are dropped; COUNTRY_ZOOM.max is 6.4
ICON_GAP = 1  # icon pixels kept clear between neighbours
NEAR_DEGREES = 2.5  # pairs farther apart than this are already clear at APPEAR_FIRST
SOLID_ALPHA = 128  # ground shadows (27% black) and transparent margins may overlap


def solid_boxes(sheet, frames):
    """Each frame's opaque pixels as (left, top, right, bottom) around its drawing anchor.

    MapIcons draws a frame with its bottom-centre (x = width / 2, y = height - 1) at the anchor.
    """
    boxes = []
    for x, y, w, h in frames:
        alpha = sheet.crop((x, y, x + w, y + h)).getchannel("A")
        left, top, right, bottom = alpha.point(lambda v: 255 if v > SOLID_ALPHA else 0).getbbox()
        boxes.append((left - w / 2, top - h + 1, right - w / 2, bottom - h + 1))
    return boxes


def clear_zoom(a, b, boxes):
    """Lowest zoom from which icons a and b ([frame, lon, lat, dx, dy, ...]) never overlap on screen."""
    (al, at, ar, ab), (bl, bt, br, bb) = boxes[a[0]], boxes[b[0]]
    dlon = (b[1] - a[1] + 180) % 360 - 180
    mid = math.radians((a[2] + b[2]) / 2)
    # Per axis: separation per unit of globe radius (east +x, north -y), the constant icon-pixel
    # offset between the two boxes' centres, and the separation they need.
    axes = (
        (math.radians(dlon) * math.cos(mid), (b[3] + (bl + br) / 2) - (a[3] + (al + ar) / 2),
         (ar - al + br - bl) / 2 + ICON_GAP),
        (-math.radians(b[2] - a[2]), (b[4] + (bt + bb) / 2) - (a[4] + (at + ab) / 2),
         (ab - at + bb - bt) / 2 + ICON_GAP),
    )
    radius = math.inf
    for per_radius, offset, need in axes:
        if abs(per_radius) < 1e-12:
            radius = min(radius, 0 if abs(offset) >= need else math.inf)
        else:
            toward = offset if per_radius > 0 else -offset
            radius = min(radius, max(0.0, (need - toward) / abs(per_radius)))
    if radius == 0:
        return -math.inf
    if radius == math.inf:
        return math.inf
    # 1% margin for the globe's curvature away from the screen centre.
    return math.log2(radius * 1.01 / ICON_PX_PER_RADIAN)


MAX_NUDGE = 40  # icon pixels a capital or landmark may be drawn away from its real site
SIDE_TOLERANCE = 12  # icon pixels at APPEAR_FIRST (about 30 km) under which either side is fair


def nudge(icon, placed, boxes):
    """Draw a capital or landmark beside the capitals and landmarks already placed, not under them.

    Some landmarks lie within a few kilometres of their capital (Meritxell, Trakai, Karlštejn), far
    closer than two icons' width at country zoom. Shift the drawing offset by the shortest move
    that clears every placed icon from APPEAR_FIRST, only ever away from the icon covering it
    most, in the quadrant where the site really lies, so the two keep their real compass relation.
    The longitude and latitude stay the real site. Without a clear spot it takes the move from
    which it can appear earliest.
    """
    blockers = [o for o in placed if clear_zoom(icon, o, boxes) > APPEAR_FIRST]
    if not blockers:
        return
    main = max(blockers, key=lambda o: clear_zoom(icon, o, boxes))
    # Real offset from the covering icon in icon pixels at APPEAR_FIRST (east +x, south +y).
    px = ICON_PX_PER_RADIAN * 2 ** APPEAR_FIRST
    east = math.radians((icon[1] - main[1] + 180) % 360 - 180) * math.cos(math.radians(icon[2])) * px
    south = math.radians(main[2] - icon[2]) * px
    # Keep the real side; an axis on which the two are closer than SIDE_TOLERANCE may use either.
    signs = [[1 if real >= 0 else -1] + ([-1 if real >= 0 else 1] if abs(real) < SIDE_TOLERANCE else [])
             for real in (east, south)]
    moves = sorted(
        ((sx * x, sy * y, (sx != signs[0][0]) + (sy != signs[1][0]))
         for x in range(MAX_NUDGE + 1) for y in range(MAX_NUDGE + 1)
         if 0 < x * x + y * y <= MAX_NUDGE * MAX_NUDGE
         for sx in signs[0] for sy in signs[1]),
        key=lambda m: (m[2], m[0] ** 2 + m[1] ** 2, m))
    best = (max(clear_zoom(icon, o, boxes) for o in placed), 0, 0)
    for x, y, _ in moves:
        trial = icon[:3] + [icon[3] + x, icon[4] + y] + icon[5:]
        clear = max(clear_zoom(trial, o, boxes) for o in placed)
        if clear <= APPEAR_FIRST:
            icon[3], icon[4] = trial[3], trial[4]
            return
        if clear < best[0] - 0.05:  # otherwise, the move that lets it appear earliest
            best = (clear, x, y)
    icon[3] += best[1]
    icon[4] += best[2]


def assign_appearance(icons, boxes):
    """Replace each country-tier icon's priority with the zoom at which it is fully visible.

    Icons are placed in priority order (capital, landmark, large town, town, tree, boat). Each one
    appears at the first zoom step from which it overlaps no icon placed before it that is already
    visible, so once shown it never has to disappear. Continent icons stay visible, except those
    covering a capital or landmark: they get a seventh field, 1, and fade out as the country
    tier fades in. Returns all icons kept and the country icons dropped because they would only
    fit beyond APPEAR_LAST.
    """
    def near(a, b):
        dlon = abs((b[1] - a[1] + 180) % 360 - 180) * math.cos(math.radians(a[2]))
        return abs(b[2] - a[2]) <= NEAR_DEGREES and dlon <= NEAR_DEGREES

    shown = [(icon, -math.inf) for icon in icons if icon[5] == 0]
    kept, dropped = [], []
    for icon in sorted((i for i in icons if i[5] == 1), key=lambda i: i[6]):
        if icon[6][0] <= 1:  # capitals and landmarks: continent decoration makes way
            for other, _ in [s for s in shown if s[0][5] == 0 and near(icon, s[0])]:
                if clear_zoom(icon, other, boxes) > APPEAR_FIRST:
                    other[6:] = [1]
                    shown.remove((other, -math.inf))
            nudge(icon, [o for o, _ in shown if o[5] == 1 and near(icon, o)], boxes)
        appear = APPEAR_FIRST
        for other, other_appear in shown:
            if not near(icon, other):
                continue
            clear = clear_zoom(icon, other, boxes)
            if clear > other_appear:  # the other icon is visible while the two still overlap
                appear = max(appear, clear)
        if appear != math.inf:  # inf: it sits exactly on an icon already shown
            steps = math.ceil(round((appear - APPEAR_FIRST) / APPEAR_STEP, 6))
            appear = round(APPEAR_FIRST + steps * APPEAR_STEP, 1)
        if appear > APPEAR_LAST:
            dropped.append(icon)
            continue
        icon[6] = appear
        shown.append((icon, appear))
        kept.append(icon)
    kept_ids = {id(i) for i in kept}
    return [i for i in icons if i[5] == 0 or id(i) in kept_ids], dropped


def in_bounds(lon, lat, bounds):
    west, south, east, north = bounds
    return south <= lat <= north and (lon >= west or lon <= east if west > east else west <= lon <= east)


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

    def building(kind, lon, lat, dx, dy, seed=0, priority=(4, 0)):
        # The seventh field holds the placement priority until assign_appearance replaces it.
        icons.append([frame_index(kind, seed), round(lon, 4), round(lat, 4), dx, dy, 1, priority])

    for spec in COUNTRY_TIER:
        w, s_, e, n = spec["bounds"]
        # Scan a continuous grid across 180°, then wrap only the output coordinate.
        if w > e:e += 360
        cities = sorted(
            (p for p in places if p["adm0_a3"] == spec["adm0"]
             and in_bounds(p["longitude"], p["latitude"], spec["bounds"])),
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
            # One sprite per place. The capital and the two largest towns appear first; smaller
            # towns alternate between a church and a house as more room opens up (assign_appearance).
            if city["name"] == spec["capital"]:
                building("castle", lon, lat, 0, 0, priority=(0, 0))
            elif rank <= 2:
                building("church", lon, lat, 0, 0, priority=(2, rank))
            else:
                building("church" if rank % 2 else "house", lon, lat, 0, 0, rank, priority=(3, rank))
        for kind, lon, lat in spec.get("landmarks", []):
            building(kind, lon, lat, 0, 0, priority=(1, 0))
            towns.append((lon, lat))
        trees, boats = [], []
        step = spec.get("decoration_grid", GRID)
        for y in range(int((90 - n) / step), int((90 - s_) / step)):
            for x in range(int((w + 180) / step), int((e + 180) / step)):
                lon, lat = -180+(x+.5)*step, 90-(y+.5)*step
                if lon > 180:lon -= 360
                if not in_bounds(lon, lat, spec["bounds"]):
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
        if spec["adm0"] == "RUS":
            # Keep forest decoration in the boreal belt, away from Arctic desert/tundra.
            trees = [(lon, lat) for lon, lat in trees if 50 <= lat <= 64 and lon < 140]
        if "tree_bounds" in spec:
            trees = [(lon, lat) for lon, lat in trees if in_bounds(lon, lat, spec["tree_bounds"])]
        tree_sites = spread(trees, spec.get("trees", 7 if spec["adm0"] == "PRT" else 12),
                            spec.get("decoration_km", 70), 51, towns, spec.get("decoration_km", 45))
        # Italy spans Alpine forests and Mediterranean islands: distribute its seven trees
        # across three latitude bands rather than letting one seeded cluster fill the north.
        if spec["adm0"] == "ITA":
            tree_sites = []
            for south, north, count in ((44, 48, 2), (40, 44, 2), (35, 40, 3)):
                candidates = [t for t in trees if south <= t[1] < north
                              and all(great_circle_km(t, other) >= 70 for other in tree_sites)]
                tree_sites += spread(candidates, count, 70, 51, towns, 45)
        for lon, lat in tree_sites:
            if spec["adm0"] in ("SWE", "NOR", "FIN", "EST", "LVA", "LTU", "RUS"):
                kind = "pine" if lat > 60 or spec["adm0"] in ("EST", "LVA", "LTU", "RUS") else "oak"
                building(kind, lon, lat, 0, 0, int(h01(lon * 9, lat * 9) * 9))
                continue
            if spec["adm0"] == "ITA":
                kind = "pine" if lat >= 44 else "oak" if lat >= 40 else "olive"
                building(kind, lon, lat, 0, 0, int(h01(lon * 9, lat * 9) * 9))
                continue
            if spec["adm0"] in ("DEU", "NLD", "BEL", "GBR", "IRL", "DNK", "CZE", "POL", "LUX", "SVK", "HUN", "SVN", "MDA", "BLR", "UKR"):
                kind = "pine" if (spec["adm0"] in ("DEU", "POL") and lat > 53 or spec["adm0"] in ("GBR", "DNK") and lat > 56
                                  or spec["adm0"] == "SVN" and lat > 46.2 or spec["adm0"] == "BLR" and lat > 54.3
                                  or spec["adm0"] == "UKR" and (lat > 50.8 or lon < 25 and lat < 49)) else "oak"
                building(kind, lon, lat, 0, 0, int(h01(lon * 9, lat * 9) * 9))
                continue
            if spec["adm0"] == "BGR":
                kind = "pine" if lat < 43 and lon < 25 or 42.4 < lat < 43.1 and 24 < lon < 27 else "oak"
                building(kind, lon, lat, 0, 0, int(h01(lon * 9, lat * 9) * 9))
                continue
            if spec["adm0"] == "ROU":
                kind = "pine" if 45.2 < lat < 47.4 and 22 < lon < 26.5 else "oak"
                building(kind, lon, lat, 0, 0, int(h01(lon * 9, lat * 9) * 9))
                continue
            if spec["adm0"] == "HRV":
                # Olives on the Dalmatian coast and islands, pines in Istria, Gorski kotar and Lika, oaks inland.
                kind = "olive" if lat < 44.3 else "pine" if lon < 15.8 and lat < 45.5 else "oak"
                building(kind, lon, lat, 0, 0, int(h01(lon * 9, lat * 9) * 9))
                continue
            if spec["adm0"] == "CYP":
                kind = "pine" if lat > 34.91 and lon < 33.18 else "olive"
                building(kind, lon, lat, 0, 0, int(h01(lon * 9, lat * 9) * 9))
                continue
            if spec["adm0"] == "MNE":
                kind = "olive" if lat < 42.4 else "pine"
                building(kind, lon, lat, 0, 0, int(h01(lon * 9, lat * 9) * 9))
                continue
            if spec["adm0"] == "KOS":
                kind = "pine" if lon < 20.6 else "oak"
                building(kind, lon, lat, 0, 0, int(h01(lon * 9, lat * 9) * 9))
                continue
            if spec["adm0"] == "MKD":
                kind = "pine" if lon < 21.3 or lat > 41.8 else "oak"
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
            # Separate the foreground pine from Vaduz's castle at the fixed icon scale.
            dx = 22 if spec["adm0"] == "LIE" and lat < towns[0][1] else 0
            building(kind, lon, lat, dx, 0, int(h01(lon * 9, lat * 9) * 9))
        if "boat_bounds" in spec:
            bw, bs, be, bn = spec["boat_bounds"]
            boats = [(lon, lat) for lon, lat in boats if bw <= lon <= be and bs <= lat <= bn]
        for lon, lat in spread(boats, spec.get("boats", 2), spec.get("decoration_km", 75)*2, 53):
            building("boat", lon, lat, 0, 0, priority=(5, 0))


    images = [sprites.ICONS[kind](seed) for kind, seed in FRAMES]
    sheet = Image.new("RGBA", (sum(img.width + 1 for img in images), max(img.height for img in images)))
    frames, x = [], 0
    for img in images:
        sheet.alpha_composite(img, (x, 0))
        frames.append([x, 0, img.width, img.height])
        x += img.width + 1
    icons, dropped = assign_appearance(icons, solid_boxes(sheet, frames))
    icons.sort(key=lambda i: (-i[2] + i[4] * 0.01, i[1]))
    sheet.save(SHEET, optimize=True)
    # "omitted": country icons left out because they would only fit beyond APPEAR_LAST. The app
    # ignores them; tests use them to check the builder's site choices separately from placement.
    DATA.write_text(json.dumps(
        {"names": [kind for kind, _ in FRAMES], "frames": frames, "icons": icons,
         "omitted": [icon[:6] for icon in dropped]},
        separators=(",", ":"),
    ) + "\n")
    kinds = {}
    for frame, *_ in icons:
        kinds[FRAMES[frame][0]] = kinds.get(FRAMES[frame][0], 0) + 1
    print(f"{len(icons)} icons, sheet {sheet.size} {SHEET.stat().st_size} bytes:", kinds)
    steps = {}
    for icon in icons:
        if icon[5] == 1:
            steps[icon[6]] = steps.get(icon[6], 0) + 1
    gone = {}
    for frame, *_ in dropped:
        gone[FRAMES[frame][0]] = gone.get(FRAMES[frame][0], 0) + 1
    print("country icons per appearance zoom:", dict(sorted(steps.items())), "dropped:", gone)


if __name__ == "__main__":
    main()
