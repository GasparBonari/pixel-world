"""A small isometric pixel-art painter for capital-city scenes (ART_CONTRACT.md, capital scale).

Tiles are 16x8 art pixels (2:1). Tile (i, j) has its top corner at screen x = (i - j) * 8,
y = (i + j) * 4, minus its elevation. Objects are painted back to front by depth (i + j).
Light comes from the upper left: south-west walls are lit, south-east walls are shaded.
Every face is outlined in a dark shade of its own material.
"""

import math

from PIL import Image, ImageDraw

import sprites

TW, TH = 16, 8


def rgb(value):
    return sprites.hex_rgb(value)


def shade(color, amount):
    target = 255 if amount > 0 else 0
    return tuple(int(c + (target - c) * abs(amount)) for c in color)


def h01(*values):
    return sprites.h01(*values)


class Scene:
    def __init__(self, width, height, origin):
        self.img = Image.new("RGBA", (width, height), (0, 0, 0, 255))
        self.px = self.img.load()
        self.w, self.h = width, height
        self.ox, self.oy = origin
        self.objects = []  # (depth, order, draw)

    def screen(self, i, j, elevation=0):
        return self.ox + (i - j) * TW / 2, self.oy + (i + j) * TH / 2 - elevation

    def put(self, x, y, color):
        x, y = int(x), int(y)
        if 0 <= x < self.w and 0 <= y < self.h:
            self.px[x, y] = (*color[:3], 255)

    def blend(self, x, y, color, alpha):
        x, y = int(x), int(y)
        if 0 <= x < self.w and 0 <= y < self.h:
            r, g, b, _ = self.px[x, y]
            self.px[x, y] = (int(r + (color[0] - r) * alpha), int(g + (color[1] - g) * alpha),
                             int(b + (color[2] - b) * alpha), 255)

    def add(self, depth, draw):
        self.objects.append((depth, len(self.objects), draw))

    def paint_objects(self):
        for _, _, draw in sorted(self.objects, key=lambda o: (o[0], o[1])):
            draw(self)

    def sprite(self, image, x, y):
        """Paste an RGBA sprite with its bottom-centre at (x, y)."""
        self.img.alpha_composite(image, (int(x - image.width / 2), int(y - image.height + 1)))


def polygon_pixels(points):
    xs, ys = [p[0] for p in points], [p[1] for p in points]
    x0, y0 = int(math.floor(min(xs))), int(math.floor(min(ys)))
    x1, y1 = int(math.ceil(max(xs))) + 1, int(math.ceil(max(ys))) + 1
    mask = Image.new("1", (max(1, x1 - x0), max(1, y1 - y0)))
    ImageDraw.Draw(mask).polygon([(x - x0, y - y0) for x, y in points], fill=1)
    data = mask.load()
    return [(x + x0, y + y0) for y in range(y1 - y0) for x in range(x1 - x0) if data[x, y]]


def fill(scene, points, color_at, cover=None):
    pixels = polygon_pixels(points)
    for x, y in pixels:
        scene.put(x, y, color_at(x, y))
        if cover is not None:
            cover.add((x, y))
    return pixels


def outline(scene, cover, color):
    """Dark ring around everything an object painted (its silhouette)."""
    for x, y in list(cover):
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y - 1), (x, y + 1)):
            if (nx, ny) not in cover:
                scene.put(nx, ny, color)


def line(scene, a, b, color):
    steps = int(max(abs(b[0] - a[0]), abs(b[1] - a[1]))) or 1
    for k in range(steps + 1):
        scene.put(a[0] + (b[0] - a[0]) * k / steps, a[1] + (b[1] - a[1]) * k / steps, color)


# ------------------------------------------------------------------ ground --

def diamond(scene, i, j, elevation=0):
    x, y = scene.screen(i, j, elevation)
    return [(x, y), (x + TW / 2, y + TH / 2), (x, y + TH), (x - TW / 2, y + TH / 2)]


def ground_tile(scene, i, j, color_at, elevation=0, wall=None):
    """Top diamond; with elevation, also the lit left and shaded right retaining walls."""
    top = diamond(scene, i, j, elevation)
    if elevation and wall:
        x, y = scene.screen(i, j, elevation)
        left = [(x - TW / 2, y + TH / 2), (x, y + TH), (x, y + TH + elevation), (x - TW / 2, y + TH / 2 + elevation)]
        right = [(x, y + TH), (x + TW / 2, y + TH / 2), (x + TW / 2, y + TH / 2 + elevation), (x, y + TH + elevation)]
        fill(scene, left, lambda px, py: wall(px, py, True))
        fill(scene, right, lambda px, py: wall(px, py, False))
    fill(scene, top, color_at)


