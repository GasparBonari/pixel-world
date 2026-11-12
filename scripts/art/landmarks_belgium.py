"""Brussels' Brabant Gothic, Belgian brick and eight landmarks in projected (i, j, z).

Run directly for individual 4× inspection plots. North-up site anchors and architectural
references are recorded in DEVELOPMENT_PLAN.md. All ornament follows its supporting face.
"""

import itertools
import math

import iso
from iso import rgb
from landmarks_paris import P, seg, poly, corners, facade, mansard, preview, GLASS
from landmarks_iberia import hip_roof, stone_courses, arch_opening, palette_of, tones
from landmarks_amsterdam import gable_roof, octagon


STONE = tones("#F6EBD6", "#DCCBAA", "#C4B18E", "#A49173", "#73624E", "#B3A080", "#493D30")
BLUE_STONE = tones("#C1C8C5", "#9AA8AB", "#818F94", "#65747D", "#44515B", "#718087", "#303D47")
BRICK = tones("#D69A7B", "#B57458", "#995E46", "#784734", "#503227", "#955A42", "#3D2923")
PALE = tones("#FFF7DF", "#E8DCBF", "#CFC1A1", "#B4A284", "#887357", "#BDAB8A", "#514430")
SLATE = tones("#A0AAB2", "#738393", "#5E6C7D", "#465362", "#303C4C", "#596879", "#26313E")
COPPER = tones("#B0C8AC", "#7DA78F", "#628974", "#416957", "#2D4A3E", "#5C806B", "#263D31")
BRONZE = tones("#A2AA7B", "#77845F", "#58694E", "#3B503E", "#283A2D", "#4F6147", "#223126")
GOLD = tones("#FFF2AF", "#EAC464", "#CCA047", "#A77B30", "#775324", "#B78D3A", "#513D22")
SILVER = tones("#F4F8F5", "#CFDBDC", "#A6BCC4", "#78929F", "#4E6372", "#91A8B2", "#354853")
WOOD = rgb("#624430")
IRON = rgb("#303C3D")
WALLS = [rgb(c) for c in ("#AA694D", "#82503D", "#C28C64", "#D9C59E", "#B88268", "#E5D6B9")]


def block(s, i, j, wi, wj, height, material=STONE, pattern=None, z=0, cap=True):
    cover = facade(s, i, j, wi, wj, height, pattern or stone_courses(material, 4, 9),
                   palette=material, z0=z)
    if cap:
        iso.fill(s, list(corners(s, i, j, wi, wj, z + height)), lambda x, y: material["mid"], cover)
    iso.outline(s, cover, material["outline"])
    return cover


def spire(s, i, j, wi, wj, base, rise, material=SLATE):
    T, R, B, L = corners(s, i, j, wi, wj, base)
    apex = P(s, i + wi / 2, j + wj / 2, base + rise)
    for pts, key in (([T, R, apex], "mid"), ([T, L, apex], "mid"),
                     ([L, B, apex], "lit"), ([B, R, apex], "dark")):
        poly(s, pts, lambda x, y, key=key: material["line"] if int(y) % 5 == 0 else material[key])
    for end in (L, B, R):
        seg(s, apex, end, material["outline"])
    seg(s, apex, L, material["hi"])


def dome(s, ci, cj, radius, base, rise, material):
    """Shaded 3D copper/gold hemisphere; its elliptical foot sits on the projected drum."""
    faces = []
    for row in range(10):
        for column in range(24):
            pts, vertices = [], []
            for rr, cc in ((row, column), (row, column + 1), (row + 1, column + 1), (row + 1, column)):
                latitude, longitude = rr * math.pi / 20, cc * math.tau / 24
                r = radius * math.cos(latitude)
                vertex = (ci + r * math.cos(longitude), cj + r * math.sin(longitude),
                          base + rise * math.sin(latitude))
                vertices.append(vertex)
                pts.append(P(s, *vertex))
            angle = (column + .5) * math.tau / 24
            light = math.sin(angle) * .8 - math.cos(angle) * .45
            key = "lit" if light > .35 else "dark" if light < -.2 else "mid"
            depth = sum(a + b + z / 8 for a, b, z in vertices) / 4
            faces.append((depth, pts, key, column, row))
    for _, pts, key, column, row in sorted(faces):
        poly(s, pts, lambda x, y, key=key: material[key])
        if column % 3 == 0:
            seg(s, pts[0], pts[3], material["line"] if key == "lit" else material["deep"])
        if row in (0, 3, 6):
            seg(s, pts[0], pts[1], material["hi"] if key == "lit" else material["line"])


