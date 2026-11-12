"""Berlin's landmarks and Gründerzeit houses, built in projected (i, j, z) geometry.

Run alone to regenerate the 4× inspection plots in docs/art/capitals/berlin-*.png.
The lit +j and shaded +i walls share the capital pipeline's material-aware helpers.
Reference locations and architectural sources are recorded in DEVELOPMENT_PLAN.md.
"""

import math

import iso
from iso import rgb, shade
from landmarks_paris import P, seg, poly, corners, facade, mansard, egg_dome, preview, GLASS
from landmarks_iberia import hip_roof, stone_courses, arch_opening, palette_of, tones


SAND = tones("#FFF3D5", "#E5D1AA", "#CDB88F", "#AD9574", "#78644D", "#B6A17E", "#463B2E")
BRICK = tones("#E9AB87", "#BD7256", "#A45D48", "#844A3E", "#58392F", "#945A48", "#402B26")
COPPER = tones("#B4D5B4", "#78AB91", "#5D8D7A", "#436A61", "#2C4D46", "#537E6B", "#263D36")
ROOF = tones("#B3AFAD", "#8A8584", "#726D70", "#56525B", "#34323B", "#65616A", "#302D35")
SILVER = tones("#F7FAED", "#D3DFDF", "#AFBEC5", "#8193A2", "#526776", "#94AAB5", "#303F4C")
GOLD = tones("#FFF1AD", "#EFC85D", "#CCA044", "#A77B32", "#795226", "#BD913B", "#513C22")
RED_STONE = palette_of(rgb("#9D6C62"))
WALLS = [rgb(c) for c in ("#D6BC8F", "#C5CCB0", "#D3ADA0", "#E0D6BF", "#B9C7C7")]
INK = rgb("#343238")
WOOD = rgb("#654C3C")


def block(s, i, j, wi, wj, height, stone=SAND, pattern=None, z=0):
    """An ashlar or patterned solid, including its horizontal top and material outline."""
    cover = facade(s, i, j, wi, wj, height, pattern or stone_courses(stone), palette=stone, z0=z)
    iso.fill(s, list(corners(s, i, j, wi, wj, z + height)), lambda x, y: stone["mid"], cover)
    iso.outline(s, cover, stone["outline"])
    return cover


def cylinder(s, i, j, radius, z, height, stone, pattern=None):
    """24-sided solid cylinder; surface strips project from real ground-space circles."""
    count = 24
    # Back strips first; front-most strips last.
    strips = sorted(range(count), key=lambda k: math.cos((k + .5) * math.tau / count)
                    + math.sin((k + .5) * math.tau / count))
    for k in strips:
        a, b = k * math.tau / count, (k + 1) * math.tau / count
        aa, bb = (i + radius * math.cos(a), j + radius * math.sin(a)), \
                 (i + radius * math.cos(b), j + radius * math.sin(b))
        light = (-.45 * math.cos((a + b) / 2) + .8 * math.sin((a + b) / 2))
        tone = stone["hi" if light > .65 else "lit" if light > 0 else "mid" if light > -.5 else "dark"]
        pts = [P(s, *aa, z), P(s, *bb, z), P(s, *bb, z + height), P(s, *aa, z + height)]
        foot_a, foot_b = P(s, *aa, z), P(s, *bb, z)
        slope = (foot_b[1] - foot_a[1]) / (foot_b[0] - foot_a[0] or .001)
        poly(s, pts, lambda x, y, k=k, tone=tone, foot=foot_a, slope=slope:
             (pattern(k, int(foot[1] + (x - foot[0]) * slope - y)) if pattern else None) or tone)
    ring = [P(s, i + radius * math.cos(k * math.tau / count),
              j + radius * math.sin(k * math.tau / count), z + height) for k in range(count)]
    poly(s, ring, lambda x, y: stone["hi"])
    for a, b in zip(ring, ring[1:] + ring[:1]):
        seg(s, a, b, stone["line"])