def stone_wall(base):
    light, dark, mortar = shade(base, 0.12), shade(base, -0.22), shade(base, -0.38)

    def color(x, y, lit):
        if y % 4 == 0 or (x + (y // 4) * 3) % 6 == 0:
            return mortar if not lit else shade(mortar, 0.15)
        return light if lit else dark
    return color


# --------------------------------------------------------------- buildings --

class Box:
    """An isometric block: footprint wi x wj tiles from tile (i, j), walls `height` px tall."""

    def __init__(self, scene, i, j, wi, wj, height, elevation=0):
        self.s = scene
        self.T = scene.screen(i, j, elevation)
        self.R = scene.screen(i + wi, j, elevation)
        self.B = scene.screen(i + wi, j + wj, elevation)
        self.L = scene.screen(i, j + wj, elevation)
        self.h = height
        self.wi, self.wj = wi, wj

    def up(self, p, extra=0):
        return p[0], p[1] - self.h - extra

    def walls(self, wall_color, cover, windows=True, seed=0, door=True, balconies=True, tiles=None):
        """Left (south-west, lit) and right (south-east, shaded) walls with windows."""
        lit, dark = shade(wall_color, 0.08), shade(wall_color, -0.2)
        floor = 9
        left = [self.L, self.B, self.up(self.B), self.up(self.L)]
        right = [self.B, self.R, self.up(self.R), self.up(self.B)]

        def face(origin, lit_side, slope):
            base = lit if lit_side else dark
            frame = shade(sprites.hex_rgb("#FFFFFF"), 0 if lit_side else -0.12)
            glass, glint = sprites.hex_rgb("#34405A"), sprites.hex_rgb("#8FB4D8")
            iron, wood = sprites.hex_rgb("#2E2A28"), sprites.hex_rgb("#6B4228")

            def color(x, y):
                u = int(x - origin[0])
                v = int(origin[1] + (x - origin[0]) * slope - y)  # height above the wall's foot
                if v <= 0:
                    return shade(base, -0.3)  # plinth
                if not windows:
                    return base
                level, inside = divmod(v - 1, floor)
                bay, col = divmod(u, 7)
                # Ground floor: a door every third bay, otherwise a shop window.
                if level == 0:
                    if (bay + seed) % 3 == 0 and door and 2 <= col <= 4 and inside <= 6:
                        return wood if inside < 6 or col == 3 else frame
                    if 2 <= col <= 4 and 2 <= inside <= 5:
                        return glass if col != 3 else frame
                    return shade(base, -0.06)
                # Upper floors: framed two-pane windows, a sill, and some iron balconies.
                if 2 <= col <= 4 and 2 <= inside <= 6:
                    if col == 3 or inside in (2, 6):
                        return frame
                    return glint if inside == 3 and col == 2 else glass
                if balconies and inside == 1 and 1 <= col <= 5 and (bay + level + seed) % 3 == 0:
                    return iron
                if inside == 1 and 2 <= col <= 4:
                    return frame  # sill
                if tiles and (u + v) % 2 == 0:
                    return tiles[0] if lit_side else shade(tiles[0], -0.2)
                return base
            return color

        fill(self.s, left, face(self.L, True, 0.5), cover)
        fill(self.s, right, face(self.B, False, -0.5), cover)
        line(self.s, self.B, self.up(self.B), shade(dark, -0.25))  # front corner

    def gable_roof(self, roof_color, wall_color, cover, rise=None):
        """Pitched roof with its ridge along the longer side; the front gable end is wall."""
        rise = rise if rise is not None else 4 + 2 * min(self.wi, self.wj)
        T, R, B, L = (self.up(p) for p in (self.T, self.R, self.B, self.L))
        light, base, dark = shade(roof_color, 0.18), roof_color, shade(roof_color, -0.22)

        def tiled(c):
            def color(x, y):
                return shade(c, -0.12) if (y % 3 == 0 and (x + y) % 2 == 0) else c
            return color

        if self.wi >= self.wj:  # ridge runs along i (screen down-right)
            S = ((T[0] + L[0]) / 2, (T[1] + L[1]) / 2 - rise)
            E = ((R[0] + B[0]) / 2, (R[1] + B[1]) / 2 - rise)
            fill(self.s, [T, R, E, S], tiled(dark), cover)  # back slope
            fill(self.s, [S, E, B, L], tiled(light), cover)  # front slope, lit
            fill(self.s, [R, B, E], lambda x, y: shade(wall_color, -0.2), cover)  # gable end
            line(self.s, S, E, shade(light, 0.2))
        else:  # ridge runs along j (screen down-left)
            S = ((T[0] + R[0]) / 2, (T[1] + R[1]) / 2 - rise)
            E = ((L[0] + B[0]) / 2, (L[1] + B[1]) / 2 - rise)
            fill(self.s, [T, L, E, S], tiled(light), cover)  # back-left slope, lit
            fill(self.s, [S, E, B, R], tiled(base), cover)  # front-right slope
            fill(self.s, [L, B, E], lambda x, y: shade(wall_color, 0.08), cover)  # gable end
            line(self.s, S, E, shade(light, 0.2))
        line(self.s, L, B, shade(roof_color, -0.45))  # eaves
        line(self.s, B, R, shade(roof_color, -0.45))

    def flat_top(self, color, cover, crenels=False):
        T, R, B, L = (self.up(p) for p in (self.T, self.R, self.B, self.L))
        fill(self.s, [T, R, B, L], lambda x, y: color, cover)
        if crenels:
            for a, b in ((L, B), (B, R), (T, L), (T, R)):
                steps = int(abs(b[0] - a[0]))
                for k in range(0, steps, 3):
                    x = a[0] + (b[0] - a[0]) * k / max(1, steps)
                    y = a[1] + (b[1] - a[1]) * k / max(1, steps)
                    for dy in range(1, 3):
                        self.s.put(x, y - dy, shade(color, -0.1 if dy == 1 else 0.1))
                        self.s.put(x + 1, y - dy, shade(color, -0.25))
                        cover.update({(int(x), int(y - dy)), (int(x + 1), int(y - dy))})


def house(scene, i, j, wi, wj, floors, wall, roof, seed, elevation=0, tiles=None, rise=None):
    box = Box(scene, i, j, wi, wj, floors * 9 + 2, elevation)
    cover = set()
    box.walls(wall, cover, seed=seed, tiles=tiles)
    box.gable_roof(roof, wall, cover, rise=rise)
    outline(scene, cover, sprites.hex_rgb("#3A2A22"))
