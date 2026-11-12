"""London's Portland stone, Gothic towers and brick terraces in true (i, j, z).

Run directly for eight individual 4× landmark plots and a terrace study. Architectural
sources and north-up site anchors are recorded in DEVELOPMENT_PLAN.md.
"""

import math

import iso
from iso import rgb
from landmarks_paris import P, seg, corners, facade, preview, GLASS
from landmarks_iberia import hip_roof, crenellate, stone_courses, arch_opening, palette_of, tones
from landmarks_amsterdam import octagon
from landmarks_belgium import dome, spire, pediment, relief


STONE = tones("#FFF6DF", "#E5D7B9", "#CDBD9D", "#AB997D", "#78684F", "#B9A78A", "#4B4032")
SAND = tones("#F4DBA7", "#D6B87E", "#BD9A65", "#94764F", "#6D5439", "#AC8A59", "#483727")
BRICK = tones("#D59475", "#AD7051", "#91583F", "#754633", "#503325", "#8F5C43", "#3B2B23")
PALE = tones("#FFFCEF", "#F0E6CF", "#D9CEB7", "#B7AB94", "#877A65", "#C1B49D", "#51483B")
SLATE = tones("#A2A8B0", "#77818D", "#606C7A", "#45515F", "#303C48", "#586573", "#26303B")
LEAD = tones("#BFC5C4", "#919D9E", "#748388", "#55666E", "#3B4D56", "#6A7A81", "#2B3941")
BLUE = tones("#B1E2EF", "#77B9D1", "#5193AE", "#37657F", "#25465F", "#4C7E97", "#20394D")
STEEL = tones("#FFFFFF", "#E1ECE6", "#B6C8C7", "#879FA3", "#566E79", "#A4B9B8", "#344D5C")
GOLD = tones("#FFF3AC", "#EDCA65", "#CCA34A", "#A87C32", "#755325", "#BA943D", "#503B21")
BRONZE = tones("#9DA88A", "#74866B", "#566C58", "#3C5143", "#293C32", "#52634E", "#243029")
IRON, WOOD, CLOCK_BLUE = rgb("#2D383B"), rgb("#62422F"), rgb("#28527A")
FLAG_RED = rgb("#C95857")
WALLS = [rgb(c) for c in ("#AD7051", "#967451", "#BE9070", "#846249", "#D7C7A6", "#B67B61")]


def block(s, i, j, wi, wj, height, material=STONE, pattern=None, z=0):
    cover = facade(s, i, j, wi, wj, height, pattern or stone_courses(material, 4, 10),
                   palette=material, z0=z)
    iso.fill(s, list(corners(s, i, j, wi, wj, z + height)), lambda x, y: material["mid"], cover)
    iso.outline(s, cover, material["outline"])
    return cover


def windows(material, height, bay=9, gothic=False):
    courses = stone_courses(material, 4, 10)
    def pattern(u, v, lit):
        c, v = int(u) % bay, int(v)
        level = v % 12
        trim = PALE["lit" if lit else "dark"]
        if v in (1, height - 2) or v % 12 == 0:
            return trim
        if 2 <= c <= bay - 2 and 3 <= level <= 10 and v < height - 3:
            head = 10 - abs(c - bay / 2) * (1 if gothic else 0)
            if level <= head:
                if c in (2, bay - 2) or level in (3, int(head)) or c == bay // 2 or level == 6:
                    return trim
                return GLASS["mid" if lit else "dark"]
        return courses(u, v, lit)
    return pattern


def pinnacle(s, i, j, base, height=10, material=SAND):
    block(s, i - .16, j - .16, .32, .32, height * .55, material, z=base)
    spire(s, i - .23, j - .23, .46, .46, base + height * .55, height * .45, material)


def cross(s, i, j, z, material=GOLD):
    block(s, i - .08, j - .08, .16, .16, 7, material, z=z)
    block(s, i - .38, j - .08, .76, .16, 1.2, material, z=z + 4)


