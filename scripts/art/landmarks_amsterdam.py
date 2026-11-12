"""Amsterdam: Dutch brick, carved gables and eight landmarks in true (i, j, z) geometry.

Run this file for the individual 4× inspection plots. Locations and reference sources live in
DEVELOPMENT_PLAN.md. The +j wall is lit, the +i wall shaded, including all projected ornament.
"""

import math

import iso
from iso import rgb, h01
from landmarks_paris import P, seg, poly, corners, facade, egg_dome, preview, GLASS
from landmarks_iberia import hip_roof, stone_courses, arch_opening, palette_of, tones


STONE = tones("#F7EAD2", "#DCCCAD", "#C4B292", "#A39178", "#75634F", "#B09C7D", "#493D32")
BRICK = tones("#DCA185", "#AE6551", "#925340", "#713E34", "#4D302A", "#8D5646", "#382620")
PALE = tones("#FFF9E8", "#F1E8D3", "#DAD1BD", "#BBB09C", "#8F826D", "#C7BBA2", "#514739")
SLATE = tones("#A7AFB5", "#7C8792", "#65717D", "#4A5563", "#303D49", "#596773", "#29323B")
CLAY = tones("#E8AE7C", "#C77D50", "#AD623D", "#88482F", "#583626", "#A56745", "#492D23")
COPPER = tones("#B3CBB5", "#80AA99", "#638D7D", "#436D64", "#2E4E49", "#5B8576", "#273E38")
GOLD = tones("#FFF1AF", "#E5BF61", "#C69A42", "#9E742D", "#6C4B23", "#AD883C", "#4B3823")
BLUE = tones("#8BBADA", "#4889BA", "#326D9C", "#255078", "#23394F", "#42799D", "#1E3049")
WOOD = tones("#B09B7B", "#8D7657", "#6F5D47", "#514436", "#352F29", "#75644E", "#302923")
WALLS = [rgb(c) for c in ("#975745", "#75483B", "#AE6C50", "#60514A", "#C0906E", "#E0D5BD")]
IRON = rgb("#323C3D")
WATER = (rgb("#447F8B"), rgb("#346575"), rgb("#78AFB8"))


def block(s, i, j, wi, wj, height, material=STONE, pattern=None, z=0):
    cover = facade(s, i, j, wi, wj, height, pattern or stone_courses(material, 4, 9),
                   palette=material, z0=z)
    iso.fill(s, list(corners(s, i, j, wi, wj, z + height)), lambda x, y: material["mid"], cover)
    iso.outline(s, cover, material["outline"])
    return cover


def octagon(s, ci, cj, radius, base, height, material, roof=False, openings=False):
    """An eight-sided drum or pointed roof, with flat cardinal faces and bevelled corners."""
    cut = math.sqrt(2) - 1
    ring = [(ci + radius * a, cj + radius * b) for a, b in
            ((-cut, -1), (cut, -1), (1, -cut), (1, cut),
             (cut, 1), (-cut, 1), (-1, cut), (-1, -cut))]
    pairs = list(zip(ring, ring[1:] + ring[:1]))
    for a, b in sorted(pairs, key=lambda pair: sum(pair[0]) + sum(pair[1])):
        dx, dy = b[0] - a[0], b[1] - a[1]
        light = -dx - .4 * dy  # outward +j is lit; outward +i shaded
        key = "lit" if light > .1 else "dark" if light < -.1 else "mid"
        foot_a, foot_b = P(s, *a, base), P(s, *b, base)
        top = P(s, ci, cj, base + height)
        pts = [foot_a, foot_b, top] if roof else [foot_a, foot_b, P(s, *b, base + height), P(s, *a, base + height)]
        span = foot_b[0] - foot_a[0]
        slope = (foot_b[1] - foot_a[1]) / (span or .001)
        def surface(x, y, key=key, foot=foot_a, slope=slope, span=span):
            u = (x - foot[0]) / (span or .001)
            v = foot[1] + (x - foot[0]) * slope - y
            if openings and .25 < u < .75 and 3 < v < height - 2:
                return SLATE["deep"]
            if int(v) % (4 if roof else 6) == 0:
                return material["line" if key == "lit" else "deep"]
            return material[key]
        poly(s, pts, surface)
        seg(s, pts[-1], foot_a, material["outline"])
        if not roof:
            seg(s, pts[2], pts[3], material["hi"] if key == "lit" else material["mid"])
    if not roof:
        poly(s, [P(s, *point, base + height) for point in ring], lambda x, y: material["mid"])