def dressed_windows(material, height, bay=8, gothic=False, arcade=False):
    courses = stone_courses(material, 4, 9)
    def pattern(u, v, lit):
        c, v = int(u) % bay, int(v)
        level = v % 13
        trim = PALE["lit" if lit else "dark"]
        if v in (1, height - 2, height) or v % 13 == 0:
            return trim
        if arcade and v < 10:
            opening = arch_opening(c, v, bay / 2, 2.2, 6, material["deep"])
            if opening:
                return opening
        if 2 <= c <= bay - 2 and 3 <= level <= 10 and v < height - 3:
            head = 10 - abs(c - bay / 2) * (.85 if gothic else .15)
            if level <= head:
                if c in (2, bay - 2) or level in (3, int(head)) or c == bay // 2 or level == 6:
                    return trim
                return GLASS["mid" if lit else "dark"]
        if gothic and c == 0:
            return trim
        return courses(u, v, lit)
    return pattern


def pinnacle(s, i, j, base, height=13, material=STONE):
    block(s, i - .15, j - .15, .3, .3, height * .5, material, z=base)
    spire(s, i - .24, j - .24, .48, .48, base + height * .5, height * .5, material)


def relief(s, i, j, z, material=PALE, wings=False):
    """A filled robed figure in an i/z plane, with a shaded thickness and carved face."""
    profile = [(-.3, 0), (.3, 0), (.2, 3), (.18, 6), (.12, 7),
               (.16, 9), (-.13, 9), (-.2, 7), (-.12, 6), (-.23, 4)]
    face = [P(s, i + di, j, z + dz) for di, dz in profile]
    back = [P(s, i + di, j - .12, z + dz) for di, dz in profile]
    for a in range(len(face)):
        b = (a + 1) % len(face)
        poly(s, [back[a], back[b], face[b], face[a]], lambda x, y: material["dark"])
    poly(s, face, lambda x, y: material["lit"] if int(x) % 3 else material["mid"])
    if wings:
        for sign in (-1, 1):
            points = [(0, 5), (sign * .4, 8), (sign * .95, 9), (sign * .7, 5), (sign * .2, 3)]
            poly(s, [P(s, i + di, j, z + dz) for di, dz in points], lambda x, y: material["lit"])
            seg(s, P(s, i + sign * .2, j, z + 5), P(s, i + sign * .75, j, z + 8), material["hi"])


def pediment(s, i, j, width, base, rise, material=STONE):
    pts = [P(s, i, j, base), P(s, i + width, j, base), P(s, i + width / 2, j, base + rise)]
    poly(s, pts, lambda x, y: material["lit"] if (int(x) + int(y)) % 7 else material["mid"])
    for a, b in zip(pts, pts[1:] + pts[:1]):
        seg(s, a, b, material["hi"], 2)


def belgian_flag(s, i, j, base):
    seg(s, P(s, i, j, base), P(s, i, j, base + 13), SILVER["dark"])
    for k, c in enumerate((rgb("#30323A"), GOLD["lit"], rgb("#C75649"))):
        poly(s, [P(s, i + k * .25, j, base + 12), P(s, i + (k + 1) * .25, j, base + 12),
                 P(s, i + (k + 1) * .25, j, base + 7), P(s, i + k * .25, j, base + 7)], lambda x, y, c=c: c)