def union_flag(s, i, j, z):
    seg(s, P(s, i, j, z), P(s, i, j, z + 15), SLATE["dark"])
    # The flag occupies a projected i/z plane, including both saltire and upright crosses.
    def flag(u, v, lit):
        if abs(v - 4) < .9 or abs(u - 5) < .9:
            return FLAG_RED
        if abs(v - 4) < 1.7 or abs(u - 5) < 1.7 or abs(v - u * .8) < 1 or abs(v + u * .8 - 8) < 1:
            return PALE["hi"]
        return CLOCK_BLUE
    facade(s, i, j, 1.25, .06, 8, flag, palette=BLUE, z0=z + 6)


def terrace(scene, i, j, wi=2.5, wj=3, floors=3, seed=0):
    """London stock/red brick: sash windows, fanlight door, iron guards and chimney pots."""
    wall = palette_of(WALLS[seed % len(WALLS)])
    height = 11 * floors + 3
    courses = stone_courses(wall, 3, 7)
    def pattern(u, v, lit):
        c, v = int(u) % 10, int(v)
        level = (v - 3) % 11
        trim = PALE["lit" if lit else "dark"]
        if v <= 2 or v in (height - 3, height - 1):
            return trim
        if 1 <= c <= 6 and 3 <= level <= 9 and v < height - 3:
            if c in (1, 6) or level in (3, 9):
                return trim
            if v < 13 and int(u) // 10 % 2 == 0:
                return GLASS["dark"] if v > 9 else WOOD if seed % 2 else CLOCK_BLUE
            return trim if level == 6 or c == 3 else GLASS["mid" if lit else "dark"]
        if v > 13 and level == 2 and 1 <= c <= 6:
            return trim  # projecting stone sill
        if v < 5 and c % 2 == 0:
            return IRON
        return courses(u, v, lit)
    def draw(s):
        block(s, i, j, wi, wj, height, wall, pattern)
        hip_roof(s, i, j, wi, wj, height, 7, roof=SLATE)
        # Georgian parapet screens part of the roof; occasional Victorian bay adds variety.
        if seed % 3:
            block(s, i, j + wj - .1, wi, .18, 3, wall, z=height)
        else:
            block(s, i + .7, j + wj, .95, .45, 17, PALE, windows(PALE, 17, 7), z=4)
            hip_roof(s, i + .6, j + wj, 1.15, .6, 21, 3, roof=SLATE)
        block(s, i + .2, j + .5, .55, .7, 10, BRICK, z=height + 1)
        for a in (.24, .54):
            block(s, i + a, j + .65, .16, .19, 4, BRICK, z=height + 11)
        if seed % 4 == 0:
            # A restrained wrought-iron first-floor guard along the lit face.
            for a in range(1, int(wi * 8), 3):
                seg(s, P(s, i + a / 8, j + wj + .12, 14),
                    P(s, i + a / 8, j + wj + .12, 17), IRON)
            seg(s, P(s, i + .2, j + wj + .12, 17), P(s, i + wi - .2, j + wj + .12, 17), IRON)
    scene.add(i + j + wi + wj + .8, draw)