def windows(material, height, bay=8, gothic=False):
    """Brick joints, dressed multi-pane windows, sills, sandstone bands and cornices."""
    courses = stone_courses(material, 3, 7)
    def pattern(u, v, lit):
        u, v = int(u), int(v)
        c, level = u % bay, v % 12
        trim = PALE["lit" if lit else "dark"]
        if v in (1, height - 2, height) or v % 12 == 0:
            return trim
        if 2 <= c <= bay - 2 and 3 <= level <= 10 and v < height - 3:
            top = 10 - abs(c - bay / 2) * (.65 if gothic else .25)
            if level > top:
                return courses(u, v, lit)
            if c in (2, bay - 2) or level in (3, int(top)):
                return trim
            return trim if c == bay // 2 or level == 6 else GLASS["mid" if level > 6 else "dark"]
        if c == 0 and gothic:
            return trim  # dressed buttress / pier
        return courses(u, v, lit)
    return pattern


def church_windows(material, height, bay=9):
    """Tall traceried church lights, with pointed heads, buttress piers and dressed sills."""
    courses = stone_courses(material, 3, 8)
    def pattern(u, v, lit):
        c, v = int(u) % bay, int(v)
        trim = PALE["lit" if lit else "dark"]
        if v in (1, height - 1) or c == 0:
            return trim
        top = height - 3 - abs(c - bay / 2) * .85
        if 2 <= c <= bay - 2 and 5 <= v <= top:
            if c in (2, bay - 2) or v in (5, int(top)):
                return trim
            if c == bay // 2 or v in (10, 16):
                return PALE["mid" if lit else "deep"]
            return GLASS["mid" if v > 16 else "dark"]
        return courses(u, v, lit)
    return pattern