def brussels_house(scene, i, j, wi=2.5, wj=3, floors=3, seed=0, guild=False):
    """Brick/stone town house; baroque guild gables and occasional Art Nouveau iron bays."""
    wall = palette_of(WALLS[seed % len(WALLS)])
    height = floors * 10 + 3
    courses = stone_courses(wall, 3, 8)
    def pattern(u, v, lit):
        c, v = int(u) % 10, int(v)
        level = v % 10
        trim = PALE["lit" if lit else "dark"]
        if v <= 2:
            return BLUE_STONE["lit" if lit else "dark"]
        if v in (height - 1, height - 3) or guild and c == 0:
            return GOLD["lit" if lit else "dark"] if guild else trim
        if 1 <= c <= 5 and 3 <= level <= 8 and v < height - 3:
            if c in (1, 5) or level in (3, 8):
                return trim
            if v < 10:
                return WOOD if int(u) // 7 % 3 == 0 else GLASS["dark"]
            return trim if level == 6 else GLASS["mid" if lit else "dark"]
        if v >= 10 and level in (1, 2) and 1 <= c <= 5:
            return IRON if level == 1 or c % 2 else wall["dark"]
        return courses(u, v, lit)
    def draw(s):
        block(s, i, j, wi, wj, height, wall, pattern)
        if seed % 4 == 3 and not guild:
            mansard(s, i, j, wi, wj, height, 12, .5, roof=SLATE, dormers=7)
        else:
            gable_roof(s, i, j, wi, wj, height, 12, SLATE, wall,
                       ("bell", "step", "neck")[seed % 3])
        block(s, i + .2, j + .4, .35, .4, 8, BRICK, z=height + 5)
        if guild:
            # Gilded pilasters, carved cartouche, scrolls and roof finial in the gable plane.
            fj = j + wj + .15
            for a in (.2, wi - .2):
                seg(s, P(s, i + a, fj, 10), P(s, i + a, fj, height - 3), GOLD["lit"])
            for a in (.2, wi - .2):
                center = P(s, i + a, fj, height + 6)
                for t in range(18):
                    angle = t / 3
                    radius = 3 * (1 - t / 23)
                    s.put(center[0] + math.cos(angle) * radius,
                          center[1] + math.sin(angle) * radius, GOLD["hi"])
            relief(s, i + wi / 2, fj, height + 5, GOLD)
        elif seed % 7 == 0:
            # Projecting glazed bay with a curved iron balcony, a Brussels Art Nouveau accent.
            block(s, i + .55, j + wj, wi - 1, .45, 17, PALE,
                  dressed_windows(PALE, 17, 7), z=10)
            for a in range(6):
                u = (wi - 1) * a / 5
                seg(s, P(s, i + .55 + u, j + wj + .48, 10),
                    P(s, i + .55 + u, j + wj + .48, 13 + math.sin(a)), IRON)
    scene.add(i + j + wi + wj + .7, draw)


def town_hall(scene, i, j):
    """Asymmetric Gothic wings, arcades, statues, corner turrets and open octagonal spire."""
    W, D, H = 11, 4, 37
    def draw(s):
        block(s, i, j, W, D, H, STONE, dressed_windows(STONE, H, 8, True, True))
        hip_roof(s, i, j, W, D, H, 17, roof=SLATE)
        # Slate dormers and sculpted niches punctuate the long frontage.
        for a in range(1, 11):
            relief(s, i + a, j + D + .08, 24)
            if a % 2:
                block(s, i + a - .2, j + D - .6, .45, .6, 6, PALE, z=H + 3)
                spire(s, i + a - .25, j + D - .65, .55, .7, H + 9, 5, SLATE)
        for a, b in ((i, j + D), (i + W, j + D), (i, j)):
            octagon(s, a, b, .37, 28, 17, STONE, openings=True)
            spire(s, a - .5, b - .5, 1, 1, 45, 15, SLATE)
        ti, tj = i + 4.2, j + D - 1.5  # deliberately off-centre, as on the real facade
        block(s, ti, tj, 1.9, 1.9, 62, STONE, dressed_windows(STONE, 62, 7, True, True))
        for z, radius, height in ((62, .91, 15), (77, .7, 13), (90, .49, 10)):
            octagon(s, ti + .95, tj + .95, radius, z, height, STONE, openings=True)
            for di, dj in ((-1, -1), (-1, 1), (1, 1), (1, -1)):
                pinnacle(s, ti + .95 + di * radius, tj + .95 + dj * radius, z + height - 2, 7)
        spire(s, ti + .48, tj + .48, .94, .94, 100, 18, SLATE)
        relief(s, ti + .95, tj + .95, 120, GOLD, wings=True)
        # Michael's spear and a compact dragon under his feet.
        seg(s, P(s, ti + 1.4, tj + .95, 120), P(s, ti + 1.45, tj + .95, 129), GOLD["hi"])
        poly(s, [P(s, ti + u, tj + .95, z) for u, z in ((.3, 120), (.7, 122), (1.3, 121), (1.5, 119))],
             lambda x, y: GOLD["dark"])
    scene.add(i + j + W + D + 1, draw)