def parliament(scene, i, j):
    """Riverside Gothic palace: Victoria, Central and Elizabeth towers; blue/gold clocks."""
    W, D, H = 5, 15, 29
    def draw(s):
        block(s, i, j, W, D, H, SAND, windows(SAND, H, 7, True))
        hip_roof(s, i, j, W, D, H, 10, roof=SLATE)
        for b in range(1, 15, 2):
            block(s, i + W - .18, j + b, .35, .35, 33, SAND)
            pinnacle(s, i + W, j + b, 33, 7)
        # Victoria Tower is at the southwestern end, slightly taller than Elizabeth Tower.
        tower_windows = windows(SAND, 104, 9, True)
        def victoria(u, v, lit):
            c = int(u) % 9
            if 2 <= c <= 6 and (72 < v < 89 - abs(c - 4) or 49 < v < 66 - abs(c - 4)):
                return SAND["deep"] if c != 4 else SAND["lit" if lit else "dark"]
            return tower_windows(u, v, lit)
        block(s, i, j + D - 3, 3.3, 3.3, 104, SAND, victoria)
        cover = set()
        crenellate(s, i, j + D - 3, 3.3, 3.3, 104, SAND, cover, step=4, height=3)
        for a, b in ((0, D - 3), (3.3, D - 3), (0, D + .3), (3.3, D + .3)):
            pinnacle(s, i + a, j + b, 102, 13)
        union_flag(s, i + 1.7, j + D - 1.4, 108)
        octagon(s, i + 2.5, j + 7, .75, H + 8, 18, SAND, openings=True)
        spire(s, i + 1.6, j + 6.1, 1.8, 1.8, H + 26, 29, SLATE)
        # Elizabeth Tower at the NE end, with clock patterns clipped to each wall plane.
        ti, tj, tw = i + 2.6, j - .5, 2.4
        masonry = windows(SAND, 77, 8, True)
        def clock_face(u, v, lit):
            center, cz, radius = tw * 4, 64, 6.4
            dx, dy = u - center, v - cz
            r = math.hypot(dx, dy)
            if r < radius:
                if r > radius - 1.2:
                    return GOLD["lit" if lit else "dark"]
                if abs(dx) < .75 and -1 < dy < 4 or abs(dy - .65 * dx) < .7 and -4 < dx < 1:
                    return CLOCK_BLUE
                angle = math.atan2(dy, dx)
                if r > radius - 2.3 and abs(math.sin(angle * 6)) < .3:
                    return CLOCK_BLUE
                return PALE["hi" if lit else "mid"]
            if v in (55, 73, 76):
                return GOLD["lit" if lit else "dark"]
            return masonry(u, v, lit)
        block(s, ti, tj, tw, tw, 77, SAND, clock_face)
        block(s, ti + .2, tj + .2, 2, 2, 10, SAND, windows(SAND, 10, 5, True), z=77)
        spire(s, ti - .1, tj - .1, 2.6, 2.6, 87, 18, SLATE)
        for a, b in ((0, 0), (tw, 0), (0, tw), (tw, tw)):
            pinnacle(s, ti + a, tj + b, 76, 12, GOLD)
        block(s, ti + 1, tj + 1, .4, .4, 5, GOLD, z=103)
    scene.add(i + j + W + D + .5, draw)


def westminster_abbey(scene, i, j):
    """Twin west towers, pointed portals, rose, nave, flying buttresses and Henry VII chapel."""
    W, D, H = 9, 5.5, 32
    def draw(s):
        block(s, i + 1, j + .5, W - 1, D - 1, H, STONE, windows(STONE, H, 8, True))
        hip_roof(s, i + 1, j + .5, W - 1, D - 1, H, 13, roof=LEAD)
        # Henry VII's east chapel with tall tracery windows, buttresses and a pierced parapet.
        block(s, i + W - 1, j + 1, 3.5, 3.6, 25, STONE, windows(STONE, 25, 6, True))
        hip_roof(s, i + W - 1, j + 1, 3.5, 3.6, 25, 7, roof=LEAD)
        for a in (2, 4, 6, 8, 10):
            for b in (j + .3, j + D - .3):
                block(s, i + a, b, .35, .4, 22, STONE)
                pinnacle(s, i + a + .15, b + .2, 22, 10, STONE)
                side = j + 1.3 if b < j + 1 else j + D - 1.3
                seg(s, P(s, i + a + .15, b + .2, 21), P(s, i + a + .15, side, 33), STONE["outline"], 2)
                seg(s, P(s, i + a + .15, b + .2, 23), P(s, i + a + .15, side, 35), PALE["lit"], 2)
        # A recessed portal volume connects the west towers; patterns remain face-specific.
        masonry = stone_courses(STONE)
        def west_front(u, v, lit):
            if not lit:
                center = (D - 3.2) * 4
                opening = arch_opening(u, v, center, 4, 12, STONE["deep"])
                if opening:
                    return opening
                if abs(u - center) < 4 and 19 < v < 28 - abs(u - center):
                    return PALE["mid"] if int(u) % 3 == 0 else GLASS["dark"]
            return masonry(u, v, lit)
        block(s, i + .15, j + 1.6, 1.3, D - 3.2, 33, STONE, west_front)
        # A real volume for the west front; the two towers are on its west end.
        tower_windows = windows(STONE, 55, 7, True)
        def belfry(u, v, lit):
            c = int(u) % 7
            if 1 < c < 6 and 36 < v < 49 - abs(c - 3.5):
                return STONE["deep"] if int(v) % 3 else STONE["line"]
            return tower_windows(u, v, lit)
        for b in (j, j + D - 1.6):
            block(s, i, b, 1.8, 1.8, 55, STONE, belfry)
            for a, bb in ((i, b), (i + 1.8, b), (i, b + 1.8), (i + 1.8, b + 1.8)):
                pinnacle(s, a, bb, 54, 10, STONE)
        # North transept rose and portal remain on the lit face rather than leaking onto side walls.
        def transept(u, v, lit):
            if lit:
                r = math.hypot(u - 12, v - 23)
                if r < 5:
                    return PALE["lit"] if r > 4 or abs(math.sin(math.atan2(v - 23, u - 12) * 4)) < .3 else GLASS["dark"]
                opening = arch_opening(u, v, 12, 4, 11, STONE["deep"])
                if opening:
                    return opening
            return masonry(u, v, lit)
        block(s, i + 3.5, j + D - .5, 3, 1.8, 34, STONE, transept)
        hip_roof(s, i + 3.5, j + D - .5, 3, 1.8, 34, 10, roof=LEAD)
        pediment(s, i + 3.5, j + D + 1.3, 3, 34, 10, STONE)
    scene.add(i + j + W + D + 3, draw)


