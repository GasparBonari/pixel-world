"""Rome in travertine, ochre stucco and Roman brick, built in projected (i, j, z).

Run directly for eight isolated 4× landmark studies and a palazzo study.
Geographic anchors and primary architectural references: DEVELOPMENT_PLAN.md.
"""
import math

import iso
from iso import rgb, h01
from landmarks_paris import P, seg, poly, corners, facade, preview, GLASS
from landmarks_iberia import hip_roof, crenellate, stone_courses, arch_opening, palette_of, tones
from landmarks_belgium import dome, pediment, relief

STONE = tones('#FFF2D9', '#E7D4AD', '#CEB990', '#AC9571', '#796447', '#B5A07B', '#4B3D2C')
MARBLE = tones('#FFFFF0', '#F3EBD4', '#DCD2B8', '#B9AE93', '#877C64', '#C6B99B', '#534936')
BRICK = tones('#DBA77C', '#B88259', '#9C6948', '#7E523B', '#533A29', '#946340', '#3F2D22')
CLAY = tones('#F2B27C', '#CE7E4D', '#B3633D', '#8D472E', '#603122', '#9F5736', '#4F2A20')
LEAD = tones('#BBC4BF', '#8B9D98', '#758A83', '#546B65', '#364D46', '#657D74', '#2B3D36')
BRONZE = tones('#AFBE9B', '#7C957D', '#597662', '#3E584A', '#2A4035', '#587560', '#23362C')
IRON, WOOD = rgb('#373D32'), rgb('#69432C')
WATER = (rgb('#66ACA4'), rgb('#418681'), rgb('#B9E0CE'))
WALLS = [rgb(c) for c in ('#D5A561', '#C17D52', '#D8B883', '#B77B60', '#E4CBA1', '#CB976F')]
SHUTTER = rgb('#526B4C')


def block(s, i, j, wi, wj, height, material=STONE, pattern=None, z=0):
    cover = facade(s, i, j, wi, wj, height, pattern or stone_courses(material, 4, 10), palette=material, z0=z)
    iso.fill(s, list(corners(s, i, j, wi, wj, z + height)), lambda x, y: material['mid'], cover)
    iso.outline(s, cover, material['outline'])
    return cover