def column(s, i, j, height, radius=.18, z=0, stone=SAND):
    cylinder(s, i, j, radius * 1.45, z, 2, stone)
    cylinder(s, i, j, radius, z + 2, height - 4, stone,
             lambda k, v: stone["line"] if k % 4 == 0 else None)
    block(s, i - radius * 1.4, j - radius * 1.4, radius * 2.8, radius * 2.8,
          2, stone, z=z + height - 2)


def dome(s, i, j, radius, base, rise, stone=COPPER):
    """Ribbed dome on a projected circular drum, with cornice, lantern and a cross."""
    cylinder(s, i, j, radius, base, 9, SAND,
             lambda k, v: GLASS["dark"] if k % 3 == 0 and 2 <= v <= 7 else None)
    x, y = P(s, i, j, base + 9)
    rx = max(3, round(radius * 11.3))
    egg_dome(s, x, y, rx, rise, (stone["lit"], stone["mid"], stone["dark"]))
    # Projected meridians make the copper ribs follow the volume rather than screen stripes.
    for angle in (.1, .75, 1.4, 2.1, 2.8):
        points = []
        for k in range(17):
            t = k / 16 * math.pi / 2
            points.append((x + rx * math.cos(angle) * math.cos(t),
                           y + radius * 5.65 * math.sin(angle) * math.cos(t) - rise * math.sin(t)))
        for a, b in zip(points, points[1:]):
            seg(s, a, b, stone["hi"] if angle > 1.4 else stone["deep"])
    cylinder(s, i, j, .16, base + 9 + rise - 1, 6, stone)
    xx, yy = P(s, i, j, base + 9 + rise + 9)
    seg(s, (xx, yy + 4), (xx, yy - 2), GOLD["lit"])
    seg(s, (xx - 2, yy), (xx + 2, yy), GOLD["lit"])


def classical(stone, height, bay=8):
    courses = stone_courses(stone, rows=4, every=9)

    def pattern(u, v, lit):
        u, v = int(u), int(v)
        col = u % bay
        hi, line = stone["hi" if lit else "mid"], stone["line" if lit else "deep"]
        if v in (1, 10, height - 3, height - 1):
            return hi if v != 10 else line
        if v < 9:
            opening = arch_opening(col, v, bay / 2, 2, 4, stone["deep"])
            return opening or courses(u, v, lit)
        if col in (0, 1):
            return hi if col == 0 else line  # pilasters
        level = (v - 11) % 10
        if 3 <= col <= bay - 2 and 1 <= level <= 8 and v < height - 4:
            if col in (3, bay - 2) or level in (1, 8):
                return hi
            return hi if col == 5 or level == 4 else GLASS["mid"] if level < 4 else GLASS["dark"]
        if level == 0 and v > 12:
            return line
        return None
    return pattern


