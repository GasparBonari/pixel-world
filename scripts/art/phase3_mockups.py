"""Phase 3 design mockups: continent-scale pixel art rendered from pinned real geography.

Design tool for the P2-06/Phase 3 art contract (docs/art/ART_CONTRACT.md). It prototypes the
offline raster pipeline from TECHNICAL_PLAN.md and writes review images to docs/art/phase3/.
Nothing here is loaded by the app. Run with the pinned Pillow version:

    python3 scripts/art/phase3_mockups.py
"""

from hashlib import sha256
import json
import math
from pathlib import Path
import urllib.request

from PIL import Image, ImageDraw, ImageFont

import sprites as icon_art  # detailed map icons (scripts/art/sprites.py)

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / ".cache" / "geography"
OUTPUT = ROOT / "docs" / "art" / "phase3"
LOCK = Path(__file__).with_name("phase3-sources.lock.json")
SYSTEM_FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT = ROOT / "node_modules/@expo-google-fonts/pixelify-sans/700Bold/PixelifySans_700Bold.ttf"
REVISION = "ca96624a56bd078437bca8184e78163e5039ad19"
NE = f"https://raw.githubusercontent.com/nvkelso/natural-earth-vector/{REVISION}/geojson"
SOURCES = {
    "land-10m": f"{NE}/ne_10m_land.geojson",
    "lakes-10m": f"{NE}/ne_10m_lakes.geojson",
    "countries-50m": f"{NE}/ne_50m_admin_0_countries.geojson",
    "rivers-10m": f"{NE}/ne_10m_rivers_lake_centerlines.geojson",
    "regions-10m": f"{NE}/ne_10m_geography_regions_polys.geojson",
    "places-10m": f"{NE}/ne_10m_populated_places_simple.geojson",
}

# Shared palette tokens (ART_CONTRACT.md, draft 2: closer to the GlobeQuest concept image).
P = {
    # Night sea: the globe's deep blue, darkened so the map reads like the space scene it zooms from.
    "night": "#16325A", "night_band": "#1D4272", "sea_band": "#25579A", "coast_band": "#2E6DAF",
    "edge_light": "#A8DDEB", "sparkle": "#9FC3E8", "sparkle_core": "#FFFFFF",
    # Raised land: lit top edge, green cliff face below south-facing coasts.
    "land_hi": "#B9DD63", "cliff_top": "#5F8A2C", "cliff": "#41662A",
    "grass": "#8AC240", "grass_dark": "#74AC3D", "grass_light": "#A3CF4E", "forest": "#5FA83C",
    "boreal": "#6FA845", "tundra": "#A9C27E", "dry": "#B4C35A", "sand": "#D1B363", "dune": "#BF9A50",
    "snow": "#F4F6EE", "border": "#EEF5C8", "relief": "#A6A862",
    # Selection glow.
    "glow_in": "#FFD25A", "glow_out": "#F28C2E", "select_fill": "#FFAD3D",
    # Icons (warm outline, upper-left light).
    "outline": "#3A2A20", "leaf_hi": "#B9DD63", "leaf": "#5FA83C", "leaf_dark": "#3F7E32",
    "trunk": "#79543B", "rock_light": "#B88A5A", "rock_shade": "#8A6240", "roof": "#E0394C",
    "wall": "#F4F6EE", "hull": "#A0673E", "cloud": "#FFFFFF", "cloud_shade": "#C8DCEF",
    # Screen furniture: parchment UI, label chips.
    "parchment": "#F3DFB4", "parchment_light": "#FFF3D6", "parchment_edge": "#6B4426",
    "parchment_shadow": "#C9A36B", "ink": "#3A2318", "chip": "#FFFDF5", "button": "#5FA83C",
    # Country scale.
    "salt": "#DDEFF2", "urban": "#C2CF6E",
}
RGB = {k: tuple(int(v[i : i + 2], 16) for i in (1, 3, 5)) for k, v in P.items()}

# Terrain-scale marks only: sea sparkles and the small pin in card rows.
# Map icons (trees, mountains, buildings, boats, map pin) live in scripts/art/sprites.py.
SPRITES = {
    "pin": [
        "..ooooo..", ".oRRRRRo.", "oRRWWWRRo", "oRWWWWWRo", "oRWWWWWRo", "oRRWWWRRo",
        ".oRRRRRo.", "..oRRRo..", "...oRo...", "....o....",
    ],
    "sparkle": ["..s..", "..s..", "ssCss", "..s..", "..s.."],
}
SPRITE_COLORS = {
    "o": RGB["outline"], "k": RGB["outline"], "H": RGB["leaf_hi"], "G": RGB["leaf"],
    "D": RGB["leaf_dark"], "t": RGB["trunk"], "W": RGB["wall"], "L": RGB["rock_light"],
    "S": RGB["rock_shade"], "R": RGB["roof"], "h": RGB["hull"], "s": RGB["sparkle"],
    "C": RGB["sparkle_core"],
}
SNOWLESS = {"hill"}
ART_SCALE = 3  # screen points per terrain pixel (the concept image's chunky ground)
ICON_SCALE = 2  # screen points per icon pixel: icons carry finer detail, as in the concept image
_ICONS = {}


