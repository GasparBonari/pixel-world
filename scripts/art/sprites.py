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



def brown_bear(seed=0):
    """Brown bear: heavy body, shoulder hump, round ears, short muzzle."""
    s = Sprite(24, 17)
    fur = ramp("#7C4F2E")
    ground_shadow(s, 12, 15.6, 9)
    for x in (8, 17):
        limb(s, x, 11, 15, fur, far=True, width=2)
    blob(s, 13.5, 9.0, 7.5, 4.2, fur)
    blob(s, 9.5, 7.0, 3.6, 3.4, fur)  # shoulder hump
    for x in (10, 19):
        limb(s, x, 11, 15, fur, width=2, hoof=fur[0][0])
    blob(s, 4.5, 8.0, 3.2, 2.6, fur)
    dots(s, [(1, 9), (2, 9)], ramp("#B07A4E")[0][2], fur[1])
    s.put(1, 8, INK, fur[1])
    eye(s, 4, 7, fur[1])
    dots(s, [(5, 5), (7, 5)], fur[0][0], fur[1])
    return s.image()


def wild_boar(seed=0):
    """Wild boar: wedge-shaped dark body, bristly mane, long snout, white tusk."""
    s = Sprite(21, 14)
    hide = ramp("#5E4B3E")
    ground_shadow(s, 11, 12.6, 7)
    limb(s, 7, 9, 12, hide, far=True)
    limb(s, 15, 9, 12, hide, far=True)
    blob(s, 11.5, 7.0, 6.5, 3.4, hide,
         lambda x, y, nx, ny, t: hide[0][0] if ny < -0.6 and x % 2 == 0 else None)
    limb(s, 8, 9, 12, hide, hoof=INK)
    limb(s, 16, 9, 12, hide, hoof=INK)
    blob(s, 4.5, 7.4, 3.0, 2.2, hide)
    dots(s, [(0, 8), (1, 8)], hex_rgb("#C9928A"), hide[1])
    dots(s, [(2, 9), (2, 10)], hex_rgb("#F4EEDA"), hide[1])
    eye(s, 4, 6, hide[1])
    s.put(6, 4, hide[0][0], hide[1])
    s.put(18, 6, hide[0][0], hide[1])
    return s.image()


def lion(seed=0):
    """Lion: tawny body, dark full mane, tufted tail."""
    s = Sprite(24, 16)
    coat, mane = ramp("#D9A65C"), ramp("#9A5A2A")
    ground_shadow(s, 12, 14.6, 8)
    limb(s, 9, 10, 14, coat, far=True)
    limb(s, 17, 10, 14, coat, far=True)
    for x, y in ((19, 9), (20, 8), (21, 7), (22, 6)):
        s.put(x, y, coat[0][1], coat[1])
    dots(s, [(22, 5), (23, 5), (23, 6)], mane[0][1], mane[1])
    blob(s, 13.0, 9.0, 6.5, 2.8, coat)
    limb(s, 10, 10, 14, coat, width=2)
    limb(s, 18, 10, 14, coat, width=2)
    blob(s, 6.5, 7.0, 4.2, 4.4, mane)  # mane
    blob(s, 4.8, 7.4, 2.6, 2.3, coat)  # face
    s.put(2, 8, INK, coat[1])
    eye(s, 4, 7, coat[1])
    return s.image()


