"""Vaduz landmark studies and Rhine-valley houses in projected (i, j, z)."""
import math

import iso
from iso import h01, rgb, shade
from landmarks_amsterdam import gable_roof
from landmarks_denmark import clock, spire
from landmarks_iberia import arch_opening, crenellate, hip_roof, palette_of, stone_courses, tones
from landmarks_italy import cylinder
from landmarks_paris import GLASS, P, corners, poly, preview, seg
from landmarks_slovakia import band, block
from landmarks_slovenia import revolve, slab

STONE = tones('#E8E3CF', '#CBC6AC', '#B7B298', '#95937F', '#646555', '#AEA98F', '#484B3F')
WHITE = tones('#FFFAE7', '#EAE3CB', '#D6CEB5', '#B8B097', '#79735F', '#CEC4AA', '#514B3B')
RED = tones('#DA8368', '#B75442', '#A74539', '#843833', '#5B2B27', '#963D33', '#4C2824')
CLAY = tones('#D29D7D', '#A86B52', '#915943', '#704637', '#52352E', '#8F5747', '#432B25')
SLATE = tones('#A7A7A2', '#777873', '#62635F', '#4C4C49', '#373932', '#646660', '#30332E')
TIMBER = tones('#AF9072', '#896B53', '#735641', '#574334', '#3F3027', '#765A45', '#392D24')
SAND = tones('#F8E6AF', '#E8D3A1', '#D5BC89', '#B59A71', '#78654F', '#CBB385', '#5D503E')
BRICK = tones('#ECCE82', '#D2A858', '#BE944E', '#987040', '#6A492D', '#BA904F', '#533B2A')
BASALT = tones('#8C918C', '#555956', '#474B49', '#333837', '#252A2A', '#606561', '#262D2D')
ZINC = tones('#BFC1AD', '#9A9F94', '#7D837C', '#626B66', '#434C49', '#858C84', '#46524D')
WALLS = [rgb(c) for c in ('#E5D9B8', '#F1E9D1', '#CAB393', '#D6D9C0', '#D9BEA7', '#C4CDC9')]
SHUTTERS = [rgb(c) for c in ('#44614F', '#4F665E', '#6F473A', '#5D5440')]
GOLD = rgb('#E4BA62')
RECESS = rgb('#302E2C')


def pane(u, v, centre, bottom, top, half, lit, trim=WHITE, pointed=False, shutters=None):
    """Set a dressed sill, masonry frame and divided glass into a wall plane."""
    du, level = abs(u-centre), int(v-bottom)
    peak = top-bottom - (du*.82 if pointed else 0)
    if level == 0 and du <= half+1:
        return trim['hi' if lit else 'mid']
    if 1 <= level <= peak and du <= half:
        if du >= half-1 or level >= peak-1:
            return trim['hi' if lit else 'mid']
        if du < .6:
            return GLASS['frame']
        return GLASS['mid' if lit and level > 2 else 'dark']
    if shutters and half < du <= half+1.7 and 2 <= level < peak:
        return shade(shutters, .2 if lit and level % 3 == 0 else -.15 if not lit else 0)
    return None