def kings_house(scene, i, j):
    """Maison du Roi: three traceried galleries, steep roof, pinnacles and open lantern."""
    W, D, H = 7.5, 4.3, 36
    def gallery(u, v, lit):
        c, v = int(u) % 7, int(v)
        level = v % 12
        trim = STONE["hi" if lit else "mid"]
        if v % 12 in (0, 1) or c == 0:
            return trim
        top = 11 - abs(c - 5) * .65
        if 1 <= c <= 9 and 2 <= level <= top:
            if c in (1, 9) or level == int(top) or level == 3 or c == 5 and level > 6:
                return trim
            return BLUE_STONE["deep"]
        return stone_courses(STONE, 4, 9)(u, v, lit)
    def draw(s):
        block(s, i, j, W, D, H, STONE, gallery)
        hip_roof(s, i, j, W, D, H, 19, roof=SLATE)
        for a in (.3, 1.6, 3, 4.5, 6, 7.2):
            pinnacle(s, i + a, j + D, H, 12)
            relief(s, i + a, j + D + .1, 25)
        for z in (12, 24, 36):
            block(s, i - .1, j + D - .1, W + .2, .3, 1.5, PALE, z=z, cap=False)
        # Central projecting octagonal lantern and its tall copper weather vane.
        for radius, base, height in ((.75, 34, 13), (.58, 47, 12), (.38, 59, 9)):
            octagon(s, i + 3.75, j + 2.9, radius, base, height, STONE, openings=True)
            octagon(s, i + 3.75, j + 2.9, radius + .1, base + height, 1, PALE)
        spire(s, i + 3.35, j + 2.5, .8, .8, 69, 12, SLATE)
        belgian_flag(s, i + 3.75, j + 2.9, 82)
        for a in (1.3, 5.7):
            gable_roof(s, i + a, j + D - 1.1, .9, 1.1, 41, 11, SLATE, STONE)
    scene.add(i + j + W + D + 1, draw)


def cathedral(scene, i, j):
    """Saint Michael and Saint Gudula: twin flat towers, great west window and flying buttresses."""
    W, D, H = 7.6, 9, 30
    def draw(s):
        block(s, i + .7, j, W - 1.4, D, H, STONE, dressed_windows(STONE, H, 8, True))
        gable_roof(s, i + .7, j, W - 1.4, D, H, 20, SLATE, STONE)
        for b in (j + 1, j + 3, j + 5, j + 7):
            block(s, i + W - .3, b, .55, .5, 22, STONE)
            seg(s, P(s, i + W, b + .2, 22), P(s, i + W - 1.2, b + .2, 33), PALE["lit"], 2)
            pinnacle(s, i + W, b + .2, 22, 9)
        # Broad west front. Brussels has a tall pointed window, not Notre-Dame's rose.
        fj = j + D
        def front(u, v, lit):
            if not lit:
                return dressed_windows(STONE, 36, 8, True)(u, v, lit)
            if 17 < v < 34 - abs(u - 12) * .65 and 3 < u < 21:
                return PALE["lit"] if int(u) % 4 == 0 or int(v) % 7 == 0 else GLASS["mid"]
            if v < 12:
                opening = arch_opening(u, v, 12, 4, 7, STONE["deep"])
                if opening:
                    return opening
            return stone_courses(STONE, 4, 9)(u, v, lit)
        block(s, i + 2.3, fj - .8, 3, 1.5, 39, STONE, front)
        pediment(s, i + 2.3, fj + .72, 3, 39, 12)
        for a in (i, i + W - 2.3):
            def tower_pattern(u, v, lit):
                if 44 < v < 61 and int(u) % 9 in (2, 3, 5, 6):
                    return BLUE_STONE["deep"] if int(v) % 3 else BLUE_STONE["dark"]
                return dressed_windows(STONE, 65, 9, True)(u, v, lit)
            block(s, a, fj - 2, 2.3, 2.6, 65, STONE, tower_pattern)
            # Paired dark belfry louvres, open stone parapet and four corner pinnacles.
            for z in (39, 62, 66):
                block(s, a - .08, fj - 2.08, 2.46, 2.76, 1.5, PALE, z=z, cap=z == 66)
            for di, dj in ((0, 0), (2.3, 0), (0, 2.6), (2.3, 2.6)):
                pinnacle(s, a + di, fj - 2 + dj, 67, 8)
        # Broad flight of entrance stairs.
        for step in range(4):
            block(s, i + 2, fj + .7 + step * .3, 3.6, .35, 4 - step, BLUE_STONE)
    scene.add(i + j + W + D + 3, draw)