def st_pauls(scene, i, j):
    """Wren's lead dome, colonnaded drum, lantern/cross and paired Baroque west towers."""
    W, D, H = 10, 5.5, 30
    def draw(s):
        block(s, i, j, W, D, H, STONE, windows(STONE, H, 9))
        hip_roof(s, i, j, W, D, H, 8, roof=LEAD)
        # Crossing drum with an open peristyle represented by paired light columns/deep recesses.
        ci, cj = i + 6.4, j + 2.7
        octagon(s, ci, cj, 2.1, H + 5, 18, STONE, openings=True)
        for n in range(24):
            angle = n * math.tau / 24
            a, b = ci + 1.98 * math.cos(angle), cj + 1.98 * math.sin(angle)
            seg(s, P(s, a, b, H + 8), P(s, a, b, H + 22), STONE["lit" if math.sin(angle) > 0 else "dark"])
        dome(s, ci, cj, 2.2, H + 23, 32, LEAD)
        octagon(s, ci, cj, .48, H + 55, 10, STONE, openings=True)
        dome(s, ci, cj, .55, H + 65, 5, LEAD)
        cross(s, ci, cj, H + 70)
        for b in (j + .1, j + D - 1.6):
            block(s, i, b, 1.7, 1.7, 44, STONE, windows(STONE, 44, 7))
            octagon(s, i + .85, b + .85, .8, 44, 9, STONE, openings=True)
            dome(s, i + .85, b + .85, .85, 53, 8, STONE)
            pinnacle(s, i + .85, b + .85, 61, 6, STONE)
        # West entrance with two column tiers and a sculpted pediment, built on the +i face.
        block(s, i + .1, j + 1.6, 1.2, D - 3.1, 29, STONE, windows(STONE, 29, 6))
        for b in range(1, 6):
            block(s, i - .4, j + b * .75, .28, .25, 23, PALE, z=4)
        # Visible south portico and broad steps give the dome a substantial architectural base.
        for k in range(4):
            block(s, i + 3.2, j + D + .2 + k * .25, 4, .3, 4 - k, STONE)
        for a in range(5):
            block(s, i + 3.4 + a * .85, j + D + .1, .28, .3, 23, PALE, z=4)
        pediment(s, i + 3.1, j + D + .4, 4.1, 28, 9, STONE)
        relief(s, i + 5.1, j + D + .42, 29, PALE)
    scene.add(i + j + W + D + 2, draw)