def giraffe(seed=0):
    """Giraffe: long legs and neck, brown patches on cream, small ossicones."""
    s = Sprite(20, 28)
    coat = ([hex_rgb("#D9B47A"), hex_rgb("#EED2A0"), hex_rgb("#F6E2BA"), hex_rgb("#FBEDD0")], hex_rgb("#5A3A1E"))
    patch = hex_rgb("#A8642E")

    def patches(x, y, nx, ny, tone):
        return patch if (x // 2 + y // 2) % 2 == 0 and (x + y) % 2 == 0 else None

    ground_shadow(s, 11, 26.6, 6)
    limb(s, 9, 18, 26, coat, far=True, hoof=INK)
    limb(s, 15, 18, 26, coat, far=True, hoof=INK)
    blob(s, 12.5, 16.0, 5.0, 3.0, coat, patches)
    limb(s, 10, 18, 26, coat, hoof=INK)
    limb(s, 16, 18, 26, coat, hoof=INK)
    for i, y in enumerate(range(5, 15)):  # neck, leaning forward
        x = 6 + i * 0.35
        for dx in (0, 1):
            s.put(x + dx, y, patch if (y + dx) % 3 == 0 else coat[0][2 - dx], coat[1])
    blob(s, 4.5, 4.0, 2.8, 1.6, coat)
    eye(s, 5, 3, coat[1])
    dots(s, [(5, 1), (7, 1)], hex_rgb("#5A3A1E"), coat[1])
    s.put(2, 4, coat[0][0], coat[1])
    return s.image()


def rhinoceros(seed=0):
    """White rhinoceros: massive grey body, low head, two horns."""
    s = Sprite(26, 17)
    hide, horn = ramp("#8E918E"), hex_rgb("#D8D0BE")
    ground_shadow(s, 13, 15.6, 10)
    for x in (9, 18):
        limb(s, x, 11, 15, hide, far=True, width=2)
    blob(s, 14.5, 8.5, 8.5, 4.2, hide,
         lambda x, y, nx, ny, t: hide[0][0] if x in (11, 12) and -0.6 < ny < 0.5 else None)
    for x in (11, 20):
        limb(s, x, 11, 15, hide, width=3)
    blob(s, 5.0, 10.0, 3.8, 2.6, hide)
    dots(s, [(1, 8), (1, 9), (2, 7), (2, 8), (2, 9)], horn, hide[1])
    dots(s, [(4, 7), (4, 8)], horn, hide[1])
    eye(s, 6, 9, hide[1])
    dots(s, [(7, 6), (8, 6)], hide[0][0], hide[1])
    return s.image()


def camel(seed=0):
    """Bactrian camel: two humps, long legs, curved neck, shaggy throat."""
    s = Sprite(22, 23)
    coat = ramp("#B88C5A")
    ground_shadow(s, 12, 21.6, 7)
    limb(s, 9, 14, 21, coat, far=True)
    limb(s, 16, 14, 21, coat, far=True)
    blob(s, 13.0, 12.0, 6.0, 3.0, coat)
    blob(s, 10.5, 8.6, 2.2, 2.2, coat)  # humps
    blob(s, 15.5, 8.6, 2.2, 2.2, coat)
    limb(s, 10, 14, 21, coat)
    limb(s, 17, 14, 21, coat)
    for i, (x, y) in enumerate(((7, 12), (6, 11), (5, 10), (5, 9), (5, 8), (5, 7), (5, 6))):
        s.put(x, y, coat[0][2], coat[1])
        s.put(x + 1, y, coat[0][1] if i < 3 else coat[0][0], coat[1])
    blob(s, 3.5, 5.2, 2.6, 1.6, coat)
    eye(s, 3, 4, coat[1])
    dots(s, [(6, 10), (7, 11)], coat[0][0], coat[1])  # shaggy throat
    s.put(4, 3, coat[0][0], coat[1])
    return s.image()


def orangutan(seed=0):
    """Orangutan sitting: shaggy orange-red hair, long arms, dark face."""
    s = Sprite(18, 19)
    hair, face = ramp("#C8622E"), ramp("#6B3E28")
    ground_shadow(s, 9, 17.6, 6)
    blob(s, 9.5, 11.5, 5.0, 5.5, hair,
         lambda x, y, nx, ny, t: hair[0][0] if (x + y) % 4 == 0 and t < 3 else None)
    for x, y in ((4, 9), (3, 10), (3, 11), (3, 12), (3, 13), (3, 14), (3, 15), (4, 16)):  # long arm
        s.put(x, y, hair[0][1], hair[1])
    for x, y in ((14, 9), (15, 10), (15, 11), (15, 12), (15, 13), (15, 14), (14, 15)):
        s.put(x, y, hair[0][0], hair[1])
    blob(s, 9.0, 4.5, 3.2, 3.0, hair)
    blob(s, 8.6, 5.2, 2.2, 1.9, face)
    dots(s, [(8, 4), (10, 4)], INK, face[1])
    for x in range(6, 13):
        s.put(x, 17, hair[0][0], hair[1])
    return s.image()


def snow_leopard(seed=0):
    """Snow leopard: pale smoky coat, dark rosettes, very long thick tail."""
    s = big_cat("#C9C6BA", hex_rgb("#EEEDE6"), hex_rgb("#4A4A50"), "rosettes")
    tail = ramp("#C9C6BA")
    for x, y in ((19, 9), (20, 10), (21, 10), (22, 9), (23, 8), (23, 7)):
        s.put(x, y, tail[0][1], tail[1])
    return s.image()


def wolf(seed=0):
    """Gray wolf: grizzled grey coat, darker saddle, pale chest, long legs."""
    s = Sprite(22, 16)
    coat, pale = ramp("#8C9096"), hex_rgb("#E2E2DC")
    ground_shadow(s, 11, 14.6, 7)
    limb(s, 7, 10, 14, coat, far=True)
    limb(s, 14, 10, 14, coat, far=True)
    for x, y in ((17, 8), (18, 9), (19, 10), (20, 11)):
        s.put(x, y, coat[0][0], coat[1])
    blob(s, 11.0, 8.4, 5.6, 2.5, coat,
         lambda x, y, nx, ny, t: pale if ny > 0.45 else coat[0][0] if ny < -0.5 else None)
    limb(s, 8, 10, 14, coat)
    limb(s, 15, 10, 14, coat)
    blob(s, 5.0, 6.4, 2.8, 2.1, coat, lambda x, y, nx, ny, t: pale if ny > 0.35 else None)
    dots(s, [(1, 7), (2, 7)], coat[0][1], coat[1])
    s.put(0, 7, INK, coat[1])
    eye(s, 4, 6, coat[1])
    dots(s, [(5, 3), (5, 4), (7, 3), (7, 4)], coat[0][0], coat[1])
    return s.image()


def alligator(seed=0):
    """American alligator: low, long, ridged dark-green body, splayed legs, broad snout."""
    s = Sprite(28, 9)
    hide = ramp("#4E6A3A")
    ground_shadow(s, 14, 7.6, 12, 1.0)
    for x in (8, 18):
        dots(s, [(x, 7), (x + 1, 7)], hide[0][0], hide[1])
    blob(s, 14.0, 4.8, 8.5, 2.2, hide,
         lambda x, y, nx, ny, t: hide[0][0] if ny < -0.5 and x % 2 == 0 else hex_rgb("#C9C48E") if ny > 0.6 else None)
    for i, x in enumerate(range(22, 28)):  # tapering tail
        s.put(x, 4 + i // 3, hide[0][1], hide[1])
        if i < 3:
            s.put(x, 5 + i // 3, hide[0][0], hide[1])
    blob(s, 3.5, 5.0, 3.8, 1.3, hide)
    eye(s, 6, 3, hide[1])
    for x in (9, 19):
        dots(s, [(x, 7), (x + 1, 7)], hide[0][1], hide[1])
    return s.image()


def guanaco(seed=0):
    """Guanaco: slender Andean camelid, long upright neck, white belly, upright ears."""
    s = Sprite(18, 22)
    coat, belly = ramp("#C48A52"), hex_rgb("#F2E6D2")
    ground_shadow(s, 10, 20.6, 6)
    limb(s, 8, 14, 20, coat, far=True, hoof=INK)
    limb(s, 14, 14, 20, coat, far=True, hoof=INK)
    blob(s, 11.5, 12.0, 5.0, 2.6, coat, lambda x, y, nx, ny, t: belly if ny > 0.4 else None)
    limb(s, 9, 14, 20, coat, hoof=INK)
    limb(s, 15, 14, 20, coat, hoof=INK)
    for y in range(4, 12):
        s.put(6, y, coat[0][2], coat[1])
        s.put(7, y, coat[0][1], coat[1])
    blob(s, 5.0, 3.6, 2.6, 1.6, coat, lambda x, y, nx, ny, t: hex_rgb("#5A4A40") if nx < -0.4 else None)
    eye(s, 5, 3, coat[1])
    dots(s, [(6, 1), (7, 1)], coat[0][1], coat[1])
    return s.image()


def toucan(seed=0):
    """Toco toucan perched on a branch: black body, white throat, huge orange bill."""
    s = Sprite(16, 18)
    plumage = ramp("#2B2E36", "#101216")
    bill, bill_tip, throat = hex_rgb("#F28C2E"), hex_rgb("#2B2E36"), hex_rgb("#F6F4EC")
    branch = ramp("#7A5A3E")
    ground_shadow(s, 9, 16.6, 4)
    for y in range(12, 17):
        s.put(9, y, branch[0][1], branch[1])
    for x in range(4, 15):
        s.put(x, 12, branch[0][2], branch[1])
    blob(s, 10.0, 7.5, 2.8, 4.2, plumage,
         lambda x, y, nx, ny, t: throat if nx < -0.2 and -0.8 < ny < -0.1 else None)
    for x in range(11, 14):  # tail
        s.put(x, 11 + (x - 11), plumage[0][0], plumage[1])
    for x, y in ((2, 4), (3, 4), (4, 4), (5, 4), (6, 4), (3, 5), (4, 5), (5, 5), (6, 5), (7, 5)):
        s.put(x, y, bill, hex_rgb("#7A3A10"))
    s.put(1, 5, bill_tip, hex_rgb("#7A3A10"))
    s.put(9, 4, hex_rgb("#4EA0E8"), plumage[1])
    s.put(9, 5, INK, plumage[1])
    return s.image()


def koala(seed=0):
    """Koala in a eucalyptus fork: round grey body, big fluffy ears, large black nose."""
    s = Sprite(16, 18)
    fur, ear = ramp("#9EA4AA"), hex_rgb("#EDEDEA")
    trunk = ramp("#D8CDB6", "#5A4E3E")
    ground_shadow(s, 8, 16.6, 4)
    for y in range(6, 17):
        s.put(10, y, trunk[0][2], trunk[1])
        s.put(11, y, trunk[0][1], trunk[1])
    blob(s, 8.0, 10.5, 3.6, 4.0, fur, lambda x, y, nx, ny, t: ear if nx < -0.3 and ny > 0.1 else None)
    blob(s, 7.5, 5.0, 3.2, 2.6, fur)
    blob(s, 4.5, 3.6, 1.6, 1.6, fur, lambda x, y, nx, ny, t: ear if nx < 0.2 else None)
    blob(s, 10.5, 3.6, 1.6, 1.6, fur, lambda x, y, nx, ny, t: ear if nx > -0.2 else None)
    dots(s, [(7, 5), (7, 6), (8, 6)], INK, fur[1])
    dots(s, [(6, 4), (9, 4)], INK, fur[1])
    dots(s, [(9, 9), (10, 9)], fur[0][0], fur[1])  # arm hugging the trunk
    return s.image()


def emu(seed=0):
    """Emu: tall shaggy brown body, long bare blue-grey neck, long legs."""
    s = Sprite(16, 26)
    plumage, skin = ramp("#7A6652"), ramp("#6E7F96")
    legs = ramp("#8A7A6A")
    ground_shadow(s, 8, 24.6, 4.5)
    limb(s, 7, 15, 24, legs, far=True)
    limb(s, 9, 15, 24, legs)
    dots(s, [(5, 24), (6, 24), (10, 24), (11, 24)], legs[0][0], legs[1])
    blob(s, 9.0, 11.5, 5.2, 4.2, plumage,
         lambda x, y, nx, ny, t: plumage[0][0] if (x * 3 + y) % 5 == 0 and t < 3 else None)
    for y in range(3, 9):
        s.put(5, y, skin[0][2], skin[1])
        s.put(6, y, skin[0][1], skin[1])
    blob(s, 4.5, 2.6, 2.0, 1.5, skin)
    dots(s, [(1, 3), (2, 3)], hex_rgb("#3A3530"), skin[1])
    eye(s, 4, 2, skin[1])
    return s.image()


def orca(seed=0):
    """Orca surfacing: black back and tall dorsal fin, white eye patch, splash at the waterline."""
    s = Sprite(26, 14)
    body = ramp("#22252C", "#0C0E12")
    white = hex_rgb("#F4F6F8")
    for y in range(2, 11):
        for x in range(1, 25):
            arch = 10 - math.sin((x - 1) / 23 * math.pi) * 6.5
            if y >= arch and y <= 10:
                tone = 2 if y < arch + 1.2 else 1 if x < 14 else 0
                color = body[0][tone]
                if 5 <= x <= 7 and arch + 1 <= y <= arch + 2:
                    color = white  # eye patch
                if y == 10 and 3 < x < 20:
                    color = white  # pale belly at the waterline
                s.put(x, y, color, body[1])
    for i, (x, y) in enumerate(((13, 3), (13, 2), (14, 1), (14, 0), (15, 0))):  # dorsal fin
        s.put(x, y, body[0][1], body[1])
    for x in range(0, 26):
        if h01(seed, x) < 0.75:
            s.put(x, 11, C["foam"], C["foam"])
        if h01(seed, x, 2) < 0.3:
            s.put(x, 12, C["foam"], C["foam"])
    return s.image()



def windmill(seed=0):
    """La Mancha windmill: whitewashed round tower, dark conical cap, four lattice sails."""
    s = Sprite(23, 26)
    white = ([hex_rgb("#C9CCC6"), hex_rgb("#EDEDE6"), hex_rgb("#F8F8F2"), hex_rgb("#FFFFFF")], hex_rgb("#4E4A44"))
    cap, wood = ramp("#3E3A38"), ramp("#8A6240")
    ground_shadow(s, 11.5, 24.4, 5)
    for y in range(10, 25):
        for x in range(8, 16):
            tone = 2 if x < 10 else 0 if x > 13 else 1
            s.put(x, y, white[0][tone], white[1])
    dots(s, [(11, 22), (12, 22), (11, 23), (12, 23), (11, 24), (12, 24)], hex_rgb("#4A3426"), white[1])
    dots(s, [(10, 15), (13, 17)], hex_rgb("#34405A"), white[1])
    for y in range(6, 10):
        half = (y - 5) * 1.2
        for x in range(int(11.5 - half), int(11.5 + half) + 1):
            s.put(x, y, cap[0][1 if x < 12 else 0], cap[1])
    hub = (11, 8)
    for ex, ey in ((1, 0), (22, 1), (3, 17), (21, 16)):  # the X of sails
        line(s, hub[0], hub[1], ex, ey, wood[0][1], wood[1])
        for k in (0.45, 0.7, 0.95):
            x, y = hub[0] + (ex - hub[0]) * k, hub[1] + (ey - hub[1]) * k
            s.put(x, y - 1, wood[0][2], wood[1])
            s.put(x + 1, y, wood[0][2], wood[1])
    s.put(hub[0], hub[1], INK, cap[1])
    return s.image()


def mont_saint_michel(seed=0):
    """Mont-Saint-Michel: a granite island ringed by ramparts, houses climbing to the abbey and its spire."""
    s = Sprite(27, 30)
    rock, wall = ramp("#9A8F7E"), ramp("#CFC6B0", "#4A3E30")
    roofs, sand = ramp("#5E6878"), hex_rgb("#E2D2A8")
    for x in range(1, 26):  # the tidal flats
        s.put(x, 28, sand, sand)
        if 3 < x < 23:
            s.put(x, 29, hex_rgb("#A8DDEB"), hex_rgb("#A8DDEB"))
    blob(s, 13.5, 24.0, 11.5, 5.0, rock, clip=lambda x, y: y <= 27)  # the rock
    for x in range(3, 25):  # ramparts with towers
        for y in (24, 25, 26, 27):
            if y >= 24 + (0 if 5 < x < 22 else 1):
                s.put(x, y, wall[0][2 if x < 13 else 1], wall[1])
        if x % 5 == 0:
            for y in (22, 23):
                s.put(x, y, wall[0][2], wall[1])
    for x0, y0, w, h in ((6, 19, 4, 4), (11, 18, 3, 5), (16, 19, 4, 4)):  # houses on the slope
        for y in range(y0, y0 + h):
            for x in range(x0, x0 + w):
                s.put(x, y, roofs[0][2] if y == y0 else wall[0][1 if x < x0 + w - 1 else 0], wall[1])
    for y in range(10, 19):  # the abbey church
        for x in range(10, 18):
            tone = 2 if x < 13 else 1 if x < 16 else 0
            s.put(x, y, roofs[0][tone] if y < 12 else wall[0][tone], wall[1])
    for y in range(1, 10):  # the spire with Saint Michael in gold
        w = max(0, (y - 1) // 3)
        for x in range(13 - w, 15 + w):
            s.put(x, y, roofs[0][2 if x < 14 else 0], roofs[1])
    s.put(14, 0, hex_rgb("#F2C14E"), roofs[1])
    return s.image()


def vineyard(seed=0):
    """A vineyard: neat rows of vines on warm soil, a few dark grapes."""
    s = Sprite(25, 14)
    soil, leaves = hex_rgb("#C49A6C"), ramp("#6FA845", "#2E4A22")
    for y in range(2, 13):
        for x in range(1, 24):
            skew = (12 - y) * 0.6
            if 1 + skew * 0.3 <= x <= 23 - skew * 0.3:
                row = (x + y) % 4
                if row in (0, 1, 2):
                    s.put(x, y, leaves[0][3 if row == 0 else 2 if row == 1 else 1], leaves[1])
                    if h01(seed, x, y) < 0.08:
                        s.put(x, y, hex_rgb("#5A2A5E"), leaves[1])
                else:
                    s.put(x, y, soil if row == 2 else shade(soil, -0.12), hex_rgb("#7A5A3A"))
    return s.image()


def neuschwanstein(seed=0):
    """Neuschwanstein: pale Romanesque palace on a rocky ridge, square keep and conical turrets."""
    s = Sprite(31, 33)
    wall, roof = ramp("#E5DFCC", "#514B3D"), ramp("#596B83", "#2D3548")
    rock = ramp("#9B9588", "#49483E")
    ground_shadow(s, 15.5, 31, 13, 1)
    blob(s, 15, 29, 13, 4, rock, clip=lambda x, y: y <= 31)
    # Main Palas: lit west face and shaded east return, arcaded windows and string courses.
    for y in range(13, 29):
        for x in range(8, 24):
            tone = 2 if x < 17 else 1 if x < 21 else 0
            color = wall[0][tone]
            if y in (19, 25):
                color = wall[0][0]
            elif x % 4 in (1, 2) and y % 6 in (2, 3, 4):
                color = C["window"]
            s.put(x, y, color, wall[1])
    for y in range(8, 14):
        for x in range(7 + (13 - y) // 2, 25 - (13 - y) // 2):
            s.put(x, y, roof[0][2 if x < 17 else 0] if y % 3 else roof[0][1], roof[1])
    # Tall square tower and the large western round turret have different silhouettes.
    for x0, top, bottom, width in ((4, 9, 29, 5), (22, 6, 27, 5), (11, 7, 14, 3)):
        for y in range(top, bottom):
            for x in range(x0, x0 + width):
                color = wall[0][2 if x < x0 + 2 else 0]
                if y % 7 in (3, 4) and x == x0 + width // 2:
                    color = C["window"]
                s.put(x, y, color, wall[1])
        for dy in range(6):
            half = (5 - dy) * (width / 2) / 5
            for x in range(math.ceil(x0 + width / 2 - half), math.floor(x0 + width / 2 + half) + 1):
                s.put(x, top - dy, roof[0][2 if x < x0 + width / 2 else 0], roof[1])
    # Rectangular south-west keep: battlemented crown, paired Romanesque windows.
    for y in range(13, 27):
        for x in range(15, 20):
            s.put(x, y, C["window"] if y % 6 in (3, 4) and x in (16, 18)
                  else wall[0][2 if x < 18 else 0], wall[1])
    for x in (15, 17, 19):
        s.put(x, 12, wall[0][3], wall[1])
    return s.image()


def kinderdijk(seed=0):
    """Kinderdijk's polder mills: a brick ground-sailer and a thatched smock mill by a channel."""
    s = Sprite(33, 32)
    brick, thatch, cap, wood = ramp("#9B7454", "#48372C"), ramp("#B59A69", "#57452D"), \
        ramp("#4C5148", "#2D332E"), ramp("#C6B994", "#514735")
    ground_shadow(s, 16, 30, 14)
    for x in range(2, 31):
        y = 29 - x // 12
        s.put(x, y, C["leaf"], C["leaf_ol"])
        s.put(x, y + 1, C["foam"] if x % 5 == 0 else C["glass"], C["hull_ol"])

    def mill(cx, foot, height, material):
        top = foot - height
        for y in range(top + 4, foot):
            half = 2 + (y - top - 4) * 2.7 / (height - 4)
            for x in range(math.ceil(cx - half), math.floor(cx + half) + 1):
                tone = 2 if x < cx - 1 else 0 if x > cx + 2 else 1
                if y % 3 == 0 and (x + y // 3) % 4 == 0:
                    tone = max(0, tone - 1)
                s.put(x, y, material[0][tone], material[1])
        for y in range(top, top + 5):
            half = 1.2 + (y - top) * .65
            for x in range(math.ceil(cx - half), math.floor(cx + half) + 1):
                s.put(x, y, cap[0][2 if x < cx else 0], cap[1])
        for y in range(foot - 4, foot):
            s.put(cx, y, C["door"], material[1])
        s.put(cx - 2, top + 9, C["glass"], material[1])
        s.put(cx + 1, top + 13, C["glass"], material[1])
        # Long narrow lattice sails, with two spars and widely spaced crosspieces.
        hx, hy = cx, top + 4
        for dx, dy in ((-7, -7), (7, -7), (7, 7), (-7, 7)):
            line(s, hx, hy, hx + dx, hy + dy, wood[0][1], wood[1])
            nx, ny = (-1 if dy > 0 else 1), (1 if dx > 0 else -1)
            line(s, hx + dx * .4 + nx, hy + dy * .4 + ny,
                 hx + dx + nx, hy + dy + ny, wood[0][2], wood[1])
            for t in (.45, .7, 1):
                line(s, hx + dx * t, hy + dy * t, hx + dx * t + nx, hy + dy * t + ny,
                     wood[0][3], wood[1])
        s.put(hx, hy, cap[0][3], cap[1])

    mill(24, 26, 17, thatch)
    mill(10, 29, 23, brick)
    return s.image()


def gravensteen(seed=0):
    """Ghent's Gravensteen: tall square donjon, battlemented curtain and round wall turrets."""
    s = Sprite(35, 32)
    stone = ramp("#BCAF91", "#514733")
    water = ramp("#527D87", "#334F59")
    ground_shadow(s, 17, 30, 15)
    # Leie moat under the west/south curtain; reflections stay inside its narrow basin.
    for x in range(3, 32):
        y = 28 + abs(x - 17) // 10
        s.put(x, y, water[0][2 if x % 5 == 0 else 1], water[1])

    def wall(left, right, top, foot, slit=False):
        for x in range(left, right):
            for y in range(top, foot):
                tone = 2 if x < (left + right) / 2 else 0
                if y % 4 == 0 or (x + y // 4 * 2) % 6 == 0:
                    tone = max(0, tone - 1)
                if slit and x == (left + right) // 2 and top + 4 <= y <= top + 7:
                    s.put(x, y, C["window"], stone[1])
                else:
                    s.put(x, y, stone[0][tone], stone[1])
        for x in range(left, right, 3):
            s.put(x, top - 1, stone[0][3], stone[1])
            s.put(x, top - 2, stone[0][2], stone[1])

    # Rear curtain, then the keep and gate; near turrets overlap their connecting wall.
    wall(5, 30, 17, 25)
    wall(11, 24, 5, 24)
    for x in (14, 20):
        for y in (11, 12, 18, 19):
            s.put(x, y, C["window"], stone[1])
            s.put(x + 1, y, C["window"], stone[1])
        s.put(x, 13, stone[0][3], stone[1])
    wall(4, 31, 22, 28)
    for x, top in ((4, 17), (11, 19), (24, 19), (29, 17)):
        wall(x - 2, x + 3, top, 28, slit=True)
    wall(15, 22, 18, 29)
    for y in range(23, 29):
        for x in range(17, 20):
            if y > 23 or x == 18:
                s.put(x, y, C["door"] if y % 2 else stone[0][0], stone[1])
    return s.image()


def stonehenge(seed=0):
    """Surviving sarsen ring, three complete inner trilithons and fallen stones on grass."""
    import iso

    s = Sprite(39, 32)
    ground_shadow(s, 19, 29, 16, 2)
    stone = [hex_rgb(c) for c in ("#615B4D", "#97927D", "#BDB69B", "#E0D7B8")]
    outline = hex_rgb("#454338")
    def block(x, foot, width, height, depth=2):
        # Upright stones are volumes: lit front, shaded return and a pale upper face.
        for pts, tone in (([(x, foot - height), (x + width, foot - height),
                           (x + width, foot), (x, foot)], 2),
                          ([(x + width, foot - height), (x + width + depth, foot - height - 1),
                            (x + width + depth, foot - 1), (x + width, foot)], 1),
                          ([(x, foot - height), (x + depth, foot - height - 2),
                            (x + width + depth, foot - height - 2), (x + width, foot - height)], 3)):
            for a, b in iso.polygon_pixels(pts):
                colour = stone[max(0, tone - 1)] if h01(a, b, seed) < .09 else stone[tone]
                s.put(a, b, colour, outline)
    # Three complete trilithons, separated enough that the openings survive at icon size.
    # The incomplete outer ring and low fallen sarsens keep the present-day ruin silhouette.
    block(16, 12, 2, 7, 1)
    for x, foot, height, gap in ((5, 16, 9, 5), (23, 16, 8, 5)):
        block(x, foot, 2, height, 1)
        block(x + gap + 2, foot, 2, height, 1)
        block(x - 1, foot - height, gap + 5, 2, 1)
    block(2, 24, 3, 8, 1)
    block(33, 24, 2, 7, 1)
    block(13, 27, 3, 13, 1)
    block(23, 27, 3, 13, 1)
    block(12, 14, 15, 3, 1)
    block(6, 28, 4, 2, 2)
    block(29, 28, 6, 2, 1)
    return s.image()


def rock_of_cashel(seed=0):
    """Roofless Gothic cathedral, crossing tower, round tower and Cormac's Chapel on limestone."""
    import iso
    from landmarks_ireland import block, STONE, GRANITE, gothic_windows
    from landmarks_paris import P, poly
    from landmarks_amsterdam import octagon
    from landmarks_iberia import hip_roof

    scene = iso.Scene(59, 54, (29, 24))
    shadow = Sprite(59, 54)
    ground_shadow(shadow, 29, 49.5, 25, 2.5)
    scene.img = shadow.image()
    scene.px = scene.img.load()
    top = [P(scene, -1.1, -.5), P(scene, 3.1, -.5), P(scene, 3.3, 2.4), P(scene, -.9, 2.5)]
    for points, color in (([top[3], top[2], (top[2][0] - 2, top[2][1] + 6),
                           (top[3][0] + 2, top[3][1] + 5)], '#8C9878'),
                          ([top[2], top[1], (top[1][0] - 2, top[1][1] + 5),
                           (top[2][0] - 2, top[2][1] + 6)], '#616F5C'), (top, '#8EAE61')):
        poly(scene, points, lambda x, y, color=color: hex_rgb(color) if h01(x, y, seed) > .15 else hex_rgb('#A6B782'))
    # North round tower is slender and capped, unlike the square open crossing tower.
    octagon(scene, -.65, .1, .27, 0, 16, STONE)
    octagon(scene, -.65, .1, .32, 16, 4, GRANITE, roof=True)
    # Roofless nave and choir: low walls expose the grass-floored interior.
    for a, b, w, d in ((-.2, .2, 3, .18), (-.2, .2, .2, 1.4), (2.6, .2, .2, 1.4)):
        block(scene, a, b, w, d, 10, STONE, gothic_windows(STONE, 10, 6))
    # Broken Gothic end gable, as a thick i/z volume with a pointed traceried light.
    block(scene, 2.5, .2, .25, 1.5, 13, STONE, gothic_windows(STONE, 13, 10))
    poly(scene, [P(scene, 2.75, .2, 13), P(scene, 2.75, 1.7, 13), P(scene, 2.75, .95, 19)], lambda x, y: GRANITE['dark'])
    block(scene, .7, .2, .9, .9, 17, STONE, gothic_windows(STONE, 17, 6, belfry=True))
    for a, b in ((.65, .15), (1.45, .15), (.65, .95), (1.45, .95)):
        block(scene, a, b, .22, .22, 2, STONE, z=17)
    block(scene, -.2, 1.5, 3, .18, 8, STONE, gothic_windows(STONE, 8, 6))
    # Small Cormac's Chapel on the south: warm sandstone and a steep stone roof.
    chapel = {**GRANITE, 'lit': hex_rgb('#C1AC83'), 'dark': hex_rgb('#8D8064')}
    block(scene, .3, 1.9, 1.7, .6, 7, chapel, gothic_windows(chapel, 7, 5))
    hip_roof(scene, .3, 1.9, 1.7, .6, 7, 5, roof=GRANITE)
    block(scene, 1.7, 1.85, .35, .35, 12, chapel)
    hip_roof(scene, 1.7, 1.85, .35, .35, 12, 3, roof=GRANITE)
    return scene.img


def leaning_tower_pisa(seed=0):
    """White-marble campanile: leaning cylinder, six open galleries and narrower bell chamber."""
    import iso
    from landmarks_italy import cylinder, MARBLE, STONE
    from landmarks_iberia import arch_opening

    scene = iso.Scene(39, 58, (16, 50))
    shadow = Sprite(39, 58)
    ground_shadow(shadow, 20, 53, 13, 2)
    scene.img = shadow.image()
    scene.px = scene.img.load()
    def arcade(u, v, lit):
        c = u % 4.5
        if arch_opening(c, v, 2.25, 1.3, 2.2, STONE['deep']):
            return STONE['deep']
        return MARBLE['hi' if lit else 'mid'] if c < .8 else None
    # Each successive ring translates along the lean, without resampling pixels.
    cylinder(scene, 0, 0, 1.02, 1.02, 0, 6, MARBLE, arcade)
    for level in range(6):
        z = 6 + level * 5
        di = z * .012
        cylinder(scene, di, -di, 1.05, 1.05, z, 1.2, MARBLE)
        cylinder(scene, di, -di, .94, .94, z + 1.2, 3.8, MARBLE, arcade)
    cylinder(scene, .45, -.45, 1.03, 1.03, 36, 1.5, MARBLE)
    cylinder(scene, .47, -.47, .72, .72, 37.5, 5, MARBLE, arcade)
    cylinder(scene, .51, -.51, .8, .8, 42.5, 1.3, MARBLE)
    return scene.img


def kronborg(seed=0):
    """Kronborg at Helsingør: pale courtyard wings, red roofs and its great copper-capped tower."""
    import iso
    from landmarks_denmark import block, spire, windows, STONE, BRICK, CLAY, COPPER
    from landmarks_iberia import hip_roof
    from landmarks_paris import P, poly

    scene = iso.Scene(61, 63, (30, 33))
    shadow = Sprite(61, 63)
    ground_shadow(shadow, 30, 59, 26, 2)
    scene.img = shadow.image()
    scene.px = scene.img.load()
    poly(scene, [P(scene, -.2, -.2), P(scene, 3.25, -.2), P(scene, 3.25, 3.0), P(scene, -.2, 3.0)],
         lambda x, y: hex_rgb('#477F8B') if int(y) % 3 else hex_rgb('#8EBDBF'))
    block(scene, 0, 0, 3, 2.8, 3, STONE)
    for i, j, wi, wj in ((0, 0, 3, .65), (0, .65, .65, 2.15), (2.35, .65, .65, 2.15), (.65, 2.15, 1.7, .65)):
        block(scene, i, j, wi, wj, 12, STONE, windows(STONE, 12, bay=6, floor=11), z=3)
        hip_roof(scene, i, j, wi, wj, 15, 5, CLAY)
    block(scene, 1.25, .05, .8, .85, 25, STONE, windows(STONE, 25, bay=5), z=3)
    spire(scene, 1.65, .48, .63, 28, 7, COPPER, onion=True)
    for i,j in ((.05,1.9),(2.25,.05)):
        block(scene,i,j,.55,.55,18,BRICK,windows(BRICK,18,bay=5),z=3)
        spire(scene,i+.27,j+.27,.45,21,9,COPPER)
    # Gateway in the near curtain and corner bastions are independent shaded volumes.
    block(scene,1.1,2.16,.75,.67,10,STONE,
          lambda u,v,lit: hex_rgb('#4B3D30') if 1<int(u)<5 and v<7 else None,z=3)
    for i,j in ((-.05,2.3),(2.4,2.3)):
        block(scene,i,j,.65,.65,5,STONE,z=1)
    return scene.img


def gripsholm(seed=0):
    """Gripsholm's four round brick towers, copper caps, courtyard and Mälaren shore."""
    import iso
    from landmarks_sweden import block, windows, spire, cylinder, BRICK, STONE, COPPER, IRON, WATER
    from landmarks_iberia import hip_roof
    from landmarks_paris import P, poly

    scene = iso.Scene(67, 72, (33, 39))
    shadow = Sprite(67, 72)
    ground_shadow(shadow, 33, 68, 29, 2)
    scene.img = shadow.image()
    scene.px = scene.img.load()
    poly(scene,[P(scene,-.6,-.5),P(scene,3.5,-.5),P(scene,3.5,3),P(scene,-.6,3)],
         lambda x,y:WATER[0] if int(y)%4 else WATER[2])
    block(scene,-.15,-.15,3.1,2.75,3,STONE)
    def tower(a,b,height,lantern=False):
        cylinder(scene,a,b,.49,.49,3,height,BRICK,windows(BRICK,height,bay=6,floor=10))
        cylinder(scene,a,b,.54,.54,height+2,2,STONE)
        spire(scene,a,b,.6,height+4,10,COPPER,onion=True)
        if lantern:
            block(scene,a-.18,b-.18,.36,.36,4,COPPER,
                  lambda u,v,lit:IRON['deep'] if 1<v<3 else None,z=height+11)
            spire(scene,a,b,.28,height+15,5,COPPER)
    tower(0,0,20)
    tower(2.8,0,19)
    for a,b,wi,wj in ((0,0,2.8,.65),(0,.65,.65,1.75),(2.15,.65,.65,1.75),(.65,1.75,1.5,.65)):
        block(scene,a,b,wi,wj,15,BRICK,windows(BRICK,15,bay=6,floor=10),z=3)
        hip_roof(scene,a,b,wi,wj,18,6,IRON)
    tower(0,2.4,18)
    tower(2.8,2.4,22,True)
    block(scene,1.05,2.4,.75,.18,10,STONE,
          lambda u,v,lit:BRICK['outline'] if lit and 1<int(u)<5 and v<7 else None,z=3)
    return scene.img


def borgund(seed=0):
    """Borgund Stave Church: tarred timber, overlapping shingle roofs and dragon ridges."""
    import iso
    from landmarks_norway import block, TIMBER, GRANITE
    from landmarks_iberia import palette_of
    from landmarks_paris import P, seg, poly, corners

    scene = iso.Scene(59, 72, (29, 45))
    shadow = Sprite(59, 72)
    ground_shadow(shadow, 29, 68, 24, 2)
    scene.img = shadow.image()
    scene.px = scene.img.load()
    roof = palette_of(hex_rgb('#665044'))
    def shingle_roof(i,j,wi,wj,z,rise):
        top,right,bottom,left=corners(scene,i,j,wi,wj,z)
        rear,front=P(scene,i+wi/2,j,z+rise),P(scene,i+wi/2,j+wj,z+rise)
        for pts,key in (([top,left,front,rear],'lit'),([rear,front,bottom,right],'dark')):
            poly(scene,pts,lambda x,y,key=key:roof['line'] if int(y)%3==0
                 else roof['hi'] if (int(x)+int(y)//3*2)%7==0 else roof[key])
        poly(scene,[left,bottom,front],lambda x,y:TIMBER['lit'] if int(x)%4 else TIMBER['line'])
        for a,b in ((left,front),(front,bottom),(rear,front)):
            seg(scene,a,b,TIMBER['hi'])
    def timber(u,v,lit):
        if int(u)%4==0:return TIMBER['line' if lit else 'deep']
        if int(v) in (1,9,17):return TIMBER['hi' if lit else 'mid']
        return None
    block(scene,0,0,2.8,3.2,2,GRANITE)
    block(scene,.1,.1,2.6,3,11,TIMBER,timber,z=2)
    shingle_roof(-.05,-.05,2.9,3.3,13,8)
    block(scene,.5,.4,1.8,2.4,9,TIMBER,timber,z=17)
    shingle_roof(.35,.25,2.1,2.7,26,9)
    block(scene,.9,1.05,1,1.1,6,TIMBER,timber,z=32)
    shingle_roof(.75,.9,1.3,1.4,38,8)
    # Small projecting apse, shingled cap and the carved portal under the gallery eaves.
    block(scene,2.45,.65,.55,1,9,TIMBER,timber,z=2)
    shingle_roof(2.4,.6,.65,1.1,11,6)
    block(scene,.95,3.13,.9,.15,9,TIMBER,
          lambda u,v,lit:TIMBER['outline'] if lit and 1<u<6 and v<7 else TIMBER['hi'],z=2)
    # Curved dragon necks are filled wooden silhouettes, with snout and an open jaw.
    for ci,cj,z,direction in ((1.4,-.05,21,-1),(1.4,3.25,21,1),(1.4,.25,35,-1),(1.4,2.95,35,1)):
        points=[(ci,cj,z),(ci,cj+direction*.25,z+2),(ci,cj+direction*.35,z+6),
                (ci,cj+direction*.65,z+7),(ci,cj+direction*.72,z+5),
                (ci,cj+direction*.45,z+5),(ci,cj+direction*.4,z+1)]
        poly(scene,[P(scene,*p) for p in points],lambda x,y:TIMBER['hi'])
        seg(scene,P(scene,ci,cj+direction*.35,z+6),P(scene,ci,cj+direction*.68,z+6),TIMBER['deep'])
    seg(scene,P(scene,1.4,1.6,46),P(scene,1.4,1.6,52),TIMBER['hi'])
    seg(scene,P(scene,1.12,1.6,49),P(scene,1.68,1.6,49),TIMBER['hi'])
    return scene.img


def olavinlinna(seed=0):
    """Olavinlinna's three surviving round towers and curtain on a Saimaa rock island."""
    import iso
    from landmarks_finland import block, GRANITE, BRICK, SLATE, WATER
    from landmarks_italy import cylinder, ellipse
    from landmarks_denmark import spire
    from landmarks_paris import P, seg
    from landmarks_iberia import stone_courses, arch_opening

    scene = iso.Scene(65, 73, (32, 54))
    shadow = Sprite(65, 73)
    ground_shadow(shadow, 32, 69, 29, 2)
    scene.img = shadow.image()
    scene.px = scene.img.load()
    ellipse(scene,0,0,2.6,1.65,0,lambda x,y:WATER[2] if (x+y)%9==0 else WATER[0])
    cylinder(scene,0,0,2.25,1.4,0,4,GRANITE,stone_courses(GRANITE,2,5))
    def slits(u,v,lit):
        if int(u)%8 in (3,4) and int(v)%12 in (4,5,6,7):return GRANITE['outline']
        return stone_courses(GRANITE,3,6)(u,v,lit)
    # Rear curtain, occupied wings, then the two foreground towers: actual depth order.
    block(scene,-1.5,-.7,3,.35,22,GRANITE,slits,z=4)
    block(scene,-1.5,-.7,.4,1.9,19,GRANITE,slits,z=4)
    block(scene,-1.1,-.5,2.3,1.5,17,GRANITE,slits,z=4)
    for a,b,h in ((-.95,-.55,28),(1.25,-.1,25),(-.8,1,23)):
        cylinder(scene,a,b,.62,.62,4,h,GRANITE,slits)
        cylinder(scene,a,b,.65,.65,h+1,5,BRICK,slits)
        spire(scene,a,b,.86,h+6,8,SLATE,conical=True)
        # The shared spire helper ends with a gilt finial; these roofs have plain metal tips.
        seg(scene,P(scene,a,b,h+14),P(scene,a,b,h+17),SLATE['lit'],2)
    # Forward curtain has a real arched gate, projecting wall walk and stone landing.
    block(scene,-.5,1.15,2.15,.4,17,GRANITE,
          lambda u,v,lit:(arch_opening(u,v,9,2.4,5,GRANITE['outline']) if lit else None)
          or slits(u,v,lit),z=4)
    block(scene,-.55,1.08,2.25,.55,2,GRANITE,z=21)
    block(scene,.4,1.6,.8,1.1,2,GRANITE,z=1)
    for a in (-.4,1.4):
        seg(scene,P(scene,a,1.58,21),P(scene,a,1.58,24),GRANITE['lit'])
    return scene.img


def gullfoss(seed=0):
    """Gullfoss: broad upper cascade, transverse lower plunge and a narrow Hvítá gorge."""
    import iso
    from landmarks_iceland import block, BASALT, WATER, WHITE, GREEN
    from landmarks_paris import P, poly, seg, corners

    scene = iso.Scene(71, 66, (35, 36))
    shadow = Sprite(71, 66)
    ground_shadow(shadow, 35, 62, 32, 2)
    scene.img = shadow.image()
    scene.px = scene.img.load()
    # Layered canyon rims and grassy cap, with a diagonal turn between the falls.
    block(scene, -2.1, -1.3, 4.2, 3, 8, BASALT)
    block(scene, -2.1, -1.3, 4.2, 1.5, 11, BASALT, z=8)
    poly(scene, list(corners(scene, -2.1, -1.3, 4.2, 1.5, 19)),
         lambda x, y: GREEN['lit'] if (int(x)+int(y)) % 4 else GREEN['hi'])
    poly(scene, list(corners(scene, -1.8, -1.3, 3.3, 1.5, 20)),
         lambda x, y: WATER[2] if (int(x)+int(y)) % 5 == 0 else WATER[0])
    # Falling sheets have light rims, darker troughs and broken foam at their feet.
    for a, b, wi, wj, base, height in ((-1.8, .18, 3.3, .13, 10, 10), (.6, .5, .14, 1.2, 0, 10)):
        block(scene, a, b, wi, wj, height, WHITE,
              lambda u, v, lit: WATER[2] if int(u) % 4 or int(v) < 2 else WATER[0], z=base)
    poly(scene, list(corners(scene, -1.8, .3, 2.5, 1.2, 10)),
         lambda x, y: WATER[2] if h01(x, y, 289) < .32 else WATER[0])
    # The outflow vanishes into a deep slot below the transverse second fall.
    poly(scene, list(corners(scene, .7, .65, 1.1, 1.3, 1)), lambda x, y: WATER[1])
    block(scene, 1.8, .2, .35, 1.7, 12, BASALT)
    for a, b, z in ((-.8, .4, 10), (.3, 1, 10), (.8, 1.5, 2), (1.4, 1.7, 2)):
        seg(scene, P(scene, a, b, z), P(scene, a+.45, b, z+1), WHITE['hi'], 2)
    return scene.img


def chillon(seed=0):
    """Chillon: lake island, Savoyard round towers, red roofs and a tall square keep."""
    import iso
    from landmarks_switzerland import block, windows, SAND, PALE, CLAY, WATER
    from landmarks_italy import cylinder
    from landmarks_iberia import hip_roof
    from landmarks_denmark import spire
    from landmarks_paris import P, poly, seg

    scene = iso.Scene(59, 60, (29, 35))
    shadow = Sprite(59, 60)
    ground_shadow(shadow, 29, 56, 25, 2)
    scene.img = shadow.image()
    scene.px = scene.img.load()
    # The oval rocky islet and lake remain part of the icon, not continent art.
    lake = [P(scene, -1.9, -.5), P(scene, 1.4, -.75), P(scene, 1.9, 1.5),
            P(scene, .5, 2.5), P(scene, -1.7, 1.5)]
    poly(scene, lake, lambda x, y: WATER[2] if (int(x)+int(y)) % 11 == 0 else WATER[0])
    block(scene, -1.45, -.1, 3, 1.95, 3, SAND)
    # Back residential wing, then donjon and lake-facing halls.
    block(scene, -1.35, -.1, 2.7, .65, 10, PALE, windows(PALE, 10, 5, 9), z=3)
    hip_roof(scene, -1.45, -.2, 2.9, .85, 13, 5, CLAY)
    block(scene, -.25, .25, .9, .8, 23, PALE,
          lambda u, v, lit: C['window'] if 2 < u % 6 < 4 and 5 < v % 10 < 8
          else None, z=3)
    hip_roof(scene, -.35, .15, 1.1, 1, 26, 6, CLAY)
    for a, b, wi, wj in ((-1.35, .65, .8, 1.15), (-.55, 1.2, 2, .6)):
        block(scene, a, b, wi, wj, 12, PALE, windows(PALE, 12, 5, 10), z=3)
        hip_roof(scene, a-.07, b-.07, wi+.14, wj+.14, 15, 5, CLAY)
    for a, b, h in ((-1.25, .55, 17), (1.2, .15, 15), (1.2, 1.55, 15)):
        cylinder(scene, a, b, .3, .3, 3, h, PALE,
                 lambda u, v, lit: C['window'] if 1 < u % 6 < 3 and 5 < v % 9 < 8 else None)
        spire(scene, a, b, .37, h+3, 6, CLAY, conical=True)
    for a in (-.9, 0, .6):
        seg(scene, P(scene, a, 1.95, 1), P(scene, a+.5, 1.95, 1), WATER[2])
    return scene.img


def melk_abbey(seed=0):
    """Melk's yellow Baroque abbey: twin onion belfries, great dome and cliff terrace."""
    import iso
    from landmarks_austria import block, windows, band, clock, STONE, PALE, YELLOW, COPPER, CLAY
    from landmarks_iberia import hip_roof
    from landmarks_belgium import dome
    from landmarks_italy import cylinder
    from landmarks_denmark import spire
    from landmarks_paris import P, poly

    scene = iso.Scene(46, 56, (24, 39))
    shadow = Sprite(46, 56)
    ground_shadow(shadow, 23, 52, 20, 2)
    scene.img = shadow.image()
    scene.px = scene.img.load()
    # Native small geometry, not a resampled capital building. The cliff has two stone faces.
    for pts, color in (([(-1.3, 0, 0), (1.3, 0, 0), (1.3, 1.5, 0), (-1.3, 1.5, 0)], YELLOW['deep']),
                       ([(-1.2, 1.4, 5), (1.2, 1.4, 5), (1.3, 1.5, 0), (-1.3, 1.5, 0)], STONE['mid']),
                       ([(1.2, -.1, 5), (1.2, 1.4, 5), (1.3, 1.5, 0), (1.3, 0, 0)], STONE['deep'])):
        poly(scene, [P(scene, *p) for p in pts], lambda x, y, c=color: shade(c, -.1) if (int(x)+int(y)) % 7 == 0 else c)
    block(scene, -1.15, -.1, 2.3, 1.4, 2, STONE, z=4)
    for a,b,wi,wj in ((-.5,0,1.8,.45), (.7,.4,.6,.8), (-1.1,.2,.55,1)):
        block(scene, a, b, wi, wj, 10, YELLOW, windows(YELLOW, 10, 7, 10), z=6)
        hip_roof(scene, a-.05, b-.05, wi+.1, wj+.1, 16, 3, CLAY)
    cylinder(scene, .2, -.25, .5, .5, 18, 5, YELLOW)
    dome(scene, .2, -.25, .55, 23, 8, COPPER)
    spire(scene, .2, -.25, .13, 31, 2, COPPER)
    block(scene, -.8, .7, 1.3, .4, 13, YELLOW, windows(YELLOW, 13, 7, 10, arcade=True), z=6)
    for a in (-1, .25):
        block(scene, a, .85, .5, .5, 20, YELLOW,
              lambda u,v,lit: STONE['deep'] if 1 <= int(u) % 4 <= 2 and 3 < v % 8 < 7 else None, z=6)
        band(scene, a-.04, .81, .58, .58, 24, height=2)
        clock(scene, a+.25, 1.39, 22, 2)
        spire(scene, a+.25, 1.1, .35, 26, 8, COPPER, onion=True)
    return scene.img


def gozo_citadel(seed=0):
    """Gozo's limestone bastions, domeless cathedral, bell tower and entrance steps."""
    import iso
    from landmarks_malta import bastion, block, band, pediment, flat_roof, STONE, PALE, ROOF, RED
    from landmarks_paris import P, seg

    scene = iso.Scene(31, 34, (15, 21))
    shadow = Sprite(31, 34)
    ground_shadow(shadow, 15, 30, 12, 1.5)
    scene.img = shadow.image()
    scene.px = scene.img.load()
    bastion(scene, [(-.7,-.3),(.5,-.45),(1,.2),(.7,.9),(-.55,.85),(-.95,.25)], 6)
    block(scene,-.43,-.14,.8,.7,7,STONE,
          lambda u,v,lit: RED['dark'] if 2 < u < 5 and v < 5 else None,z=6)
    flat_roof(scene,-.43,-.14,.8,.7,13)
    pediment(scene,-.47,.6,.9,13,3)
    block(scene,.4,-.16,.32,.32,10,STONE,
          lambda u,v,lit: STONE['deep'] if 7 < v < 10 and 1 < u < 3 else None,z=6)
    band(scene,.36,-.2,.4,.4,16,height=1)
    seg(scene,P(scene,.56,0,17),P(scene,.56,0,19),ROOF['deep'])
    for n in range(3):
        block(scene,-.3-n*.05,.67+n*.13,.7+n*.1,.14,1,PALE,z=5-n*1.5)
    return scene.img


def shade(color, amount):
    target = 255 if amount > 0 else 0
    return tuple(int(c + (target - c) * abs(amount)) for c in color)

def karlstejn(seed=0):
    """Karlštejn's stepped rocky hill, Great/Marian Towers and slate-roofed Imperial Palace."""
    import iso
    from landmarks_czechia import block, windows, band, STONE, PALE, GOTHIC, SLATE
    from landmarks_iberia import hip_roof, crenellate
    from landmarks_paris import P, poly

    scene = iso.Scene(34, 42, (18, 32))
    shadow = Sprite(34, 42)
    ground_shadow(shadow, 17, 39, 14, 1.5)
    scene.img = shadow.image()
    scene.px = scene.img.load()
    # Native small geometry, with no resampling of the capital-scale castle.
    for points, material in (([(-.9, -.3, 5), (-.9, 1.05, 5), (.9, 1.05, 5), (.75, 1.2, 0), (-.98, 1.13, 0)], STONE['dark']),
                             ([(.9, -.3, 5), (.9, 1.05, 5), (.75, 1.2, 0), (1.05, -.23, 0)], GOTHIC['deep'])):
        poly(scene, [P(scene, *p) for p in points], lambda x, y, c=material: shade(c, -.13) if int(x+y) % 6 == 0 else c)
    block(scene, -.9, -.3, 1.8, 1.35, 5, STONE, z=2)
    # Great Tower above the lower Imperial Palace and Marian Tower.
    block(scene, -.41, -.53, .71, .71, 15, PALE, windows(PALE, 15, 5, 7), z=7)
    band(scene, -.41, -.53, .71, .71, 20, GOTHIC)
    hip_roof(scene, -.5, -.62, .89, .89, 22, 6, SLATE)
    for aa, bb in ((-.49, -.56), (.32, -.56), (-.49, .24), (.32, .24)):
        block(scene, aa, bb, .1, .1, 3, SLATE, z=22)
    block(scene, .26, .08, .6, .64, 12, PALE, windows(PALE, 12, 5, 6), z=6)
    hip_roof(scene, .18, -.01, .77, .8, 18, 5, SLATE)
    block(scene, -.71, .53, 1.28, .49, 8, PALE, windows(PALE, 8, 5, 7), z=5)
    hip_roof(scene, -.77, .47, 1.4, .61, 13, 4, SLATE)
    block(scene, -.86, .94, 1.73, .19, 4, STONE, z=4)
    crenellate(scene, -.86, .94, 1.73, .19, 8, STONE, set(), step=3, height=2)
    return scene.img


def malbork(seed=0):
    """Malbork's brick High Castle, steep red roofs, Grand Masters' Palace and curtain towers."""
    import iso
    from landmarks_poland import block, band, windows, BRICK, CLAY, STONE, SLATE
    from landmarks_iberia import hip_roof, crenellate, stone_courses
    from landmarks_amsterdam import gable_roof
    from landmarks_denmark import spire
    from landmarks_italy import cylinder

    scene = iso.Scene(40, 44, (22, 32))
    shadow = Sprite(40, 44)
    ground_shadow(shadow, 20, 41, 17, 1.2)
    scene.img = shadow.image()
    scene.px = scene.img.load()
    block(scene, -1.3, -.45, 2.6, 1.5, 2, STONE)
    # The broad High Castle's roof dominates; its little church gable has pinnacles.
    block(scene, -.07, -.4, 1.2, .8, 12, BRICK, windows(BRICK, 12, 5, 8), z=2)
    gable_roof(scene, -.1, -.43, 1.26, .86, 14, 8, CLAY, BRICK, 'point')
    for a, H in ((.04, 3), (.28, 5), (.51, 7), (.75, 5), (.98, 3)):
        block(scene, a, .42, .08, .1, H, BRICK, z=15)
    block(scene, .9, -.33, .27, .27, 15, BRICK, windows(BRICK, 15, 4, 8), z=2)
    crenellate(scene, .9, -.33, .27, .27, 17, BRICK, set(), step=3, height=2)
    # Grand Masters' Palace, lower outer ward and the Nogat-facing curtain.
    block(scene, -1.2, -.23, .87, 1.13, 9, BRICK, windows(BRICK, 9, 5, 8), z=2)
    hip_roof(scene, -1.25, -.28, .97, 1.23, 11, 6, CLAY)
    block(scene, -1.2, .8, 2.4, .2, 4, BRICK, stone_courses(BRICK, 3, 6), z=2)
    crenellate(scene, -1.2, .8, 2.4, .2, 6, BRICK, set(), step=4, height=2)
    for a, b, radius, H in ((-1, .87, .22, 7), (1.07, .6, .23, 8)):
        cylinder(scene, a, b, radius, radius, 2, H, BRICK,
                 lambda u, v, lit: BRICK['deep'] if int(u) % 5 == 2 and 3 < v < 6 else None)
        band(scene, a-radius, b-radius, radius*2, radius*2, H+2, STONE, 1)
        spire(scene, a, b, radius+.08, H+3, 5, CLAY, conical=True)
    block(scene, -1.2, .07, .3, .33, 10, BRICK, windows(BRICK, 10, 4, 8), z=2)
    hip_roof(scene, -1.25, .02, .4, .43, 12, 4, SLATE)
    return scene.img


def vianden(seed=0):
    """Vianden's hilltop Romanesque/Gothic residence, paired halls, chapel and curtain."""
    import iso
    from landmarks_luxembourg import block, STONE, ROCK, SLATE, PALE, GLAZE
    from landmarks_iberia import hip_roof, crenellate, stone_courses
    from landmarks_amsterdam import gable_roof
    from landmarks_italy import cylinder
    from landmarks_denmark import spire

    def openings(u, v, lit):
        c, level = int(u) % 5, int(v) % 8
        if c in (1, 2) and 3 <= level <= 5:
            return GLAZE['deep']
        if c in (0, 3) and 2 <= level <= 6 or level == 2 and c in (1, 2):
            return PALE['lit' if lit else 'dark']
        return stone_courses(STONE, 4, 7)(u, v, lit)

    scene = iso.Scene(38, 46, (20, 34))
    shadow = Sprite(38, 46)
    ground_shadow(shadow, 19, 43, 16, 1.3)
    scene.img = shadow.image()
    scene.px = scene.img.load()
    block(scene,-1.1,-.7,2.3,1.8,6,ROCK)
    # The two contiguous palas have very steep, long slate roofs.
    for a,b,w,d,h in ((-.8,-.45,1.25,.7,14),(.15,-.5,1.15,.8,15)):
        block(scene,a,b,w,d,h,STONE,openings,z=6)
        gable_roof(scene,a,b,w,d,h+6,8,SLATE,STONE,'point')
    # Romanesque chapel's polygonal end, separate round defensive tower and cap.
    cylinder(scene,-.7,.55,.4,.4,6,12,PALE,openings)
    hip_roof(scene,-1.1,.15,.8,.8,18,5,SLATE)
    cylinder(scene,-1,.1,.25,.25,2,17,STONE,openings)
    spire(scene,-1,.1,.28,19,5,SLATE,conical=True)
    cover=block(scene,-.7,.8,1.8,.3,6,STONE)
    crenellate(scene,-.7,.8,1.8,.3,6,STONE,cover,step=3,height=2)
    block(scene,.7,.35,.5,.65,9,STONE,openings)
    hip_roof(scene,.67,.32,.56,.71,9,4,SLATE)
    return scene.img


def spis_castle(seed=0):
    """Spiš Castle: roofless palas, round donjon and long irregular lower curtain on limestone."""
    import iso
    from landmarks_slovakia import block, STONE, ROCK, WHITE
    from landmarks_paris import P, poly
    from landmarks_iberia import crenellate, stone_courses
    from landmarks_italy import cylinder

    scene=iso.Scene(50,52,(27,31))
    shadow=Sprite(50,52)
    ground_shadow(shadow,25,49,21,1.2)
    scene.img=shadow.image();scene.px=scene.img.load()
    # Limestone promontory: higher upper ward to the west, lower terraces to the east.
    top=[P(scene,a,b,z) for a,b,z in ((-1.5,-.6,4),(-.2,-.8,6),(2.1,-.1,2),(2.4,1.2,2),(.2,1.6,4),(-1.7,.8,4))]
    base=[P(scene,a,b,0) for a,b in ((-1.8,-.8),(-.2,-1),(2.3,-.2),(2.6,1.4),(.2,1.9),(-2,.9))]
    poly(scene,top,lambda x,y:ROCK['lit'])
    for n,key in ((2,'dark'),(3,'dark'),(4,'lit'),(5,'lit')):
        poly(scene,[top[n],top[(n+1)%6],base[(n+1)%6],base[n]],
             lambda x,y,k=key:ROCK['line'] if (int(x)+int(y)*2)%7==0 else ROCK[k])
    def slits(u,v,lit):
        if int(u)%6 in (2,3) and 5<v<10:return STONE['deep']
        return stone_courses(STONE,3,7)(u,v,lit)
    # Roofless rectangular Romanesque palace, open square ward and broken wall tops.
    for a,b,w,d in ((-1.3,-.5,1.45,.22),(-1.3,-.3,.22,1.1),(-.1,-.3,.25,1.1),(-1.1,.6,1.15,.22)):
        cover=block(scene,a,b,w,d,13,STONE,slits,z=5)
        crenellate(scene,a,b,w,d,18,STONE,cover,step=4,height=2)
    cylinder(scene,.35,.35,.35,.35,5,16,STONE,slits,cap=False)
    cylinder(scene,.35,.35,.37,.37,20,1,WHITE,cap=False)
    # Round keep's dark open top, with a lit inner edge rather than a roof.
    poly(scene,[P(scene,.35+.22*math.cos(t*math.tau/16),.35+.22*math.sin(t*math.tau/16),21) for t in range(16)],lambda x,y:STONE['deep'])
    for a,b,w,d in ((.1,-.45,1.7,.18),(1.7,-.3,.22,1.4),(.1,1.08,1.8,.2)):
        cover=block(scene,a,b,w,d,6,STONE,slits,z=2)
        crenellate(scene,a,b,w,d,8,STONE,cover,step=4,height=2)
    block(scene,1.4,.85,.4,.4,8,STONE,slits,z=2)
    return scene.img


def tihany_abbey(seed=0):
    """Tihany's twin Baroque onion towers, red-roofed abbey and Balaton peninsula bluff."""
    import iso
    from landmarks_hungary import block, band, windows, STONE, WHITE, RED, SLATE, HILL_GRASS
    from landmarks_paris import P, poly
    from landmarks_iberia import hip_roof
    from landmarks_denmark import spire
    scene=iso.Scene(46,68,(23,49))
    shadow=Sprite(46,68)
    ground_shadow(shadow,23,64,19,1.3)
    scene.img=shadow.image();scene.px=scene.img.load()
    # Actual peninsula landform, rather than an invented sea surrounding the abbey.
    poly(scene,[P(scene,a,b,z) for a,b,z in ((-1.5,-.8,0),(1.4,-.8,0),(1.8,1,0),(-1,1.5,0))],
         lambda x,y:STONE['dark'] if int(y)%3 else STONE['line'])
    poly(scene,[P(scene,a,b,4) for a,b in ((-1.4,-.7),(1.3,-.7),(1.5,.9),(-1,1.2))],
         lambda x,y:HILL_GRASS)
    for a,b,w,d in ((-.9,-.65,1.8,.6),(.6,-.1,.5,1),(-.9,.6,2,.45)):
        block(scene,a,b,w,d,10,WHITE,windows(WHITE,10,5,8),z=4)
        hip_roof(scene,a,b,w,d,14,6,RED)
    # Long church nave behind its paired western towers.
    block(scene,-1,-.4,.8,1.45,16,WHITE,windows(WHITE,16,5,10),z=4)
    hip_roof(scene,-1,-.4,.8,1.45,20,8,RED)
    for a in (-1.1,.1):
        block(scene,a,.8,.58,.65,26,WHITE,windows(WHITE,26,5,10),z=4)
        for z in (6,19,29):band(scene,a,.8,.58,.65,z,WHITE)
        spire(scene,a+.29,1.125,.44,31,12,SLATE,onion=True)
    return scene.img


def kuressaare(seed=0):
    """Saaremaa's square episcopal castle: tall keep, lower tower and clay-roofed ranges."""
    import iso
    from landmarks_estonia import STONE, WHITE, CLAY, windows
    from landmarks_slovakia import block, band
    from landmarks_iberia import hip_roof
    from landmarks_paris import P, poly
    scene = iso.Scene(56, 68, (28, 46))
    shadow = Sprite(56, 68)
    ground_shadow(shadow, 28, 62, 23)
    scene.img = shadow.image(); scene.px = scene.img.load()
    # Low moat, grassy bastion and limestone retaining edge.
    poly(scene, [P(scene,a,b) for a,b in ((-2,-1),(1.6,-1),(2,1.3),(-1.6,1.4))],
         lambda x,y:hex_rgb('#477E91') if int(y)%3 else hex_rgb('#75A7AE'))
    block(scene,-1.5,-.8,2.8,1.9,3,STONE)
    for a,b,w,d in ((-1.2,-.65,2.3,.5),(-1.2,-.15,.5,1.15),
                    (.6,-.15,.5,1.15),(-.7,.55,1.3,.45)):
        block(scene,a,b,w,d,13,STONE,windows(STONE,13,6,10),z=3)
        hip_roof(scene,a,b,w,d,16,7,CLAY)
    for a,b,h in ((-.95,-.55,26),(.45,.4,19)):
        block(scene,a,b,.65,.65,h,STONE,windows(STONE,h,5,10),z=3)
        band(scene,a,b,.65,.65,h+2,WHITE)
        hip_roof(scene,a-.04,b-.04,.73,.73,h+3,8,CLAY)
    return scene.img


def rundale(seed=0):
    """Compact Rastrelli palace, low enough to leave nearby Riga's castle visible."""
    import iso
    from landmarks_latvia import YELLOW, PALE, SLATE, STONE, GLASS
    from landmarks_slovakia import block, band, pediment
    from landmarks_iberia import hip_roof
    from landmarks_paris import P, poly

    def openings(u,v,lit):
        c,level=int(u)%5,int(v)%7
        if 1<=c<=3 and 2<=level<=5:
            return PALE['lit' if lit else 'dark'] if c in (1,3) or level in (2,5) else GLASS['mid' if lit else 'dark']
        return YELLOW['lit' if lit else 'dark']
    scene=iso.Scene(46,29,(23,14))
    shadow=Sprite(46,29)
    ground_shadow(shadow,23,26,19)
    scene.img=shadow.image();scene.px=scene.img.load()
    poly(scene,[P(scene,a,b) for a,b in ((-1.3,-.7),(1.3,-.7),(1.3,1.6),(-1.3,1.6))],
         lambda x,y:C['leaf'] if int(x)%5 else STONE['lit'])
    for a,b,w,d in ((-1.2,-.6,2.4,.5),(-1.2,-.1,.5,1.2),(.7,-.1,.5,1.2)):
        block(scene,a,b,w,d,6,YELLOW,openings)
        for z in (1,5):band(scene,a,b,w,d,z,PALE)
        hip_roof(scene,a,b,w,d,6,2,SLATE)
    block(scene,-.45,-.65,.9,.7,7,YELLOW,openings)
    hip_roof(scene,-.45,-.65,.9,.7,7,2,SLATE)
    pediment(scene,-.5,-.05,1,.15,7,2,PALE)
    for a in (-.95,-.3,.35):
        poly(scene,[P(scene,a+u,1.2+v,.3) for u,v in ((0,0),(.35,0),(.35,.35),(0,.35))],
             lambda x,y:PALE['lit'] if (int(x)+int(y))%3==0 else C['leaf'])
    return scene.img


def trakai(seed=0):
    """Compact island fortress, leaving nearby Vilnius's capital castle visible."""
    import iso
    from landmarks_lithuania import BRICK, CLAY, STONE, WATER
    from landmarks_slovakia import block
    from landmarks_iberia import hip_roof, palette_of
    from landmarks_italy import cylinder
    from landmarks_denmark import spire
    from landmarks_paris import P, poly, seg

    def openings(u,v,lit):
        if int(u)%5 in (2,3) and 2<v<5:
            return BRICK['deep']
        return None
    scene=iso.Scene(44,29,(23,16))
    shadow=Sprite(44,29)
    ground_shadow(shadow,23,24,17)
    scene.img=shadow.image();scene.px=scene.img.load()
    poly(scene,[P(scene,a,b) for a,b in ((-1.5,-.9),(1.4,-.9),(1.4,1.2),(-1.5,1.2))],
         lambda x,y:WATER[2] if (int(x)+int(y))%7==0 else WATER[0])
    block(scene,-1.15,-.65,2.3,1.5,1,STONE)
    # Low ducal hall and taller keep, behind the open outer courtyard.
    block(scene,-.9,-.5,1.3,.55,4,BRICK,openings,z=1)
    hip_roof(scene,-.9,-.5,1.3,.55,5,2,CLAY)
    block(scene,-.55,-.4,.5,.55,7,BRICK,openings,z=1)
    hip_roof(scene,-.6,-.45,.6,.65,8,3,CLAY)
    for a,b,w,d in ((-1.1,.05,.3,.7),(.8,.05,.3,.7),(-.8,.65,1.6,.25)):
        block(scene,a,b,w,d,3,BRICK,openings,z=1)
        hip_roof(scene,a,b,w,d,4,2,CLAY)
    for a,b in ((-.95,.75),(.95,.75),(.95,-.5)):
        cylinder(scene,a,b,.23,.23,1,5,BRICK,openings)
        spire(scene,a,b,.3,6,3,CLAY,conical=True)
    block(scene,-.22,.9,.44,.8,1,palette_of(hex_rgb('#886348')),z=.5)
    for a in (-.22,.22):
        seg(scene,P(scene,a,.9,2.5),P(scene,a,1.7,2.5),C['bark_ol'])
    return scene.img


def bled(seed=0):
    """Bled Island in its lake: wooded island, Baroque stair from the south landing, white
    pilgrimage church with clay roof and the slender bell tower under its steep spire."""
    import iso
    from landmarks_slovenia import WHITE, CLAY, STONE, WATER, ROOF, GOLD
    from landmarks_slovakia import block, band
    from landmarks_iberia import hip_roof, arch_opening, palette_of
    from landmarks_italy import cylinder
    from landmarks_paris import P, poly, seg

    scene = iso.Scene(52, 64, (26, 46))
    shadow = Sprite(52, 64)
    ground_shadow(shadow, 26, 58, 21)
    scene.img = shadow.image(); scene.px = scene.img.load()
    poly(scene, [P(scene, a, b) for a, b in ((-1.45, -1.45), (1.45, -1.45), (1.45, 1.45), (-1.45, 1.45))],
         lambda x, y: WATER[2] if (int(x)*3+int(y)) % 11 == 0 else WATER[0] if (int(x)+int(y)) % 4 else WATER[1])
    # Low island: stone shore, lawn, and a wooded rim around the church.
    cylinder(scene, 0, 0, 1.25, 1.15, 0, 2, STONE)
    cylinder(scene, 0, 0, 1.15, 1.05, 2, 1, palette_of(hex_rgb('#6E9B4E')))
    leaf = ramp('#5C8F45', '#203C21')[0]
    def tree(a, b):
        x, y = P(scene, a, b, 3)
        for dx in range(-3, 4):
            for dy in range(-7, 1):
                if dx*dx/10 + (dy+3.5)**2/12 <= 1:
                    scene.put(x+dx, y+dy, leaf[0] if dx*dx/10+(dy+3.5)**2/12 > .7 else leaf[1] if dx > 0 else leaf[2])
        scene.put(x, y+1, C['bark'])
    for a, b in ((-.95, -.55), (.55, -.85), (.9, -.2)):
        tree(a, b)
    # Church nave and apse, then the west bell tower and the stair down to the landing.
    block(scene, -.45, -.55, .75, 1.05, 9, WHITE,
          lambda u, v, lit: arch_opening(int(u) % 5, v, 2.5, 1, 5, WHITE['deep']) if 2 < v < 8 else None, z=3)
    hip_roof(scene, -.5, -.6, .85, 1.15, 12, 5, CLAY)
    block(scene, -.36, .45, .34, .34, 22, WHITE,
          lambda u, v, lit: WHITE['deep'] if int(u) % 4 == 1 and 15 < v < 19 else None, z=3)
    band(scene, -.36, .45, .34, .34, 18, WHITE)
    T, R, B, L = [P(scene, a, b, 25) for a, b in ((-.38, .43), (0, .43), (0, .81), (-.38, .81))]
    apex = P(scene, -.19, .62, 40)
    poly(scene, [L, B, apex], lambda x, y: ROOF['lit'] if int(y) % 3 else ROOF['line'])
    poly(scene, [B, R, apex], lambda x, y: ROOF['dark'] if int(y) % 3 else ROOF['deep'])
    seg(scene, B, apex, ROOF['hi'])
    seg(scene, apex, (apex[0], apex[1]-3), GOLD['lit'])
    for a, b in ((-1.0, .55), (.75, .6)):
        tree(a, b)
    for k in range(4):
        block(scene, -.3+k*.02, .95+k*.12, .45, .16, 3-k*.7, STONE)
    return scene.img


def plitvice(seed=0):
    """Plitvice Lakes at Veliki slap: a wooded travertine cliff, the tall white fall dropping into
    a turquoise pool, two lake terraces stepping down over mossy travertine barriers with small
    cascades, and a timber boardwalk along the water."""
    import iso
    from landmarks_croatia import ROCK
    from landmarks_slovakia import block
    from landmarks_paris import P, poly, seg

    scene = iso.Scene(48, 47, (24, 29))
    shadow = Sprite(48, 47)
    ground_shadow(shadow, 24, 43, 19)
    scene.img = shadow.image(); scene.px = scene.img.load()
    lake = (hex_rgb('#4FC3C0'), hex_rgb('#37A3A8'), hex_rgb('#C8F2EC'))
    moss = hex_rgb('#7FA65A')
    def water(x, y):
        return lake[2] if (int(x)*3+int(y)) % 13 == 0 else lake[0] if (int(x)+int(y)) % 5 else lake[1]
    # Back: the travertine cliff with forest on top; the fall drops down its lit face.
    def cliff(u, v, lit):
        if lit and 8 <= u <= 10:
            return WHITE_FALL[int(v+u) % 3]
        if int(v) % 4 == 0 or h01(int(u), int(v), 8101) < .15:
            return ROCK['line' if lit else 'deep']
        return None
    block(scene, -1.3, -1.4, 2.6, .8, 13, ROCK, cliff)
    leaf = ramp('#4F8A3E', '#1C3A1E')[0]
    def tree(a, b, z, h=9):
        x, y = P(scene, a, b, z)
        for dx in range(-3, 4):
            for dy in range(-h, 1):
                e = dx*dx/9+(dy+h/2)**2/(h*h/4)
                if e <= 1:
                    scene.put(x+dx, y+dy, leaf[0] if e > .7 else leaf[1] if dx > 0 else leaf[2])
        scene.put(x, y+1, C['bark'])
    for a in (-1.1, -.4, .3):
        tree(a, -1.05, 13, 6)
    # Upper pool at the foot of the fall, then the barrier and the lower lake.
    block(scene, -1.4, -.6, 2.8, 1.0, 4, ROCK,
          lambda u, v, lit: moss if v > 2.5 else lake[2] if lit and int(u) % 6 in (1, 2) else None)
    poly(scene, [P(scene, a, b, 4) for a, b in ((-1.3, -.6), (1.3, -.6), (1.3, .35), (-1.3, .35))], water)
    x, y = P(scene, -.25, -.6, 4)
    for k in range(3):
        scene.put(x-1+k, y, lake[2]); scene.put(x+k, y+1, lake[2])        # spray at the fall's foot
    poly(scene, [P(scene, a, b, 0) for a, b in ((-1.4, .45), (1.4, .45), (1.4, 1.4), (-1.4, 1.4))], water)
    # Boardwalk along the lower lake.
    for k in range(7):
        a = -1.2+k*.36
        seg(scene, P(scene, a, 1.05, 1), P(scene, a, 1.3, 1), hex_rgb('#9C7A52'))
    seg(scene, P(scene, -1.2, 1.05, 1), P(scene, 1.0, 1.05, 1), hex_rgb('#6E5236'))
    for a, b in ((-1.5, .1), (1.45, -.25), (1.5, .85)):
        tree(a, b, 0, 8)
    return scene.img


def stari_most(seed=0):
    """Mostar's single high limestone arch and the two bridge-keeper towers over the Neretva."""
    import iso
    from landmarks_bosnia import STONE, WHITE, LEAD, BLUE
    from landmarks_slovakia import block, band
    from landmarks_iberia import hip_roof, stone_courses
    from landmarks_paris import P, poly, seg

    scene = iso.Scene(40, 34, (20, 24))
    shadow = Sprite(40, 34)
    ground_shadow(shadow, 20, 30, 17, 1.5)
    scene.img = shadow.image(); scene.px = scene.img.load()
    water = (hex_rgb('#398D94'), hex_rgb('#59B7B1'), hex_rgb('#D3F0DF'))
    poly(scene, [P(scene,a,b) for a,b in ((-.65,-1),(.65,-1),(.65,1.2),(-.65,1.2))],
         lambda x,y:water[2] if h01(int(x)//3,int(y),8201)<.06 else water[int(h01(int(x)//4,int(y)//2,8202)<.25)])
    # Limestone bank abutments and the higher eastern (Tara) keeper tower.
    for a,b,h in ((-1.45,.07,10),(1,-.45,13)):
        courses = stone_courses(STONE,3,7)
        block(scene,a,b,.48,.6,h,STONE,
              lambda u,v,lit: BLUE['deep'] if int(u)%4==2 and 4<v<8 else courses(u,v,lit))
        band(scene,a,b,.48,.6,h-1,WHITE,1)
        hip_roof(scene,a-.07,b-.07,.62,.74,h,3,LEAD)
    start=P(scene,-1.2,.45)
    length=19.6
    for x,y in iso.polygon_pixels([P(scene,-1.2,.45),P(scene,1.25,.45),
                                  P(scene,1.25,.45,11),P(scene,-1.2,.45,11)]):
        u=(x-start[0])/length
        v=start[1]+(x-start[0])*.5-y
        arch=8.5*math.sqrt(max(0,1-((u-.5)/.5)**2))
        if arch <= v <= arch+2:
            scene.put(x,y,STONE['lit'] if int(v)%3 else STONE['line'])
    # The hump-backed deck is a succession of 3D cross-sections, with two continuous parapets.
    previous = None
    for k in range(25):
        a=-1.2+2.45*k/24
        z=2+8.5*math.sqrt(max(0,1-((k/24-.5)/.5)**2))
        cross=[P(scene,a,b,z) for b in (.1,.45)]
        if previous:
            poly(scene,[previous[0],cross[0],cross[1],previous[1]],lambda x,y:WHITE['lit'])
            for old,new in zip(previous,cross):
                seg(scene,old,new,WHITE['hi'])
        previous=cross
    return scene.img


def golubac(seed=0):
    """Danube-edge limestone fortress climbing an Iron Gate crag; hilltop keep and cannon tower.
    Compressed selected towers, rather than a claim that every tower fits this country sprite.
    """
    import iso
    from landmarks_serbia import STONE, ROCK, CLAY, IRON
    from landmarks_bosnia import cylinder
    from landmarks_slovakia import block, band
    from landmarks_iberia import stone_courses, crenellate
    from landmarks_paris import P, poly
    from landmarks_slovenia import revolve

    scene = iso.Scene(44, 52, (22, 40))
    shadow = Sprite(44, 52)
    ground_shadow(shadow, 22, 48, 19, 1.8)
    scene.img = shadow.image(); scene.px = scene.img.load()
    poly(scene, [P(scene,a,b) for a,b in ((-1.6,-1.1),(1.8,-1.1),(1.8,.3),(-1.6,.3))],
         lambda x,y:hex_rgb('#B6D6D2') if h01(x//3,y,8300)<.04 else hex_rgb('#537F88'))
    # Rocky ridge rises inland; the highest cylindrical keep carries a conical tiled cap.
    poly(scene,[(6,43),(10,31),(23,22),(31,29),(40,45),(25,49)],
         lambda x,y:ROCK['line'] if (x+3*y)%8==0 else ROCK['lit' if x<23 else 'dark'])
    cylinder(scene,.15,-.25,.34,.34,17,14,STONE,
             lambda u,v,lit:IRON if 6<v<9 and int(u)%4==1 else stone_courses(STONE,3,6)(u,v,lit),segments=12)
    revolve(scene,.15,-.25,.4,31,6,[(0,1),(1,0)],CLAY,ribs=3)
    # Rising curtains and five of the lower square towers, with arrow slits and crenels.
    for a,b,w,d,z,h in ((-1.3,.2,1.4,.22,2,8),(.15,.15,1.2,.22,4,11),
                      (-.35,.2,.2,1.4,4,10),(.9,.2,.2,1.1,2,9)):
        cover=block(scene,a,b,w,d,h,STONE,stone_courses(STONE,3,6),z=z)
        crenellate(scene,a,b,w,d,z+h,STONE,cover,step=3,height=2)
    for a,b,z,h in ((-1.4,.1,1,13),(-.55,.75,5,14),(.62,.1,8,15),(1.05,1,1,12),(-.65,1.45,0,10)):
        cover=block(scene,a,b,.5,.55,h,STONE,
                    lambda u,v,lit:IRON if 4<v<7 and int(u)%4==2 else stone_courses(STONE,3,6)(u,v,lit),z=z)
        crenellate(scene,a,b,.5,.55,z+h,STONE,cover,step=3,height=2)
    # Later low polygonal cannon tower at the actual water edge.
    cylinder(scene,-1.15,-.6,.42,.42,0,7,STONE,
             lambda u,v,lit:IRON if 2<v<4 and int(u)%4==1 else None,segments=8)
    band(scene,-1.55,-1,.8,.8,6,STONE)
    return scene.img


def ostrog(seed=0):
    """Upper Ostrog's white arcaded cliff monastery, at native country-icon resolution."""
    import iso
    from landmarks_montenegro import ROCK, WHITE, CLAY, GOLD, IRON
    from landmarks_slovakia import block, band
    from landmarks_iberia import hip_roof, arch_opening, stone_courses
    from landmarks_paris import poly, P

    scene = iso.Scene(48, 60, (24, 46))
    shadow = Sprite(48, 60)
    ground_shadow(shadow, 24, 55, 20, 2)
    scene.img = shadow.image(); scene.px = scene.img.load()
    # The upper monastery is embedded in a much taller, overhanging limestone escarpment.
    poly(scene, [(5,53),(3,20),(10,8),(19,4),(25,2),(38,9),(44,27),(42,51),(25,57)],
         lambda x,y: ROCK['line'] if (x+2*y)%13 == 0 else ROCK['lit' if x<24 else 'dark'])
    poly(scene, [(7,27),(14,16),(32,14),(40,25),(36,44),(13,46)],
         lambda x,y: ROCK['deep'] if x>17 else ROCK['dark'])
    # Low terraced plinth; two white storeys and their shaded end face project out of the cave.
    block(scene,-1.8,-.1,3.4,1.5,6,ROCK,stone_courses(ROCK,3,8))
    def arcade(u,v,lit):
        c = int(u)%6
        if int(v)%8 == 0:return WHITE['hi' if lit else 'mid']
        opening = arch_opening(c,v%8-1,3,1.6,3,IRON)
        if opening and 1<v<15:return opening
        return None
    block(scene,-1.6,-.15,3.2,1.25,17,WHITE,arcade,z=6)
    for zz in (6,14,22):band(scene,-1.6,-.15,3.2,1.25,zz,WHITE)
    hip_roof(scene,-1.7,-.2,3.4,1.35,23,3,CLAY)
    # Upper icon recesses nestle immediately beneath the rock, with a small square bell stage.
    block(scene,-.75,-.25,1.6,.8,10,WHITE,
          lambda u,v,lit: arch_opening(int(u)%5,v,2.5,1.5,5,GOLD['dark']) if lit else None,z=23)
    hip_roof(scene,-.85,-.3,1.8,.9,33,3,CLAY)
    block(scene,1.05,.1,.65,.7,12,WHITE,
          lambda u,v,lit: IRON if 6<v<10 and 1<int(u)%5<4 else None,z=22)
    hip_roof(scene,1,.05,.75,.8,34,3,CLAY)
    segs=[((1.38,.45,37),(1.38,.45,41)),((1.2,.45,39),(1.56,.45,39))]
    for a,b in segs:iso.line(scene,P(scene,*a),P(scene,*b),GOLD['lit'])
    return scene.img


def kruje(seed=0):
    """Krujë's limestone fortress hill and the museum's round/stepped stone masses."""
    import iso
    from landmarks_albania import STONE, WHITE, ROCK, LEAD, IRON
    from landmarks_slovakia import block, band
    from landmarks_bosnia import cylinder
    from landmarks_iberia import crenellate, arch_opening, stone_courses
    from landmarks_paris import poly

    scene = iso.Scene(54, 66, (27, 50))
    shadow = Sprite(54, 66)
    ground_shadow(shadow, 27, 60, 21, 2)
    scene.img = shadow.image(); scene.px = scene.img.load()
    poly(scene, [(6,54),(9,44),(16,35),(34,34),(46,43),(49,57),(34,62),(16,60)],
         lambda x,y:ROCK['line'] if (x+2*y)%11==0 else ROCK['lit' if x<24 else 'dark'])
    # A selected curtain and the museum inside it; the whole complex is compressed.
    block(scene,-1.6,-.6,3.4,2.1,8,STONE,stone_courses(STONE,3,7),z=3)
    block(scene,-.7,-1.2,2.4,1.5,20,STONE,
          lambda u,v,lit:arch_opening(int(u)%6,v,3,1.4,10,IRON) if v<13 else stone_courses(STONE,4,9)(u,v,lit),z=8)
    band(scene,-.7,-1.2,2.4,1.5,28,WHITE,2)
    cylinder(scene,-1.05,-.1,.8,.8,11,25,STONE,
             lambda u,v,lit:arch_opening(int(u)%6,v-16,3,1.4,4,IRON) if v>16 else stone_courses(STONE,4,8)(u,v,lit),segments=16)
    cylinder(scene,-1.05,-.1,.86,.86,35,2,WHITE,segments=16)
    for a,b,wi,wj,zz in ((-.7,-1.2,2.4,1.5,30),(-1.7,.9,3.6,.4,11)):
        block(scene,a,b,wi,wj,.8,LEAD,z=zz)
        crenellate(scene,a,b,wi,wj,zz+1,STONE,set(),step=4,height=3)
    block(scene,.5,.15,1.1,.9,15,STONE,
          lambda u,v,lit:arch_opening(u,v,4,1.8,7,IRON) if lit else stone_courses(STONE,4,8)(u,v,lit),z=8)
    return scene.img


def kaneo(seed=0):
    """St John at Kaneo: one Byzantine drum/dome, clay cross roofs, cliff above Lake Ohrid."""
    import iso
    from landmarks_macedonia import STONE, BRICK, CLAY, ROCK, WHITE, WOOD
    from landmarks_slovakia import block, band
    from landmarks_bosnia import cylinder
    from landmarks_iberia import hip_roof, stone_courses, arch_opening
    from landmarks_slovenia import revolve, DOME
    from landmarks_paris import poly, P, seg

    scene = iso.Scene(52, 62, (25, 44))
    shadow = Sprite(52, 62)
    ground_shadow(shadow, 26, 58, 22, 2)
    scene.img = shadow.image(); scene.px = scene.img.load()
    poly(scene, [(3,53),(15,48),(37,48),(49,54),(43,59),(16,59)],
         lambda x,y:hex_rgb('#A9D7DF') if (x+3*y)%11==0 else hex_rgb('#457FA0'))
    poly(scene, [(5,44),(13,36),(36,36),(44,44),(38,55),(14,55)],
         lambda x,y:ROCK['line'] if (x+2*y)%13==0 else ROCK['lit' if x<23 else 'dark'])
    def masonry(u,v,lit):
        if int(v)%5==0:return BRICK['lit' if lit else 'dark']
        hole=arch_opening(int(u)%8,v-3,4,1.5,7,WOOD['deep']) if 3<v<12 else None
        return hole or stone_courses(STONE,3,8)(u,v,lit)
    block(scene,-1.3,-.7,2.7,1.6,14,STONE,masonry,z=3)
    hip_roof(scene,-1.42,-.82,2.94,1.84,17,6,CLAY)
    block(scene,-.7,-1.2,1.5,2.7,14,STONE,masonry,z=3)
    hip_roof(scene,-.82,-1.32,1.74,2.94,17,6,CLAY)
    # Eastern apse behind the nave, one polygonal central drum.
    cylinder(scene,.9,-.8,.65,.6,3,11,STONE,masonry,segments=8)
    hip_roof(scene,.35,-1.4,1.2,1.2,14,4,CLAY)
    cylinder(scene,.05,.1,.78,.78,20,12,BRICK,masonry,segments=8)
    band(scene,-.57,-.52,1.24,1.24,31,STONE,1)
    revolve(scene,.05,.1,.86,32,6,DOME,CLAY,ribs=4,segments=16)
    seg(scene,P(scene,.05,.1,38),P(scene,.05,.1,43),WHITE['dark'])
    seg(scene,P(scene,-.15,.1,41),P(scene,.25,.1,41),WHITE['lit'])
    return scene.img


def meteora(seed=0):
    """Holy Trinity, Meteora: a clay-roofed monastery on its sheer sandstone pillar."""
    import iso
    from landmarks_greece import ROCK, MARBLE, WHITE, CLAY, WOOD, GROUND
    from landmarks_slovakia import block
    from landmarks_bosnia import cylinder
    from landmarks_iberia import hip_roof, stone_courses, arch_opening
    from landmarks_slovenia import revolve, DOME
    from landmarks_paris import poly, P, seg

    scene=iso.Scene(52,72,(26,60))
    shadow=Sprite(52,72);ground_shadow(shadow,26,68,21,2)
    scene.img=shadow.image();scene.px=scene.img.load()
    # Unequal polygonal strata keep this a weathered rock pillar, not a castle pedestal.
    base=[(-1.5,-.7),(-.5,-1.4),(1,-1.05),(1.65,.2),(1.1,1.15),(-.7,1.3),(-1.6,.3)]
    top=[(-1.4,-.6),(-.5,-1.2),(1.1,-.9),(1.45,.25),(.9,1.05),(-.6,1.15),(-1.4,.3)]
    faces=[]
    for k in range(len(base)):
        a,b=base[k],base[(k+1)%len(base)];c,d=top[k],top[(k+1)%len(base)]
        faces.append((sum(a+b),[P(scene,*a,0),P(scene,*b,0),P(scene,*d,34),P(scene,*c,34)],k))
    for _,pts,k in sorted(faces):
        poly(scene,pts,lambda x,y,k=k:ROCK['line'] if (x*3+y//5)%13==0 else
             ROCK['lit' if k in (4,5) else 'dark' if k in (2,3) else 'mid'])
    poly(scene,[P(scene,*p,34) for p in top],lambda x,y:GROUND['dust'])
    # Terraced stair cut into the southern rock, without an invented bridge.
    for n in range(13):
        a=-.75+n*.11;b=.85
        seg(scene,P(scene,a,b,3+n*2.15),P(scene,a+.32,b+.25,3+n*2.15),MARBLE['lit'])
    def openings(u,v,lit):
        c=int(u)%7
        if 3<v<9:
            return arch_opening(c,v-2,3,1.4,6,WOOD['deep']) or stone_courses(MARBLE,3,8)(u,v,lit)
        return stone_courses(MARBLE,3,8)(u,v,lit)
    # Low cells along the rock edge, enclosing a small court.
    for a,b,w,d in ((-1.2,-.9,2.25,.65),(-1.2,-.3,.65,1.3),(.45,-.2,.65,1.1)):
        block(scene,a,b,w,d,10,MARBLE,openings,z=34)
        hip_roof(scene,a-.08,b-.08,w+.16,d+.16,44,4,CLAY)
    block(scene,-.4,-.1,.8,.95,10,WHITE,openings,z=34)
    hip_roof(scene,-.48,-.18,.96,1.11,44,4,CLAY)
    cylinder(scene,0,.35,.32,.32,47,5,MARBLE,openings,segments=8)
    revolve(scene,0,.35,.39,52,3,DOME,CLAY,ribs=2,segments=12)
    seg(scene,P(scene,0,.35,55),P(scene,0,.35,59),WHITE['dark'])
    seg(scene,P(scene,-.13,.35,57),P(scene,.13,.35,57),WHITE['lit'])
    return scene.img


def bran(seed=0):
    """Bran's irregular white courtyard castle, clay-roofed round SW tower and rocky spur."""
    import iso
    from landmarks_romania import WHITE, STONE, CLAY, ROCK, WOOD, windows
    from landmarks_slovakia import block, band
    from landmarks_bosnia import cylinder
    from landmarks_iberia import hip_roof
    from landmarks_slovenia import revolve, slab

    scene = iso.Scene(60,76,(30,62))
    shadow = Sprite(60,76)
    ground_shadow(shadow,30,71,24,3)
    scene.img = shadow.image()
    scene.px = scene.img.load()
    slab(scene,[(-1.8,-1),(-.7,-1.65),(1.6,-1.2),(1.9,.5),(.9,1.65),(-1.6,1.1)],0,10,ROCK,
         lambda u,v,lit: ROCK['line'] if (int(u)*3+int(v)//4)%11==0 else None)
    # Unequal roofed wings enclose the small court. The higher rear block is rectangular.
    for a,b,w,d,h in ((-1.3,-1.1,2.5,.7,21),(-1.4,-.4,.7,1.6,18),(.7,-.3,.7,1.7,25)):
        block(scene,a,b,w,d,h,WHITE,windows(WHITE,h,8,10,True),z=10)
        hip_roof(scene,a-.05,b-.05,w+.1,d+.1,10+h,8,CLAY)
    block(scene,-.7,-1.1,1.1,1,36,WHITE,windows(WHITE,36,8,10),z=10)
    band(scene,-.7,-1.1,1.1,1,44,STONE,2)
    hip_roof(scene,-.8,-1.2,1.3,1.2,46,11,CLAY)
    # A timbered inner gallery, openings and roof seam highlights remain legible at native pixels.
    block(scene,-.7,-.35,1.4,.3,9,STONE,
          lambda u,v,lit: WOOD if int(u)%4==0 or int(v) in (1,7) else None,z=22)
    hip_roof(scene,-.75,-.4,1.5,.5,31,5,CLAY)
    cylinder(scene,-.6,1.05,.55,.55,10,27,WHITE,windows(WHITE,27,8,10),segments=16)
    revolve(scene,-.6,1.05,.76,37,15,[(0,1),(1,.02)],CLAY,ribs=3,segments=24)
    return scene.img


def pamukkale(seed=0):
    """Pamukkale's white calcite terraces, irregular mineral curtains and blue thermal pools."""
    import iso
    from landmarks_ankara import WHITE, GROUND
    from landmarks_slovenia import slab
    from landmarks_paris import P, seg, poly

    scene = iso.Scene(68, 68, (34, 42))
    shadow = Sprite(68, 68)
    ground_shadow(shadow, 34, 54, 27, 3)
    scene.img = shadow.image()
    scene.px = scene.img.load()
    # Recurring rim shapes vary by level; the deposits are a landscape, not equal stair slabs.
    for n in range(5):
        a,b=-2.0+n*.12,-1.7+n*.08
        w,d=3.9-n*.48,3.4-n*.43
        points=[(a,b+.2),(a+.5,b-.12),(a+w-.4,b),(a+w,b+.45),
                (a+w-.12,b+d-.35),(a+w-.65,b+d),(a+.6,b+d+.1),(a-.13,b+d-.45)]
        bottom,top=n*3,(n+1)*3
        slab(scene,points,bottom,top,WHITE,
             lambda u,v,lit:WHITE['line'] if (int(u)*3+int(v))%13==0 else
             WHITE['hi' if lit else 'mid'] if int(u)%3==0 else None)
        # Pools inset behind thick white scalloped lips, with sparse reflected glints.
        centre=(a+w/2,b+d/2)
        pool=[(centre[0]+(x-centre[0])*.91,centre[1]+(y-centre[1])*.91) for x,y in points]
        poly(scene,[P(scene,x,y,top+.1) for x,y in pool],
             lambda x,y:GROUND['pool_hi'] if (x*3+y)%19==0 else
             GROUND['pool_dark'] if (x+2*y)%13<3 else GROUND['pool'])
        for p,q in zip(pool,pool[1:]+pool[:1]):
            seg(scene,P(scene,*p,top+.2),P(scene,*q,top+.2),WHITE['hi'])
    return scene.img


WHITE_FALL = (hex_rgb('#FFFFFF'), hex_rgb('#DDF3F4'), hex_rgb('#B6E2E6'))


FAUNA = {
    "deer": deer, "fox": fox, "elephant": elephant, "zebra": zebra, "panda": panda,
    "tiger": tiger, "bison": bison, "moose": moose, "jaguar": jaguar, "capybara": capybara,
    "kangaroo": kangaroo, "kiwi": kiwi, "penguin": penguin, "seal": seal,
    "brown-bear": brown_bear, "wild-boar": wild_boar, "lion": lion, "giraffe": giraffe,
    "rhinoceros": rhinoceros, "camel": camel, "orangutan": orangutan, "snow-leopard": snow_leopard,
    "wolf": wolf, "alligator": alligator, "guanaco": guanaco, "toucan": toucan, "koala": koala,
    "emu": emu, "orca": orca,
}
FLORA = {
    "oak": tree, "pine": pine, "olive": olive, "acacia": acacia, "baobab": baobab, "palm": palm,
    "bamboo": bamboo, "eucalyptus": eucalyptus, "fern": fern, "grass": grass, "cactus": cactus,
    "dune": dune, "red-rock": red_rock, "volcano": volcano, "glacier": glacier, "iceberg": iceberg,
    "windmill": windmill, "mont-saint-michel": mont_saint_michel, "vineyard": vineyard,
}


def meritxell(seed=0):
    """Bofill's NEW Meritxell sanctuary: white arch rims, open court and square bell tower."""
    import iso
    from landmarks_andorra import GRANITE, PALE, SLATE, porch
    from landmarks_slovakia import block, band
    from landmarks_iberia import hip_roof, stone_courses
    from landmarks_paris import P, poly

    scene = iso.Scene(56, 40, (29, 23))
    shadow = Sprite(56, 40)
    ground_shadow(shadow,29,35,21,2)
    scene.img=shadow.image();scene.px=scene.img.load()
    # Low rear sanctuary and side ranges enclose a genuinely open paved court.
    block(scene,-1.0,-.7,2.1,.85,10,GRANITE,stone_courses(GRANITE,3,6))
    hip_roof(scene,-1.05,-.75,2.2,.95,10,4,SLATE)
    poly(scene,[P(scene,a,b) for a,b in ((-1.4,.15),(1.4,.15),(1.4,1.6),(-1.4,1.6))],
         lambda x,y:PALE['mid'] if (x+y)%6 else GRANITE['mid'])
    for a in (-1.5,1.0):
        block(scene,a,.05,.5,1.35,6,GRANITE,stone_courses(GRANITE,3,6))
        band(scene,a,.05,.5,1.35,6,PALE,1)
    # Distinctive white-rimmed broad arches leave transparent/dark court recesses behind.
    porch(-1.5,1.2,3.0,.35,0,9,2,PALE,s=scene)
    block(scene,1.08,-.45,.58,.65,21,GRANITE,
          lambda u,v,lit:SLATE['deep'] if 14<v<19 and 1<int(u)%5<4 else stone_courses(GRANITE,3,6)(u,v,lit))
    band(scene,1.08,-.45,.58,.65,20,PALE,1)
    return scene.img


def rila(seed=0):
    """Rila's cloister court, striped five-domed Nativity church and separate Hrelyo tower."""
    import iso
    from landmarks_bulgaria import WHITE, BRICK, IVORY, CLAY, LEAD, WOOD, windows, cross
    from landmarks_iberia import hip_roof
    from landmarks_slovakia import block, band
    from landmarks_bosnia import cylinder
    from landmarks_slovenia import revolve, DOME
    from landmarks_paris import P, poly

    scene=iso.Scene(72,66,(36,38))
    shadow=Sprite(72,66);ground_shadow(shadow,36,58,30,3)
    scene.img=shadow.image();scene.px=scene.img.load()
    poly(scene,[P(scene,a,b) for a,b in ((-2,-1.8),(2.1,-1.8),(2.1,2),(-2,2))],
         lambda x,y:IVORY['mid'] if (x+2*y)%7 else IVORY['line'])
    def arcade(u,v,lit):
        c,k=int(u)%6,int(v)%7
        if k<5 and 1<c<5:return WOOD if k<3 or abs(c-3)<2 else WHITE['dark']
        if k==6:return BRICK['lit' if lit else 'dark']
        return WHITE['lit' if lit else 'dark']
    # Back and side cloister wings leave the courtyard and central church visible.
    for a,b,w,d in ((-1.85,-1.65,3.9,.55),(-1.85,-1.1,.6,3.1),(1.55,-1.1,.6,3.1)):
        block(scene,a,b,w,d,15,WHITE,arcade)
        hip_roof(scene,a-.07,b-.07,w+.14,d+.14,16,5,CLAY)
        band(scene,a,b,w,d,7,BRICK,1)
    # Medieval stone tower stands separately to the NE of the Nativity church.
    block(scene,.8,-.95,.65,.7,28,IVORY,windows(IVORY,28,6,9))
    band(scene,.8,-.95,.65,.7,26,BRICK,2)
    hip_roof(scene,.72,-1.03,.81,.86,29,3,CLAY)
    # Five copper/lead domes: main dome, two western and two eastern smaller domes.
    church_windows=windows(WHITE,13,7,10,True)
    def stripes(u,v,lit):
        return BRICK['lit' if lit else 'dark'] if int(v)%5 in (0,1) else church_windows(u,v,lit)
    block(scene,-.75,-.35,1.5,2.2,12,WHITE,stripes)
    hip_roof(scene,-.82,-.42,1.64,2.34,13,4,CLAY)
    for a,b,r,base,rise in ((-.48,-.05,.29,16,4),(.48,-.05,.29,16,4),
                           (-.48,1.32,.29,16,4),(.48,1.32,.29,16,4),(0,.65,.48,21,6)):
        cylinder(scene,a,b,r*.8,r*.8,base-4,4,WHITE,stripes,segments=12)
        revolve(scene,a,b,r,base,rise,DOME,LEAD,ribs=3,segments=16)
        cross(scene,a,b,base+rise,3)
    # The western porch is shown as an arcade, rather than a solid wall of dark stripes.
    block(scene,-.9,1.7,1.8,.42,7,WHITE,arcade)
    hip_roof(scene,-.98,1.62,1.96,.58,8,3,CLAY)
    return scene.img


def soroca(seed=0):
    """Soroca's round Dniester fortress: four round towers and one eastern gate tower."""
    import iso
    from landmarks_paris import P, seg, poly
    from landmarks_bosnia import cylinder
    from landmarks_slovakia import block, band
    from landmarks_iberia import stone_courses, hip_roof
    from landmarks_slovenia import revolve
    from landmarks_moldova import STONE, WHITE, CLAY

    scene=iso.Scene(72,68,(36,50))
    # Native pixels, transparent margins; no fractional image resampling.
    scene.img=Image.new('RGBA',(72,68),(0,0,0,0));scene.px=scene.img.load()
    ri=1.95
    def slit(u,v,lit):
        if int(u)%9 in (4,5) and 7<v<11:return STONE['deep']
        return stone_courses(STONE,3,9)(u,v,lit)
    parts=[]
    # A curved curtain ring around an actual open paved court.
    poly(scene,[P(scene,ri*math.cos(k*math.tau/40),ri*math.sin(k*math.tau/40),0)
                for k in range(40)],lambda x,y:WHITE['dark'] if (x+2*y)%6 else STONE['line'])
    for k in range(32):
        a,b=k*math.tau/32,(k+1)*math.tau/32
        ps=[(ri*math.cos(t),ri*math.sin(t)) for t in (a,b)]
        parts.append((sum(sum(p) for p in ps)/2,'wall',ps))
    # East is +i,-j; the single rectangular river-facing gate occupies that compass point.
    for k in range(5):
        a=-math.pi/4+k*math.tau/5
        ci,cj=ri*math.cos(a),ri*math.sin(a)
        parts.append((ci+cj,'gate' if k==0 else 'tower',(ci,cj)))
    for _,kind,data in sorted(parts):
        if kind=='wall':
            (ai,aj),(bi,bj)=data
            a,b=P(scene,ai,aj),P(scene,bi,bj)
            lit=(ai+bi)<(aj+bj)
            poly(scene,[a,b,(b[0],b[1]-16),(a[0],a[1]-16)],
                 lambda x,y,lit=lit:STONE['line'] if y%3==0 else STONE['lit' if lit else 'dark'])
            seg(scene,(a[0],a[1]-16),(b[0],b[1]-16),WHITE['lit'])
            continue
        ci,cj=data
        if kind=='gate':
            block(scene,ci-.52,cj-.52,1.04,1.04,22,STONE,slit)
            band(scene,ci-.52,cj-.52,1.04,1.04,20,WHITE,2)
            hip_roof(scene,ci-.65,cj-.65,1.3,1.3,23,7,CLAY)
        else:
            cylinder(scene,ci,cj,.62,.62,0,22,STONE,slit,segments=20)
            cylinder(scene,ci,cj,.7,.7,21,2,WHITE,segments=20)
            revolve(scene,ci,cj,.8,23,9,[(0,1),(1,.01)],CLAY,ribs=5,segments=20)
    return scene.img


ICONS = {
    "tree": tree, "pine": pine, "mountain": mountain, "hill": hill, "castle": castle,
    "church": church, "house": house, "boat": sailboat, "pin": pin, "neuschwanstein": neuschwanstein,
    "kinderdijk": kinderdijk, "gravensteen": gravensteen, "stonehenge": stonehenge, "rock-of-cashel": rock_of_cashel,
    "leaning-tower-pisa": leaning_tower_pisa, "kronborg": kronborg, "gripsholm": gripsholm, "borgund": borgund,
    "olavinlinna": olavinlinna,
    "gullfoss": gullfoss,
    "chillon": chillon,
    "melk-abbey": melk_abbey,
    "gozo-citadel": gozo_citadel,
    "karlstejn": karlstejn,
    "malbork": malbork,
    "vianden": vianden,
    "spis-castle": spis_castle,
    "tihany-abbey": tihany_abbey,
    "kuressaare": kuressaare,
    "rundale": rundale,
    "trakai": trakai,
    "bled": bled,
    "plitvice": plitvice,
    "stari-most": stari_most,
    "golubac": golubac,
    "ostrog": ostrog,
    "kruje": kruje,
    "kaneo": kaneo,
    "meteora": meteora,
    "bran": bran,
    "pamukkale": pamukkale,
    "meritxell": meritxell,
    "rila": rila,
    "soroca": soroca,
    **FLORA, **FAUNA,
}


def preview(path, scale=5):
    """Rows: buildings and landmarks, flora and landforms, fauna."""
    rows = [
        ["tree", "pine", "mountain", "hill", "castle", "church", "house", "boat", "pin", "neuschwanstein"],
        list(FLORA),
        list(FAUNA)[:14],
        list(FAUNA)[14:],
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