def basilica(scene, i, j):
    """Koekelberg's Art Deco brick masses, huge green dome and paired entrance towers."""
    W, D = 8.5, 10
    def deco(u, v, lit):
        c, v = int(u) % 9, int(v)
        if v in (1, 24, 27):
            return PALE["lit" if lit else "dark"]
        if 2 <= c <= 6 and 8 <= v <= 23 - abs(c - 4) * .8:
            return PALE["lit" if lit else "dark"] if c in (2, 4, 6) or v == 8 else GLASS["dark"]
        return stone_courses(BRICK, 3, 8)(u, v, lit)
    def draw(s):
        block(s, i + 1.2, j, W - 2.4, D, 28, BRICK, deco)
        hip_roof(s, i + 1.2, j, W - 2.4, D, 28, 8, roof=COPPER)
        block(s, i - .7, j + 2.5, W + 1.4, 3.5, 27, BRICK, deco)
        hip_roof(s, i - .7, j + 2.5, W + 1.4, 3.5, 27, 8, roof=COPPER)
        for a in (i + .2, i + W - 1.8):
            block(s, a, j + D - 1.5, 1.6, 2, 48, BRICK, dressed_windows(BRICK, 48, 6))
            block(s, a - .1, j + D - 1.6, 1.8, 2.2, 3, PALE, z=48)
            hip_roof(s, a - .1, j + D - 1.6, 1.8, 2.2, 51, 5, roof=COPPER)
        block(s, i + 2.4, j + D - .5, 3.7, 1.4, 28, BRICK,
              dressed_windows(BRICK, 28, 8, False, True))
        ci, cj = i + W / 2, j + 4.5
        octagon(s, ci, cj, 2.3, 25, 21, BRICK, openings=True)
        octagon(s, ci, cj, 2.55, 46, 4, PALE)
        dome(s, ci, cj, 2.55, 50, 30, COPPER)
        # Broad segmented copper cap with a small lantern and cross.
        octagon(s, ci, cj, .38, 80, 7, PALE, openings=True)
        spire(s, ci - .45, cj - .45, .9, .9, 87, 6, COPPER)
        seg(s, P(s, ci, cj, 94), P(s, ci, cj, 103), BRONZE["lit"])
        seg(s, P(s, ci - .3, cj, 100), P(s, ci + .3, cj, 100), BRONZE["lit"])
    scene.add(i + j + W + D + 1, draw)


def royal_palace(scene, i, j):
    """Long Louis XVI frontage, central pediment, stone balustrade, pavilions and Belgian flag."""
    W, D, H = 14, 4.5, 31
    def draw(s):
        block(s, i, j, W, D, H, STONE, dressed_windows(STONE, H, 8))
        mansard(s, i, j, W, D, H, 11, .8, roof=SLATE, dormers=9)
        for a in (i, i + W - 2.4):
            block(s, a, j + D - 2.7, 2.4, 3, 36, STONE, dressed_windows(STONE, 36, 7))
            mansard(s, a, j + D - 2.7, 2.4, 3, 36, 12, .5, roof=SLATE, dormers=7)
        # Projecting central entrance block and paired Corinthian pilasters.
        ci, fj = i + 4.6, j + D + .25
        block(s, ci, fj - 1, 4.8, 1.25, 37, STONE, dressed_windows(STONE, 37, 8, False, True))
        for a in (.15, .55, 1.5, 1.9, 2.9, 3.3, 4.25, 4.65):
            block(s, ci + a, fj + .27, .12, .18, 22, PALE, z=10)
        pediment(s, ci - .2, fj + .5, 5.2, 36, 12)
        # Sculpted Belgium with seated allegories under the pediment.
        relief(s, ci + 2.5, fj + .52, 37, PALE)
        for a in (1.5, 3.5):
            poly(s, [P(s, ci + a + u, fj + .53, 38 + v) for u, v in ((-.35, 0), (.35, 0), (.25, 3), (0, 5), (-.2, 2))],
                 lambda x, y: PALE["lit"])
        for a in range(28):
            block(s, i + a * .5, j + D + .08, .13, .13, 3, PALE, z=H)
        for a in (0, W):
            relief(s, i + a, j + D, 38)
        belgian_flag(s, i + W / 2, j + 2, 47)
        # Front fence, with piers kept distinct from the facade.
        for a in range(15):
            block(s, i + a, j + D + 2.6, .18, .18, 5, BLUE_STONE)
        for z in (2, 4):
            seg(s, P(s, i, j + D + 2.6, z), P(s, i + W, j + D + 2.6, z), IRON)
    scene.add(i + j + W + D + 3, draw)