def buckingham_palace(scene, i, j):
    """Portland-stone east front, central balcony, pediment, balustrade and courtyard wings."""
    W, D, H = 13, 6.5, 32
    def draw(s):
        # Rear ranges leave an actual open quadrangle visible behind the front range.
        for a, b, w, d in ((i, j, W, 1.5), (i, j + 1.5, 1.8, D - 3), (i + W - 1.8, j + 1.5, 1.8, D - 3)):
            block(s, a, b, w, d, H - 3, STONE, windows(STONE, H - 3, 9))
            hip_roof(s, a, b, w, d, H - 3, 5, roof=SLATE)
        block(s, i, j + D - 1.8, W, 1.8, H, STONE, windows(STONE, H, 9))
        hip_roof(s, i, j + D - 1.8, W, 1.8, H, 4, roof=SLATE)
        for a in range(1, 13):
            block(s, i + a, j + D, .18, .25, 23, PALE, z=8)
            if a % 2:
                block(s, i + a, j + D - 1.5, .35, .4, 8, STONE, z=H)
        block(s, i + 4.6, j + D - .2, 3.8, .6, H + 3, STONE, windows(STONE, H + 3, 10))
        pediment(s, i + 4.5, j + D + .4, 4, H + 3, 7, STONE)
        block(s, i + 5, j + D + .4, 3, .65, 2, PALE, z=15)
        for a in range(12):
            block(s, i + 5 + a / 4, j + D + 1, .1, .1, 4, STONE, z=17)
        seg(s, P(s, i + 5, j + D + 1, 21), P(s, i + 8, j + D + 1, 21), STONE["hi"])
        for a in range(27):
            block(s, i + a * .5, j + D, .13, .16, 3, STONE, z=H)
        union_flag(s, i + W / 2, j + D - 1, H + 10)
        # Front gates: sparse iron uprights on dressed stone piers, with gilded finials.
        for a in (1, 4, 9, 12):
            block(s, i + a, j + D + 2.1, .6, .6, 10, STONE)
            dome(s, i + a + .3, j + D + 2.4, .28, 10, 3, GOLD)
        for a in range(12, 100, 3):
            seg(s, P(s, i + a / 8, j + D + 2.4, 1), P(s, i + a / 8, j + D + 2.4, 8), IRON)
        seg(s, P(s, i + 1, j + D + 2.4, 7), P(s, i + 12, j + D + 2.4, 7), IRON)
    scene.add(i + j + W + D + 4, draw)


def trafalgar(scene, i, j):
    """Nelson's fluted Corinthian column, filled statue, four bronze lions and two fountains."""
    def draw(s):
        ci, cj = i + 4, j + 4
        for k in range(3):
            block(s, ci - 1.5 + k * .2, cj - 1.5 + k * .2, 3 - k * .4, 3 - k * .4, 3, STONE, z=k * 3)
        block(s, ci - .65, cj - .65, 1.3, 1.3, 9, STONE, z=9)
        octagon(s, ci, cj, .4, 18, 49, STONE)
        for a in (-.25, 0, .25):
            seg(s, P(s, ci + a, cj + .35, 19), P(s, ci + a, cj + .35, 66), STONE["line"])
        block(s, ci - .7, cj - .7, 1.4, 1.4, 4, STONE, z=67)
        for a in (-.55, .55):
            dome(s, ci + a, cj + .55, .2, 68, 3, STONE)
        relief(s, ci, cj, 72, STONE)
        # Nelson's broad tricorn, epaulette and coat turn the small figure into a solid silhouette.
        block(s, ci - .25, cj - .13, .5, .26, 1.5, STONE, z=79)
        seg(s, P(s, ci - .2, cj, 75), P(s, ci + .2, cj, 77), PALE["hi"])
        # Four seated lions with solid haunches, heads, manes, paws and curling tails.
        for di, dj in ((-1.7, -1.7), (1.7, -1.7), (-1.7, 1.7), (1.7, 1.7)):
            a, b = ci + di, cj + dj
            block(s, a - .5, b - .2, 1.2, .7, 3, BRONZE, z=2)
            dome(s, a, b, .35, 5, 4, BRONZE)
            dome(s, a + .2, b + .25, .25, 8, 3, BRONZE)
            for u in (-.25, .25):
                block(s, a + u, b + .3, .16, .6, 2, BRONZE, z=2)
            seg(s, P(s, a - .5, b, 3), P(s, a - .7, b + .5, 4), BRONZE["lit"])
        for di, dj in ((-3.2, -1), (2.6, -2.5)):
            a, b = ci + di, cj + dj
            octagon(s, a, b, 1.3, 0, 2, STONE)
            octagon(s, a, b, 1.05, 2, 1, BLUE)
            octagon(s, a, b, .2, 3, 7, BRONZE)
            octagon(s, a, b, .6, 9, 1, BRONZE)
            for n in range(6):
                t = n * math.tau / 6
                seg(s, P(s, a, b, 11), P(s, a + math.cos(t) * .8, b + math.sin(t) * .8, 4), STEEL["lit"])
    scene.add(i + j + 17, draw)