def sill_roof(s, i, j, w, d, z, rise, roof, wall, *, along_i=False, stepped=False, skylight=False):
    """Textured gable whose ridge may run along either tile axis."""
    t, r, b, l = corners(s, i, j, w, d, z)
    if along_i:
        a, c = P(s, i, j+d/2, z+rise), P(s, i+w, j+d/2, z+rise)
        slopes = ((t, r, c, a), (l, b, c, a))
        gables = ((i, j, False), (i+w, j, True))
    else:
        a, c = P(s, i+w/2, j, z+rise), P(s, i+w/2, j+d, z+rise)
        slopes = ((r, b, c, a), (t, l, c, a))
        gables = ((i, j, False), (i, j+d, True))

    def face(start_i, start_j, near):
        def point(u, v):
            return P(s, start_i if along_i else start_i+w*u,
                     start_j+d*u if along_i else start_j, z+rise*v)

        if stepped:
            profile = ((0, 0), (0, .31), (.14, .31), (.14, .55), (.28, .55), (.28, .81),
                       (.42, .81), (.42, 1.12), (.58, 1.12), (.58, .81), (.72, .81),
                       (.72, .55), (.86, .55), (.86, .31), (1, .31), (1, 0))
        else:
            profile = ((0, 0), (.5, 1), (1, 0))
        points = [point(u, v) for u, v in profile]
        foot = point(1 if along_i else 0, 0)
        width = (d if along_i else w)*8
        lit = not along_i and near
        course = stone_courses(wall, 4, 9)

        def plaster(x, y):
            u = x-foot[0]
            v = foot[1]+u*(-.5 if along_i else .5)-y
            return ((pane(u, v, width/2, 3, 11, 3, lit) if stepped and near else None)
                    or course(u, v, lit) or wall['lit' if lit else 'dark'])

        poly(s, points, plaster)
        for p, q in zip(points, points[1:]):
            seg(s, p, q, wall['hi' if stepped and near else 'line' if near else 'outline'])

    face(*gables[0])
    for (e0, e1, p1, p0), lit in zip(slopes, (False, True)):
        tone = roof['lit' if lit else 'dark']
        slope = (e1[1]-e0[1])/(e1[0]-e0[0])

        def tile(x, y):
            row = round(y-e0[1]-(x-e0[0])*slope)
            if row % 4 == 0:
                return shade(tone, -.15)
            return shade(tone, .14) if (x+2*(row//4)) % 7 == 0 else tone

        poly(s, [e0, e1, p1, p0], tile)
        seg(s, e0, e1, roof['outline'])
    face(*gables[1])
    seg(s, a, c, roof['hi'])
    if skylight:
        k = .17
        end_a, end_c = slopes[1][:2]
        for n in range(1, 10):
            q0, q1 = n/11, (n+.76)/11
            ridge = [(a[0]+(c[0]-a[0])*q, a[1]+(c[1]-a[1])*q) for q in (q0, q1)]
            eave = [(end_a[0]+(end_c[0]-end_a[0])*q, end_a[1]+(end_c[1]-end_a[1])*q)
                    for q in (q0, q1)]
            edge = [(p[0]+(e[0]-p[0])*k, p[1]+(e[1]-p[1])*k) for p, e in zip(ridge, eave)]
            poly(s, ridge+edge[::-1], lambda x, y: GLASS['dark'] if (x+y) % 3 else GLASS['mid'])


def townhouse(scene, i, j, floors, seed, z=0):
    """Alpine plaster over a stone plinth, deep eaves, shutters and timber galleries."""
    w, d = (3.2 if seed % 6 else 3.75), 3.05
    h = 11*floors+4
    wall = palette_of(WALLS[seed % len(WALLS)])
    shutter = SHUTTERS[(seed//7) % len(SHUTTERS)]
    roof = SLATE if seed % 5 == 0 else CLAY

    def front(u, v, lit):
        bay = 6 if u < 12 else 18
        trim = WHITE['hi' if lit else 'mid']
        if v < 2 or int(v) in (h-1, h-3):
            return STONE['mid' if lit else 'dark']
        if 2 <= v <= 10 and lit and bay == 6 and abs(u-bay) < 3.3:
            if abs(u-bay) >= 2.2 or v >= 9:
                return trim
            return TIMBER['deep'] if int(u) % 2 else TIMBER['dark']
        if v < 10:
            return pane(u, v, bay, 3, 9, 3.5, lit)
        level = (int(v)-11) % 11
        return pane(u, level, bay, 2, 9, 3, lit, shutters=shutter)

    def draw(s):
        block(s, i, j, w, d, h, wall, front, z=z)
        band(s, i, j, w, d, z+h-2, TIMBER)
        sill_roof(s, i-.18, j-.18, w+.36, d+.36, z+h, 11+(seed % 3), roof, wall, along_i=seed % 4 == 0)
        block(s, i+.52, j+1.1, .44, .48, 9, STONE, z=z+h+3)
        band(s, i+.52, j+1.1, .44, .48, z+h+11, STONE)
        if floors == 2 and seed % 3 != 1:
            # Deep boards over two diagonal brackets and a spaced balustrade.
            a, b = i+.25, j+d
            band(s, a, b, w-.5, .37, z+12, TIMBER, 2)
            for q in (.36, w-.86):
                seg(s, P(s, a+q, b+.37, z+12), P(s, a+q, b, z+8), TIMBER['deep'])
            for k in range(7):
                x = a+.06+k*(w-.62)/6
                seg(s, P(s, x, b+.36, z+14), P(s, x, b+.36, z+18), TIMBER['deep'])
            seg(s, P(s, a, b+.36, z+18), P(s, a+w-.5, b+.36, z+18), TIMBER['hi'])

    scene.add(i+j+w+d, draw)


def red_house(scene, i, j, z=0):
    """The dark-red stepped house, central stone tower and eastern winepress barn."""
    courses = stone_courses(STONE, 4, 8)

    def tower(u, v, lit):
        if v >= 30:
            if int(u) % 5 == 0 or int(v) in (31, 35, 40):
                return TIMBER['lit' if lit else 'dark']
            return pane(u, v, 9, 32, 39, 3, lit)
        return (pane(u, v, 9, 5+9*(int(v)//9), 12+9*(int(v)//9), 3, lit)
                or courses(u, v, lit))

    def house(u, v, lit):
        if v < 3:
            return courses(u, v, lit) or STONE['dark']
        return pane(u, (v-3) % 12, 4+9*(int(u)//9), 3, 10, 3, lit, shutters=SHUTTERS[0])

    def draw(s):
        # East barn behind the tower and on its right in the valley view.
        block(s, i+1.5, j, 3.3, 3.05, 16, WHITE, house, z=z)
        sill_roof(s, i+1.4, j-.08, 3.5, 3.21, z+16, 11, CLAY, WHITE, along_i=True)
        block(s, i+1.2, j+2.7, 2.45, 2.45, 42, STONE, tower, z=z)
        block(s, i+1.2, j+2.7, 2.45, 2.45, 13, WHITE, tower_plaster, z=z+30)
        band(s, i+1.15, j+2.65, 2.55, 2.55, z+41, TIMBER, 2)
        # A broken pitch, with a steep upper pyramid above the flared eaves.
        t, r, b, l = corners(s, i+1.02, j+2.52, 2.81, 2.81, z+43)
        ti, ri, bi, li = corners(s, i+1.49, j+2.99, 1.87, 1.87, z+49)
        for a, c, d, e, key in ((t, r, ri, ti, 'mid'), (t, l, li, ti, 'lit'),
                               (l, b, bi, li, 'lit'), (b, r, ri, bi, 'dark')):
            poly(s, [a, c, d, e], lambda x, y: CLAY['line'] if (x+y)%5 == 0 else CLAY[key])
            seg(s, a, c, CLAY['outline'])
        hip_roof(s, i+1.49, j+2.99, 1.87, 1.87, z+49, 22, CLAY)

        block(s, i+.35, j+4.55, 3.7, 3.55, 23, RED, house, z=z)
        band(s, i+.35, j+4.55, 3.7, 3.55, z+2, STONE)
        sill_roof(s, i+.35, j+4.55, 3.7, 3.55, z+23, 18, CLAY, RED, along_i=True, stepped=True)

    def tower_plaster(u, v, lit):
        return tower(u, v+30, lit)

    scene.add(i+j+12.1, draw)


def kunstmuseum(scene, i, j, z=0):
    """The polished basalt/river-pebble monolith between two levels of the town."""
    w, d, h = 4.75, 11.35, 34

    def polished(u, v, lit):
        ix, iy = int(u), int(v)
        if (not lit and 11 < u < 72 and 2 <= v < 10) or (lit and 6 < u < 29 and 3 <= v < 8):
            if ix % 8 == 0 or iy in (3, 9):
                return BASALT['deep']
            if (ix+iy*2) % 19 < 3:
                return rgb('#829292')
            return rgb('#677B7C') if lit else rgb('#485A5C')
        if iy in (0, 1):
            return BASALT['outline']
        if iy == h-2:
            return BASALT['line' if lit else 'mid']
        stone = BASALT['lit' if lit else 'dark']
        fleck = h01(ix, iy, 322)
        if fleck < .12:
            return shade(stone, .20 if fleck < .045 else -.16)
        reflection = .09*math.cos(u/13)+.047*math.cos((u+v*.6)/4)
        return shade(stone, reflection)

    def draw(s):
        block(s, i, j, w, d, h, BASALT, polished, z=z)
        poly(s, list(corners(s, i+.12, j+.12, w-.24, d-.24, z+h+.25)),
             lambda x, y: shade(BASALT['mid'], .07 if h01(x, y, 323) < .11 else 0))
        _, r, b, l = corners(s, i, j, w, d, z+h)
        seg(s, l, b, BASALT['hi'])
        seg(s, b, r, BASALT['line'])
        # Thin sill and frame set into the continuous south band.
        seg(s, P(s, i+w, j+d-1.45, z+2), P(s, i+w, j+2.4, z+2), BASALT['line'])

    scene.add(i+j+w+d, draw)


def vaduz_castle(scene, i, j, z=0):
    """Eastern square keep, north and south roundels and plaster ranges around the court."""
    masonry = stone_courses(STONE, 4, 9)
    pale_courses = stone_courses(WHITE, 6, 13)

    def range_wall(u, v, lit):
        level = int(v) % 10
        return (pane(u, level, 5+11*(int(u)//11), 3, 9, 3, lit)
                or (WHITE['mid' if lit else 'line'] if v < 2 else None)
                or (pale_courses(u, v, lit) if v < 7 else None))

    def keep_wall(u, v, lit):
        if v > 26:
            return (pane(u, v, 10, 33, 40, 4, lit, STONE)
                    or (STONE['mid'] if int(u) % 9 < 2 else None) or masonry(u, v, lit))
        return pane(u, v, 10, 16, 24, 2, lit, STONE) or masonry(u, v, lit)

    def barrel(u, v, lit):
        if 5 < v < 10 and int(u) % 18 in (7, 8):
            return STONE['deep']
        if v > 19:
            return TIMBER['deep'] if int(u) % 6 == 0 or int(v) in (20, 25) else WHITE['lit' if lit else 'dark']
        return masonry(u, v, lit)

    def roundel(s, a, b, radius, h):
        cylinder(s, a, b, radius, radius, z, h, STONE, barrel)
        cylinder(s, a, b, radius+.1, radius+.1, z+h-1.6, 1.6, TIMBER)
        revolve(s, a, b, radius+.23, z+h, 11, [(0, 1), (.43, .7), (1, .08)], CLAY, ribs=6)
        cylinder(s, a, b, .13, .13, z+h+10, 2, CLAY)

    def draw(s):
        # The north roundel sits behind both ranges; the other anchors the south end.
        roundel(s, i+3.05, j+2.07, 2, 24)
        iso.fill(s, list(corners(s, i+3.3, j+3.2, 5.5, 4.15, z)),
                 lambda x, y: STONE['hi'] if h01(x, y, 325) < .12 else STONE['mid'])
        block(s, i+2.85, j+2.78, 6.1, 1.55, 17, WHITE, range_wall, z=z)
        hip_roof(s, i+2.74, j+2.67, 6.32, 1.77, z+17, 9, CLAY)

        # The eastern keep has no ornamental spire: its tent rises above the court ranges.
        a, b = i+6.15, j+1.72
        block(s, a, b, 3.1, 3.05, 49, STONE, keep_wall, z=z)
        band(s, a, b, 3.1, 3.05, z+46, WHITE, 2)
        hip_roof(s, a-.16, b-.16, 3.42, 3.37, z+49, 23, CLAY)

        block(s, i+2.85, j+6.05, 8.2, 2.25, 26, WHITE, range_wall, z=z)
        sill_roof(s, i+2.73, j+5.94, 8.42, 2.51, z+26, 13, CLAY, WHITE, along_i=True)
        for di in (4.8, 6.45):
            block(s, i+di, j+7.35, .57, .61, 5, WHITE, range_wall, z=z+29)
            sill_roof(s, i+di-.06, j+7.3, .69, .73, z+34, 4, CLAY, WHITE)
        block(s, i+9.65, j+4.58, 2.26, 3.44, 28, WHITE, range_wall, z=z)
        gable_roof(s, i+9.58, j+4.48, 2.43, 3.64, z+28, 13, CLAY, WHITE)
        for di, dj, base in ((4.05, 6.55, 33), (8.15, 6.6, 33), (8.02, 3.35, 22)):
            block(s, i+di, j+dj, .45, .45, 6, WHITE, z=z+base)
            band(s, i+di, j+dj, .45, .45, z+base+5, CLAY)

        # Southwest entry and a low crenellated outer curtain on the valley side.
        def gate(u, v, lit):
            return arch_opening(u, v, 14, 5, 7, STONE['deep']) or masonry(u, v, lit)

        cover = block(s, i+4.2, j+8.3, 6.25, .7, 13, STONE, gate, z=z)
        crenellate(s, i+4.2, j+8.3, 6.25, .7, z+13, STONE, cover, step=8, height=3)
        roundel(s, i+12.25, j+6.13, 2.25, 31)

    scene.add(i+j+22, draw)


def landtag(scene, i, j, z=0):
    """High House in yellow clinker, glass link and the lower, elongated Long House."""
    def brick(u, v, lit):
        row = int(v)//3
        if int(v) % 3 == 0 or (int(u)+row*3) % 7 == 0:
            return BRICK['line' if lit else 'deep']
        return BRICK['hi' if lit else 'mid'] if h01(int(u)//3, int(v), 326) < .14 else None

    def long_wall(u, v, lit):
        if 5 <= int(v) % 10 < 9 and 3 < u < (44 if lit else 27):
            return BRICK['deep'] if int(u)%6 == 0 else rgb('#6E7770')
        return brick(u, v, lit)

    def glazing(u, v, lit):
        if int(u) % 5 == 0 or int(v) % 5 == 0:
            return BRICK['deep']
        return rgb('#B79B63') if int(v) < 9 else GLASS['dark' if lit else 'frame']

    def high_wall(u, v, lit):
        if lit and 2.8 < u < 31.5:
            if 0 <= v < 12 or 22 < v < 30:
                return glazing(u, v, lit)
            if int(v) in (12, 13, 21, 30):
                return BRICK['hi']
        return brick(u, v, lit)

    def draw(s):
        block(s, i+3.45, j, 6.3, 3.05, 25, BRICK, long_wall, z=z)
        band(s, i+3.45, j, 6.3, 3.05, z+25, BRICK, 2)
        poly(s, list(corners(s, i+3.62, j+.17, 5.96, 2.71, z+25.6)),
             lambda x, y: BRICK['mid'] if (x+y)%7 else BRICK['line'])
        block(s, i+3.6, j+2.66, 2.85, 1.8, 24, ZINC, glazing, z=z)
        band(s, i+3.6, j+2.66, 2.85, 1.8, z+24, BRICK)
        block(s, i, j+2.8, 4.35, 4.15, 37, BRICK, high_wall, z=z)
        sill_roof(s, i, j+2.8, 4.35, 4.15, z+37, 33, BRICK, BRICK, skylight=True)

    scene.add(i+j+16.7, draw)


def government_building(scene, i, j, z=0):
    """The eleven-bay Renaissance Revival front, central balcony and corner pavilions."""
    w, d, h, bay = 10.25, 5.05, 38, 7.45

    def facade_window(u, v, lit):
        width = w*8 if lit else d*8
        centres = 11 if lit else 5
        module = width/centres
        centre = module*(math.floor(u/module)+.5)
        a = abs(u-centre)
        trim = SAND['hi' if lit else 'mid']
        if v <= 3 or int(v) in (13, 25, 35, 37):
            return trim if int(v)%2 else SAND['line']
        if v < 13:
            return (arch_opening(u, v-3, centre, 2.1, 5.3, RECESS)
                    or (trim if a < 3 and v < 11 else SAND['line'] if int(v)%3 == 0 else None))
        if 16 <= v <= 33:
            base = 15 if v < 25 else 26
            if int(v) in (base+1, base+8) and a < 3.6:
                return trim
            return pane(u, v, centre, base+1, base+8, 2.65, lit, SAND)
        return None

    def centre_front(u, v, lit):
        if not lit:
            return facade_window(u, v, False)
        centre = bay*(math.floor(u/bay)+.5)
        trim = SAND['hi']
        if v < 15:
            portal = arch_opening(u, v, bay*1.5, 3.5, 8, RECESS)
            if portal:
                return portal
        if 22 < v < 37:
            return (arch_opening(u, v-23, centre, 2.5, 7, RECESS)
                    or (trim if abs(u-centre) < 3.4 else None))
        if 37 <= v <= 41 and abs(u-bay*1.5) < 3.5:
            return rgb('#726F69') if v < 39 else rgb('#8D785D')
        if int(v) in (15, 21, 37) or int(u)%7 == 0:
            return trim
        return pane(u, v, centre, 15, 22, 2.9, True, SAND)

    def draw(s):
        block(s, i, j, w, d, h, SAND, facade_window, z=z)
        band(s, i, j, w, d, z+h-1, SAND, 2)
        length, width, base = w+.24, d+.22, z+h+1
        a, b = i-.12, j-.11
        hip_roof(s, a, b, length, width, base, 12, CLAY)
        _, _, corner, eave = corners(s, a, b, length, width, base)
        ridge_a = P(s, a+width/2, b+width/2, base+12)
        ridge_b = P(s, a+length-width/2, b+width/2, base+12)

        # Olive-glazed tiles alternate with the clay in shallow chevrons on the long slope.
        glazed = rgb('#777759')
        for x, y in iso.polygon_pixels([eave, corner, ridge_b, ridge_a]):
            row = round(y-eave[1]-(x-eave[0])*.5)
            zigzag = abs((int(x-row*.7) % 24)-12)//3
            if (-row//3-zigzag) % 8 in (3, 4):
                s.put(x, y, shade(glazed, -.13 if row%3 == 0 else .06))
        seg(s, ridge_a, ridge_b, CLAY['hi'])
        seg(s, eave, corner, CLAY['outline'])
        for offset in (0, 8.02):
            x = i+offset
            block(s, x, j+2.9, 2.22, 2.23, h+3, SAND, facade_window, z=z)
            band(s, x, j+2.9, 2.22, 2.23, z+h+1, WHITE, 1.5)
            hip_roof(s, x-.09, j+2.81, 2.4, 2.42, z+h+3, 16, CLAY)
            seg(s, P(s, x+1.11, j+4.02, z+h+19), P(s, x+2.31, j+5.23, z+h+3), CLAY['hi'])
        a = i+3.73
        block(s, a, j+3.62, 2.79, 1.9, h+6, SAND, centre_front, z=z)
        sill_roof(s, a-.12, j+3.48, 3.03, 2.18, z+h+6, 13, CLAY, SAND)
        band(s, a-.09, j+5.5, 2.95, .53, z+13, SAND, 2)
        for n in range(9):
            x = a+n*.34
            seg(s, P(s, x, j+5.98, z+15), P(s, x, j+5.98, z+19), SAND['hi'])
        seg(s, P(s, a-.05, j+5.98, z+19), P(s, a+2.84, j+5.98, z+19), SAND['lit'])
        for n in range(3):
            band(s, a+.58-n*.08, j+5.47+.2*n, 1.64+n*.16, .38, z+3-n, STONE)

    scene.add(i+j+w+d+.6, draw)


def st_florin(scene, i, j, z=0):
    """A west tower with one needle spire, three aisles and the eastern polygonal apse."""
    joints = stone_courses(STONE, 5, 9)
    w, d = 5.6, 11.2

    def aisle(u, v, lit):
        width = w*8 if lit else 65.6
        bay = width/(4 if lit else 6)
        c = bay*(int(u/bay)+.5)
        if int(v) in (1, 19, 21):
            return STONE['hi' if lit else 'mid']
        return pane(u, v, c, 4, 19, 3.8, lit, STONE, pointed=True) or joints(u, v, lit)

    def shaft(u, v, lit):
        c = 10.5
        if lit and 0 <= v < 17 and abs(u-c) < 5:
            if v < 14-1.7*abs(u-c) and abs(u-c) < 3.7:
                return TIMBER['deep']
            if v < 17-1.4*abs(u-c):
                return STONE['hi']
        if 45 < v < 62:
            for centre in (5, 16):
                distance = abs(u-centre)
                top = 61-distance*1.2
                if distance < 3.2 and 47 <= v <= top:
                    if distance > 2.3 or v > top-1:
                        return STONE['hi' if lit else 'mid']
                    return SLATE['lit'] if int(v) % 3 == 0 else SLATE['deep']
        if int(v) in (2, 18, 33, 45, 64):
            return STONE['hi' if lit else 'mid']
        return pane(u, v, c, 22, 31, 2.7, lit, STONE, pointed=True) or joints(u, v, lit)

    def draw(s):
        apse = [(i+1.15, j+.65), (i+1.92, j), (i+3.75, j), (i+4.45, j+.69),
                (i+4.45, j+2.57), (i+1.15, j+2.57)]
        slab(s, apse, z, z+24, STONE, aisle)
        hip_roof(s, i+1.13, j+.27, 3.35, 3, z+24, 11, SLATE)
        block(s, i+.77, j+1.25, 4.06, 7.55, 32, STONE, aisle, z=z)
        sill_roof(s, i+.67, j+1.12, 4.26, 7.8, z+32, 18, SLATE, STONE)
        # The south aisle and sloping buttresses sit forward of the nave roof.
        block(s, i+4.21, j+1.04, 1.37, 8.2, 21, STONE, aisle, z=z)
        poly(s, [P(s, i+4.16, j+.93, z+28), P(s, i+4.16, j+9.34, z+28),
                 P(s, i+w+.09, j+9.34, z+21), P(s, i+w+.09, j+.93, z+21)],
             lambda x, y: SLATE['line'] if (y+x//2)%4 == 0 else SLATE['dark'])
        for b in (1.31, 2.81, 4.31, 5.81, 7.31, 8.81):
            block(s, i+w-.09, j+b, .37, .24, 12, STONE, z=z)
            hip_roof(s, i+w-.1, j+b-.02, .39, .28, z+12, 5, STONE)

        # Low sacristy outside the choir on its south side.
        block(s, i+4.55, j+.7, 1.32, 2.13, 13, STONE, aisle, z=z)
        hip_roof(s, i+4.47, j+.62, 1.48, 2.29, z+13, 5, SLATE)

        a, b = i+1.48, j+8.55
        block(s, a, b, 2.64, 2.65, 65, STONE, shaft, z=z)
        # Two stair arms from the ends of the raised western landing.
        band(s, a+.79, b+2.64, 1.06, .52, z+2.6, STONE, 1.2)
        for n in range(3):
            for x in (a+.24+n*.18, a+2.22-n*.18):
                band(s, x, b+2.72, .19, .42, z+n, STONE)
        clock(s, a+1.32, b+2.65, 3.9, z+39)
        clock(s, a+2.64, b+1.32, 3.9, z+39, False)
        band(s, a, b, 2.64, 2.65, z+63, STONE, 2)
        for u, v in ((.18, .18), (2.46, .18), (.18, 2.46), (2.46, 2.46)):
            cylinder(s, a+u, b+v, .16, .16, z+65, 3, STONE)
            revolve(s, a+u, b+v, .21, z+68, 6, [(0, 1), (1, .08)], SLATE, ribs=0, segments=8)
        spire(s, a+1.32, b+1.32, 1.28, z+65, 35, SLATE, conical=True)
        seg(s, P(s, a+1.32, b+1.32, z+102), P(s, a+1.32, b+1.32, z+107), GOLD)
        seg(s, P(s, a+1.08, b+1.32, z+105), P(s, a+1.56, b+1.32, z+105), GOLD)

    scene.add(i+j+w+d, draw)


def old_rhine_bridge(scene, i, j, z=0):
    """Five piers and two abutments carry one continuous covered timber passage."""
    w, d, deck, h = 1.65, 13, z+14, 12

    def boards(u, v, lit):
        if not lit:
            if v < 2 or v >= h-2:
                return TIMBER['line']
            if v > 7 and 2 < int(u) % 17 < 5:
                return TIMBER['deep']
            return TIMBER['lit' if int(u)%3 == 0 else 'line' if int(u)%3 == 1 else 'mid']
        return TIMBER['lit']

    def draw(s):
        for k, offset in enumerate((1.85, 4.15, 6.5, 8.8, 11.1)):
            b = j+offset
            base = z+(2 if k in (0, 4) else -3)
            block(s, i+.11, b-.18, w-.2, .37, deck-base-3, STONE, z=base)
            band(s, i+.11, b-.18, w-.2, .37, deck-3, TIMBER, 2)
            for a in (i+.21, i+w-.42):
                seg(s, P(s, a, b-.49, deck-1), P(s, a, b, deck-7), TIMBER['deep'])
                seg(s, P(s, a, b, deck-7), P(s, a, b+.49, deck-1), TIMBER['hi'])
        for b in (j, j+d-.4):
            block(s, i-.06, b, w+.12, .4, 9, STONE, z=z+4)
        # The open SW portal shows the boards running into the dark passage.
        poly(s, list(corners(s, i, j, w, d, deck)), lambda x, y: TIMBER['mid'])
        for k in range(1, 8):
            a = i+w*k/8
            seg(s, P(s, a, j, deck), P(s, a, j+d, deck), TIMBER['deep'])
        poly(s, [P(s, i, j, deck), P(s, i, j+d, deck),
                 P(s, i, j+d, deck+h), P(s, i, j, deck+h)], lambda x, y: TIMBER['deep'])
        t, r, b, _ = corners(s, i, j, w, d, deck)
        poly(s, [r, b, (b[0], b[1]-h), (r[0], r[1]-h)],
             lambda x, y: boards(x-b[0], b[1]-(x-b[0])*.5-y, False))
        for a in (i+.06, i+w-.1):
            seg(s, P(s, a, j+d, deck), P(s, a, j+d, deck+h), TIMBER['hi'], 2)
            far = i+w*.5
            seg(s, P(s, a, j+d, deck+h-5), P(s, (a+far)/2, j+d, deck+h), TIMBER['mid'])
        sill_roof(s, i-.13, j-.12, w+.26, d+.24, deck+h, 6, SLATE, TIMBER)
        seg(s, P(s, i-.02, j+d+.03, deck), P(s, i+w, j+d+.03, deck), TIMBER['hi'])

    scene.add(i+j+w+d, draw)


def main():
    keys = ('red-house', 'kunstmuseum', 'castle', 'landtag', 'government', 'st-florin', 'rhine-bridge')
    for key, (_, builder, (w, d), _, _, _) in zip(keys, SITES):
        # Origin leaves headroom for the cathedral spire and enough ground beyond every footprint.
        print(preview([lambda s: builder(s, 5, 5)], f'vaduz-{key}', size=(250, 244),
                      origin=(125-round((w-d)*3), 88), tiles=20))
    print(preview([lambda s, k=k, seed=seed: townhouse(s, 2.5+k*3.9, 9-k*2.4, 1+k%2, seed)
                   for k, seed in enumerate((3, 12, 5, 6))], 'vaduz-houses',
                  size=(292, 178), origin=(92, 38), tiles=23))


# name, builder, (width, depth), (longitude, latitude), screen ground anchor, elevation
SITES = [
    ('Red House', red_house, (4.85, 8.2), (9.52182, 47.14480), (300, 131), 12),
    ('Kunstmuseum', kunstmuseum, (4.75, 11.35), (9.52211, 47.13950), (365, 207), 0),
    ('Vaduz Castle', vaduz_castle, (14.8, 9.2), (9.52434, 47.13951), (580, 223), 49),
    ('Landtag', landtag, (9.75, 6.95), (9.52286, 47.13766), (503, 313), 0),
    ('Government Building', government_building, (10.25, 6.0), (9.52274, 47.13711), (378, 349), 0),
    ('Cathedral of St Florin', st_florin, (6.0, 11.25), (9.52276, 47.13622), (482, 451), 0),
    ('Old Rhine Bridge', old_rhine_bridge, (1.65, 13), (9.51168, 47.13246), (165, 462), 0),
]

if __name__ == '__main__':
    main()