def windows(material, height, bay=10, arcade=False):
    courses = stone_courses(material, 5, 12)
    def pattern(u, v, lit):
        c, v = int(u) % bay, int(v)
        level, trim = v % 13, MARBLE['lit' if lit else 'dark']
        if v < 2 or v in (height - 1, height - 3) or level == 0:
            return trim
        if arcade and v < 11:
            opening = arch_opening(c, v, bay / 2, 2.5, 6, material['deep'])
            if opening:
                return opening
        if 2 <= c <= bay - 3 and 3 <= level <= 10 and v < height - 4:
            if c in (2, bay - 3, bay // 2) or level in (3, 7, 10):
                return trim
            return GLASS['mid' if lit else 'dark']
        return courses(u, v, lit)
    return pattern


def column(s, i, j, base, height, material=MARBLE, width=.42):
    block(s, i - width / 2, j - width / 2, width, width, height, material,
          lambda u, v, lit: material['line' if lit else 'deep'] if int(u) % 3 == 0 else None, z=base)
    for z in (base, base + height - 2):
        block(s, i - width * .7, j - width * .7, width * 1.4, width * 1.4, 2, material, z=z)
    # Corinthian foliage/volutes as a filled capital, attached to its shaft.
    for di in (-.28, .2):
        block(s, i + di, j - .12, .17, .25, 3, material, z=base + height - 2)


def cross(s, i, j, z, material=MARBLE):
    block(s, i - .09, j - .08, .18, .16, 7, material, z=z)
    block(s, i - .3, j - .08, .6, .16, 1.2, material, z=z + 4)


def ellipse(s, ci, cj, ri, rj, z, color):
    points = [P(s, ci + ri * math.cos(a * math.tau / 64), cj + rj * math.sin(a * math.tau / 64), z) for a in range(64)]
    poly(s, points, color if callable(color) else lambda x, y: color)


def cylinder(s, ci, cj, ri, rj, base, height, material=STONE, pattern=None, cap=True):
    """Faceted elliptical volume: texture coordinates stay on each projected wall."""
    faces = []
    for n in range(64):
        a, b = n * math.tau / 64, (n + 1) * math.tau / 64
        va = ci + ri * math.cos(a), cj + rj * math.sin(a)
        vb = ci + ri * math.cos(b), cj + rj * math.sin(b)
        pa, pb = P(s, *va, base), P(s, *vb, base)
        lit = math.sin((a + b) / 2) - .5 * math.cos((a + b) / 2) > 0
        faces.append((sum(va + vb), n, pa, pb, lit))
    for _, n, pa, pb, lit in sorted(faces):
        dx = pb[0] - pa[0]
        def color(x, y):
            t = max(0, min(1, (x - pa[0]) / dx)) if abs(dx) > .01 else .5
            v = pa[1] + t * (pb[1] - pa[1]) - y
            u = (n + t) * (ri + rj) * math.pi * 4 / 64
            c = pattern(u, v, lit) if pattern else None
            return c or material['lit' if lit else 'dark']
        poly(s, [pa, pb, (pb[0], pb[1] - height), (pa[0], pa[1] - height)], color)
    if cap:
        ellipse(s, ci, cj, ri, rj, base + height, material['mid'])


def basin(s, i, j, ri, rj, z=0):
    cylinder(s, i, j, ri, rj, z, 3, MARBLE)
    ellipse(s, i, j, ri - .18, rj - .18, z + 3.2,
            lambda x, y: WATER[2] if h01(x // 3, y, 146) < .08 else WATER[(int(x) // 4 + int(y)) % 2])


def obelisk(s, i, j, base, height=30):
    block(s, i - .35, j - .35, .7, .7, 4, MARBLE, z=base)
    block(s, i - .17, j - .17, .34, .34, height, STONE,
          lambda u, v, lit: STONE['deep'] if int(v) % 5 == 0 and int(u) % 2 == 0 else None, z=base + 4)
    tip = P(s, i, j, base + height + 9)
    for a, b, tone in ((P(s, i - .17, j + .17, base + height + 4), P(s, i + .17, j + .17, base + height + 4), 'lit'),
                        (P(s, i + .17, j + .17, base + height + 4), P(s, i + .17, j - .17, base + height + 4), 'dark')):
        poly(s, [a, b, tip], lambda x, y, tone=tone: STONE[tone])


def palazzo(scene, i, j, wi=2.5, wj=3, floors=3, seed=0):
    """Roman stucco, green shutters, rusticated shop floor and overhanging clay eaves."""
    wall, height = palette_of(WALLS[seed % len(WALLS)]), floors * 11 + 4
    def pattern(u, v, lit):
        c, v = int(u) % 10, int(v)
        level, trim = v % 11, MARBLE['lit' if lit else 'dark']
        if v < 2 or v in (height - 1, height - 3):
            return trim
        if v < 12:
            if 2 <= c <= 7 and v < 9:
                if c in (2, 7) or v == 8:
                    return trim
                return WOOD if (int(u) // 10 + seed) % 2 else GLASS['dark']
            return wall['line' if lit else 'deep'] if v % 4 == 0 else None
        if 1 <= c <= 8 and 3 <= level <= 9 and v < height - 4:
            if c in (1, 8):
                return SHUTTER if level % 2 else wall['deep']
            if c in (2, 7, 4) or level in (3, 9):
                return trim
            return GLASS['mid' if lit else 'dark']
        if level == 2 and 1 <= c <= 8:
            return trim
        return None
    def draw(s):
        block(s, i, j, wi, wj, height, wall, pattern)
        hip_roof(s, i - .12, j - .12, wi + .24, wj + .24, height, 6, roof=CLAY)
        block(s, i + .35, j + .45, .45, .6, 7, BRICK, z=height + 2)
        block(s, i + .27, j + .38, .61, .74, 1.5, MARBLE, z=height + 9)
        if seed % 4 == 0:
            # Individual projecting iron balcony, rather than a repeated façade stripe.
            block(s, i + .5, j + wj, 1.3, .35, 1.5, MARBLE, z=14)
            for a in (.55, .85, 1.15, 1.65):
                seg(s, P(s, i + a, j + wj + .35, 16), P(s, i + a, j + wj + .35, 20), IRON)
            seg(s, P(s, i + .5, j + wj + .35, 20), P(s, i + 1.8, j + wj + .35, 20), IRON)
    scene.add(i + j + wi + wj + .5, draw)


def st_peters(scene, i, j):
    """Ribbed great dome, lantern, Maderno façade and Bernini's embracing colonnades.

    The real basilica faces east, so the façade is the shaded +i (south-east) face: the
    transept and dome stand at the -i (west) end, the long nave runs forward along +i, and
    St Peter's Square opens further along +i towards Via della Conciliazione and the Tiber.
    Footprint about 15.3 × 11 tiles."""
    def side_pediment(s, fi, j0, width, base, rise, material):
        # A pediment in the j/z plane, on a wall whose front faces +i.
        pts = [P(s, fi, j0, base), P(s, fi, j0 + width, base), P(s, fi, j0 + width / 2, base + rise)]
        poly(s, pts, lambda x, y: material['dark'] if (int(x) + int(y)) % 7 else material['line'])
        for a, b in zip(pts, pts[1:] + pts[:1]):
            seg(s, a, b, material['hi'], 2)

    def side_statue(s, fi, fj, z, material):
        # The façade's attic saints, standing in the j/z plane and facing +i.
        profile = [(-.3, 0), (.3, 0), (.2, 3), (.18, 6), (.12, 7),
                   (.16, 9), (-.13, 9), (-.2, 7), (-.12, 6), (-.23, 4)]
        face = [P(s, fi, fj + dj, z + dz) for dj, dz in profile]
        back = [P(s, fi - .12, fj + dj, z + dz) for dj, dz in profile]
        for a in range(len(face)):
            b = (a + 1) % len(face)
            poly(s, [back[a], back[b], face[b], face[a]], lambda x, y: material['dark'])
        poly(s, face, lambda x, y: material['lit'] if int(x) % 3 else material['mid'])

    def draw(s):
        # Transept and crossing at the west end, its arms running north-south (along j).
        block(s, i, j + 1, 4.4, 9, 35, STONE, windows(STONE, 35))
        hip_roof(s, i, j + 1, 4.4, 9, 35, 8, roof=CLAY)
        ci, cj = i + 2.2, j + 5.5
        cylinder(s, ci, cj, 2.15, 2.15, 40, 19, MARBLE, windows(MARBLE, 23, 8))
        for n in range(12):
            a = n * math.tau / 12
            column(s, ci + 2.1 * math.cos(a), cj + 2.1 * math.sin(a), 41, 18, width=.23)
        # Raised ogival profile: stacked hemisphere mesh is taller than its radius.
        dome(s, ci, cj, 2.5, 60, 36, LEAD)
        for n in range(16):
            a = n * math.tau / 16
            if math.cos(a) + math.sin(a) < -.25:
                continue
            points = [P(s, ci + 2.5 * math.cos(t * math.pi / 32) * math.cos(a),
                        cj + 2.5 * math.cos(t * math.pi / 32) * math.sin(a),
                        60 + 36 * math.sin(t * math.pi / 32)) for t in range(17)]
            for p, q in zip(points, points[1:]):
                seg(s, p, q, MARBLE['mid'] if math.sin(a) > 0 else LEAD['deep'])
        cylinder(s, ci, cj, .48, .48, 96, 10, MARBLE, windows(MARBLE, 14, 5))
        dome(s, ci, cj, .65, 106, 5, LEAD)
        cross(s, ci, cj, 111)
        # Long nave running east from the crossing to the façade, ridge along i.
        block(s, i + 4.4, j + 3.5, 4.2, 4, 33, STONE, windows(STONE, 33))
        hip_roof(s, i + 4.4, j + 3.5, 4.2, 4, 33, 7, roof=CLAY)
        # Maderno's east façade, wider than the nave: a wall with arched portals and
        # eight giant engaged columns, the central four under the pediment.
        fi = i + 10
        block(s, i + 8.4, j + .5, 1.6, 10, 33, MARBLE, windows(MARBLE, 33, 11, True))
        for a in range(8):
            column(s, fi + .12, j + 2 + a, 2, 29, width=.35)
        block(s, i + 8.4, j + .35, 1.75, 10.3, 4, MARBLE, z=33)
        side_pediment(s, fi + .16, j + 3, 5, 37, 9, MARBLE)
        for a in range(13):
            side_statue(s, fi + .05, j + .75 + a * .79, 38, MARBLE)
        # Two elliptical arms east of the façade, open towards the river: independent
        # columns with upper lintels; the far (north) arm first, then the obelisk, then the near arm.
        def arm(side):
            ring = []
            for n in range(14):
                a = -.9 + n * 1.8 / 13
                ci2 = i + 12.9 + 2.2 * math.sin(a)
                cj2 = j + 5.5 + side * (3.9 + 1.4 * math.cos(a))
                column(s, ci2, cj2, 0, 12, width=.25)
                ring.append(P(s, ci2, cj2, 14))
                if n % 3 == 0:
                    side_statue(s, ci2, cj2, 15, MARBLE)
            for a, b in zip(ring, ring[1:]):
                seg(s, a, b, MARBLE['lit'], 2)
        arm(-1)
        obelisk(s, i + 12.9, j + 5.5, 0, 24)
        arm(1)
    scene.add(i + j + 26, draw)


def castel_santangelo(scene, i, j):
    """Hadrian's cylindrical tomb above a square bastion, battlements and bronze angel."""
    def draw(s):
        block(s, i, j, 8, 7, 12, STONE, windows(STONE, 20, 14, True))
        ci, cj = i + 4, j + 3.5
        cylinder(s, ci, cj, 3.1, 3.1, 12, 37, STONE, stone_courses(STONE, 4, 10))
        cylinder(s, ci, cj, 3.25, 3.25, 47, 5, BRICK)
        for n in range(24):
            a = n * math.tau / 24
            block(s, ci + 3.15 * math.cos(a) - .18, cj + 3.15 * math.sin(a) - .18,
                  .36, .36, 4, STONE, z=52)
        block(s, ci - 1.5, cj - 1, 3, 2, 13, BRICK, windows(BRICK, 20, 7), z=52)
        hip_roof(s, ci - 1.5, cj - 1, 3, 2, 65, 5, roof=CLAY)
        block(s, ci - .35, cj - .35, .7, .7, 5, MARBLE, z=70)
        relief(s, ci, cj, 76, BRONZE, wings=True)
        # Michael's raised sword and scabbard, attached to a filled winged figure.
        seg(s, P(s, ci + .3, cj, 81), P(s, ci + .8, cj, 87), BRONZE['hi'], 2)
        for di, dj in ((.3, .3), (7.4, .3), (.3, 6.4), (7.4, 6.4)):
            cover = block(s, i + di, j + dj, .7, .7, 17, BRICK)
            crenellate(s, i + di, j + dj, .7, .7, 17, STONE, cover, step=3)
    scene.add(i + j + 16, draw)


def spanish_steps(scene, i, j):
    """Butterfly flights and terraces, Trinità's twin belfries, obelisk and Barcaccia."""
    def draw(s):
        block(s, i + 2, j, 5, 2.6, 25, MARBLE, windows(MARBLE, 25, 10, True), z=23)
        pediment(s, i + 2.4, j + 2.65, 4.2, 48, 9, MARBLE)
        for a in (2, 6):
            block(s, i + a, j, 1, 1.1, 42, MARBLE, windows(MARBLE, 42, 8, True), z=23)
            hip_roof(s, i + a, j, 1, 1.1, 65, 6, roof=CLAY)
            cross(s, i + a + .5, j + .55, 71)
        # Stair treads are individual 3D slabs; the landing divides changing-width flights.
        for step in range(16):
            depth = 2.7 + step * .29
            width = 3.5 + 2.2 * math.sin(step * math.pi / 15) ** 2
            x = i + 4.5 - width / 2
            block(s, x, j + depth, width, .3, 24 - step * 1.4, MARBLE,
                  lambda u, v, lit: MARBLE['lit' if lit else 'dark'])
            for a in (x - .12, x + width - .12):
                block(s, a, j + depth, .24, .32, 3, STONE, z=24 - step * 1.4)
        obelisk(s, i + 4.5, j + 2.9, 24, 23)
        basin(s, i + 4.5, j + 8.4, 1.4, .65)
        # Sunken boat fountain: curled prows and central jet.
        for a in (-1.1, 1.1):
            block(s, i + 4.5 + a, j + 8.4, .35, .45, 4, MARBLE, z=2)
        seg(s, P(s, i + 4.5, j + 8.4, 4), P(s, i + 4.5, j + 8.4, 9), WATER[2])
    scene.add(i + j + 20, draw)


def trevi(scene, i, j):
    """Palazzo Poli's giant order, triumphal niche, Oceanus, sea horses and rocky cascades."""
    def draw(s):
        block(s, i, j, 10, 2, 49, STONE, windows(STONE, 49, 10))
        hip_roof(s, i, j, 10, 2, 49, 5, roof=CLAY)
        def niche(u, v, lit):
            if lit:
                opening = arch_opening(u, v - 7, 40, 10, 22, STONE['deep'])
                if opening:
                    return opening
            return windows(MARBLE, 43, 12)(u, v, lit)
        block(s, i + 1, j + 1.5, 8, 1, 43, MARBLE, niche)
        for a in (2, 3.4, 6.6, 8):
            column(s, i + a, j + 2.65, 7, 35, width=.6)
        block(s, i + .9, j + 1.5, 8.2, 1.2, 4, MARBLE, z=43)
        pediment(s, i + 3.2, j + 2.71, 3.6, 47, 8, MARBLE)
        for a in (1.4, 3, 7, 8.6):
            relief(s, i + a, j + 2.2, 49, MARBLE)
        basin(s, i + 5, j + 5.2, 4.9, 2.4)
        # Irregular travertine rocks, clustered beneath the statuary and clipped inside basin.
        for a, b, r, h in ((1.8, 3.4, .6, 7), (3.4, 3.9, .9, 6), (5, 3.7, 1, 9),
                            (7, 3.4, .7, 8), (6.8, 5, .5, 5)):
            cylinder(s, i + a, j + b, r, r * .7, 3, h, MARBLE, stone_courses(MARBLE, 4, 7))
        # Oceanus dominates the niche: a solid torso, drapery, face, beard and extended arms.
        profile = [(-.5, 0), (.5, 0), (.4, 4), (.25, 9), (.6, 12),
                   (1.1, 10), (1.25, 11), (.65, 14), (.25, 15), (.25, 18),
                   (-.1, 19), (-.35, 18), (-.3, 15), (-.65, 14),
                   (-1.2, 12), (-1.1, 11), (-.5, 12), (-.25, 8)]
        front = [P(s, i + 5 + a, j + 3.8, 13 + z) for a, z in profile]
        back = [P(s, i + 5 + a, j + 3.5, 13 + z) for a, z in profile]
        for n in range(len(front)):
            poly(s, [back[n - 1], front[n - 1], front[n], back[n]], lambda x, y: MARBLE['dark'])
        poly(s, front, lambda x, y: MARBLE['lit'])
        for a in (-.2, .15):
            seg(s, P(s, i + 5 + a, j + 3.81, 14), P(s, i + 5 + a / 2, j + 3.81, 22), MARBLE['line'])
        seg(s, P(s, i + 4.85, j + 3.81, 29), P(s, i + 5.05, j + 3.81, 27), MARBLE['dark'], 2)
        for a in (2.5, 7.4):
            horse(s, i + a, j + 4.2, 9, MARBLE, rider=False)
            relief(s, i + a - .6, j + 4.6, 7, MARBLE)
        for a in (3.8, 5.2, 6.2):
            seg(s, P(s, i + a, j + 4, 10), P(s, i + a, j + 4.6, 3.5), WATER[2], 2)
    scene.add(i + j + 20, draw)


def horse(s, i, j, base, material=BRONZE, rider=True, scale=1):
    """Filled equine volume with four legs, arched neck, head, tail and optional rider."""
    profile = [(-.9, 5), (-.9, 1), (-.7, 0), (-.5, 5), (.35, 5), (.5, 0),
               (.7, 0), (.65, 6), (1, 10), (1.5, 10), (1.5, 12), (.8, 13),
               (.4, 11), (.05, 8), (-.65, 8), (-1.1, 7), (-1.4, 4), (-1.2, 3)]
    front = [P(s, i + a * scale, j, base + b * scale) for a, b in profile]
    back = [P(s, i + a * scale, j - .35 * scale, base + b * scale) for a, b in profile]
    poly(s, back, lambda x, y: material['dark'])
    for n in range(len(front)):
        poly(s, [back[n - 1], front[n - 1], front[n], back[n]], lambda x, y: material['mid'])
    poly(s, front, lambda x, y: material['lit'] if (int(x) + int(y)) % 5 else material['mid'])
    seg(s, P(s, i - .7, j - .3, base + 5), P(s, i - .4, j - .3, base), material['dark'], 2)
    seg(s, P(s, i + .4, j - .3, base + 5), P(s, i + .2, j - .3, base), material['dark'], 2)
    if rider:
        relief(s, i - .1, j, base + 8, material)


def navona(scene, i, j):
    """Stadium piazza, three basins, Four Rivers obelisk and Sant'Agnese's baroque front."""
    def draw(s):
        # Church west of the long piazza; facing the fountain across an open paved square.
        ci, cj = i - 2, j + 1
        block(s, ci, cj + 2, 6, 2, 27, STONE, windows(STONE, 27, 10, True))
        for a in (0, 5):
            block(s, ci + a, cj + 2, 1, 1.5, 43, MARBLE, windows(MARBLE, 43, 8, True))
            dome(s, ci + a + .5, cj + 2.7, .7, 43, 7, LEAD)
            cross(s, ci + a + .5, cj + 2.7, 50)
        cylinder(s, ci + 3, cj + 2.6, 1.3, 1.3, 29, 12, MARBLE, windows(MARBLE, 18, 7))
        dome(s, ci + 3, cj + 2.6, 1.6, 42, 17, LEAD)
        cross(s, ci + 3, cj + 2.6, 59)
        for a in (1.6, 2.5, 3.5, 4.4):
            column(s, ci + a, cj + 4.1, 0, 26, width=.3)
        pediment(s, ci + 1.5, cj + 4.12, 3, 27, 7, MARBLE)
        # Three distinct fountains along the old stadium's long axis.
        for a, b in ((8, .9), (8, 5.3), (8, 10)):
            basin(s, i + a, j + b, 1.6, 1)
        for a, b, r, h in ((7.3, 5, .45, 6), (8.2, 5.3, .65, 9), (8.6, 5.7, .4, 6)):
            cylinder(s, i + a, j + b, r, r, 3, h, MARBLE)
        for a, b in ((7.3, 4.9), (8.9, 5), (7.4, 5.9), (8.8, 6)):
            relief(s, i + a, j + b, 5, MARBLE)
        obelisk(s, i + 8, j + 5.3, 12, 35)
        # Small dove above Bernini's obelisk, a filled winged silhouette.
        poly(s, [P(s, i + 7.5, j + 5.3, 56), P(s, i + 7.8, j + 5.3, 58),
                 P(s, i + 8, j + 5.3, 57), P(s, i + 8.4, j + 5.3, 59),
                 P(s, i + 8.3, j + 5.3, 56)], lambda x, y: MARBLE['hi'])
        for b in (.9, 10):
            relief(s, i + 8, j + b, 4, BRONZE)
    scene.add(i + j + 25, draw)


def pantheon(scene, i, j):
    """Brick rotunda, stepped concrete dome and open oculus, eight-column granite portico."""
    def draw(s):
        ci, cj = i + 4.5, j + 3.1
        cylinder(s, ci, cj, 3.7, 3.7, 0, 30, BRICK, stone_courses(BRICK, 3, 10))
        for z, r in ((25, 3.9), (29, 3.8), (32, 3.6)):
            cylinder(s, ci, cj, r, r, z, 2, STONE)
        dome(s, ci, cj, 3.65, 33, 18, STONE)
        # The black ellipse is the opening, with a highlighted inner masonry rim.
        ellipse(s, ci, cj, .65, .65, 51, MARBLE['hi'])
        ellipse(s, ci, cj, .43, .43, 51.2, BRICK['deep'])
        # Portico has two rows, with all eight front columns visible under a thick pediment.
        block(s, i, j + 6, 9, 3, 3, STONE)
        block(s, i + .8, j + 5.6, 7.4, .5, 26, BRICK,
              lambda u, v, lit: WOOD if 21 < u < 36 and v < 23 else None)
        for b in (6.2, 8.6):
            for a in range(8):
                column(s, i + .5 + a * 1.14, j + b, 3, 27, STONE, width=.4)
        hip_roof(s, i - .2, j + 5.5, 9.4, 3.5, 30, 11, roof=CLAY)
        block(s, i - .2, j + 8.5, 9.4, .4, 3, STONE, z=30)
        pediment(s, i - .2, j + 8.94, 9.4, 33, 16, STONE)
        # Agrippa inscription as irregular carved glyphs within the entablature plane.
        for a in range(5, 70):
            if (a * 7) % 11 < 6:
                seg(s, P(s, i + a / 8, j + 8.95, 31), P(s, i + a / 8, j + 8.95, 32), STONE['deep'])
    scene.add(i + j + 21, draw)


def vittoriano(scene, i, j):
    """White marble terraces, great Corinthian colonnade, quadrigas and equestrian king."""
    def draw(s):
        # Continuous dressed-marble substructure supports the entire upper portico.
        courses = stone_courses(MARBLE, 5, 12)
        def relief_wall(u, v, lit):
            c = int(u) % 14
            if int(v) in (2, 5, 18, 21) or c in (0, 13):
                return MARBLE['hi' if lit else 'mid']
            if 7 < v < 15 and 3 <= c <= 10:
                return MARBLE['line'] if (c + int(v)) % 4 == 0 else MARBLE['lit' if lit else 'dark']
            return courses(u, v, lit)
        block(s, i + .7, j, 11.6, 4.5, 22, MARBLE, relief_wall)
        for step in range(9):
            inset = step * .22
            block(s, i + inset, j + inset, 13 - 2 * inset, 7 - inset, 2, MARBLE, z=step * 2)
        block(s, i + 1, j, 11, 1.4, 19, MARBLE, windows(MARBLE, 27, 9), z=19)
        for a in range(17):
            # The rear colonnade's slight bow is compressed into an isometric stepped arc.
            b = .6 * math.sin(a * math.pi / 16)
            column(s, i + 1.4 + a * .64, j + 1.7 + b, 23, 29, width=.3)
        block(s, i + .7, j + .4, 11.6, 1.8, 5, MARBLE, z=52)
        for a in (.5, 10.5):
            block(s, i + a, j, 2, 2.6, 18, MARBLE, relief_wall, z=22)
            # Open propylaea: independent giant columns and a recessed inner wall,
            # with actual sky visible between the freestanding shafts.
            block(s, i + a + .2, j + .1, 1.6, .2, 19, MARBLE, relief_wall, z=40)
            for di in (.15, .7, 1.3, 1.85):
                column(s, i + a + di, j + 2.55, 40, 20, width=.25)
            for dj in (.35, 1.1, 1.8):
                column(s, i + a + 1.85, j + dj, 40, 20, width=.25)
            block(s, i + a - .1, j, 2.2, 2.8, 3, MARBLE, z=60)
            # Each roof group has four solid horses plus Victory's raised wings.
            for b in (0, .5, 1, 1.5):
                horse(s, i + a + 1.05, j + .4 + b, 64, BRONZE, rider=False, scale=.65)
            block(s, i + a - .2, j + .5, .65, 1, 4, BRONZE, z=64)
            relief(s, i + a + .1, j + .6, 70, BRONZE, wings=True)
        block(s, i + 5.5, j + 4.2, 2, 1.5, 12, MARBLE, z=18)
        horse(s, i + 6.5, j + 5, 32, BRONZE)
        # Tomb of the Unknown Soldier, central Roma niche, eternal flames and winged groups.
        block(s, i + 5.2, j + 6.5, 2.6, .7, 5, STONE, z=2)
        relief(s, i + 6.5, j + 6.8, 8, MARBLE)
        for a in (4.8, 8.2):
            block(s, i + a, j + 6.8, .3, .3, 4, BRONZE, z=3)
            seg(s, P(s, i + a + .15, j + 6.95, 7), P(s, i + a + .15, j + 6.95, 10), CLAY['hi'], 2)
        for a in (.8, 11.8):
            relief(s, i + a, j + 6.2, 15, MARBLE, wings=True)
    scene.add(i + j + 22, draw)


def colosseum(scene, i, j):
    """Hollow elliptical amphitheatre: surviving high outer arcade, broken south rim, hypogeum."""
    def draw(s):
        ci, cj, ri, rj = i + 5.2, j + 3.7, 5.2, 3.7
        ring = []
        for n in range(72):
            a, b = n * math.tau / 72, (n + 1) * math.tau / 72
            mid = (a + b) / 2
            depth = ri * math.cos(mid) + rj * math.sin(mid)
            # The northern outer wall survives; the southern side exposes the inner tiers.
            height = 58 if depth < -1.3 else 43 if depth < .6 else 29
            ring.append((depth, n, a, b, height))
        # Back wall first, so the open interior can be seen above the low broken near rim.
        def wall(item):
            depth, n, a, b, height = item
            va, vb = (ci + ri * math.cos(a), cj + rj * math.sin(a)), (ci + ri * math.cos(b), cj + rj * math.sin(b))
            pa, pb = P(s, *va), P(s, *vb)
            lit = math.sin((a + b) / 2) - .5 * math.cos((a + b) / 2) > 0
            dx = pb[0] - pa[0]
            def color(x, y):
                t = max(0, min(1, (x - pa[0]) / dx)) if abs(dx) > .01 else .5
                v = pa[1] + t * (pb[1] - pa[1]) - y
                u = (n + t) * 2.6
                c, level = u % 9, v % 14
                tone = STONE['lit' if lit else 'dark']
                if level < 2:
                    return STONE['hi' if lit else 'line']
                if v < 43 and 2 < c < 7:
                    arch = arch_opening(c, level - 2, 4.5, 2.3, 6, STONE['deep'])
                    if arch:
                        return BRICK['deep'] if c > 3 else STONE['deep']
                if c < 1.4:
                    return STONE['hi' if lit else 'mid']  # engaged orders/pilasters
                return STONE['line' if lit else 'deep'] if int(v) % 5 == 0 else tone
            poly(s, [pa, pb, (pb[0], pb[1] - height), (pa[0], pa[1] - height)], color)
            # Thick exposed wall head, with visible radial masonry returns.
            innera = P(s, ci + (ri - .45) * math.cos(a), cj + (rj - .45) * math.sin(a), height)
            innerb = P(s, ci + (ri - .45) * math.cos(b), cj + (rj - .45) * math.sin(b), height)
            poly(s, [(pa[0], pa[1] - height), (pb[0], pb[1] - height), innerb, innera], lambda x, y: STONE['hi'])
            if n % 3 == 0:
                seg(s, innera, (pa[0], pa[1] - height), STONE['line'])
        for item in sorted(ring):
            if item[0] < 0:
                wall(item)
        # Terraced seating surrounds a genuinely open arena with the exposed basement grid.
        for r, z in ((.88, 5), (.77, 3), (.65, 1)):
            ellipse(s, ci, cj, ri * r, rj * r, z, STONE['mid'])
        ellipse(s, ci, cj, ri * .59, rj * .57, 1.2,
                lambda x, y: BRICK['deep'] if (int(x) + 2 * int(y)) % 13 < 3 or (int(x) - 2 * int(y)) % 17 < 3 else STONE['dark'])
        for item in sorted(ring):
            if item[0] >= 0:
                wall(item)
    scene.add(i + j + 17, draw)


LANDMARKS = [
    ('st-peters', st_peters), ('castel-santangelo', castel_santangelo),
    ('spanish-steps', spanish_steps), ('trevi', trevi), ('navona', navona),
    ('pantheon', pantheon), ('vittoriano', vittoriano), ('colosseum', colosseum),
]

if __name__ == '__main__':
    for name, builder in LANDMARKS:
        # St Peter's runs 15 tiles east from its dome to the colonnade, so it gets a larger plot.
        frame = dict(size=(270, 250), origin=(125, 115)) if builder is st_peters else dict(size=(250, 230), origin=(120, 110))
        print(preview([lambda s, builder=builder: builder(s, 2, 2)], f'rome-{name}', tiles=20, **frame))
    print(preview([lambda s: palazzo(s, 2, 3, 3, 3, 3, 0),
                   lambda s: palazzo(s, 7, 2, 3, 3, 4, 3),
                   lambda s: palazzo(s, 7, 7, 3, 3, 2, 5)], 'rome-houses',
                  size=(230, 200), origin=(105, 55), tiles=17))