def tower_of_london(scene, i, j):
    """White Tower's four turret roofs, Norman paired windows and battlemented curtain."""
    W, D = 8.5, 7
    def draw(s):
        masonry = stone_courses(STONE, 4, 9)
        block(s, i, j, W, .6, 15, STONE)
        block(s, i, j, .6, D, 15, STONE)
        block(s, i + 2, j + 1.5, 4.8, 3.8, 42, PALE, windows(PALE, 42, 9))
        hip_roof(s, i + 2, j + 1.5, 4.8, 3.8, 42, 5, roof=LEAD)
        for a, b, round_turret in ((2, 1.5, True), (6.8, 1.5, False), (2, 5.3, False), (6.8, 5.3, False)):
            if round_turret:
                octagon(s, i + a, j + b, .55, 36, 15, PALE, openings=True)
            else:
                block(s, i + a - .45, j + b - .45, .9, .9, 15, PALE, windows(PALE, 15, 5), z=36)
            spire(s, i + a - .7, j + b - .7, 1.4, 1.4, 51, 10, LEAD)
            seg(s, P(s, i + a, j + b, 61), P(s, i + a + .5, j + b, 64), GOLD["dark"])
        # Front curtain and gate; the tall keep remains exposed above it.
        def gate(u, v, lit):
            opening = arch_opening(u, v, W * 4, 3, 8, WOOD) if lit else None
            return opening or masonry(u, v, lit)
        block(s, i, j + D - .7, W, .7, 15, STONE, gate)
        block(s, i + W - .7, j, .7, D, 15, STONE)
        for a, b, w, d in ((0, 0, W, .6), (0, D - .7, W, .7), (W - .7, 0, .7, D)):
            crenellate(s, i + a, j + b, w, d, 15, STONE, set(), step=4)
        for a, b in ((0, 0), (W, 0), (0, D), (W, D)):
            octagon(s, i + a, j + b, .65, 0, 22, STONE, openings=True)
            spire(s, i + a - .8, j + b - .8, 1.6, 1.6, 22, 8, SLATE)
        union_flag(s, i + 4.4, j + 3.3, 49)
    scene.add(i + j + W + D + 2, draw)


def tower_bridge(scene, i, j):
    """Two Gothic towers, twin high-level walkways, blue suspension and closed bascules along +j."""
    W, D = 2.8, 15
    def draw(s):
        for b in (j + 2.7, j + 9.7):
            block(s, i - .65, b, W + 1.3, 2.6, 5, STONE)
        block(s, i, j, W, D, 2, SLATE, z=5)
        # Both banks' suspended approach spans. Members stay in their two vertical j/z planes.
        for a in (i, i + W):
            for b0, b1 in ((j, j + 3), (j + 12, j + D)):
                for n in range(13):
                    b = b0 + (b1 - b0) * n / 12
                    z = 10 + 30 * ((b - b0) / (b1 - b0) if b0 == j else (b1 - b) / (b1 - b0)) ** 2
                    if n:
                        seg(s, old, P(s, a, b, z), BLUE["lit"], 2)
                    old = P(s, a, b, z)
                    if n % 3 == 0:
                        seg(s, P(s, a, b, 8), old, BLUE["mid"])
        for b in (j + 3, j + 10):
            masonry = windows(STONE, 42, 7, True)
            def tower_openings(u, v, lit):
                if lit:
                    opening = arch_opening(u, v, (W + .7) * 4, 6, 14, SLATE["deep"])
                    if opening:
                        return opening
                return masonry(u, v, lit)
            block(s, i - .35, b, W + .7, 2, 42, STONE, tower_openings)
            block(s, i - .6, b - .25, W + 1.2, 2.5, 4, PALE, z=38)
            hip_roof(s, i - .35, b, W + .7, 2, 42, 11, roof=SLATE)
            for a, bb in ((i - .35, b), (i + W + .35, b), (i - .35, b + 2), (i + W + .35, b + 2)):
                block(s, a - .2, bb - .2, .4, .4, 12, STONE, z=36)
                spire(s, a - .35, bb - .35, .7, .7, 48, 9, SLATE)
        # Two separate high walkways, open underneath, rather than an opaque central wall.
        for a in (i + .15, i + W - .5):
            block(s, a, j + 5, .35, 5, 4, BLUE, z=36)
            for b in range(5, 10):
                seg(s, P(s, a + .36, j + b, 36), P(s, a + .36, j + b + 1, 40), STEEL["lit"])
        # Bascule join and road markings, then a delicate blue parapet.
        seg(s, P(s, i, j + 7.5, 7), P(s, i + W, j + 7.5, 7), IRON)
        for b in range(1, 15, 2):
            seg(s, P(s, i + W / 2, j + b, 7), P(s, i + W / 2, j + b + .6, 7), PALE["lit"])
        for a in (i, i + W):
            seg(s, P(s, a, j, 10), P(s, a, j + D, 10), BLUE["lit"])
            for b in range(16):
                seg(s, P(s, a, j + b, 7), P(s, a, j + b, 10), BLUE["dark"])
    scene.add(i + j + W + D + 1, draw)