def gable_roof(s, i, j, wi, wj, base, rise, roof=SLATE, wall=BRICK, style="point"):
    """Ridge along j, two textured slopes and a raised Dutch gable on the lit +j end.

    The profile is a polygon in the i/z plane extruded along j, never a screen-facing cutout.
    """
    T, R, B, L = corners(s, i, j, wi, wj, base)
    back, front = P(s, i + wi / 2, j, base + rise), P(s, i + wi / 2, j + wj, base + rise)
    for pts, lit in (([T, L, front, back], True), ([back, front, B, R], False)):
        tone = roof["lit" if lit else "dark"]
        poly(s, pts, lambda x, y, tone=tone: roof["line"] if int(y) % 3 == 0
             else roof["hi"] if (int(x) + int(y) // 3 * 2) % 7 == 0 else tone)
    seg(s, back, front, roof["hi"])
    if style == "step":
        profile = [(0, 0), (0, .4), (.16, .4), (.16, .7), (.32, .7), (.32, 1),
                   (.43, 1), (.43, 1.2), (.57, 1.2), (.57, 1), (.68, 1), (.68, .7),
                   (.84, .7), (.84, .4), (1, .4), (1, 0)]
    elif style == "bell":
        profile = [(0, 0), (0, .14), (.12, .17), (.23, .32), (.3, .57), (.36, .78),
                   (.43, .87), (.43, 1), (.57, 1), (.57, .87), (.64, .78), (.7, .57),
                   (.77, .32), (.88, .17), (1, .14), (1, 0)]
    elif style == "neck":
        profile = [(0, 0), (0, .17), (.2, .17), (.2, .35), (.32, .35), (.32, .95),
                   (.43, 1.08), (.57, 1.08), (.68, .95), (.68, .35), (.8, .35), (.8, .17), (1, .17), (1, 0)]
    else:
        profile = [(0, 0), (.5, 1), (1, 0)]
    # Carved gables stand above the roof slopes; profiles inside the roof triangle disappear.
    front_rise = rise if style == "point" else rise + 6
    outer = [P(s, i + u * wi, j + wj + .12, base + v * front_rise) for u, v in profile]
    rear = [P(s, i + u * wi, j + wj, base + v * front_rise) for u, v in profile]
    for k in range(len(profile) - 1):
        poly(s, [rear[k], rear[k + 1], outer[k + 1], outer[k]], lambda x, y: wall["dark"])
    foot = P(s, i, j + wj + .12, base)
    def fill(x, y):
        u, v = x - foot[0], foot[1] + (x - foot[0]) * .5 - y
        if abs(u - wi * 4) <= 2 and 2 < v < min(9, rise - 1):
            return PALE["lit"] if int(u - wi * 4) in (-2, 2) or int(v) in (3, 8) else GLASS["dark"]
        return stone_courses(wall, 3, 7)(u, v, True) or wall["lit"]
    poly(s, outer, fill)
    for a, b in zip(outer, outer[1:] + outer[:1]):
        seg(s, a, b, wall["outline"])
    if style != "point":
        for a, b in zip(outer[:-1], outer[1:]):
            seg(s, (a[0], a[1] - 1), (b[0], b[1] - 1), PALE["lit"])
    else:
        seg(s, L, front, wall["hi"])
        seg(s, front, B, wall["hi"])


def spire(s, i, j, width, depth, base, rise, roof=SLATE):
    T, R, B, L = corners(s, i, j, width, depth, base)
    apex = P(s, i + width / 2, j + depth / 2, base + rise)
    for face, key in (([T, R, apex], "mid"), ([T, L, apex], "mid"),
                      ([L, B, apex], "lit"), ([B, R, apex], "dark")):
        poly(s, face, lambda x, y, key=key: roof["line"] if int(y) % 4 == 0 else roof[key])
    for end in (L, B, R):
        seg(s, apex, end, roof["outline"])
    seg(s, apex, (apex[0], apex[1] - 5), GOLD["lit"])
    seg(s, (apex[0] - 2, apex[1] - 4), (apex[0] + 3, apex[1] - 5), GOLD["hi"])


def clock(s, i, j, z, radius=4, compass=False):
    """Clock face mapped into its vertical wall, including its two hands / compass rose."""
    center = P(s, i, j, z)
    for u in range(-radius, radius + 1):
        for v in range(-radius, radius + 1):
            r = math.hypot(u, v)
            if r <= radius:
                s.put(center[0] + u, center[1] + u * .5 - v,
                      GOLD["dark"] if r > radius - 1 else PALE["hi"])
    seg(s, center, (center[0], center[1] - radius + 1), IRON)
    seg(s, center, (center[0] + radius - 1, center[1] + (radius - 1) * .5 - 1), IRON)
    if compass:
        seg(s, (center[0] - 2, center[1] - 3), (center[0] + 2, center[1] + 3), IRON)


def canal_house(scene, i, j, wi=2.3, wj=3.5, floors=3, seed=0, style=None):
    wall = palette_of(WALLS[seed % len(WALLS)])
    height = floors * 9 + 3
    def pattern(u, v, lit):
        u, v = int(u), int(v)
        col, level = u % 6, v % 9
        trim = PALE["lit" if lit else "dark"]
        if v < 2:
            return wall["deep"]
        if v in (height - 1, height - 3):
            return trim
        if v < 9:
            if 1 <= col <= 4 and 2 <= v <= 7:
                if col in (1, 4) or v == 7:
                    return trim
                return WOOD["dark"] if int(u) // 6 == seed % 3 else GLASS["dark"]
        elif 1 <= col <= 4 and 2 <= level <= 7 and v < height - 3:
            if col in (1, 4) or level in (2, 7):
                return trim
            return trim if level == 5 else GLASS["mid" if level > 5 else "dark"]
        if seed % 5 == 0 and v in (10, 11) and 1 <= col <= 4:
            return IRON if v == 10 or col in (1, 3, 4) else GLASS["dark"]
        if v > 9 and level == 1 and 1 <= col <= 4:
            return trim  # sill
        return stone_courses(wall, 3, 8)(u, v, lit)
    def draw(s):
        cover = facade(s, i, j, wi, wj, height, pattern, palette=wall)
        iso.outline(s, cover, wall["outline"])
        gable_roof(s, i, j, wi, wj, height, 11 + seed % 4,
                   CLAY if seed % 4 == 0 else SLATE, wall,
                   style or ("step", "bell", "neck", "point")[seed % 4])
        block(s, i + .15, j + .55, .3, .4, 7, BRICK, z=height + 5)
        # Hoisting beam projecting from the attic, with a short hanging hook.
        a, b = P(s, i + wi / 2, j + wj, height + 8), P(s, i + wi / 2, j + wj + .65, height + 8)
        seg(s, a, b, WOOD["deep"])
        seg(s, b, (b[0], b[1] + 3), IRON)
        if seed % 3 == 0:
            block(s, i + .35, j + wj + .2, .8, .35, 2, STONE)
    scene.add(i + j + wi + wj, draw)


def royal_palace(scene, i, j):
    """Sandstone pilasters, seven entrances, sculpted pediment and octagonal clock cupola."""
    W, D, H = 9.5, 5, 39
    def draw(s):
        def pattern(u, v, lit):
            col, v = int(u) % 8, int(v)
            if v < 9:
                if lit:
                    for door in range(7):
                        opening = arch_opening(u, v, W * 8 * (door + .5) / 7, 2.1, 5, STONE["deep"])
                        if opening:
                            return opening
                else:
                    opening = arch_opening(col, v, 4, 1.8, 5, STONE["deep"])
                    if opening:
                        return opening
                return stone_courses(STONE, 3, 8)(u, v, lit)
            if col in (0, 1) and 10 <= v <= H - 3:
                return STONE["hi" if lit else "mid"] if col == 0 else STONE["line" if lit else "deep"]
            return windows(STONE, H, 8)(u, v, lit)
        block(s, i, j, W, D, H, STONE, pattern)
        hip_roof(s, i, j, W, D, H, 7, roof=SLATE)
        # Central projecting pediment; relief stays clipped to its own triangle.
        block(s, i + 2.6, j + D - .35, 4.3, .65, H + 2, STONE,
              lambda u, v, lit: pattern(u + 2.6 * 8 if lit else u, v, lit))
        a, b = P(s, i + 2.4, j + D + .33, H + 2), P(s, i + 7.1, j + D + .33, H + 2)
        top = P(s, i + W / 2, j + D + .33, H + 15)
        poly(s, [a, b, top], lambda x, y: STONE["lit"] if (int(x) // 3 + int(y)) % 7 < 2 else STONE["mid"])
        for p, q in ((a, b), (a, top), (top, b)):
            seg(s, p, q, STONE["hi"], 2)
        # Three filled sculptural groups inside the pediment's plane: Amsterdam and river gods.
        fj = j + D + .34
        for offset, z, profile in (
            (4.65, 43, [(-.28, 0), (.3, 0), (.2, 3), (.1, 6), (-.12, 7), (-.3, 3)]),
            (3.4, 42, [(-.45, 0), (.5, 0), (.23, 2), (.15, 4), (-.1, 5), (-.32, 3)]),
            (6.15, 42, [(-.5, 0), (.45, 0), (.32, 3), (.1, 5), (-.15, 4), (-.23, 2)])):
            poly(s, [P(s, i + offset + dx, fj, z + dz) for dx, dz in profile], lambda x, y: STONE["hi"])
        seg(s, P(s, i + 4.45, fj, 47), P(s, i + 3.95, fj, 48), STONE["hi"])
        seg(s, P(s, i + 4.85, fj, 47), P(s, i + 5.45, fj, 48), STONE["hi"])
        # Octagonal open belfry cupola, on the roof ridge.
        ci, cj = i + W / 2, j + D / 2 - .6
        octagon(s, ci, cj, 1.05, 46, 12, STONE, openings=True)
        clock(s, ci, cj + 1.06, 51, 3)
        x, y = P(s, ci, cj, 59)
        egg_dome(s, x, y, 10, 10, (COPPER["lit"], COPPER["mid"], COPPER["dark"]))
        block(s, ci - .17, cj - .17, .34, .34, 6, COPPER, z=68)
        seg(s, P(s, ci, cj, 74), P(s, ci + .65, cj, 75), GOLD["lit"])
        # Atlas behind the roofline: filled bent legs, shoulders and globe, not a stick figure.
        x, y = P(s, i + 1.7, j + .8, 47)
        poly(s, [(x - 4, y), (x - 1, y), (x, y - 4), (x + 2, y), (x + 4, y),
                 (x + 3, y - 7), (x + 1, y - 9), (x - 3, y - 7)], lambda x, y: COPPER["dark"])
        seg(s, (x - 3, y - 7), (x - 5, y - 13), COPPER["lit"], 2)
        seg(s, (x + 2, y - 7), (x + 5, y - 13), COPPER["lit"], 2)
        for dy in range(-4, 5):
            for dx in range(-4, 5):
                if dx * dx + dy * dy <= 16:
                    s.put(x + dx, y - 13 + dy, COPPER["lit"] if dx < 0 else COPPER["dark"])
    scene.add(i + j + W + D, draw)


def westerkerk(scene, i, j):
    """Renaissance church with long windows, transept gables and the blue imperial crown."""
    W, D, H = 6.5, 5, 25
    def draw(s):
        block(s, i, j, W, D, H, BRICK, church_windows(BRICK, H))
        gable_roof(s, i, j, W, D, H, 14, SLATE, BRICK)
        for a in (i + .4, i + 3.7):
            block(s, a, j + D - .5, 2.4, 1.2, 24, BRICK, church_windows(BRICK, 24, 8))
            gable_roof(s, a, j + D - .5, 2.4, 1.2, 24, 12, SLATE, PALE)
        # Tower at the western end. Successive stages shrink, with dressed corners and galleries.
        ti, tj = i - .9, j + 1.4
        for a, b, width, depth, base, height, mat in (
            (ti, tj, 2.2, 2.2, 0, 48, BRICK),
            (ti + .15, tj + .15, 1.9, 1.9, 48, 17, STONE),
            (ti + .36, tj + .36, 1.48, 1.48, 65, 14, PALE),
            (ti + .55, tj + .55, 1.1, 1.1, 79, 9, SLATE)):
            def stage(u, v, lit, mat=mat, height=height):
                if int(v) in (1, height - 1) or int(u) % 8 in (0, 1):
                    return PALE["lit" if lit else "dark"]
                opening = 31 < v < 39 or 6 < v < 15 if height == 48 else 4 < v < height - 3
                if int(u) % 8 in (3, 4, 5) and opening:
                    return SLATE["deep"]
                return stone_courses(mat, 4, 8)(u, v, lit)
            block(s, a, b, width, depth, height, mat, stage, z=base)
            block(s, a - .15, b - .15, width + .3, depth + .3, 2, PALE, z=base + height)
        clock(s, ti + 1.05, tj + 2.21, 43, 4)
        x, y = P(s, ti + 1.1, tj + 1.1, 90)
        egg_dome(s, x, y, 7, 9, (BLUE["lit"], BLUE["mid"], BLUE["dark"]))
        # Blue crown's golden arches, orb and cross.
        for dx in (-5, -2, 2, 5):
            seg(s, (x + dx, y), (x + dx * .4, y - 8), GOLD["lit"])
        seg(s, (x - 6, y), (x + 6, y), GOLD["hi"])
        seg(s, (x, y - 9), (x, y - 16), GOLD["lit"])
        seg(s, (x - 2, y - 14), (x + 2, y - 14), GOLD["hi"])
    scene.add(i + j + W + D, draw)


def oude_kerk(scene, i, j):
    """Low medieval hall church: parallel pitched aisles, buttresses and octagonal spire."""
    W, D, H = 5.8, 7.2, 23
    def draw(s):
        block(s, i, j, W, D, H, BRICK, church_windows(BRICK, H))
        for k in range(3):
            gable_roof(s, i + k * W / 3, j, W / 3, D, H, 12, CLAY, BRICK)
        for b in (j + 1, j + 2.7, j + 4.4, j + 6.1):
            block(s, i + W - .1, b, .5, .35, 18, STONE)
            hip_roof(s, i + W - .1, b, .5, .35, 18, 4, roof=SLATE)
        ti, tj = i + .2, j + D - 1.3
        block(s, ti, tj, 1.8, 1.8, 43, STONE, windows(STONE, 43, 7, True))
        clock(s, ti + .9, tj + 1.81, 37, 4)
        block(s, ti + .12, tj + .12, 1.56, 1.56, 3, PALE, z=43)
        octagon(s, ti + .9, tj + .9, .86, 46, 13, COPPER, openings=True)
        x, y = P(s, ti + .9, tj + .9, 59)
        egg_dome(s, x, y, 9, 8, (COPPER["lit"], COPPER["mid"], COPPER["dark"]))
        octagon(s, ti + .9, tj + .9, .53, 66, 8, COPPER, openings=True)
        octagon(s, ti + .9, tj + .9, .65, 74, 14, COPPER, roof=True)
        seg(s, P(s, ti + .9, tj + .9, 88), P(s, ti + .9, tj + .9, 93), GOLD["lit"])
    scene.add(i + j + W + D, draw)


def centraal_station(scene, i, j):
    """Cuypers' red-brick frontage: clock/compass towers, carved gables and iron/glass shed."""
    W, D, H = 13.5, 3.6, 27
    def draw(s):
        # Barrel-vaulted train shed behind the stone/brick station, constructed as roof strips.
        for k in range(16):
            a, b = k * math.pi / 16, (k + 1) * math.pi / 16
            ja, jb = j - 2.1 + 1.7 * math.cos(a), j - 2.1 + 1.7 * math.cos(b)
            za, zb = 17 + 15 * math.sin(a), 17 + 15 * math.sin(b)
            pts = [P(s, i + .5, ja, za), P(s, i + W - .5, ja, za),
                   P(s, i + W - .5, jb, zb), P(s, i + .5, jb, zb)]
            poly(s, pts, lambda x, y: GLASS["mid"] if int(x) % 7 else SLATE["dark"])
            seg(s, pts[0], pts[1], SLATE["line"])
        block(s, i, j, W, D, H, BRICK, windows(BRICK, H, 8, True))
        hip_roof(s, i, j, W, D, H, 10, roof=SLATE)
        # Central entrance pavilion and its ornamental stepped pediment.
        block(s, i + 4.9, j + .2, 3.7, D, 34, BRICK, windows(BRICK, 34, 8, True))
        gable_roof(s, i + 4.9, j + .2, 3.7, D, 34, 16, SLATE, BRICK, "step")
        # Towers flank the pavilion; the west shows wind direction, the east tells time.
        for a, compass in ((i + 3.2, True), (i + 8.9, False)):
            block(s, a, j + D - 1.6, 1.6, 1.8, 45, BRICK, windows(BRICK, 45, 7, True))
            block(s, a - .1, j + D - 1.7, 1.8, 2, 2, PALE, z=45)
            clock(s, a + .8, j + D + .21, 39, 4, compass)
            spire(s, a - .1, j + D - 1.7, 1.8, 2, 47, 14)
        for a in (i + .1, i + W - 1.8):
            block(s, a, j + .3, 1.7, D, 32, BRICK, windows(BRICK, 32, 7, True))
            gable_roof(s, a, j + .3, 1.7, D, 32, 12, SLATE, BRICK, "neck")
        # Small heraldic panels between the entrance arches.
        for a in (i + 5.3, i + 6.6, i + 7.9):
            x, y = P(s, a, j + D + .22, 26)
            poly(s, [(x - 2, y - 2), (x + 2, y), (x + 2, y + 3), (x, y + 5), (x - 2, y + 2)],
                 lambda x, y: GOLD["lit"] if int(x + y) % 3 else BRICK["deep"])
    scene.add(i + j + W + D + .3, draw)


def rijksmuseum(scene, i, j):
    """Neo-Gothic brick museum: twin steep towers, dressed bands and vaulted cycle passage."""
    W, D, H = 12, 5.8, 30
    def draw(s):
        block(s, i, j, W, D, H, BRICK, windows(BRICK, H, 9, True))
        hip_roof(s, i, j, W, D, H, 11, roof=SLATE)
        # Central gateway is cut through its front, with the far paving clipped to the opening.
        gw, gh = 4, 39
        def gateway(u, v, lit):
            if lit:
                d = abs(u - gw * 4)
                if d < 5 and v < 17 - d * .85:
                    return STONE["deep"] if d > 3.5 else STONE["dark"] if v > 5 else PALE["dark"]
                if d < 6 and v < 19 - d * .8:
                    return PALE["lit"]
            return windows(BRICK, gh, 8, True)(u, v, lit)
        block(s, i + 4, j + D - 2.4, gw, 2.6, gh, BRICK, gateway)
        gable_roof(s, i + 4, j + D - 2.4, gw, 2.6, gh, 15, SLATE, BRICK, "step")
        for a in (i + 2.3, i + 8):
            block(s, a, j + D - 2.1, 1.7, 2.3, 47, BRICK, windows(BRICK, 47, 7, True))
            block(s, a - .1, j + D - 2.2, 1.9, 2.5, 2, PALE, z=47)
            spire(s, a - .1, j + D - 2.2, 1.9, 2.5, 49, 21)
        for a in (i, i + W - 1.8):
            block(s, a, j + D - 2.2, 1.8, 2.2, 35, BRICK, windows(BRICK, 35, 7, True))
            spire(s, a, j + D - 2.2, 1.8, 2.2, 35, 12)
        # Carved stone historical panels and medallions below the roof cornice.
        for a in (i + .7, i + 1.7, i + 9.9, i + 10.9):
            x, y = P(s, a, j + D + .03, 26)
            for dx, dy in ((-1, 0), (0, -1), (1, 0), (0, 1)):
                s.put(x + dx, y + dy + dx * .5, GOLD["lit"])
    scene.add(i + j + W + D + .4, draw)


def anne_frank_house(scene, i, j):
    """Prinsengracht 263: restrained dark-brick three-bay frontage and the rear Annex."""
    W, D, H = 2.8, 4.3, 33
    def draw(s):
        dark = palette_of(rgb("#66524A"))
        # Small rear Annex, separated from the front house by a courtyard.
        block(s, i + .1, j - 2.2, W - .2, 1.7, 26, dark, windows(dark, 26, 7))
        hip_roof(s, i + .1, j - 2.2, W - .2, 1.7, 26, 7, roof=CLAY)
        block(s, i, j, W, D, H, dark, windows(dark, H, 7))
        hip_roof(s, i, j, W, D, H, 10, roof=SLATE)
        # Flat white cornice and one broad attic dormer, rather than an invented ornate gable.
        block(s, i - .05, j + D - .12, W + .1, .25, 2, PALE, z=H)
        block(s, i + .65, j + D - .6, 1.5, .9, 6, dark,
              lambda u, v, lit: PALE["lit"] if int(u) % 5 == 0 or int(v) in (0, 5)
              else GLASS["dark"], z=H + 2)
        hip_roof(s, i + .6, j + D - .65, 1.6, 1, H + 8, 3, roof=SLATE)
        # Door, stone surround and narrow front steps.
        block(s, i + .15, j + D, .65, .15, 9, PALE,
              lambda u, v, lit: WOOD["deep"] if 1 <= int(u) <= 4 and v < 8 else None)
        block(s, i + .1, j + D + .2, .8, .3, 1, STONE)
        block(s, i + .12, j + .7, .35, .4, 6, BRICK, z=H + 6)
    scene.add(i + j + W + D, draw)


def nemo(scene, i, j):
    """Copper hull rising from Oosterdok; curved sides, panel seams and stepped roof piazza."""
    W, D = 8, 4.2
    def rise(t):
        return 8 + 34 * math.sin(t * math.pi / 2)
    def draw(s):
        # The roof curves upwards along +i; each strip is a real ruled 3D surface.
        for k in range(16):
            a, b = k / 16, (k + 1) / 16
            za, zb = rise(a), rise(b)
            pts = [P(s, i + W * (.08 + .84 * a), j + D - .55, 4),
                   P(s, i + W * (.08 + .84 * b), j + D - .55, 4),
                   P(s, i + W * b, j + D, zb), P(s, i + W * a, j + D, za)]
            poly(s, pts, lambda x, y: COPPER["line"] if int(y) % 13 == 0
                 else COPPER["hi"] if h01(x, y, 73) < .035 else COPPER["lit"])
            seg(s, pts[1], pts[2], COPPER["dark"])
            roof = [P(s, i + W * a, j, za), P(s, i + W * b, j, zb), pts[2], pts[3]]
            poly(s, roof, lambda x, y: STONE["lit"] if int(y) % 3 else STONE["line"])
            seg(s, roof[2], roof[3], COPPER["hi"])
            if k % 2 == 0:
                seg(s, roof[0], roof[3], PALE["lit"])
        # The rounded prow flares out above a narrower foot; its cap is a series of 3D facets.
        for k in range(12):
            a, b = k / 12, (k + 1) / 12
            def prow(t, top):
                return P(s, i + W + (.45 * math.sin(t * math.pi) if top else -.85),
                         j + (D * t if top else .55 + (D - 1.1) * t), rise(1) if top else 4)
            pts = [prow(a, False), prow(b, False), prow(b, True), prow(a, True)]
            poly(s, pts, lambda x, y: COPPER["line"] if int(y) % 13 == 0 else COPPER["dark"])
            seg(s, pts[1], pts[2], COPPER["line"])
            seg(s, pts[2], pts[3], COPPER["hi"])
            # Close the curved terrace edge too, so no ground leaks through the roof/prow seam.
            poly(s, [P(s, i + W, j + D * a, rise(1)), P(s, i + W, j + D * b, rise(1)),
                     prow(b, True), prow(a, True)], lambda x, y: STONE["mid"])
        block(s, i - .3, j + .8, .7, 2.5, 7, SLATE,
              lambda u, v, lit: GLASS["mid"] if 1 < v < 6 and int(u) % 4 else None)
        # Roof terrace planters and two slender railings follow the curved roof's edge.
        for a in (.24, .5, .75):
            block(s, i + W * a, j + .35, .6, .65, 3, STONE, z=rise(a))
            block(s, i + W * a + .08, j + .43, .45, .48, 2, COPPER, z=rise(a) + 3)
        for jj in (j + .08, j + D - .08):
            for k in range(12):
                a, b = k / 12, (k + 1) / 12
                seg(s, P(s, i + W * a, jj, rise(a) + 3), P(s, i + W * b, jj, rise(b) + 3), COPPER["deep"])
    scene.add(i + j + W + D + .5, draw)


def magere_brug(scene, i, j, length=10):
    """White double drawbridge along +j: open lifting portals, beams, chains and railings."""
    W, deck = 1.7, 7
    def draw(s):
        # Piers and deck; leave real openings showing the river between supports.
        for b in (j + .3, j + 2.5, j + length - 2.8, j + length - .6):
            for a in (i + .1, i + W - .35):
                block(s, a, b, .25, .35, deck, WOOD)
        block(s, i, j, W, length, 2, PALE,
              lambda u, v, lit: PALE["line"] if int(u) % 5 == 0 else None, z=deck)
        for b in (j + 3, j + length - 3):
            # Two upright posts connected over the roadway, with a dark clear opening beneath.
            for a in (i - .1, i + W - .15):
                block(s, a, b, .3, .4, 21, PALE, z=deck)
                block(s, a - .08, b - 1.15, .45, 2.5, 3, PALE, z=deck + 20)
            block(s, i - .15, b, W + .3, .4, 3, PALE, z=deck + 18)
            direction = 1 if b < j + length / 2 else -1
            for a in (i, i + W):
                seg(s, P(s, a, b + direction * 1.1, deck + 22),
                    P(s, a, b + direction * 2, deck + 2), IRON)
                block(s, a - .2, b - direction * 1.2, .4, .7, 3, WOOD, z=deck + 19)
        for a in (i, i + W):
            for k in range(21):
                b = j + k * length / 20
                seg(s, P(s, a, b, deck + 2), P(s, a, b, deck + 6), PALE["lit"])
            seg(s, P(s, a, j, deck + 6), P(s, a, j + length, deck + 6), PALE["hi"])
        seg(s, P(s, i, j + length / 2, deck + 2), P(s, i + W, j + length / 2, deck + 2), WOOD["deep"])
    scene.add(i + j + W + length, draw)


if __name__ == "__main__":
    plots = [
        ("palace", royal_palace, (250, 200), (105, 90)),
        ("westerkerk", westerkerk, (230, 220), (100, 120)),
        ("oude-kerk", oude_kerk, (230, 210), (115, 95)),
        ("centraal", centraal_station, (285, 200), (85, 85)),
        ("rijksmuseum", rijksmuseum, (275, 210), (105, 95)),
        ("anne-frank-house", anne_frank_house, (180, 170), (90, 65)),
        ("nemo", nemo, (230, 170), (100, 65)),
        ("magere-brug", magere_brug, (210, 175), (110, 60)),
    ]
    for name, builder, size, origin in plots:
        print(preview([lambda s, build=builder: build(s, 3, 3)], f"amsterdam-{name}",
                      size=size, origin=origin, tiles=17))
    print(preview([lambda s: canal_house(s, 2, 2, seed=0),
                   lambda s: canal_house(s, 5, 2, floors=4, seed=1),
                   lambda s: canal_house(s, 8, 2, seed=2),
                   lambda s: canal_house(s, 11, 2, seed=3)], "amsterdam-houses",
                  size=(255, 190), origin=(75, 70), tiles=17))
