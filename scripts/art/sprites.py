"""Original map icons for Pixel World, built from simple shapes with pixel-art shading rules.

Each function returns an RGBA image whose bottom-centre pixel is the icon's ground anchor.
Rules (ART_CONTRACT.md): light from the upper left; 3-4 tones per material; a darker outline
in each material's own hue; a soft ground shadow (semi-transparent black) under the icon.
Deterministic: the same seed always gives the same icon.

Preview: .venv/bin/python scripts/art/sprites.py  ->  docs/art/phase3/sprites.png
"""

import math
from pathlib import Path

from PIL import Image


def hex_rgb(value):
    return tuple(int(value[i : i + 2], 16) for i in (1, 3, 5))


C = {k: hex_rgb(v) for k, v in {
    # Foliage
    "leaf_hi": "#D4EC7A", "leaf_lt": "#9BD04A", "leaf": "#62AC3C", "leaf_dk": "#3E7F34",
    "leaf_ol": "#22472A",
    "pine_lt": "#5FA86A", "pine": "#3E8550", "pine_dk": "#2A5E3C",
    "bark_lt": "#A7764A", "bark": "#79543B", "bark_ol": "#3A2A20",
    # Rock and snow
    "rock_hi": "#D9B07A", "rock_lt": "#C2925E", "rock": "#9A6E46", "rock_dk": "#714E33",
    "rock_ol": "#4A3222", "snow": "#FFFFFF", "snow_sh": "#CFE0EE", "grass_tuft": "#6FB443",
    # Buildings
    "wall_hi": "#FFFFFF", "wall": "#F3EEE3", "wall_sh": "#D6CCBC", "wall_dk": "#B5A894",
    "wall_ol": "#4E4038", "roof_hi": "#FF7F78", "roof": "#E2434E", "roof_sh": "#B32F40",
    "roof_ol": "#5A1E28", "window": "#3D4A6B", "glass": "#7FA8D8", "door": "#6B4630",
    "gold": "#F2C14E",
    # Boat
    "sail": "#FFFFFF", "sail_sh": "#D3DEE9", "hull_lt": "#B7804F", "hull": "#8A5A36",
    "hull_ol": "#3A2A20", "foam": "#E4F4FA", "flag": "#E2434E",
    # Pin
    "pin_hi": "#FF8E8E", "pin": "#E8404A", "pin_sh": "#A82634", "pin_ol": "#4A1A20",
}.items()}
SHADOW = (0, 0, 0, 70)
LIGHT = (-0.55, -0.6, 0.58)  # upper-left, towards the viewer
BAYER = [[0, 2], [3, 1]]


class Sprite:
    """A small pixel grid: painted cells, per-cell outline colour, and ground shadow."""

    def __init__(self, width, height):
        self.w, self.h = width, height
        self.px = {}  # (x, y) -> rgb
        self.ol = {}  # (x, y) -> outline rgb for this material
        self.shadow = set()

    def put(self, x, y, color, outline):
        x, y = int(x), int(y)
        if 0 <= x < self.w and 0 <= y < self.h:
            self.px[(x, y)] = color
            self.ol[(x, y)] = outline

    def image(self):
        img = Image.new("RGBA", (self.w, self.h))
        for x, y in self.shadow:
            if 0 <= x < self.w and 0 <= y < self.h:
                img.putpixel((x, y), SHADOW)
        # Outline: empty cells touching a painted cell take that material's outline colour.
        for (x, y), _ in list(self.px.items()):
            if self.ol[(x, y)] is None:  # this material opts out of outlining (fine grass blades)
                continue
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if (nx, ny) not in self.px and 0 <= nx < self.w and 0 <= ny < self.h:
                    img.putpixel((nx, ny), (*self.ol[(x, y)], 255))
        for (x, y), color in self.px.items():
            img.putpixel((x, y), (*color, 255))
        return img


def h01(*values):
    n = 2166136261
    for v in values:
        n = ((n ^ (int(v) & 0xFFFFFFFF)) * 16777619) & 0xFFFFFFFF
    # Final avalanche (murmur3 fmix32): small, similar inputs still spread over [0, 1).
    n ^= n >> 16
    n = (n * 0x85EBCA6B) & 0xFFFFFFFF
    n ^= n >> 13
    n = (n * 0xC2B2AE35) & 0xFFFFFFFF
    n ^= n >> 16
    return n / 4294967296


def ground_shadow(s, cx, cy, rx, ry=1.2):
    for y in range(int(cy - ry - 1), int(cy + ry + 2)):
        for x in range(int(cx - rx - 1), int(cx + rx + 2)):
            if ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 <= 1:
                s.shadow.add((x, y))


def lit(nx, ny):
    nz = math.sqrt(max(0.0, 1 - nx * nx - ny * ny))
    lx, ly, lz = LIGHT
    n = math.sqrt(lx * lx + ly * ly + lz * lz)
    return (nx * lx + ny * ly + nz * lz) / n


def tree(seed=0):
    """Round broadleaf tree: clumped canopy, dithered shading, leaf specks, two-tone trunk."""
    s = Sprite(15, 17)
    ground_shadow(s, 7.5, 15.4, 5.5)
    for y in range(11, 16):
        s.put(6, y, C["bark_lt"], C["bark_ol"])
        s.put(7, y, C["bark"], C["bark_ol"])
    s.put(5, 15, C["bark_lt"], C["bark_ol"])
    s.put(8, 15, C["bark"], C["bark_ol"])
    j = h01(seed, 1) - 0.5
    clumps = [(7.5 + j, 5.6, 4.9), (4.4, 8.4, 3.7), (10.6 + j, 8.6, 3.6), (7.5, 9.6, 3.6)]
    tones = ["leaf_dk", "leaf", "leaf_lt", "leaf_hi"]
    for y in range(s.h):
        for x in range(s.w):
            best = None
            for cx, cy, r in clumps:
                d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
                if d <= r and (best is None or (cy - r) < best[1] - best[2]):
                    best = (cx, cy, r)
            if not best:
                continue
            cx, cy, r = best
            value = lit((x + 0.5 - cx) / r, (y + 0.5 - cy) / r)
            value += (BAYER[y % 2][x % 2] / 4 - 0.375) * 0.28  # ordered dither at tone edges
            value += (h01(seed, x, y) - 0.5) * 0.12  # leafy irregularity
            tone = 0 if value < 0.25 else 1 if value < 0.55 else 2 if value < 0.82 else 3
            s.put(x, y, C[tones[tone]], C["leaf_ol"])
    return s.image()