def london_eye(scene, i, j):
    """Cantilevered wheel in a vertical 3D plane: twin rims, tension spokes, 32 glazed pods."""
    def draw(s):
        ci, cj, cz, radius = i + 4, j + 4, 64, 52
        def point(t, back=0, r=radius):
            u = math.cos(t) * r * .72
            return P(s, ci + u / 16, cj - u / 16 + back, cz + math.sin(t) * r)
        block(s, ci - 1.5, cj - .7, 3, 1.4, 5, STONE)
        hub = P(s, ci, cj, cz)
        for a, b in ((ci - 1.5, cj), (ci + 1.4, cj + 1.6)):
            seg(s, P(s, a, b, 4), hub, STEEL["outline"], 2)
            seg(s, P(s, a + .15, b, 4), hub, STEEL["lit"], 2)
        for back, key in ((-.24, "dark"), (0, "lit")):
            for n in range(192):
                t, tt = n * math.tau / 192, (n + 1) * math.tau / 192
                seg(s, point(t, back), point(tt, back), STEEL[key])
        for n in range(32):
            t = n * math.tau / 32
            seg(s, hub, point(t, r=radius - 1), STEEL["mid"])
        # Glazed capsules are small three-dimensional boxes, sorted by physical depth.
        for n in sorted(range(32), key=lambda n: -math.cos(n * math.tau / 32)):
            t = n * math.tau / 32
            u = math.cos(t) * (radius + 3) * .72
            a, b, z = ci + u / 16, cj - u / 16, cz + math.sin(t) * (radius + 3)
            block(s, a - .13, b - .13, .27, .3, 3, STEEL,
                  lambda u, v, lit: GLASS["mid" if lit else "dark"] if 1 < v < 3 else STEEL["lit"], z=z - 1.5)
        octagon(s, ci, cj, .3, cz - 3, 6, STEEL)
    scene.add(i + j + 16, draw)


if __name__ == "__main__":
    for name, builder, size, origin in (
        ("parliament", parliament, (250, 255), (145, 80)),
        ("abbey", westminster_abbey, (250, 215), (95, 65)),
        ("st-pauls", st_pauls, (260, 240), (100, 95)),
        ("buckingham", buckingham_palace, (285, 225), (100, 60)),
        ("trafalgar", trafalgar, (225, 220), (110, 90)),
        ("tower", tower_of_london, (255, 220), (120, 65)),
        ("tower-bridge", tower_bridge, (250, 245), (155, 65)),
        ("eye", london_eye, (210, 255), (105, 105)),
    ):
        print(preview([lambda s, b=builder: b(s, 3, 3)], f"london-{name}", size=size, origin=origin, tiles=20))
    print(preview([lambda s: terrace(s, 3, 3, seed=0), lambda s: terrace(s, 6, 3, seed=1),
                   lambda s: terrace(s, 9, 3, seed=4), lambda s: terrace(s, 6, 8, floors=2, seed=3)],
                  "london-houses", size=(240, 195), origin=(110, 60), tiles=18))