def pediment(s, i, j, width, depth, base, rise, stone=SAND):
    """Triangular gabled temple roof, with a recessed tympanum and raking cornice."""
    T, R, B, L = corners(s, i, j, width, depth, base)
    a, b = P(s, i + width / 2, j, base + rise), P(s, i + width / 2, j + depth, base + rise)
    poly(s, [T, L, b, a], lambda x, y: ROOF["lit"] if int(y) % 3 else ROOF["line"])
    poly(s, [a, b, B, R], lambda x, y: ROOF["dark"] if int(y) % 3 else ROOF["deep"])
    poly(s, [L, B, b], lambda x, y: stone["dark"])
    for aa, bb in ((L, B), (L, b), (b, B)):
        seg(s, aa, bb, stone["hi"], 2)
    # Sculpted relief, clipped to the triangular front.
    for x, y in iso.polygon_pixels([L, B, b]):
        u, v = x - L[0], L[1] + (x - L[0]) * .5 - y
        if 2 < v < rise - 2 and (int(u) // 3 + int(v)) % 7 == 0:
            s.put(x, y, stone["lit"])


def horse(s, i, j, z):
    """A solid bronze horse: body, raised neck, muzzle, ears and four separated legs."""
    body = [(i, j, z + 3), (i + .54, j, z + 3), (i + .56, j, z + 7),
            (i + .36, j, z + 10), (i + .2, j, z + 10), (i + .2, j, z + 7), (i, j, z + 6)]
    pts = [P(s, *p) for p in body]
    poly(s, pts, lambda x, y: COPPER["lit"] if int(x) % 3 else COPPER["hi"])
    for a, b in zip(pts, pts[1:] + pts[:1]):
        seg(s, a, b, COPPER["deep"])
    for di, dj in ((0, 0), (.42, 0), (0, -.16), (.42, -.16)):
        seg(s, P(s, i + di, j + dj, z + 4), P(s, i + di - .08, j + dj, z), COPPER["dark"])
    seg(s, P(s, i + .25, j, z + 10), P(s, i + .25, j, z + 12), COPPER["lit"])
    seg(s, P(s, i, j, z + 5), P(s, i - .24, j, z + 1), COPPER["deep"])


def winged_figure(s, i, j, z, stone=GOLD, size=1):
    """Filled robe, head, outstretched feathered wings and laurel; never a stick statue."""
    x, y = P(s, i, j, z)
    def shape(points, color):
        poly(s, [(x + a * size, y - b * size) for a, b in points], lambda x, y: color)
    shape([(-2, 0), (3, 0), (2, 6), (0, 10), (-2, 6)], stone["lit"])
    shape([(0, 5), (-5, 8), (-9, 15), (-6, 13), (-3, 12), (0, 9)], stone["hi"])
    shape([(1, 6), (5, 10), (9, 14), (8, 10), (5, 7), (2, 5)], stone["dark"])
    shape([(-1, 10), (1, 10), (2, 12), (0, 14), (-2, 12)], stone["hi"])
    seg(s, (x + 2 * size, y - 8 * size), (x + 5 * size, y - 14 * size), stone["mid"])
    for dx, dy in ((4, 14), (5, 15), (6, 14), (5, 13)):
        s.put(x + dx * size, y - dy * size, stone["hi"])


def brandenburg_gate(scene, i, j):
    """Six Doric columns in each row, five open passages, relief attic, four-horse Quadriga."""
    W, D, H = 8.2, 2.0, 35
    def draw(s):
        for a in (i - 1.8, i + W + .3):
            block(s, a, j - .2, 1.5, D + .4, 21,
                  pattern=lambda u, v, lit: arch_opening(u, v, 6, 2, 10, SAND["deep"])
                  or (SAND["hi" if lit else "mid"] if int(v) in (2, 17, 20) or int(u) % 10 == 0
                      else stone_courses(SAND, 5, 10)(u, v, lit)))
            hip_roof(s, a, j - .2, 1.5, D + .4, 21, 5, roof=COPPER)
        block(s, i - .45, j - .4, W + .9, D + .8, 2)
        for jj in (j + .35, j + D - .35):
            for n in range(6):
                column(s, i + .35 + n * (W - .7) / 5, jj, H - 3, .25, z=2)
        # Continuous entablature on the open colonnade: triglyphs and figured metopes.
        def frieze(u, v, lit):
            u, v = int(u), int(v)
            if v in (1, 7, 9):
                return SAND["hi" if lit else "mid"]
            if 3 <= v <= 6:
                return SAND["deep"] if u % 7 in (0, 2) else SAND["line"] if (u + v) % 5 == 0 else None
            return None
        block(s, i - .2, j - .25, W + .4, D + .5, 10, pattern=frieze, z=H)
        block(s, i + 2.7, j, 2.8, D, 5, z=H + 10)
        # Four individually modelled horses, two chariot wheels, robed driver and eagle standard.
        for n in range(4):
            horse(s, i + 2.3 + n * .8, j + 1.5, H + 15)
        x, y = P(s, i + 4.0, j + .4, H + 17)
        for dx in (-5, 3):
            for a in range(16):
                ang = a * math.tau / 16
                s.put(x + dx + 2 * math.cos(ang), y - 2 + 2 * math.sin(ang), COPPER["deep"])
        block(s, i + 3.4, j + .1, 1.2, .5, 4, COPPER, z=H + 17)
        winged_figure(s, i + 3.9, j + .3, H + 21, COPPER, .65)
    scene.add(i + j + W + D, draw)


def reichstag(scene, i, j):
    """Four corner pavilions, pilastered wings, pedimented portico and Foster's ribbed glass dome."""
    W, D, H = 10, 6, 31
    def draw(s):
        block(s, i, j, W, D, H, pattern=classical(SAND, H))
        hip_roof(s, i, j, W, D, H + 1, 3, roof=ROOF)
        # Four squared pavilions project through the low roof.
        for a, b in ((i, j), (i + W - 1.6, j), (i, j + D - 1.6), (i + W - 1.6, j + D - 1.6)):
            block(s, a - .1, b - .1, 1.8, 1.8, 39, pattern=classical(SAND, 39, 7))
            block(s, a - .2, b - .2, 2, 2, 3, z=39)
        # Entrance stairs and six-column portico.
        for k in range(5):
            block(s, i + 2.8, j + D + .15 + k * .28, 4.4, .32, 5 - k)
        for k in range(6):
            column(s, i + 3.05 + k * .76, j + D + .1, 22, .17, z=7)
        pediment(s, i + 2.6, j + D - .7, 4.8, 1.4, 31, 9)
        # Dome as a translucent-looking solid with sparse projected meridians and circular ribs.
        cx, cy = i + W / 2, j + D / 2
        cylinder(s, cx, cy, 1.55, 34, 4, SILVER)
        x, y = P(s, cx, cy, 38)
        egg_dome(s, x, y, 18, 25, (GLASS["lit"], GLASS["mid"], SILVER["dark"]))
        for k in range(1, 7):
            t = k / 7 * math.pi / 2
            rx = 18 * math.cos(t)
            yy = y - 25 * math.sin(t)
            seg(s, (x - rx, yy), (x + rx, yy), SILVER["lit"])
        for f in (-.78, -.4, 0, .4, .78):
            pts = [(x + 18 * f * math.cos(t / 24 * math.pi / 2),
                    y - 25 * math.sin(t / 24 * math.pi / 2)) for t in range(25)]
            for a, b in zip(pts, pts[1:]):
                seg(s, a, b, SILVER["deep"])
        seg(s, (x - 2, y - 24), (x + 2, y - 24), SILVER["deep"])  # open crown / oculus
        # German flag above the west pavilion.
        x, y = P(s, i + .8, j + D - .8, 43)
        seg(s, (x, y), (x, y - 14), SILVER["deep"])
        for dy in range(7):
            for dx in range(1, 10):
                s.put(x + dx, y - 14 + dy + (dx // 4) % 2,
                      (INK, rgb("#BE4944"), GOLD["lit"])[min(2, dy // 2)])
    scene.add(i + j + W + D, draw)


def berlin_cathedral(scene, i, j):
    """Berliner Dom: great ribbed copper dome, four domed corner towers, arched portals and rose."""
    W, D, H = 7.4, 6.2, 34
    def draw(s):
        block(s, i, j, W, D, H, pattern=classical(SAND, H, 9))
        hip_roof(s, i, j, W, D, H, 6, roof=COPPER)
        # The rear towers sit behind the main drum; front towers frame the portals.
        for a, b in ((i + .6, j + .6), (i + W - .6, j + .6)):
            block(s, a - .65, b - .65, 1.3, 1.3, 42, pattern=classical(SAND, 42, 7))
            dome(s, a, b, .58, 42, 11)
        dome(s, i + W / 2, j + D / 2, 1.85, H + 4, 24)
        def front(u, v, lit):
            u, v = int(u), int(v)
            if not lit:
                return classical(SAND, H, 9)(u, v, lit)
            width = (W - 1.8) * 8
            for c in (width * .23, width * .5, width * .77):
                if abs(u - c) <= 4:
                    inner = arch_opening(u, v, c, 3, 13, SAND["deep"])
                    outer = arch_opening(u, v, c, 4, 13, SAND["hi"])
                    if inner or outer:
                        return inner or outer
            r = math.hypot(u - width / 2, v - 25)
            if r < 4.5:
                return SAND["hi"] if r > 3.3 else GLASS["mid"] if (u + v) % 3 else GOLD["dark"]
            return SAND["hi"] if v in (2, 20, 32) or u % 11 == 0 else None
        block(s, i + .9, j + D - .75, W - 1.8, 1, H, pattern=front)
        for a, b in ((i + .6, j + D - .5), (i + W - .6, j + D - .5)):
            block(s, a - .65, b - .65, 1.3, 1.3, 42, pattern=classical(SAND, 42, 7))
            dome(s, a, b, .58, 42, 11)
        for k in range(4):
            block(s, i + 1.7, j + D + .2 + k * .25, W - 3.4, .3, 4 - k)
    scene.add(i + j + W + D, draw)


def tv_tower(scene, i, j):
    """Fernsehturm: flared concrete foot, tapering shaft, faceted silver sphere, glazing and mast."""
    def draw(s):
        cylinder(s, i, j, .7, 0, 7, SILVER)
        # Conical shaft, modelled as four projected tapering faces.
        low, high = corners(s, i - .32, j - .32, .64, .64, 7), corners(s, i - .13, j - .13, .26, .26, 101)
        for a, b, tone in ((1, 2, SILVER["dark"]), (2, 3, SILVER["lit"]), (3, 0, SILVER["mid"]), (0, 1, SILVER["mid"])):
            poly(s, [low[a], low[b], high[b], high[a]], lambda x, y, t=tone: t)
        # Latitude rings form a sphere; triangular facet highlights are kept on its own surface.
        x, y = P(s, i, j, 112)
        for dy in range(-15, 16):
            half = 15 * math.sqrt(max(0, 1 - (dy / 15) ** 2))
            for dx in range(-math.ceil(half), math.ceil(half) + 1):
                if abs(dx) > half:
                    continue
                tone = SILVER["hi"] if dx < -5 else SILVER["lit"] if dx < 3 else SILVER["mid"] if dx < 9 else SILVER["dark"]
                if -1 <= dy <= 3:  # continuous observation / restaurant glazing belt
                    tone = GLASS["dark"] if dx % 3 else SILVER["deep"]
                elif (dx + dy * 2) % 9 == 0:
                    tone = shade(tone, -.14)
                s.put(x + dx, y + dy, tone)
        cylinder(s, i, j, .18, 127, 9, SILVER)
        for z in range(136, 161):
            x, y = P(s, i, j, z)
            s.put(x, y, rgb("#BE4944") if (z // 5) % 2 else SILVER["hi"])
            if z < 151:
                s.put(x + 1, y, SILVER["dark"])
        # Low angular entrance pavilion, separate from the shaft.
        block(s, i - 1.6, j + .45, 3.2, 1, 5, SILVER,
              lambda u, v, lit: GLASS["dark"] if int(u) % 4 else SILVER["lit"])
    scene.add(i + j + 3, draw)


def rotes_rathaus(scene, i, j):
    """Red-brick arcaded city hall with terracotta frieze, crenellated clock tower and belfry."""
    W, D, H = 7, 5, 28
    def brick_face(u, v, lit):
        u, v = int(u), int(v)
        if v in (2, 11, 23, 26):
            return BRICK["hi" if lit else "mid"]
        if 24 <= v <= 25:
            return BRICK["deep"] if (u + v) % 5 == 0 else BRICK["lit"]
        col = u % 8
        if v < 10:
            return arch_opening(col, v, 4, 2, 5, BRICK["deep"]) or stone_courses(BRICK, 3)(u, v, lit)
        if 3 <= col <= 5 and 14 <= v <= 21:
            return BRICK["hi"] if col == 3 or v in (14, 21) else GLASS["dark"]
        return stone_courses(BRICK, 3, 9)(u, v, lit)
    def draw(s):
        block(s, i, j, W, D, H, BRICK, brick_face)
        hip_roof(s, i, j, W, D, H, 7, roof=ROOF)
        # Projecting corner risalits with lighter brick quoins.
        for a in (i, i + W - 1):
            block(s, a, j + D - .7, 1.1, 1, H + 3, BRICK, brick_face)
            hip_roof(s, a, j + D - .7, 1.1, 1, H + 3, 5, roof=ROOF)
        a, b, size = i + 3, j + D - 1.7, 2.2
        def tower_face(u, v, lit):
            u, v = int(u), int(v)
            hi = BRICK["hi" if lit else "mid"]
            centre = size * 4
            if v in (2, 30, 49, 66, 72):
                return hi
            rr = math.hypot(u - centre, v - 64)
            if rr <= 4.3:
                if rr > 3.3:
                    return SAND["hi"]
                return INK if (abs(u - centre) < 1 and v >= 64) or (v == 64 and u > centre) else SAND["mid"]
            if 46 <= v <= 57 and int(u) % 6 in (2, 3, 4):
                return BRICK["deep"]  # open belfry lancets
            if 12 <= v <= 24 and int(u) % 6 in (2, 3):
                return GLASS["dark"]
            return stone_courses(BRICK, 4, 8)(u, v, lit)
        block(s, a, b, size, size, 74, BRICK, tower_face)
        # Corner pinnacles around the pyramidal red roof and its small central finial.
        block(s, a - .1, b - .1, size + .2, size + .2, 2, BRICK, z=74)
        for aa, bb in ((a, b), (a + size - .3, b), (a, b + size - .3), (a + size - .3, b + size - .3)):
            block(s, aa, bb, .35, .35, 6, BRICK, z=76)
        hip_roof(s, a + .25, b + .25, size - .5, size - .5, 76, 9, roof=BRICK)
        cylinder(s, a + size / 2, b + size / 2, .08, 85, 5, ROOF)
    scene.add(i + j + W + D, draw)


def victory_column(scene, i, j):
    """Siegessäule: red granite relief base, mosaic colonnade, gilded barrels and winged Victoria."""
    def draw(s):
        block(s, i - 1.2, j - 1.2, 2.4, 2.4, 9, RED_STONE,
              lambda u, v, lit: RED_STONE["deep"] if 2 <= v <= 6 and int(u + v) % 7 < 2 else None)
        cylinder(s, i, j, 1.0, 9, 3, SAND)
        mosaic = (GOLD["mid"], BRICK["lit"], COPPER["mid"], SAND["hi"])
        cylinder(s, i, j, .58, 12, 10, SAND,
                 lambda k, v: mosaic[(k // 2 + v // 3) % len(mosaic)])
        for k in range(10):
            ang = k * math.tau / 10
            column(s, i + .8 * math.cos(ang), j + .8 * math.sin(ang), 10, .1, z=12)
        cylinder(s, i, j, 1.05, 22, 3, SAND)
        cylinder(s, i, j, .42, 25, 42, SAND,
                 lambda k, v: GOLD["lit"] if k % 3 == 0 and v % 11 < 8 else SAND["deep"] if v % 11 == 0 else None)
        cylinder(s, i, j, .65, 67, 3, GOLD)
        cylinder(s, i, j, .38, 70, 4, GOLD)
        winged_figure(s, i, j, 74, GOLD)
    scene.add(i + j + 3, draw)


def konzerthaus(scene, i, j):
    """Schinkel's concert hall: tall central gable, six-column portico, broad stair and Apollo."""
    W, D = 8.5, 5.2
    def draw(s):
        block(s, i, j, W, D, 27, pattern=classical(SAND, 27, 8))
        hip_roof(s, i, j, W, D, 27, 7, roof=ROOF)
        block(s, i + 1.8, j + .4, 4.9, 3.8, 40, pattern=classical(SAND, 40, 9))
        pediment(s, i + 1.65, j + .3, 5.2, 3.9, 40, 13)
        for k in range(7):
            block(s, i + 1.7, j + D + k * .3, 5.1, .35, 7 - k)
        for k in range(6):
            column(s, i + 2 + k * .9, j + D - .1, 23, .19, z=7)
        pediment(s, i + 1.65, j + D - 1.2, 5.2, 1.6, 31, 10)
        # Apollo's solid robed figure and lyre on the highest ridge.
        x, y = P(s, i + W / 2, j + 2.1, 54)
        poly(s, [(x - 2, y), (x + 3, y), (x + 1, y - 7), (x - 1, y - 7)], lambda x, y: SAND["hi"])
        for dx, dy in ((0, 9), (1, 9), (0, 8), (1, 8), (-3, 5), (-4, 7), (-2, 7)):
            s.put(x + dx, y - dy, SAND["lit"])
        # Carved lions beside the stairs, each with a body, mane and two front paws.
        for a in (i + 1.45, i + 6.8):
            block(s, a, j + D + .4, .55, .9, 4)
            xx, yy = P(s, a + .3, j + D + .65, 6)
            poly(s, [(xx - 3, yy), (xx + 3, yy), (xx + 2, yy - 4), (xx, yy - 6), (xx - 2, yy - 4)],
                 lambda x, y: SAND["lit"] if int(x) % 3 else SAND["dark"])
    scene.add(i + j + W + D + 2, draw)


def berlin_house(scene, i, j, wi, wj, floors, seed):
    """Gründerzeit Mietshaus: stucco dressings, shopfronts, bay window, iron balconies and dormers."""
    wall = palette_of(WALLS[seed % len(WALLS)])
    H = floors * 9 + 3
    def pattern(u, v, lit):
        u, v = int(u), int(v)
        col, level = u % 7, v % 9
        hi, line = wall["hi" if lit else "mid"], wall["line" if lit else "deep"]
        if v < 2 or v in (H - 1, H - 3):
            return line if v < 2 else hi
        if v < 10:
            if 2 <= col <= 5 and v < 8:
                return WOOD if (int(u) // 7 + seed) % 3 == 0 else GLASS["dark"] if col != 3 else hi
            return line if v == 9 else None
        if col in (2, 3, 4, 5) and 2 <= level <= 7:
            if col in (2, 5) or level in (2, 7):
                return hi
            return GLASS["mid"] if level < 5 else GLASS["dark"]
        if level == 1 and 1 <= col <= 6:
            return hi  # sill and ornamental window hood
        balcony = (seed + int(u) // 7 + v // 9) % 3 == 0
        if balcony and ((level == 0 and 1 <= col <= 6) or (level == 1 and col in (1, 3, 5))):
            return INK
        if col == 0 and seed % 2 == 0:
            return hi  # stucco pilaster
        return None
    def draw(s):
        cover = facade(s, i, j, wi, wj, H, pattern, palette=wall)
        if seed % 3:
            mansard(s, i, j, wi, wj, H, 9, .5, roof=ROOF, dormers=7, cover=cover)
        else:
            hip_roof(s, i, j, wi, wj, H, 10, roof=ROOF, cover=cover)
        iso.outline(s, cover, wall["outline"])
        # Projecting two-storey oriel on selected street fronts, with its own correctly mapped face.
        if seed % 4 == 0 and wi >= 3:
            block(s, i + .9, j + wj - .15, .95, .5, H - 12, wall,
                  lambda u, v, lit: GLASS["dark"] if int(u) % 5 in (2, 3) and int(v) % 9 in (3, 4, 5, 6)
                  else wall["hi"] if int(v) % 9 == 1 else None, z=10)
            hip_roof(s, i + .85, j + wj - .2, 1.05, .6, H - 2, 4, roof=ROOF)
        block(s, i + .6, j + .6, .35, .45, 7, BRICK, z=H + 5)
    scene.add(i + j + wi + wj, draw)


if __name__ == "__main__":
    plots = [
        ("gate", brandenburg_gate, (250, 180), (105, 70)),
        ("reichstag", reichstag, (270, 210), (115, 80)),
        ("cathedral", berlin_cathedral, (260, 220), (115, 100)),
        ("tv-tower", tv_tower, (180, 260), (90, 185)),
        ("rathaus", rotes_rathaus, (250, 220), (115, 105)),
        ("victory", victory_column, (180, 200), (90, 120)),
        ("konzerthaus", konzerthaus, (260, 210), (110, 90)),
    ]
    for name, builder, size, origin in plots:
        print(preview([lambda s, build=builder: build(s, 3, 3)], f"berlin-{name}",
                      size=size, origin=origin, tiles=16))
    print(preview([lambda s: berlin_house(s, 2, 2, 3, 3, 4, 0),
                   lambda s: berlin_house(s, 7, 2, 3, 3, 5, 1),
                   lambda s: berlin_house(s, 7, 7, 3, 2, 4, 3)], "berlin-houses",
                  size=(240, 200), origin=(110, 80), tiles=15))