def pine(seed=0):
    """Conifer: three stacked tiers, lit left edge, dark right flank."""
    s = Sprite(13, 18)
    ground_shadow(s, 6.5, 16.4, 4.5)
    for y in range(13, 17):
        s.put(6, y, C["bark"], C["bark_ol"])
    for top, bottom, half in ((1, 7, 3.5), (4, 11, 5), (7, 14, 6)):
        for y in range(top, bottom + 1):
            width = half * (y - top + 1) / (bottom - top + 1)
            for x in range(s.w):
                dx = x + 0.5 - 6.5
                if abs(dx) <= width:
                    side = dx / max(width, 0.5)
                    tone = "pine_lt" if side < -0.35 else "pine_dk" if side > 0.4 or y == bottom else "pine"
                    if y == bottom and side < -0.2:
                        tone = "pine"
                    s.put(x, y, C[tone], C["leaf_ol"])
    return s.image()


def mountain(seed=0, snow=True, width=21, height=18, cap=None):
    """Multi-peak mountain: lit west faces, shaded east faces, ridge lines, jagged snow caps."""
    s = Sprite(width, height)
    base = height - 2
    ground_shadow(s, width / 2, base + 0.6, width / 2 - 1, 1.1)
    peaks = [(width * 0.52, base - 15, 1.45), (width * 0.22, base - 8.5, 1.3), (width * 0.8, base - 9.5, 1.35)]
    peaks = [(px + (h01(seed, i) - 0.5) * 1.5, py, sl) for i, (px, py, sl) in enumerate(peaks)]
    for y in range(height):
        for x in range(width):
            cx = x + 0.5
            owner, top = None, None
            for px, py, slope in peaks:
                t = py + abs(cx - px) * slope
                if top is None or t < top:
                    owner, top = (px, py, slope), t
            if y + 0.5 < top or y > base:
                continue
            px, py, slope = owner
            depth = y + 0.5 - py
            east = cx > px + depth * 0.18 * (1 if h01(seed, int(depth)) > 0.3 else 0)
            # Faces: lit west, shaded east; deep shade at the far east flank and the foot.
            if east:
                tone = "rock_dk" if cx - px > depth * 0.75 or y >= base - 1 else "rock"
            else:
                tone = "rock_hi" if px - cx < depth * 0.35 and depth < 6 else "rock_lt"
                if h01(seed, x, y) < 0.12:
                    tone = "rock"  # strata specks
            if abs(cx - (px + depth * 0.18)) < 0.6 and depth > 2:
                tone = "rock_dk"  # ridge line from the summit
            snowline = (base - py) * 0.42 + (1 if h01(seed, x) > 0.5 else 0)
            if snow and depth < snowline:
                tone = "snow_sh" if east else "snow"
            elif cap == "grass" and depth < (base - py) * 0.55 + (1 if h01(seed, x) > 0.5 else 0):
                tone = "leaf_dk" if east else "leaf_hi" if depth < 2 and not east else "leaf_lt"
            if y == base and h01(seed, x, 9) < 0.45:
                tone = "grass_tuft"
            s.put(x, y, C[tone], C["rock_ol"])
    return s.image()


def hill(seed=0):
    """Low grassy hill with a rocky foot, for minor ranges."""
    return mountain(seed, snow=False, width=17, height=12, cap="grass")


def _box(s, x0, y0, x1, y1, lit_cols=1, shade_cols=1):
    """Whitewashed wall: lit west column, shaded east columns."""
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            tone = "wall_hi" if x < x0 + lit_cols else "wall_sh" if x > x1 - shade_cols else "wall"
            if y == y1:
                tone = "wall_dk" if x > x1 - shade_cols else "wall_sh"
            s.put(x, y, C[tone], C["wall_ol"])


def _cone(s, cx, top, base_y, half):
    """Conical tower roof: highlight streak, lit west half, shaded east half."""
    for y in range(top, base_y + 1):
        w = half * (y - top + 1) / (base_y - top + 1)
        for x in range(int(cx - w - 0.5), int(cx + w + 1.5)):
            dx = x + 0.5 - cx
            if abs(dx) <= w + 0.25:
                tone = "roof_sh" if dx > 0.3 else "roof_hi" if -1.4 < dx <= -0.4 and y < base_y else "roof"
                s.put(x, y, C[tone], C["roof_ol"])


def _gable(s, x0, x1, top, base_y):
    """Pitched roof seen from the front: two slopes meeting at the ridge."""
    cx = (x0 + x1 + 1) / 2
    for y in range(top, base_y + 1):
        w = (cx - x0 + 0.5) * (y - top + 1) / (base_y - top + 1)
        for x in range(x0 - 1, x1 + 2):
            dx = x + 0.5 - cx
            if abs(dx) <= w:
                tone = "roof_sh" if dx > 0 else "roof_hi" if y == base_y or abs(dx) > w - 1 else "roof"
                s.put(x, y, C[tone], C["roof_ol"])


def _tower(s, x0, x1, top, bottom, roof_top):
    _box(s, x0, top, x1, bottom)
    _cone(s, (x0 + x1 + 1) / 2, roof_top, top - 1, (x1 - x0 + 3) / 2)
    mid = (x0 + x1) // 2
    s.put(mid, top + 2, C["window"], C["wall_ol"])
    s.put(mid, top + 3, C["window"], C["wall_ol"])


def castle(seed=0):
    """Whitewashed castle: keep with flag, two cone-roofed towers, crenellated wall, gate."""
    s = Sprite(27, 24)
    ground_shadow(s, 13.5, 22.4, 12, 1.3)
    # Curtain wall with crenellations and arched gate.
    _box(s, 4, 14, 22, 21, lit_cols=1, shade_cols=2)
    for x in range(4, 23, 2):
        s.put(x, 13, C["wall_hi" if x < 12 else "wall_sh"], C["wall_ol"])
    for y in range(17, 22):
        for x in range(12, 15):
            if not (y == 17 and x != 13):
                s.put(x, y, C["door"], C["wall_ol"])
    for x in (7, 18):
        s.put(x, 16, C["window"], C["wall_ol"])
    # Keep with gable roof, windows and flag.
    _box(s, 9, 8, 17, 15, lit_cols=2, shade_cols=2)
    _gable(s, 9, 17, 3, 7)
    for x in (11, 15):
        s.put(x, 10, C["glass"], C["wall_ol"])
        s.put(x, 11, C["window"], C["wall_ol"])
    for y in range(0, 3):
        s.put(13, y, C["bark_ol"], C["bark_ol"])
    s.put(14, 0, C["flag"], C["roof_ol"])
    s.put(15, 0, C["flag"], C["roof_ol"])
    s.put(14, 1, C["flag"], C["roof_ol"])
    # Side towers.
    _tower(s, 1, 5, 9, 21, 3)
    _tower(s, 21, 25, 10, 21, 4)
    return s.image()