def palace_of_justice(scene, i, j):
    """Poelaert's massive terraced palace: colonnaded portico, square drum and gilded dome."""
    W, D = 12, 9
    def draw(s):
        block(s, i, j, W, D, 25, STONE, dressed_windows(STONE, 25, 9))
        for a in (0, 8.8):
            for b in (0, 5.8):
                block(s, i + a, j + b, 3.2, 3.2, 35, STONE, dressed_windows(STONE, 35, 8))
                block(s, i + a - .1, j + b - .1, 3.4, 3.4, 3, PALE, z=35)
        block(s, i + 2.7, j + 1.8, 6.6, 4.8, 53, STONE, dressed_windows(STONE, 53, 8))
        block(s, i + 2.4, j + 1.5, 7.2, 5.4, 3, PALE, z=53)
        # Entrance porch: six free columns, shaded recess and a large triangular pediment.
        block(s, i + 3.2, j + D - 1.8, 5.6, 1, 35, BLUE_STONE, dressed_windows(BLUE_STONE, 35, 8))
        for a in range(6):
            block(s, i + 3.1 + a * 1.05, j + D, .32, .4, 28, PALE, z=6)
            block(s, i + 3 + a * 1.05, j + D - .1, .52, .6, 2, PALE, z=33)
        pediment(s, i + 2.7, j + D + .5, 6.7, 36, 14)
        for step in range(5):
            block(s, i + 2.4 - step * .1, j + D + .55 + step * .32,
                  7.3 + step * .2, .4, 6 - step, BLUE_STONE)
        # The great square upper drum has vertical ribs, a balcony, then a gold cupola.
        ci, cj = i + 6, j + 4.2
        block(s, ci - 1.7, cj - 1.7, 3.4, 3.4, 25, STONE,
              dressed_windows(STONE, 25, 7), z=56)
        block(s, ci - 1.95, cj - 1.95, 3.9, 3.9, 3, PALE, z=80)
        for a in (-1.65, -.75, .35, 1.4):
            block(s, ci + a, cj + 1.72, .18, .18, 21, PALE, z=59)
        dome(s, ci, cj, 1.95, 83, 23, GOLD)
        octagon(s, ci, cj, .35, 106, 6, GOLD, openings=True)
        spire(s, ci - .4, cj - .4, .8, .8, 112, 7, GOLD)
    scene.add(i + j + W + D + 4, draw)


def horse(s, i, j, z, material=BRONZE):
    """Solid chest, head, mane, bent legs and tail, extruded along j."""
    profile = [(-.45, 2), (-.4, 6), (.05, 7), (.32, 11), (.62, 12), (.92, 10),
               (.66, 9), (.4, 7), (.35, 4), (.5, 0), (.25, 0), (.02, 3), (-.2, 4),
               (-.3, 0), (-.55, 0), (-.55, 3), (-.8, 5), (-.85, 7), (-.65, 6)]
    front = [P(s, i + a * .7, j + .12, z + h) for a, h in profile]
    back = [P(s, i + a * .7, j - .12, z + h) for a, h in profile]
    poly(s, back, lambda x, y: material["dark"])
    for k in range(len(front)):
        n = (k + 1) % len(front)
        poly(s, [back[k], back[n], front[n], front[k]], lambda x, y: material["mid"])
    poly(s, front, lambda x, y: material["lit"] if int(x) % 3 else material["mid"])
    for a, b in zip(front, front[1:] + front[:1]):
        seg(s, a, b, material["deep"])
    for di, dj in ((-.3, -.16), (.2, -.16), (-.3, .16), (.2, .16)):
        seg(s, P(s, i + di, j + dj, z + 4), P(s, i + di - .08, j + dj, z), material["dark"])
    seg(s, P(s, i + .3, j, z + 11), P(s, i + .3, j, z + 14), material["hi"])