def icon(name, seed=0):
    key = (name, seed)
    if key not in _ICONS:
        img = icon_art.ICONS[name](seed)
        _ICONS[key] = img.resize((img.width * ICON_SCALE, img.height * ICON_SCALE), Image.NEAREST)
    return _ICONS[key]


def place_icons(screen, placements):
    """Paste icons bottom-centre at terrain-pixel anchors, back to front (top of screen first)."""
    for y, x, name, seed in sorted(placements, key=lambda p: (p[2] == "pin", p[0], p[1])):
        img = icon(name, seed)
        sx, sy = x * ART_SCALE + ART_SCALE / 2, (y + 1) * ART_SCALE
        if sy - img.height < CARD_TOP or name == "pin":
            screen.alpha_composite(img, (int(sx - img.width / 2), int(sy - img.height)))
SCREEN = (390, 844)  # phone portrait, points


def load_sources():
    CACHE.mkdir(parents=True, exist_ok=True)
    data = {}
    for name, url in SOURCES.items():
        path = CACHE / f"{name}.source"
        if not path.exists():
            request = urllib.request.Request(url, headers={"User-Agent": "PixelWorld/0.1 design mockups"})
            with urllib.request.urlopen(request, timeout=60) as response:
                path.write_bytes(response.read(20_000_001))
        data[name] = path.read_bytes()
    checksums = {name: sha256(raw).hexdigest() for name, raw in data.items()}
    if LOCK.exists():
        if json.loads(LOCK.read_text()) != checksums:
            raise ValueError("Source checksum mismatch; review before updating phase3-sources.lock.json")
    else:
        LOCK.write_text(json.dumps(checksums, indent=2) + "\n")
    return {name: json.loads(raw) for name, raw in data.items()}


class Ortho:
    """Orthographic projection: the same sphere the globe draws, seen up close."""

    def __init__(self, lon0, lat0, km_per_px, width, height):
        self.l0, self.p0 = math.radians(lon0), math.radians(lat0)
        self.r = 6371 / km_per_px
        self.cx, self.cy = width / 2, height / 2

    def __call__(self, lon, lat, ss=1):
        l, p = math.radians(lon) - self.l0, math.radians(lat)
        x = math.cos(p) * math.sin(l)
        y = math.cos(self.p0) * math.sin(p) - math.sin(self.p0) * math.cos(p) * math.cos(l)
        if math.sin(self.p0) * math.sin(p) + math.cos(self.p0) * math.cos(p) * math.cos(l) < 0:
            n = math.hypot(x, y) or 1  # far side: pin to the horizon so fills stay bounded
            x, y = x / n, y / n
        return ((self.cx + self.r * x) * ss, (self.cy - self.r * y) * ss)

    def inverse(self, px, py):
        x, y = (px - self.cx) / self.r, (self.cy - py) / self.r
        rho = math.hypot(x, y)
        if rho >= 1:
            return None
        c = math.asin(rho)
        if rho == 0:
            return math.degrees(self.l0), math.degrees(self.p0)
        lat = math.asin(math.cos(c) * math.sin(self.p0) + y * math.sin(c) * math.cos(self.p0) / rho)
        lon = self.l0 + math.atan2(
            x * math.sin(c), rho * math.cos(c) * math.cos(self.p0) - y * math.sin(c) * math.sin(self.p0)
        )
        return math.degrees(lon), math.degrees(lat)


def polygons(geometry):
    if geometry["type"] == "Polygon":
        return [geometry["coordinates"]]
    if geometry["type"] == "MultiPolygon":
        return geometry["coordinates"]
    return []


def lines(geometry):
    if geometry["type"] == "LineString":
        return [geometry["coordinates"]]
    if geometry["type"] == "MultiLineString":
        return geometry["coordinates"]
    return []


def raster_mask(features, project, width, height, ss=4, keep_tiny=False):
    """Supersampled polygon fill, then a majority vote per art pixel for clean stepped edges."""
    big = Image.new("L", (width * ss, height * ss))
    draw = ImageDraw.Draw(big)
    tiny = []
    for feature in features:
        for polygon in polygons(feature["geometry"]):
            ring = [project(lon, lat, ss) for lon, lat, *_ in polygon[0]]
            draw.polygon(ring, fill=255)
            for hole in polygon[1:]:
                draw.polygon([project(lon, lat, ss) for lon, lat, *_ in hole], fill=0)
            xs, ys = [p[0] / ss for p in ring], [p[1] / ss for p in ring]
            if keep_tiny and max(xs) - min(xs) < 3 and max(ys) - min(ys) < 3:
                tiny.append((sum(xs) / len(xs), sum(ys) / len(ys)))
    small = big.resize((width, height), Image.BOX).point(lambda v: 255 if v >= 128 else 0)
    # Islands too small to win a pixel keep one, so small countries stay visible and selectable.
    for x, y in tiny:
        if 0 <= x < width and 0 <= y < height:
            small.putpixel((int(x), int(y)), 255)
    return small