def church(seed=0):
    """Parish church: nave with red roof, bell tower with dome and gold cross, rose window."""
    s = Sprite(19, 25)
    ground_shadow(s, 9.5, 23.4, 8.5, 1.2)
    _box(s, 2, 15, 16, 22, lit_cols=2, shade_cols=3)
    _gable(s, 2, 16, 10, 14)
    for y in range(19, 23):
        for x in range(8, 11):
            if not (y == 19 and x != 9):
                s.put(x, y, C["door"], C["wall_ol"])
    s.put(9, 16, C["glass"], C["wall_ol"])
    s.put(5, 18, C["window"], C["wall_ol"])
    s.put(13, 18, C["window"], C["wall_ol"])
    # Bell tower rising behind the façade, with a red dome and gold cross.
    _box(s, 7, 5, 11, 11, lit_cols=1, shade_cols=1)
    s.put(9, 7, C["window"], C["wall_ol"])
    s.put(9, 8, C["window"], C["wall_ol"])
    for y, half in ((3, 1.6), (4, 2.6)):
        for x in range(7, 12):
            dx = x + 0.5 - 9.5
            if abs(dx) <= half:
                s.put(x, y, C["roof_sh" if dx > 0.4 else "roof_hi" if dx < -0.6 else "roof"], C["roof_ol"])
    s.put(9, 0, C["gold"], C["bark_ol"])
    s.put(9, 1, C["gold"], C["bark_ol"])
    s.put(8, 1, C["gold"], C["bark_ol"])
    s.put(10, 1, C["gold"], C["bark_ol"])
    s.put(9, 2, C["gold"], C["bark_ol"])
    return s.image()


def house(seed=0):
    """Small whitewashed house with a red gable roof, door, window and chimney."""
    s = Sprite(13, 13)
    ground_shadow(s, 6.5, 11.4, 5.5, 1.0)
    _box(s, 2, 6, 10, 11, lit_cols=1, shade_cols=2)
    _gable(s, 2, 10, 1, 5)
    for y in range(8, 12):
        s.put(5, y, C["door"], C["wall_ol"])
    s.put(8, 8, C["glass"], C["wall_ol"])
    s.put(8, 9, C["window"], C["wall_ol"])
    s.put(9, 2, C["wall_dk"], C["wall_ol"])
    s.put(9, 1, C["wall_sh"], C["wall_ol"])
    return s.image()


def sailboat(seed=0):
    """Sailboat: shaded mainsail and jib, mast with pennant, planked hull, foam at the waterline."""
    s = Sprite(17, 19)
    for x in range(1, 16):
        if h01(seed, x) < 0.75:
            s.shadow.add((x, 17))
    for y in range(1, 14):
        s.put(8, y, C["bark_ol"], C["bark_ol"])
    s.put(9, 1, C["flag"], C["roof_ol"])
    s.put(10, 1, C["flag"], C["roof_ol"])
    s.put(9, 2, C["flag"], C["roof_ol"])
    for y in range(3, 13):  # mainsail, east of the mast, bellied
        w = (y - 2) * 0.62
        for x in range(9, 9 + int(w) + 1):
            s.put(x, y, C["sail_sh" if x - 9 > w * 0.6 else "sail"], C["wall_ol"])
    for y in range(6, 13):  # jib, west of the mast
        w = (y - 5) * 0.55
        for x in range(int(7 - w), 8):
            s.put(x, y, C["sail"], C["wall_ol"])
    for y, (x0, x1) in ((13, (2, 15)), (14, (3, 14)), (15, (4, 13))):
        for x in range(x0, x1 + 1):
            tone = "hull_lt" if y == 13 else "hull"
            s.put(x, y, C[tone], C["hull_ol"])
    for x in range(1, 17):
        if h01(seed, x, 3) < 0.6:
            s.put(x, 16, C["foam"], C["foam"])
    return s.image()


def pin(seed=0):
    """Map pin: glossy red head with a white centre, pointed tip, small shadow."""
    s = Sprite(13, 17)
    ground_shadow(s, 6.5, 15.5, 3, 0.9)
    cx, cy, r = 6.5, 5.5, 5.2
    for y in range(s.h):
        for x in range(s.w):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            d = math.hypot(dx, dy)
            in_tip = y >= 8 and abs(dx) <= (14.5 - y) * 0.55
            if d <= r or in_tip:
                if d <= 2.3:
                    tone = "wall_hi" if dx + dy < 0 else "wall"
                else:
                    v = lit(max(-1, min(1, dx / r)), max(-1, min(1, dy / r)))
                    tone = "pin_hi" if v > 0.8 else "pin" if v > 0.3 else "pin_sh"
                s.put(x, y, C[tone], C["pin_ol"])
    return s.image()


# --- Continent flora and fauna ---------------------------------------------------------------
# Built from shaded shapes. Animals stand in profile facing left, lit from the upper left;
# far legs use the material's dark tones, near legs its mid tones.


def ramp(base, outline=None):
    """Four tones (dark, mid, light, highlight) and an outline from one base colour."""
    c = hex_rgb(base)

    def mix(t):
        target = 255 if t > 0 else 0
        return tuple(int(v + (target - v) * abs(t)) for v in c)

    return [mix(-0.32), c, mix(0.2), mix(0.4)], hex_rgb(outline) if outline else mix(-0.72)