def cinquantenaire(scene, i, j):
    """Three equal open arches, coupled columns, flanking colonnades and bronze quadriga."""
    W, D, H = 10.5, 3, 43
    def draw(s):
        # Three actual tunnels: preserve ground behind the opening, including the soffit.
        background = s.img.copy()
        def face(u, v, lit):
            if lit:
                for n in range(3):
                    center = (n + .5) * W * 8 / 3
                    if arch_opening(u, v, center, 11, 20, True) \
                            and not arch_opening(u, v, center, 9, 20, True):
                        angle = math.atan2(max(0, v - 20), u - center)
                        return STONE["line"] if int(angle * 12) % 3 == 0 else STONE["lit"]
            if int(v) in (2, 35, 38, 42):
                return STONE["lit" if lit else "dark"]
            return stone_courses(BLUE_STONE, 4, 9)(u, v, lit)
        block(s, i, j, W, D, H, BLUE_STONE, face)
        for n in range(3):
            center, half, spring = (n + .5) * W * 8 / 3, 9, 20
            start = P(s, i, j + D)
            for x, y in iso.polygon_pixels([P(s, i, j + D), P(s, i + W, j + D),
                                            P(s, i + W, j + D, H), P(s, i, j + D, H)]):
                u, v = x - start[0], start[1] + (x - start[0]) * .5 - y
                if arch_opening(u, v, center, half, spring, True):
                    color = background.getpixel((x, y))[:3] if 0 <= x < s.w and 0 <= y < s.h else BLUE_STONE["deep"]
                    # Recessed right reveal and curved stone vault.
                    if u > center + half - 4 or v > spring + math.sqrt(max(0, half * half - (u - center) ** 2)) - 3:
                        color = BLUE_STONE["deep"]
                    s.put(x, y, color)
        for a in (0, 3.3, 6.9, 10.2):
            for dx in (0, .35):
                block(s, i + a + dx, j + D + .1, .2, .4, 33, STONE, z=2)
                block(s, i + a + dx - .07, j + D, .34, .6, 3, PALE, z=34)
            relief(s, i + a + .2, j + D + .55, 7, BRONZE)
        block(s, i - .2, j - .2, W + .4, D + .4, 4, STONE, z=H)
        # Attic relief panels and continuous projecting cornices on both visible faces.
        block(s, i - .25, j - .25, W + .5, D + .5, 1, PALE, z=47)
        for a in range(1, 10):
            poly(s, [P(s, i + a + u, j + D + .22, 39 + v)
                     for u, v in ((-.3, 0), (.3, 0), (.3, 2), (0, 3), (-.3, 2))],
                 lambda x, y: STONE["lit"])
        # Curved wings approximated by short receding colonnade sections in plan.
        for side in (-1, 1):
            for k in range(3):
                a = i - 1.5 - k * 1.25 if side < 0 else i + W + .8 + k * 1.25
                b = j - .1 - k * .6
                block(s, a, b, .28, .4, 22, STONE)
                block(s, a - .2, b - .1, 1.55, .65, 3, STONE, z=22)
        ci, cj = i + W / 2, j + 1.7
        block(s, ci - 2.4, cj - .6, 4.8, 1.2, 5, BRONZE, z=47)
        for n in range(4):
            horse(s, ci - 1.8 + n * 1.2, cj + .3, 52)
        block(s, ci - .35, cj - 1.4, .7, .6, 5, BRONZE, z=52)
        for di in (-.5, .5):
            x, y = P(s, ci + di, cj - .9, 54)
            for n in range(16):
                angle = n * math.tau / 16
                s.put(x + math.cos(angle) * 2, y + math.sin(angle) * 2, BRONZE["deep"])
        relief(s, ci, cj - 1, 58, BRONZE, wings=False)
        seg(s, P(s, ci + .3, cj - 1, 64), P(s, ci + .9, cj - 1, 72), BRONZE["lit"], 2)
        # Laurel wreath held aloft by Brabant.
        x, y = P(s, ci + .9, cj - 1, 74)
        for t in range(20):
            a = t * math.tau / 20
            s.put(x + math.cos(a) * 3, y + math.sin(a) * 3, BRONZE["lit"])
    scene.add(i + j + W + D + 5, draw)