def distance(mask, width, height, source_value):
    """Chamfer (3-4) distance in art pixels from pixels equal to source_value.

    Octagonal contours read as rounded, stepped bands; Manhattan distance makes diamonds.
    Pixels touching a source pixel (including diagonally) have distance 1.
    """
    far = 1 << 30
    data = mask.load()
    d = [[0 if (data[x, y] > 0) == source_value else far for x in range(width)] for y in range(height)]
    for y in range(height):
        for x in range(width):
            v = d[y][x]
            if x: v = min(v, d[y][x - 1] + 3)
            if y:
                v = min(v, d[y - 1][x] + 3)
                if x: v = min(v, d[y - 1][x - 1] + 4)
                if x + 1 < width: v = min(v, d[y - 1][x + 1] + 4)
            d[y][x] = v
    for y in range(height - 1, -1, -1):
        for x in range(width - 1, -1, -1):
            v = d[y][x]
            if x + 1 < width: v = min(v, d[y][x + 1] + 3)
            if y + 1 < height:
                v = min(v, d[y + 1][x] + 3)
                if x + 1 < width: v = min(v, d[y + 1][x + 1] + 4)
                if x: v = min(v, d[y + 1][x - 1] + 4)
            d[y][x] = v
    return [[(v + 2) // 3 for v in row] for row in d]


def hash2(ix, iy, seed=0):
    n = (ix * 374761393 + iy * 668265263 + seed * 2246822519) & 0xFFFFFFFF
    n = ((n ^ (n >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((n ^ (n >> 16)) & 0xFFFFFFFF) / 4294967296


def value_noise(x, y, seed):
    ix, iy = math.floor(x), math.floor(y)
    fx, fy = x - ix, y - iy
    fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    top = hash2(ix, iy, seed) * (1 - fx) + hash2(ix + 1, iy, seed) * fx
    bottom = hash2(ix, iy + 1, seed) * (1 - fx) + hash2(ix + 1, iy + 1, seed) * fx
    return top * (1 - fy) + bottom * fy


def fbm(x, y, seed):
    return 0.6 * value_noise(x, y, seed) + 0.3 * value_noise(2 * x, 2 * y, seed + 1) + 0.1 * value_noise(4 * x, 4 * y, seed + 2)


def stamp(image, name, x, y, colors=SPRITE_COLORS):
    """Draw a sprite with its bottom-centre at (x, y)."""
    rows = SPRITES[name]
    left, top = x - len(rows[0]) // 2, y - len(rows) + 1
    for dy, row in enumerate(rows):
        for dx, key in enumerate(row):
            px, py = left + dx, top + dy
            if key != "." and 0 <= px < image.width and 0 <= py < image.height:
                image.putpixel((px, py), colors[key])


def shade(color, amount):
    """amount > 0 lightens toward white, < 0 darkens toward black."""
    target = 255 if amount > 0 else 0
    return tuple(int(c + (target - c) * abs(amount)) for c in color)


FONT_REGULAR = ROOT / "node_modules/@expo-google-fonts/pixelify-sans/400Regular/PixelifySans_400Regular.ttf"


def art_size():
    return SCREEN[0] // ART_SCALE, -(-SCREEN[1] // ART_SCALE)


def paint_sea(px, land_px, water_dist, width, height):
    """Night sea in stepped bands; a pale 1-pixel edge where water meets land."""
    for y in range(height):
        for x in range(width):
            if not land_px[x, y]:
                d = water_dist[y][x]
                px[x, y] = RGB[
                    "edge_light" if d == 1 else "coast_band" if d <= 3 else "sea_band" if d <= 6
                    else "night_band" if d <= 11 else "night"
                ]


def raise_land(px, land_px, width, height):
    """Game-board relief: lit top edges, and a two-pixel green cliff below south-facing coasts."""
    for y in range(height):
        for x in range(width):
            if land_px[x, y]:
                if (y > 0 and not land_px[x, y - 1]) or (x > 0 and not land_px[x - 1, y]):
                    px[x, y] = RGB["land_hi"]
            elif y >= 1 and land_px[x, y - 1]:
                px[x, y] = RGB["cliff_top"]
            elif y >= 2 and land_px[x, y - 2]:
                px[x, y] = RGB["cliff"]


def spread(candidates, count, spacing, seed):
    """Deterministic, evenly spaced picks; candidates are (x, y, lon, lat)."""
    chosen = []
    for x, y, lon, lat in sorted(candidates, key=lambda c: hash2(round(c[2] * 20), round(c[3] * 20), seed)):
        if len(chosen) >= count:
            break
        if all(math.hypot(x - a, y - b) >= spacing for a, b in chosen):
            chosen.append((x, y))
    return chosen


def cloud(image, cx, cy, w):
    """Puffy pixel cloud: round top, flat shaded base, no outline (like the concept image)."""
    puffs = [(-0.32, 0.02, 0.2), (-0.1, -0.12, 0.27), (0.16, -0.08, 0.24), (0.36, 0.04, 0.17)]
    base = cy + 0.12 * w
    for y in range(int(cy - 0.45 * w), int(base) + 1):
        for x in range(int(cx - 0.6 * w), int(cx + 0.6 * w) + 1):
            if 0 <= x < image.width and 0 <= y < image.height and any(
                math.hypot(x - (cx + dx * w), y - (cy + dy * w)) <= r * w for dx, dy, r in puffs
            ):
                image.putpixel((x, y), RGB["cloud_shade"] if y >= base - 1 else RGB["cloud"])


def sea_decor(image, proj, land_px, water_dist, width, height, clouds=2):
    """Sparkles and dots on open water, then clouds; all seeded from world position."""
    for y in range(2, height - 2):
        for x in range(2, width - 2):
            if water_dist[y][x] < 6 or land_px[x, y]:
                continue
            geo = proj.inverse(x, y)
            if not geo:
                continue
            roll = hash2(round(geo[0] * proj.r / 57.3), round(geo[1] * proj.r / 57.3), 21)  # ~1 art px cells
            if roll < 0.0012 and all(water_dist[y + dy][x + dx] >= 4 for dx in (-2, 2) for dy in (-2, 2)):
                stamp(image, "sparkle", x, y + 2)
            elif roll < 0.004:
                image.putpixel((x, y), RGB["sparkle"])
    candidates = [
        (x, y, *proj.inverse(x, y)) for y in range(10, height - 30, 4) for x in range(0, width, 4)
        if water_dist[y][x] >= 8 and proj.inverse(x, y)
    ]
    for x, y in spread(candidates, clouds, 50, 23):
        cloud(image, x, y, 26)


def font(size, bold=True):
    return ImageFont.truetype(str(FONT if bold else FONT_REGULAR), size)


def parchment_box(draw, box, radius=6):
    x0, y0, x1, y1 = box
    draw.rounded_rectangle((x0 + 2, y0 + 4, x1 + 2, y1 + 4), radius, fill=RGB["parchment_shadow"])
    draw.rounded_rectangle(box, radius, fill=RGB["parchment"], outline=RGB["parchment_edge"], width=3)
    draw.rounded_rectangle((x0 + 4, y0 + 4, x1 - 4, y1 - 4), max(1, radius - 3), outline=RGB["parchment_light"], width=2)


def draw_header(image, title):
    """Title banner with back and settings buttons, as in the concept's map screens."""
    draw = ImageDraw.Draw(image)
    parchment_box(draw, (14, 50, 54, 90))
    draw.polygon([(24, 70), (34, 60), (34, 66), (44, 66), (44, 74), (34, 74), (34, 80)], fill=RGB["ink"])
    f = font(22)
    left, top, right, bottom = draw.textbbox((0, 0), title, font=f)
    w = right - left + 56
    x0 = (SCREEN[0] - w) // 2
    for side in (-1, 1):  # ribbon tails behind the banner
        tx = x0 - 8 if side < 0 else x0 + w - 12
        draw.polygon([(tx, 58), (tx + 20, 58), (tx + 20, 88), (tx, 88), (tx + (8 if side < 0 else 12), 73)],
                     fill=RGB["parchment_shadow"], outline=RGB["parchment_edge"])
    parchment_box(draw, (x0, 48, x0 + w, 92), radius=4)
    draw.text((SCREEN[0] / 2, 70), title, font=f, fill=RGB["ink"], anchor="mm")
    cx, cy = 356, 70  # gear: ring, eight teeth, hub
    for i in range(8):
        a = i * math.pi / 4
        tx, ty = cx + math.cos(a) * 15, cy + math.sin(a) * 15
        draw.rectangle((tx - 4, ty - 4, tx + 4, ty + 4), fill=RGB["parchment"], outline=RGB["parchment_edge"], width=2)
    draw.ellipse((cx - 13, cy - 13, cx + 13, cy + 13), fill=RGB["parchment"], outline=RGB["parchment_edge"], width=3)
    draw.ellipse((cx - 5, cy - 5, cx + 5, cy + 5), fill=RGB["parchment_edge"])


def draw_chip(image, text, pin):
    """White name chip beside the pin; flips left near the screen edge."""
    draw = ImageDraw.Draw(image)
    f = font(17)
    left, top, right, bottom = draw.textbbox((0, 0), text, font=f)
    w, h = right - left + 20, bottom - top + 14
    x0, y0 = pin[0] + 16, pin[1] - h // 2 - 8
    if x0 + w > SCREEN[0] - 8:
        x0 = pin[0] - 16 - w
    draw.rounded_rectangle((x0 + 2, y0 + 3, x0 + w + 2, y0 + h + 3), 6, fill=(20, 30, 50))
    draw.rounded_rectangle((x0, y0, x0 + w, y0 + h), 6, fill=RGB["chip"], outline=RGB["ink"], width=2)
    draw.text((x0 + w / 2, y0 + h / 2), text, font=f, fill=RGB["ink"], anchor="mm")


CARD_TOP = 612


def draw_card(image, card):
    """Bottom parchment card. Content is factual; progress panels arrive with saved visits (Phase 5/6)."""
    draw = ImageDraw.Draw(image)
    box = (12, CARD_TOP, SCREEN[0] - 12, SCREEN[1] - 18)
    parchment_box(draw, box, radius=8)
    draw.text((30, CARD_TOP + 30), card["title"], font=font(24), fill=RGB["ink"], anchor="lm")
    if card.get("subtitle"):
        draw.text((30, CARD_TOP + 56), card["subtitle"], font=font(14, False), fill=RGB["parchment_edge"], anchor="lm")
    y = CARD_TOP + 86
    for label, value in card["rows"]:
        image.paste(pin_icon(), (30, y - 9))
        draw.text((52, y), label, font=font(15, False), fill=RGB["ink"], anchor="lm")
        draw.text((SCREEN[0] - 30, y), value, font=font(15), fill=RGB["ink"], anchor="rm")
        draw.line((30, y + 15, SCREEN[0] - 30, y + 15), fill=RGB["parchment_shadow"], width=1)
        y += 32
    bx0, by0, bx1, by1 = 30, box[3] - 62, SCREEN[0] - 30, box[3] - 20
    draw.rounded_rectangle((bx0, by0 + 4, bx1, by1 + 4), 6, fill=RGB["leaf_dark"])
    draw.rounded_rectangle((bx0, by0, bx1, by1), 6, fill=RGB["button"], outline=RGB["outline"], width=2)
    draw.text(((bx0 + bx1) / 2 - 8, (by0 + by1) / 2), card["button"], font=font(18), fill=RGB["wall"], anchor="mm")
    cx, cy = bx1 - 26, (by0 + by1) / 2
    draw.polygon([(cx - 4, cy - 8), (cx + 4, cy), (cx - 4, cy + 8)], fill=RGB["wall"])


def pin_icon():
    rows = SPRITES["pin"]
    icon = Image.new("RGBA", (len(rows[0]), len(rows)))
    for y, row in enumerate(rows):
        for x, key in enumerate(row):
            if key != ".":
                icon.putpixel((x, y), (*SPRITE_COLORS[key], 255))
    return icon.resize((icon.width * 2, icon.height * 2), Image.NEAREST)


def finish(image, name, *, title, card, chip, pin_art, icons, attribution=None):
    """Scale terrain to screen points, add icons, then the screen-space chip, header and card."""
    scaled = image.resize((image.width * ART_SCALE, image.height * ART_SCALE), Image.NEAREST)
    scaled = scaled.crop((0, 0, *SCREEN)).convert("RGBA")
    place_icons(scaled, icons + [(pin_art[1], pin_art[0], "pin", 0)])
    pin_h = icon("pin").height
    draw_chip(scaled, chip, (pin_art[0] * ART_SCALE + ART_SCALE / 2, (pin_art[1] + 1) * ART_SCALE - pin_h * 0.62))
    draw_header(scaled, title)
    draw_card(scaled, card)
    if attribution:
        draw = ImageDraw.Draw(scaled)
        system = ImageFont.truetype(SYSTEM_FONT, 10)
        draw.text((14, CARD_TOP - 10), attribution, font=system, fill=RGB["edge_light"], anchor="lm")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    scaled.convert("RGB").save(OUTPUT / f"{name}.png", optimize=True)
    return scaled.convert("RGB")


def climate(lon, lat):
    """Decorative climate tint seeded from world coordinates (not measured land cover)."""
    band = lat + (fbm(lon / 3, lat / 3, 7) - 0.5) * 5
    if band > 67:
        return RGB["tundra"]
    if band > 57:
        return RGB["boreal"]
    if band > 40:
        return RGB["grass"]
    if band > 33.5:
        return RGB["dry"]
    return RGB["dune"] if (lon * 0.8 + lat * 1.7 + fbm(lon, lat, 5) * 2) % 1 < 0.12 else RGB["sand"]


def render_continent(sources, *, center, km_per_px, selected, title, card, name):
    width, height = art_size()
    proj = Ortho(center[0], center[1], km_per_px, width, height)
    land = raster_mask(sources["land-10m"]["features"], proj, width, height, keep_tiny=True)
    lakes = raster_mask(
        [f for f in sources["lakes-10m"]["features"] if (f["properties"].get("scalerank") or 9) <= 4],
        proj, width, height,
    )
    countries = Image.new("I", (width, height))
    draw = ImageDraw.Draw(countries)
    features = sources["countries-50m"]["features"]
    for index, feature in enumerate(features, start=1):
        for polygon in polygons(feature["geometry"]):
            draw.polygon([proj(lon, lat) for lon, lat, *_ in polygon[0]], fill=index)
    land_px, lake_px, country_px = land.load(), lakes.load(), countries.load()
    water_dist = distance(land, width, height, True)
    image = Image.new("RGB", (width, height))
    px = image.load()
    paint_sea(px, land_px, water_dist, width, height)
    forest = []

    for y in range(height):
        for x in range(width):
            if not land_px[x, y]:
                continue
            lon, lat = proj.inverse(x + 0.5, y + 0.5)
            if lake_px[x, y]:
                px[x, y] = RGB["coast_band"]
                continue
            color = climate(lon, lat)
            # Puzzle-map tone: each country is a slightly different green.
            tone = (hash2(country_px[x, y], 0, 13) - 0.5) * 0.16
            color = shade(color, tone)
            patch = fbm(lon / 1.4, lat / 1.0, 3)
            if patch > 0.62 and 40 < lat < 67:
                color = RGB["forest"]
                forest.append((x, y, lon, lat))
            elif hash2(x, y, 11) < 0.025:
                color = RGB["grass_light"] if hash2(x, y, 12) < 0.5 else RGB["grass_dark"]
            px[x, y] = color

    # Pale borders between countries, 1 pixel, never on the coast.
    for y in range(height - 1):
        for x in range(width - 1):
            c = country_px[x, y]
            if land_px[x, y] and c and any(
                land_px[nx, ny] and country_px[nx, ny] and country_px[nx, ny] != c
                for nx, ny in ((x + 1, y), (x, y + 1))
            ):
                px[x, y] = RGB["border"]

    raise_land(px, land_px, width, height)

    # Selected country: warm fill and a two-step glow around it.
    target = next(i for i, f in enumerate(features, start=1) if f["properties"]["NAME"] == selected["country"])
    chosen = [(x, y) for y in range(height) for x in range(width) if land_px[x, y] and country_px[x, y] == target]
    sx, sy = (int(v) for v in proj(*selected["capital"]))
    if not chosen:
        chosen = [(sx, sy)]
    halo = {}
    for x, y in chosen:
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                d = max(abs(dx), abs(dy))
                if d and (x + dx, y + dy) not in chosen:
                    halo[(x + dx, y + dy)] = min(halo.get((x + dx, y + dy), 9), d)
    for (x, y), d in halo.items():
        if 0 <= x < width and 0 <= y < height:
            px[x, y] = RGB["glow_in"] if d == 1 else RGB["glow_out"] if d == 2 else shade(px[x, y], 0.25)
    for x, y in chosen:
        px[x, y] = RGB["select_fill"]
    if len(chosen) < 40:
        # Tiny countries (Malta is a few pixels) also get a ring, so the selection still reads.
        mx = sum(x for x, _ in chosen) / len(chosen)
        my = sum(y for _, y in chosen) / len(chosen)
        for y in range(int(my) - 9, int(my) + 10):
            for x in range(int(mx) - 9, int(mx) + 10):
                r = math.hypot(x - mx, y - my)
                if 0 <= x < width and 0 <= y < height and 6.5 <= r < 8.5:
                    px[x, y] = RGB["glow_in"] if r < 7.5 else RGB["glow_out"]

    # Few, large icons: snowy mountains on major ranges, tree clumps in forest patches.
    icons = []
    for feature in sources["regions-10m"]["features"]:
        props = feature["properties"]
        if props["FEATURECLA"] != "Range/mtn" or props["SCALERANK"] > 4:
            continue
        mask = raster_mask([feature], proj, width, height).load()
        cells = [(x, y, *proj.inverse(x, y)) for y in range(height) for x in range(width)
                 if mask[x, y] and land_px[x, y] and proj.inverse(x, y)]
        count = max(1, min(3, len(cells) // 140)) if cells else 0
        sprite = "mountain" if props["SCALERANK"] <= 3 else "hill"
        icons += [(y, x, sprite, int(x * 7 + y)) for x, y in spread(cells, count, 14, 31)]
    for x, y in spread(forest, 8, 22, 41):
        kind = "pine" if proj.inverse(x, y)[1] > 55 else "tree"
        icons += [(y - 1, x - 3, kind, 1), (y - 1, x + 3, kind, 2), (y + 1.5, x, kind, 3)]

    sea_decor(image, proj, land_px, water_dist, width, height)
    return finish(image, name, title=title, card=card, chip=selected["country"], pin_art=(sx, sy),
                  icons=icons)


OSM_EXTRACT = ROOT / ".cache" / "osm" / "malta-261108.osm.pbf"
OSM_SHA256 = "19bdaf3ad2d14c3197fba20e800407c3e1b7c950c6d210177eed6c91e380fe13"
OSM_URL = "https://download.geofabrik.de/europe/malta-261108.osm.pbf"
# OSM tag -> art class. Later classes in CLASS_ORDER paint over earlier ones.
CLASSES = {
    ("landuse", "farmland"): "farm", ("landuse", "meadow"): "farm", ("landuse", "orchard"): "farm",
    ("landuse", "vineyard"): "farm", ("landuse", "farmyard"): "farm",
    ("landuse", "greenhouse_horticulture"): "farm",
    ("natural", "scrub"): "scrub", ("natural", "heath"): "scrub", ("natural", "grassland"): "scrub",
    ("landuse", "grass"): "scrub", ("natural", "bare_rock"): "rock",
    ("leisure", "park"): "park", ("leisure", "garden"): "park", ("leisure", "golf_course"): "park",
    ("natural", "wood"): "wood", ("landuse", "forest"): "wood",
    ("landuse", "residential"): "urban", ("landuse", "commercial"): "urban",
    ("landuse", "retail"): "urban", ("landuse", "industrial"): "urban",
    ("landuse", "construction"): "urban", ("landuse", "salt_pond"): "salt",
    ("natural", "water"): "water", ("landuse", "reservoir"): "water", ("natural", "beach"): "beach",
    ("natural", "sand"): "beach",
}
CLASS_ORDER = ["farm", "scrub", "rock", "park", "wood", "urban", "salt", "water", "beach"]
ROADS = {"motorway", "trunk", "primary", "secondary"}


def load_malta():
    """Read the pinned Geofabrik extract (ODbL) into plain lists of lon/lat geometry."""
    import osmium  # Only the country mockup needs pyosmium (scripts/art/requirements.txt).

    if not OSM_EXTRACT.exists():
        OSM_EXTRACT.parent.mkdir(parents=True, exist_ok=True)
        request = urllib.request.Request(OSM_URL, headers={"User-Agent": "PixelWorld/0.1 design mockups"})
        with urllib.request.urlopen(request, timeout=120) as response:
            OSM_EXTRACT.write_bytes(response.read(30_000_001))
    if sha256(OSM_EXTRACT.read_bytes()).hexdigest() != OSM_SHA256:
        raise ValueError("Malta extract checksum mismatch")
    data = {"land": [], "areas": {c: [] for c in CLASS_ORDER}, "roads": [], "ferries": [], "places": []}

    def rings(area):
        out = []
        for outer in area.outer_rings():
            out.append([[[n.lon, n.lat] for n in outer]] + [
                [[n.lon, n.lat] for n in inner] for inner in area.inner_rings(outer)
            ])
        return out

    for obj in osmium.FileProcessor(str(OSM_EXTRACT)).with_areas().with_locations():
        tags = dict(obj.tags)
        if obj.is_area():
            if tags.get("place") in ("island", "islet") or tags.get("natural") == "coastline":
                data["land"].append({"geometry": {"type": "MultiPolygon", "coordinates": rings(obj)}})
            for key in ("landuse", "natural", "leisure"):
                art = CLASSES.get((key, tags.get(key)))
                if art:
                    data["areas"][art].append({"geometry": {"type": "MultiPolygon", "coordinates": rings(obj)}})
                    break
        elif obj.is_way():
            coords = [[n.lon, n.lat] for n in obj.nodes if n.location.valid()]
            if tags.get("highway") in ROADS:
                data["roads"].append(coords)
            elif tags.get("route") == "ferry" and len(coords) > 1:
                # Domestic crossings only; long international routes clutter the country view.
                km = sum(
                    math.hypot((b[0] - a[0]) * 111 * math.cos(math.radians(a[1])), (b[1] - a[1]) * 111)
                    for a, b in zip(coords, coords[1:])
                )
                if km < 20:
                    data["ferries"].append(coords)
        elif obj.is_node() and tags.get("place") in ("city", "town"):
            data["places"].append({
                "name": tags.get("name:en") or tags.get("name"), "kind": tags["place"],
                "population": int(tags.get("population", "0").replace(",", "") or 0),
                "lon": obj.location.lon, "lat": obj.location.lat,
            })
    return data


def render_country(osm, *, center, km_per_px, capital, title, card, name):
    width, height = art_size()
    proj = Ortho(center[0], center[1], km_per_px, width, height)
    land = raster_mask(osm["land"], proj, width, height, keep_tiny=True)
    land_px = land.load()
    water_dist = distance(land, width, height, True)

    classes = Image.new("L", (width, height))
    draw = ImageDraw.Draw(classes)
    for index, art in enumerate(CLASS_ORDER, start=1):
        for feature in osm["areas"][art]:
            for polygon in polygons(feature["geometry"]):
                ring = [proj(lon, lat) for lon, lat in polygon[0]]
                xs, ys = [p[0] for p in ring], [p[1] for p in ring]
                if art in ("water", "salt") and max(xs) - min(xs) < 3 and max(ys) - min(ys) < 3:
                    continue  # ponds and pools smaller than ~3 art px would read as blue noise
                draw.polygon(ring, fill=index)
                for hole in polygon[1:]:
                    draw.polygon([proj(lon, lat) for lon, lat in hole], fill=0)
    class_px = classes.load()

    image = Image.new("RGB", (width, height))
    px = image.load()
    paint_sea(px, land_px, water_dist, width, height)
    greenery, scrub = [], []
    for y in range(height):
        for x in range(width):
            if not land_px[x, y]:
                continue
            art = CLASS_ORDER[class_px[x, y] - 1] if class_px[x, y] else None
            lon, lat = proj.inverse(x + 0.5, y + 0.5)
            # Bright patchwork, as in the concept's country map; OSM classes shift the tone.
            field = hash2(math.floor(lon * 45), math.floor(lat * 45), 61)
            color = RGB["grass_light"] if field < 0.35 else RGB["grass"]
            if art == "farm" and (x + y) % 5 == 0:
                color = RGB["grass_dark"]
            elif art in ("scrub", "rock"):
                color = RGB["grass_dark"] if hash2(x, y, 71) < 0.75 else RGB["dry"]
                scrub.append((x, y, lon, lat))
            elif art in ("wood", "park"):
                color = RGB["forest"]
                greenery.append((x, y, lon, lat))
            elif art == "urban":
                color = RGB["urban"] if hash2(x, y, 72) < 0.85 else RGB["dry"]
            elif art == "water":
                color = RGB["coast_band"]
            elif art == "salt":
                color = RGB["salt"] if (x + y) % 2 else RGB["edge_light"]
            elif art == "beach":
                color = RGB["sand"]
            px[x, y] = color
    raise_land(px, land_px, width, height)

    for line in osm["ferries"]:
        pts = [proj(lon, lat) for lon, lat in line]
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            steps = max(1, int(max(abs(x1 - x0), abs(y1 - y0))))
            for i in range(steps):
                x, y = int(x0 + (x1 - x0) * i / steps), int(y0 + (y1 - y0) * i / steps)
                if 0 <= x < width and 0 <= y < height and water_dist[y][x] > 1 and (x + y) % 4 < 2:
                    px[x, y] = RGB["edge_light"]

    sea_decor(image, proj, land_px, water_dist, width, height)

    # Icons: trees in woods and parks (a few on scrub), houses for towns, a castle for the other city.
    icons = [(y, x, "tree", i) for i, (x, y) in enumerate(spread(greenery, 10, 8, 81) + spread(scrub, 6, 14, 82))]
    cx, cy = (int(v) for v in proj(*capital["lonlat"]))
    placed = [(cx, cy)]
    churches = 0
    for place in sorted(osm["places"], key=lambda p: (p["kind"] != "city", -p["population"], p["name"])):
        if place["name"] == capital["name"]:
            continue
        x, y = (int(v) for v in proj(place["lon"], place["lat"]))
        if 0 <= x < width and 0 <= y < height and land_px[x, y] and all(
            math.hypot(x - a, y - b) >= 13 for a, b in placed
        ):
            placed.append((x, y))
            # Cities get a castle; the largest towns a parish church; other towns a house pair.
            if place["kind"] == "city":
                icons.append((y, x, "castle", 0))
            elif churches < 3:
                icons.append((y, x, "church", 0))
                churches += 1
            else:
                icons += [(y, x - 2, "house", 0), (y + 1, x + 2, "house", 1)]

    boats = [
        (x, y, *proj.inverse(x, y)) for y in range(20, CARD_TOP // ART_SCALE - 8, 3)
        for x in range(6, width - 6, 3) if 5 <= water_dist[y][x] <= 14
    ]
    icons += [(y, x, "boat", 0) for x, y in spread(boats, 2, 45, 95)]
    return finish(image, name, title=title, card=card, chip=capital["name"], pin_art=(cx, cy),
                  icons=icons, attribution="© OpenStreetMap contributors")


def detail_crop(image, box, factor, name):
    crop = image.crop(box)
    crop.resize((crop.width * factor, crop.height * factor), Image.NEAREST).save(
        OUTPUT / f"{name}.png", optimize=True
    )


def main():
    sources = load_sources()
    europe = render_continent(
        sources, center=(6, 45), km_per_px=20, title="Europe", name="europe-continent",
        selected={"country": "Malta", "capital": (14.5146, 35.8989)},
        card={"title": "Malta", "subtitle": "Southern Europe · island country",
              "rows": [("Capital", "Valletta"), ("Main islands", "Malta, Gozo, Comino")],
              "button": "Explore Malta"},
    )
    detail_crop(europe, (120, 300, 360, 540), 2, "europe-continent-detail")
    malta = render_country(
        load_malta(), center=(14.385, 35.9), km_per_px=0.29, title="Malta", name="malta-country",
        capital={"name": "Valletta", "lonlat": (14.5146, 35.8989)},
        card={"title": "Valletta", "subtitle": "Capital city · Grand Harbour",
              "rows": [("Detailed city map", "Coming soon"), ("Ferry", "Malta – Gozo")],
              "button": "Explore Valletta"},
    )
    detail_crop(malta, (150, 230, 390, 470), 2, "malta-country-detail")
    print("wrote", sorted(p.name for p in OUTPUT.glob("*.png")))


if __name__ == "__main__":
    main()