def blob(s, cx, cy, rx, ry, palette, pattern=None, dither=True, clip=None):
    """Shaded ellipse. pattern(x, y, nx, ny, tone) may return a colour to override."""
    tones, outline = palette
    for y in range(int(cy - ry - 1), int(cy + ry + 2)):
        for x in range(int(cx - rx - 1), int(cx + rx + 2)):
            nx, ny = (x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry
            if nx * nx + ny * ny > 1 or (clip and not clip(x, y)):
                continue
            v = lit(nx, ny) + ((BAYER[y % 2][x % 2] / 4 - 0.375) * 0.22 if dither else 0)
            tone = 0 if v < 0.25 else 1 if v < 0.55 else 2 if v < 0.82 else 3
            color = (pattern(x, y, nx, ny, tone) if pattern else None) or tones[tone]
            s.put(x, y, color, outline)


def limb(s, x, y0, y1, palette, far=False, hoof=None, width=1):
    """A straight leg; far legs are darker. hoof colours the bottom pixel."""
    tones, outline = palette
    for y in range(y0, y1 + 1):
        for dx in range(width):
            color = tones[0] if far else (tones[2] if dx == 0 and width > 1 else tones[1])
            s.put(x + dx, y, hoof if hoof and y == y1 else color, outline)


def dots(s, points, color, outline):
    for x, y in points:
        s.put(x, y, color, outline)


def line(s, x0, y0, x1, y1, color, outline):
    steps = max(1, int(max(abs(x1 - x0), abs(y1 - y0))))
    for i in range(steps + 1):
        s.put(round(x0 + (x1 - x0) * i / steps), round(y0 + (y1 - y0) * i / steps), color, outline)


INK = hex_rgb("#1E1A1A")
EYE_SHINE = hex_rgb("#FFFFFF")


def eye(s, x, y, outline):
    s.put(x, y, INK, outline)


def deer(seed=0):
    """Red deer stag: branching antlers, pale belly and rump."""
    s = Sprite(22, 19)
    coat, belly, antler = ramp("#A8683A"), hex_rgb("#EAD6B4"), ramp("#DCC49A", "#5A4632")
    ground_shadow(s, 12, 17.6, 7)
    limb(s, 8, 12, 17, coat, far=True, hoof=INK)
    limb(s, 16, 12, 17, coat, far=True, hoof=INK)
    blob(s, 12.5, 10.5, 6.8, 3.2, coat, lambda x, y, nx, ny, t: belly if ny > 0.45 or nx > 0.82 else None)
    limb(s, 10, 12, 17, coat, hoof=INK)
    limb(s, 18, 12, 17, coat, hoof=INK)
    blob(s, 6.5, 8.0, 1.8, 3.2, coat)
    blob(s, 4.3, 5.6, 2.8, 1.8, coat)
    dots(s, [(1, 6), (2, 6)], ramp("#A8683A")[0][0], coat[1])
    eye(s, 4, 5, coat[1])
    dots(s, [(6, 4), (7, 3)], coat[0][0], coat[1])  # ear
    tines = [(1, 0), (3, 0), (6, 0), (8, 0), (2, 1), (3, 1), (6, 1), (7, 1), (3, 2), (6, 2), (4, 3), (5, 3)]
    dots(s, tines, antler[0][2], antler[1])
    return s.image()


def fox(seed=0):
    """Red fox: pointed ears, white chest, black socks, bushy tail with a white tip."""
    s = Sprite(22, 15)
    coat, white = ramp("#DE7A2E"), hex_rgb("#F6F0E6")
    sock = hex_rgb("#3A2620")
    ground_shadow(s, 11, 13.6, 7)
    limb(s, 7, 10, 13, coat, far=True, hoof=sock)
    limb(s, 13, 10, 13, coat, far=True, hoof=sock)
    blob(s, 18.0, 7.6, 3.6, 2.0, coat, lambda x, y, nx, ny, t: white if nx > 0.55 else None)  # tail
    blob(s, 10.5, 8.6, 5.0, 2.4, coat, lambda x, y, nx, ny, t: white if ny > 0.5 and nx < -0.2 else None)
    limb(s, 8, 10, 13, coat, hoof=sock)
    limb(s, 14, 10, 13, coat, hoof=sock)
    blob(s, 5.0, 6.4, 2.8, 2.1, coat, lambda x, y, nx, ny, t: white if ny > 0.35 else None)
    dots(s, [(1, 7), (2, 7)], coat[0][1], coat[1])
    s.put(0, 7, INK, coat[1])
    eye(s, 4, 6, coat[1])
    dots(s, [(5, 3), (5, 4), (7, 3), (7, 4)], coat[0][0], coat[1])  # ears
    return s.image()


def elephant(seed=0):
    """African elephant: big flapping ear, curled trunk, ivory tusk."""
    s = Sprite(26, 21)
    hide, ivory = ramp("#8F969E"), hex_rgb("#F4EEDA")
    ground_shadow(s, 14, 19.6, 10)
    for x in (9, 18):
        limb(s, x, 14, 19, hide, far=True, width=2)
    blob(s, 15.0, 10.5, 8.5, 5.5, hide)
    for x in (11, 20):
        limb(s, x, 14, 19, hide, width=3)
    blob(s, 6.5, 8.0, 3.6, 3.8, hide)  # head
    blob(s, 9.2, 8.2, 2.6, 4.2, ramp("#7C838C"))  # ear
    for y in range(9, 17):  # trunk
        s.put(3 if y < 14 else 2, y, hide[0][1] if y % 3 else hide[0][0], hide[1])
    dots(s, [(2, 17), (3, 17)], hide[0][1], hide[1])
    dots(s, [(5, 12), (4, 13), (4, 14)], ivory, hide[1])
    eye(s, 5, 7, hide[1])
    s.put(24, 10, hide[0][0], hide[1])  # tail
    s.put(24, 11, INK, hide[1])
    return s.image()


def zebra(seed=0):
    """Plains zebra: bold black stripes on white, standing mane, dark muzzle."""
    s = Sprite(22, 18)
    coat = ([hex_rgb("#C9CDD2"), hex_rgb("#E9EBEE"), hex_rgb("#F7F8F8"), hex_rgb("#FFFFFF")], hex_rgb("#2A2A30"))
    stripe = hex_rgb("#26262C")

    def stripes(x, y, nx, ny, tone):
        return stripe if (x + y // 2) % 3 == 0 else None

    ground_shadow(s, 12, 16.6, 7)
    limb(s, 9, 11, 16, coat, far=True, hoof=INK)
    limb(s, 16, 11, 16, coat, far=True, hoof=INK)
    blob(s, 13.0, 9.5, 6.5, 3.0, coat, stripes)
    limb(s, 10, 11, 16, coat, hoof=INK)
    limb(s, 17, 11, 16, coat, hoof=INK)
    for y in (12, 14):
        dots(s, [(10, y), (17, y)], stripe, coat[1])
    blob(s, 7.0, 6.6, 1.9, 3.4, coat, lambda x, y, nx, ny, t: stripe if y % 2 == 0 else None)
    blob(s, 4.4, 4.2, 2.9, 1.7, coat, lambda x, y, nx, ny, t: stripe if x == 5 else None)
    dots(s, [(1, 5), (2, 5), (1, 4)], stripe, coat[1])
    eye(s, 4, 3, coat[1])
    for x, y in ((6, 2), (7, 3), (8, 4), (8, 5)):  # mane
        s.put(x, y, stripe, coat[1])
    s.put(20, 9, stripe, coat[1])
    s.put(20, 10, stripe, coat[1])
    return s.image()


def panda(seed=0):
    """Giant panda: white body, black legs and shoulder band, eye patches, round ears."""
    s = Sprite(22, 16)
    white = ([hex_rgb("#D6D8D4"), hex_rgb("#EFF0EC"), hex_rgb("#FAFAF7"), hex_rgb("#FFFFFF")], hex_rgb("#2B2B33"))
    black = ramp("#33333D", "#15151A")
    ground_shadow(s, 11, 14.6, 8)
    limb(s, 7, 10, 14, black, far=True, width=2)
    limb(s, 15, 10, 14, black, far=True, width=2)
    blob(s, 12.0, 8.5, 6.5, 3.8, white,
         lambda x, y, nx, ny, t: black[0][1 if t else 0] if -0.55 < nx < -0.05 else None)
    limb(s, 9, 10, 14, black, width=2)
    limb(s, 17, 10, 14, black, width=2)
    blob(s, 5.0, 6.0, 3.6, 3.1, white)
    dots(s, [(3, 5), (4, 6), (6, 5), (7, 6)], black[0][1], white[1])
    s.put(3, 6, EYE_SHINE, white[1])
    dots(s, [(2, 2), (3, 2), (7, 2), (8, 2)], black[0][1], white[1])
    s.put(1, 7, INK, white[1])
    return s.image()


def big_cat(base, belly, mark, pattern_kind):
    s = Sprite(24, 15)
    coat = ramp(base)
    ground_shadow(s, 12, 13.6, 8)

    def pattern(x, y, nx, ny, tone):
        if ny > 0.5:
            return belly
        if pattern_kind == "stripes" and (x + y) % 4 == 0 and ny < 0.4:
            return mark
        if pattern_kind == "rosettes" and (x * 3 + y * 5) % 7 == 0:
            return mark
        return None

    limb(s, 8, 10, 13, coat, far=True)
    limb(s, 16, 10, 13, coat, far=True)
    for x, y in ((19, 8), (20, 7), (21, 6), (22, 6), (23, 7)):  # tail
        s.put(x, y, coat[0][1] if x < 23 else mark, coat[1])
    blob(s, 12.5, 8.5, 6.5, 2.5, coat, pattern)
    limb(s, 9, 10, 13, coat, width=2)
    limb(s, 17, 10, 13, coat, width=2)
    blob(s, 5.0, 6.4, 3.0, 2.4, coat, lambda x, y, nx, ny, t: belly if ny > 0.4 else (
        mark if pattern_kind == "stripes" and x in (5, 6) and y < 6 else None))
    dots(s, [(3, 3), (6, 3)], coat[0][0], coat[1])
    eye(s, 4, 5, coat[1])
    s.put(2, 7, INK, coat[1])
    return s


def tiger(seed=0):
    """Bengal tiger: orange coat, black stripes, white belly and muzzle."""
    return big_cat("#E8892E", hex_rgb("#F6EAD8"), hex_rgb("#23180F"), "stripes").image()


def jaguar(seed=0):
    """Jaguar: golden coat with dark rosettes."""
    return big_cat("#DDAA48", hex_rgb("#F2E2BC"), hex_rgb("#3A2814"), "rosettes").image()


def bison(seed=0):
    """American bison: huge shaggy shoulder hump, dark head, short curved horns."""
    s = Sprite(24, 18)
    coat, shag = ramp("#7A5236"), ramp("#4E3424")
    horn = hex_rgb("#E8DCC0")
    ground_shadow(s, 12, 16.6, 9)
    limb(s, 8, 12, 16, shag, far=True, width=2)
    limb(s, 17, 12, 16, coat, far=True, width=2)
    blob(s, 15.0, 10.5, 6.5, 3.4, coat)
    blob(s, 9.0, 8.5, 4.8, 5.0, shag)  # hump and mane
    limb(s, 10, 12, 16, shag, width=2)
    limb(s, 19, 12, 16, coat, width=2)
    blob(s, 4.5, 10.0, 2.8, 2.8, shag)
    dots(s, [(3, 7), (2, 6)], horn, shag[1])
    eye(s, 4, 9, shag[1])
    dots(s, [(3, 13), (4, 13), (5, 13)], shag[0][0], shag[1])  # beard
    s.put(22, 10, INK, coat[1])
    return s.image()


def moose(seed=0):
    """Moose: long legs, shoulder hump, broad palmate antlers, hanging dewlap."""
    s = Sprite(24, 22)
    coat, antler = ramp("#5E4232"), ramp("#CFB68E", "#5A4632")
    ground_shadow(s, 12, 20.6, 8)
    limb(s, 9, 13, 20, coat, far=True)
    limb(s, 17, 13, 20, coat, far=True)
    blob(s, 13.5, 10.5, 7.0, 3.6, coat)
    limb(s, 11, 13, 20, coat, width=2)
    limb(s, 19, 13, 20, coat, width=2)
    blob(s, 7.0, 8.5, 2.2, 3.0, coat)
    blob(s, 4.0, 8.5, 3.4, 2.0, coat)
    dots(s, [(1, 9), (1, 10), (2, 10)], coat[0][0], coat[1])  # drooping muzzle
    dots(s, [(5, 11), (5, 12)], coat[0][0], coat[1])  # dewlap
    eye(s, 5, 8, coat[1])
    for x in range(3, 11):  # palmate antlers
        for y in range(4, 7):
            if (y == 4 and x % 2 == 0) or y > 4:
                s.put(x, y, antler[0][2 if y == 5 else 1], antler[1])
    return s.image()


def capybara(seed=0):
    """Capybara: barrel body, short legs, blunt square head, small ears."""
    s = Sprite(20, 13)
    coat = ramp("#9C6C45")
    ground_shadow(s, 10, 11.6, 7)
    limb(s, 6, 9, 11, coat, far=True, width=2)
    limb(s, 13, 9, 11, coat, far=True, width=2)
    blob(s, 11.0, 7.0, 7.0, 3.4, coat)
    limb(s, 8, 9, 11, coat, width=2)
    limb(s, 15, 9, 11, coat, width=2)
    blob(s, 4.0, 6.0, 3.4, 2.4, coat)
    dots(s, [(1, 6), (1, 7)], coat[0][0], coat[1])
    eye(s, 4, 5, coat[1])
    s.put(6, 3, coat[0][0], coat[1])
    return s.image()


def kangaroo(seed=0):
    """Red kangaroo: upright on big hind feet, thick tail, tall ears, pale belly."""
    s = Sprite(20, 22)
    coat, belly = ramp("#C47A46"), hex_rgb("#EBCBA2")
    ground_shadow(s, 10, 20.6, 7)
    for x, y in ((14, 18), (15, 19), (16, 19), (17, 20), (18, 20)):  # tail on the ground
        s.put(x, y, coat[0][0], coat[1])
    blob(s, 10.5, 13.5, 4.2, 5.8, coat, lambda x, y, nx, ny, t: belly if nx < -0.3 and ny > -0.4 else None)
    blob(s, 11.5, 17.5, 3.0, 2.5, coat)  # haunch
    for x in range(5, 12):
        s.put(x, 20, coat[0][0] if x > 8 else coat[0][1], coat[1])  # long hind foot
    blob(s, 7.5, 5.5, 2.6, 2.2, coat)
    dots(s, [(4, 6), (5, 6)], coat[0][1], coat[1])
    s.put(4, 6, INK, coat[1])
    eye(s, 7, 5, coat[1])
    dots(s, [(8, 1), (8, 2), (9, 2), (9, 3)], coat[0][0], coat[1])  # ears
    dots(s, [(7, 11), (6, 12)], coat[0][1], coat[1])  # short arm
    return s.image()


def kiwi(seed=0):
    """Kiwi: round shaggy brown body, long thin bill, stubby legs."""
    s = Sprite(18, 13)
    plumage, bill = ramp("#7E5C3C"), hex_rgb("#E2D2A6")
    ground_shadow(s, 10, 11.6, 6)
    limb(s, 9, 9, 11, ramp("#C9A27A"), width=1)
    limb(s, 12, 9, 11, ramp("#C9A27A"), far=True)
    blob(s, 10.5, 6.0, 5.5, 4.0, plumage,
         lambda x, y, nx, ny, t: plumage[0][0] if (x + y * 2) % 5 == 0 and t < 3 else None)
    line(s, 5, 6, 0, 9, bill, hex_rgb("#6B5A3A"))
    eye(s, 6, 5, plumage[1])
    return s.image()


def penguin(seed=0):
    """Emperor penguin: upright, black back, white front, golden neck patch, orange bill."""
    s = Sprite(14, 21)
    back = ramp("#2E3442", "#121520")
    front = hex_rgb("#F6F7F4")
    gold, orange = hex_rgb("#F2C14E"), hex_rgb("#F2913A")
    ground_shadow(s, 7, 19.6, 4.5)
    blob(s, 7.0, 12.5, 4.6, 7.0, back,
         lambda x, y, nx, ny, t: front if nx < 0.15 and ny > -0.55 else None)
    blob(s, 6.5, 4.5, 3.0, 2.8, back)
    dots(s, [(5, 6), (5, 7), (6, 7)], gold, back[1])
    dots(s, [(2, 5), (3, 5)], orange, back[1])
    eye(s, 5, 4, back[1])
    s.put(5, 3, EYE_SHINE, back[1])
    dots(s, [(5, 19), (6, 19), (8, 19), (9, 19)], orange, back[1])
    dots(s, [(10, 10), (11, 12), (11, 13)], back[0][0], back[1])  # flipper
    return s.image()


def seal(seed=0):
    """Weddell seal lying on the ice: long spotted body, flippers, whiskered face."""
    s = Sprite(24, 12)
    coat = ramp("#7D8A99")
    spot = hex_rgb("#55606C")
    ground_shadow(s, 12, 10.6, 10, 1.0)
    blob(s, 13.0, 7.0, 9.5, 3.0, coat,
         lambda x, y, nx, ny, t: spot if (x * 5 + y * 3) % 11 == 0 and ny < 0.5 else None)
    blob(s, 4.5, 6.0, 3.0, 2.4, coat)
    dots(s, [(21, 9), (22, 10), (23, 10), (22, 8)], coat[0][0], coat[1])  # tail flippers
    dots(s, [(9, 10), (10, 10)], coat[0][0], coat[1])
    eye(s, 3, 5, coat[1])
    s.put(1, 6, INK, coat[1])
    s.put(2, 7, coat[0][3], coat[1])
    return s.image()


# Plants and landforms.

def canopy_tree(tones, trunk, clumps, size, trunk_rows, seed=0, trunk_x=(6, 7)):
    s = Sprite(*size)
    ground_shadow(s, size[0] / 2, size[1] - 1.6, size[0] / 2 - 2)
    for y in trunk_rows:
        s.put(trunk_x[0], y, trunk[0][2], trunk[1])
        s.put(trunk_x[1], y, trunk[0][1], trunk[1])
    for cx, cy, rx, ry in clumps:
        blob(s, cx, cy, rx, ry, tones,
             lambda x, y, nx, ny, t: tones[0][min(3, t + 1)] if h01(seed, x, y) < 0.08 else None)
    return s


def olive(seed=0):
    """Olive tree: twisted grey trunk, silvery green canopy."""
    s = canopy_tree(ramp("#7E9A60", "#2E4030"), ramp("#8A7A62"),
                    [(5, 7, 4, 3.2), (10, 6.5, 4, 3.4), (7.5, 4.5, 4, 2.8)], (15, 16), range(9, 15), seed)
    s.put(5, 12, ramp("#8A7A62")[0][2], ramp("#8A7A62")[1])
    s.put(8, 11, ramp("#8A7A62")[0][1], ramp("#8A7A62")[1])
    return s.image()


def acacia(seed=0):
    """Umbrella thorn acacia: flat wide crown on a thin forked trunk."""
    s = Sprite(21, 16)
    leaves, bark = ramp("#8DB548", "#2E4520"), ramp("#7A5A3E")
    ground_shadow(s, 10.5, 14.4, 5)
    for x0, y0, x1, y1 in ((10, 14, 10, 9), (10, 9, 6, 5), (10, 9, 14, 5), (10, 11, 12, 7)):
        line(s, x0, y0, x1, y1, bark[0][1], bark[1])
    blob(s, 10.5, 4.0, 9.5, 2.4, leaves)
    blob(s, 7.0, 2.6, 4.5, 1.6, leaves)
    return s.image()


def baobab(seed=0):
    """Baobab: massive bottle trunk with a sparse crown of stubby branches."""
    s = Sprite(17, 19)
    bark, leaves = ramp("#A58C70"), ramp("#7FA84A", "#2E4520")
    ground_shadow(s, 8.5, 17.4, 6)
    blob(s, 8.5, 11.5, 4.2, 6.5, bark,
         lambda x, y, nx, ny, t: bark[0][0] if x % 3 == 0 and t < 2 else None)
    for x0, y0, x1, y1 in ((6, 5, 3, 2), (8, 5, 8, 1), (10, 5, 13, 2), (7, 5, 5, 1), (9, 5, 11, 1)):
        line(s, x0, y0, x1, y1, bark[0][1], bark[1])
    for cx, cy in ((3, 1.5), (8, 1), (13, 1.5)):
        blob(s, cx, cy, 2.2, 1.4, leaves)
    return s.image()


def palm(seed=0):
    """Coconut palm: leaning ringed trunk, long drooping fronds, coconuts."""
    s = Sprite(23, 21)
    trunk, fronds = ramp("#A8804E"), ramp("#5FAE44", "#22472A")
    ground_shadow(s, 11, 19.4, 4)
    lean = 1 if seed % 2 else -1
    for i, y in enumerate(range(19, 6, -1)):
        x = round(11 + lean * (19 - y) * 0.2)
        s.put(x, y, trunk[0][1] if i % 2 else trunk[0][2], trunk[1])
        s.put(x + 1, y, trunk[0][0], trunk[1])
    tx, ty = round(11 + lean * 13 * 0.2), 6
    for angle, length in ((-175, 10), (-145, 9), (-115, 6), (-65, 6), (-35, 9), (-5, 10)):
        a = math.radians(angle)
        for i in range(1, length + 1):
            droop = (i / length) ** 2 * 5
            x = tx + 0.5 + math.cos(a) * i
            y = ty + math.sin(a) * i * 0.55 + droop
            s.put(x, y, fronds[0][3 if i < 3 else 2 if i < length * 0.6 else 1], fronds[1])
            if i < length - 1:
                s.put(x, y + 1, fronds[0][0 if i % 2 else 1], fronds[1])
    dots(s, [(tx, ty + 1), (tx + 1, ty + 1), (tx, ty + 2)], hex_rgb("#6B4630"), trunk[1])
    return s.image()


def bamboo(seed=0):
    """Bamboo grove: jointed green stalks of different heights with leaf sprays."""
    s = Sprite(15, 20)
    stalk, leaves = ramp("#7CB04A", "#25471F"), ramp("#5FA83C", "#22472A")
    ground_shadow(s, 7.5, 18.4, 5.5)
    for x, top in ((3, 4), (6, 1), (9, 3), (12, 6)):
        for y in range(top, 19):
            node = (y - top) % 4 == 3
            s.put(x, y, stalk[0][0] if node else stalk[0][2], stalk[1])
            s.put(x + 1, y, stalk[0][0] if node else stalk[0][1], stalk[1])
        for dy, side in ((1, -1), (5, 1), (9, -1)):
            if top + dy < 16:
                line(s, x + (0 if side < 0 else 1), top + dy, x + side * 3, top + dy - 1, leaves[0][2], leaves[1])
    return s.image()


def eucalyptus(seed=0):
    """Eucalyptus: tall pale trunk, loose blue-green crown in separate clumps."""
    s = canopy_tree(ramp("#6E9C80", "#24402F"), ramp("#D8CDB6", "#5A4E3E"),
                    [(5, 5, 3.4, 2.6), (10.5, 3.8, 3.4, 2.6), (8, 8.2, 3.0, 2.2)], (16, 19), range(8, 18), seed,
                    trunk_x=(7, 8))
    return s.image()


def fern(seed=0):
    """New Zealand tree fern: slim dark trunk, crown of arching fronds."""
    s = Sprite(19, 19)
    trunk, fronds = ramp("#5A4232"), ramp("#4E9A4A", "#1E3D22")
    ground_shadow(s, 9.5, 17.4, 4)
    for y in range(6, 18):
        s.put(9, y, trunk[0][1 if y % 2 else 2], trunk[1])
        s.put(10, y, trunk[0][0], trunk[1])
    for side in (-1, 1):
        for i in range(1, 9):
            x = 9.5 + side * i
            y = 5 - math.sin(i / 8 * math.pi) * 3 + (i / 8) ** 2 * 4
            s.put(x, y, fronds[0][2 if i < 4 else 1], fronds[1])
            if i % 2:
                s.put(x, y + 1, fronds[0][0], fronds[1])
        for i in range(1, 6):
            s.put(9.5 + side * i * 0.6, 5 - i * 0.7, fronds[0][3 if i < 3 else 2], fronds[1])
    return s.image()


def grass(seed=0):
    """Tall grass tuft (savanna, steppe, prairie): separate unoutlined blades, dark at the base,
    pale seed heads at the tips, fanning out from one clump."""
    s = Sprite(17, 15)
    blades = ramp("#C8C45A")
    ground_shadow(s, 8.5, 13.4, 6, 1.0)
    for i in range(7):
        lean = (i - 3) / 3
        height = 7 + h01(seed, i) * 5 - abs(lean) * 2
        for step in range(int(height)):
            x = 8.5 + lean * (0.6 + step * 0.9)
            tip = step >= height - 2
            tone = 3 if tip else 0 if step < 2 else 2 if lean <= 0 else 1
            s.put(x, 13 - step, blades[0][tone], None)
    for x in range(6, 12):
        s.put(x, 13, blades[1], None)
    return s.image()


def cactus(seed=0):
    """Saguaro: ribbed column with two upturned arms."""
    s = Sprite(15, 20)
    flesh = ramp("#5FA45A", "#1F3D22")
    ground_shadow(s, 7.5, 18.4, 3.5)

    def column(x0, x1, y0, y1):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                tone = 2 if x == x0 else 0 if x == x1 else 1
                if y == y0 and x in (x0, x1):
                    continue
                s.put(x, y, flesh[0][tone] if (x - x0) % 2 == 0 or tone != 1 else flesh[0][3], flesh[1])

    column(6, 9, 1, 18)
    column(2, 4, 4, 11)
    for x in range(3, 6):
        s.put(x, 11, flesh[0][1], flesh[1])
        s.put(x, 12, flesh[0][0], flesh[1])
    column(11, 13, 6, 12)
    for x in range(10, 12):
        s.put(x, 12, flesh[0][1], flesh[1])
        s.put(x, 13, flesh[0][0], flesh[1])
    return s.image()


def dune(seed=0):
    """Sand dune: sharp crest, lit windward slope, shaded lee, ripple marks."""
    s = Sprite(23, 11)
    sand = ramp("#E2BF74", "#7A5A2E")
    for y in range(s.h):
        for x in range(s.w):
            crest = 8 + (h01(seed) - 0.5) * 3
            top = 2 + abs(x + 0.5 - crest) * (0.55 if x < crest else 0.95)
            if y + 0.5 >= top and y <= 9:
                tone = 2 if x < crest else 0
                if x < crest and (x + y * 2) % 6 == 0:
                    tone = 1
                if y + 0.5 - top < 1 and x < crest:
                    tone = 3
                s.put(x, y, sand[0][tone], sand[1])
    return s.image()


def red_rock(seed=0):
    """Outback monolith: rounded red rock with horizontal ribs and a lit crown."""
    s = Sprite(25, 13)
    rock = ramp("#C8643A", "#4A1E12")
    ground_shadow(s, 12.5, 11.4, 11, 1.0)
    for y in range(2, 12):
        for x in range(1, 24):
            inset = max(0, 3 - (y - 2)) * 1.6 if y < 5 else 0
            if inset <= x <= 23 - inset * 0.6:
                tone = 3 if y == 2 + (x < 8) and x < 14 else 2 if x < 9 else 1 if x < 18 else 0
                if y % 3 == 1 and y > 4:
                    tone = max(0, tone - 1)
                s.put(x, y, rock[0][tone], rock[1])
    return s.image()


def volcano(seed=0):
    """Volcano: dark cone, glowing crater and lava runs, a puff of ash."""
    s = Sprite(21, 20)
    rock, lava, ash = ramp("#6E5A50"), hex_rgb("#F2793A"), ramp("#B9B4AE")
    glow = hex_rgb("#FFC44E")
    base = 18
    ground_shadow(s, 10.5, base + 0.6, 9, 1.1)
    for y in range(7, base + 1):
        half = 2 + (y - 7) * 0.8
        for x in range(s.w):
            dx = x + 0.5 - 10.5
            if abs(dx) <= half:
                tone = 2 if dx < -half * 0.3 else 1 if dx < half * 0.35 else 0
                s.put(x, y, rock[0][tone], rock[1])
    for x in range(9, 13):
        s.put(x, 7, glow if x in (10, 11) else lava, rock[1])
    for y, x in ((8, 10), (9, 10), (10, 9), (11, 9), (12, 9), (9, 12), (10, 12), (11, 13)):
        s.put(x, y, lava, rock[1])
    blob(s, 9.0, 3.5, 3.0, 2.0, ash, dither=False)
    blob(s, 12.5, 2.2, 2.6, 1.8, ash, dither=False)
    return s.image()


def glacier(seed=0):
    """Antarctic ice mountain: icy blue faces under wind-sculpted snow."""
    s = mountain(seed, snow=True, width=21, height=18)
    ice = {C["rock_hi"]: hex_rgb("#E8F4FA"), C["rock_lt"]: hex_rgb("#C4E0EE"), C["rock"]: hex_rgb("#93BFD8"),
           C["rock_dk"]: hex_rgb("#6E9CBC"), C["rock_ol"]: hex_rgb("#2E4E6A"), C["grass_tuft"]: hex_rgb("#C4E0EE")}
    data = [(*ice.get(p[:3], p[:3]), p[3]) if p[3] == 255 else p for p in (s.get_flattened_data() if hasattr(s, "get_flattened_data") else s.getdata())]
    s.putdata(data)
    return s


def iceberg(seed=0):
    """Iceberg: angular ice above the waterline, darker ice below it, white surf."""
    s = Sprite(21, 14)
    ice = ramp("#CFE6F2", "#2E4E6A")
    under = hex_rgb("#7FB2D0")
    for y in range(1, 12):
        for x in range(1, 20):
            top = 1 + abs(x - 8) * 0.7 if x < 13 else 4 + (x - 13) * 0.9
            if y >= top:
                if y >= 10:
                    color = under
                else:
                    color = ice[0][3 if x < 8 and y < top + 2 else 2 if x < 11 else 1 if x < 16 else 0]
                s.put(x, y, color, ice[1])
    for x in range(0, 21):
        if h01(seed, x) < 0.7:
            s.put(x, 10, C["foam"], C["foam"])
    return s.image()


FAUNA = {
    "deer": deer, "fox": fox, "elephant": elephant, "zebra": zebra, "panda": panda,
    "tiger": tiger, "bison": bison, "moose": moose, "jaguar": jaguar, "capybara": capybara,
    "kangaroo": kangaroo, "kiwi": kiwi, "penguin": penguin, "seal": seal,
}
FLORA = {
    "oak": tree, "pine": pine, "olive": olive, "acacia": acacia, "baobab": baobab, "palm": palm,
    "bamboo": bamboo, "eucalyptus": eucalyptus, "fern": fern, "grass": grass, "cactus": cactus,
    "dune": dune, "red-rock": red_rock, "volcano": volcano, "glacier": glacier, "iceberg": iceberg,
}


ICONS = {
    "tree": tree, "pine": pine, "mountain": mountain, "hill": hill, "castle": castle,
    "church": church, "house": house, "boat": sailboat, "pin": pin, **FLORA, **FAUNA,
}


def preview(path, scale=5):
    """Rows: buildings and landmarks, flora and landforms, fauna."""
    rows = [
        ["tree", "pine", "mountain", "hill", "castle", "church", "house", "boat", "pin"],
        list(FLORA),
        list(FAUNA),
    ]
    pad = 4
    images = [[ICONS[name](0) for name in row] for row in rows]
    width = max(sum(img.width + pad for img in row) + pad for row in images)
    heights = [max(img.height for img in row) + pad for row in images]
    sheet = Image.new("RGBA", (width, sum(heights) + pad), (138, 194, 64, 255))
    y = pad
    for row, h in zip(images, heights):
        x = pad
        for img in row:
            sheet.alpha_composite(img, (x, y + h - pad - img.height))
            x += img.width + pad
        y += h
    sheet.resize((sheet.width * scale, sheet.height * scale), Image.NEAREST).save(path)


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "docs" / "art" / "phase3" / "sprites.png"
    preview(out)
    print("wrote", out)