def atomium(scene, i, j):
    """Body-centred cubic cell on a body diagonal: nine steel spheres and twenty tubes."""
    ci, cj = i + 4.5, j + 4.5
    # Orthonormal basis: [1,1,1] vertical; the eight cube corners retain their true connectivity.
    vertices = list(itertools.product((-1, 1), repeat=3))
    def point(v):
        a, b, c = v
        east = (a - b) / math.sqrt(2)
        north = (a + b - 2 * c) / math.sqrt(6)
        height = (a + b + c) / math.sqrt(3)
        return ci + east * 2 + north * 2.8, cj - east * 2 + north * 2.8, 66 + height * 29
    nodes = [point(v) for v in vertices] + [(ci, cj, 66)]
    edges = [(a, b) for a in range(8) for b in range(a + 1, 8)
             if sum(x != y for x, y in zip(vertices[a], vertices[b])) == 1]
    edges += [(8, a) for a in range(8)]
    def sphere(s, node, radius=9):
        x, y = P(s, *node)
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                r = (dx * dx + dy * dy) / radius ** 2
                if r <= 1:
                    light = (-dx * .55 - dy * .55 + math.sqrt(1 - r) * radius * .6) / radius
                    key = "hi" if light > .7 else "lit" if light > .25 else "mid" if light > -.2 else "dark"
                    if r > .86:
                        key = "outline"
                    elif abs(dy - radius * .22) < .8:
                        key = "deep"  # observation glazing / horizontal steel seam
                    elif abs(dx + dy * .3) < .6:
                        key = "line"
                    s.put(x + dx, y + dy, SILVER[key])
    def draw(s):
        # Three pairs of angled steel legs support the lower outer spheres.
        for n in (1, 2, 4):
            a, b, z = nodes[n]
            for offset in (-.5, .5):
                foot = P(s, a + offset, b + .8, 0)
                seg(s, foot, P(s, a, b, z), SILVER["deep"], 2)
                seg(s, (foot[0] - 1, foot[1]), P(s, a, b, z), SILVER["lit"])
        # Connections terminate inside the spheres; the cladding covers all tube ends.
        for a, b in sorted(edges, key=lambda edge: sum(sum(nodes[n][:2]) for n in edge)):
            a, b = P(s, *nodes[a]), P(s, *nodes[b])
            seg(s, (a[0] + 1, a[1]), (b[0] + 1, b[1]), SILVER["outline"], 2)
            seg(s, a, b, SILVER["lit"], 2)
        for node in sorted(nodes, key=lambda node: sum(node[:2])):
            sphere(s, node)
        block(s, ci - 1.2, cj - .5, 2.4, 1.6, 6, SILVER,
              lambda u, v, lit: GLASS["dark"] if int(u) % 5 else SILVER["lit"])
        belgian_flag(s, ci, cj, 126)
    scene.add(i + j + 18, draw)


if __name__ == "__main__":
    for name, builder, size, origin in (
        ("town-hall", town_hall, (235, 225), (97, 90)),
        ("kings-house", kings_house, (205, 190), (95, 65)),
        ("cathedral", cathedral, (235, 225), (115, 65)),
        ("basilica", basilica, (245, 235), (120, 90)),
        ("royal-palace", royal_palace, (270, 210), (100, 60)),
        ("justice", palace_of_justice, (260, 250), (115, 105)),
        ("cinquantenaire", cinquantenaire, (280, 195), (120, 70)),
        ("atomium", atomium, (220, 230), (110, 110)),
    ):
        print(preview([lambda s, b=builder: b(s, 3, 3)], f"brussels-{name}", size=size, origin=origin, tiles=19))
    print(preview([lambda s: brussels_house(s, 3, 3, seed=0, guild=True),
                   lambda s: brussels_house(s, 6, 3, seed=2, guild=True),
                   lambda s: brussels_house(s, 9, 3, seed=7),
                   lambda s: brussels_house(s, 6, 8, floors=2, seed=3)],
                  "brussels-houses", size=(250, 200), origin=(110, 60), tiles=18))
