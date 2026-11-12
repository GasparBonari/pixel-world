"""Dublin's Georgian brick, limestone and eight landmarks in projected (i, j, z).

Run for eight individual 4× plots and a Georgian house study. Site anchors and
architectural references are recorded in DEVELOPMENT_PLAN.md. No bitmap sources.
"""
import math

import iso
from iso import rgb
from landmarks_paris import P, seg, poly, corners, facade, preview, GLASS
from landmarks_iberia import hip_roof, crenellate, stone_courses, arch_opening, palette_of, tones
from landmarks_amsterdam import octagon
from landmarks_belgium import dome, spire, pediment

STONE = tones('#E8E7DC', '#C7CAC0', '#ADB4AB', '#88958F', '#596761', '#939F96', '#37483F')
PORTLAND = tones('#FFF8E5', '#E9DFC6', '#D1C5AA', '#B0A38B', '#7B705C', '#BBAF95', '#4B4235')
GRANITE = tones('#F1EEE2', '#D5D1C3', '#BAB9AD', '#969D95', '#65736B', '#A4AA9E', '#3D4A41')
SLATE = tones('#ABB7BD', '#7D8D96', '#627580', '#465C68', '#304450', '#586C76', '#283942')
COPPER = tones('#BDD1B4', '#8CAF98', '#6D947E', '#507563', '#345443', '#658B73', '#2A4034')
BRICK = tones('#DEA98B', '#AF765A', '#975C43', '#784833', '#513323', '#8D5840', '#3F2D21')
PALE = tones('#FFF9E8', '#EBE2CA', '#D6CAB0', '#B5AA91', '#82765F', '#C2B59B', '#534A38')
IRON, WOOD = rgb('#293D39'), rgb('#624735')
LAMP_GLASS = rgb('#E6D9AB')
DOORS = [rgb(c) for c in ('#3A6957', '#8F453D', '#31566A', '#C4A14E', '#373F42')]
WALLS = [rgb(c) for c in ('#AC7054', '#915F49', '#BB8868', '#9E795B', '#CAB38C', '#A16A54')]


def block(s, i, j, wi, wj, height, material=STONE, pattern=None, z=0):
    cover = facade(s, i, j, wi, wj, height, pattern or stone_courses(material, 4, 9), palette=material, z0=z)
    iso.fill(s, list(corners(s, i, j, wi, wj, z + height)), lambda x, y: material['mid'], cover)
    iso.outline(s, cover, material['outline'])
    return cover


def windows(material, height, bay=9, gothic=False):
    courses = stone_courses(material, 4, 10)
    def pattern(u, v, lit):
        c, v = int(u) % bay, int(v)
        level = v % 13
        trim = PALE['lit' if lit else 'dark']
        if v in (1, height - 2) or v % 13 == 0:
            return trim
        head = 11 - abs(c - bay / 2) * (1.1 if gothic else 0)
        if 2 <= c <= bay - 2 and 3 <= level <= head and v < height - 3:
            if c in (2, bay - 2, bay // 2) or level in (3, 7, int(head)):
                return trim
            return GLASS['mid' if lit else 'dark']
        return courses(u, v, lit)
    return pattern


def gothic_windows(material, height, bay=9, belfry=False):
    courses = stone_courses(material, 4, 9)
    def pattern(u, v, lit):
        c, v = int(u) % bay, int(v)
        trim = GRANITE['lit' if lit else 'dark']
        bottom = height - 19 if belfry else 7
        head = height - 4 - abs(c - bay / 2) * 1.4
        if v in (2, height - 2) or c == 0:
            return trim
        if 2 <= c <= bay - 2 and bottom <= v <= head:
            if c in (2, bay - 2, bay // 2) or v in (bottom, int(head)):
                return trim
            if belfry:
                return material['deep'] if v % 3 else material['line']
            return GLASS['dark'] if v < height / 2 else GLASS['mid'] if (c + v) % 4 else COPPER['mid']
        return courses(u, v, lit)
    return pattern


def relief(s, i, j, z, material=PORTLAND):
    """Filled roof sculpture: head, shoulders, bent arms and a draped, shaded body."""
    profile = [(-.3, 0), (.3, 0), (.25, 2), (.16, 5), (.4, 4), (.55, 6),
               (.4, 6.5), (.22, 5.8), (.16, 7), (.21, 7.5), (.2, 9),
               (-.15, 9.3), (-.26, 8.6), (-.22, 7), (-.35, 6), (-.5, 4), (-.33, 3)]
    front = [P(s, i + a, j, z + b) for a, b in profile]
    back = [P(s, i + a, j - .2, z + b) for a, b in profile]
    for n in range(len(front)):
        poly(s, [back[n - 1], front[n - 1], front[n], back[n]], lambda x, y: material['dark'])
    poly(s, front, lambda x, y: material['lit'])
    seg(s, P(s, i - .1, j, z + 1), P(s, i + .06, j, z + 5), material['line'])
    seg(s, P(s, i + .2, j, z + 7.5), P(s, i + .2, j, z + 8.5), material['deep'])


def round_tower(s, ci, cj, radius, height):
    """Twenty-sided masonry cylinder, projected horizontal courses and sparse framed windows."""
    ring = [(ci + radius * math.cos(n * math.tau / 20), cj + radius * math.sin(n * math.tau / 20)) for n in range(20)]
    for n in sorted(range(20), key=lambda n: sum(ring[n - 1]) + sum(ring[n])):
        a, b = ring[n - 1], ring[n]
        light = math.sin(n * math.tau / 20) - .45 * math.cos(n * math.tau / 20)
        key = 'lit' if light > .4 else 'dark' if light < -.2 else 'mid'
        pa, pb = P(s, *a), P(s, *b)
        slope = (pb[1] - pa[1]) / (pb[0] - pa[0] or .001)
        def color(x, y, pa=pa, slope=slope, key=key, n=n):
            v = pa[1] + (x - pa[0]) * slope - y
            if n in (3, 7) and (12 < v < 19 or 28 < v < 35):
                return PALE['mid'] if int(v) in (13, 18, 29, 34) else STONE['deep']
            if int(v) % 4 == 0 or (int(x) + int(v) // 4 * 3) % 9 == 0:
                return STONE['line' if key == 'lit' else 'deep']
            return STONE[key]
        poly(s, [pa, pb, P(s, *b, height), P(s, *a, height)], color)
    poly(s, [P(s, *a, height) for a in ring], lambda x, y: STONE['mid'])
    for n in range(16):
        angle = n * math.tau / 16
        a, b = ci + radius * math.cos(angle), cj + radius * math.sin(angle)
        block(s, a - .15, b - .15, .3, .3, 3, STONE, z=height - 2)
    for n in range(12):
        angle = n * math.tau / 12
        a, b = ci + radius * math.cos(angle), cj + radius * math.sin(angle)
        block(s, a - .18, b - .18, .36, .36, 5, STONE, z=height)


def column(s, i, j, base, height, material=PORTLAND, width=.45):
    block(s, i - width / 2, j - width / 2, width, width, height, material,
          lambda u, v, lit: material['line' if lit else 'deep'] if int(u) % 3 == 0 else None, z=base)
    for z in (base, base + height - 2):
        block(s, i - width * .7, j - width * .7, width * 1.4, width * 1.4, 2, material, z=z)


def balustrade(s, i, j, width, base, material=PORTLAND):
    for a in range(0, int(width * 8), 4):
        block(s, i + a / 8, j, .17, .2, 3, material, z=base)
    block(s, i, j, width, .25, 1.5, material, z=base + 3)


def flag(s, i, j, z):
    seg(s, P(s, i, j, z), P(s, i, j, z + 17), IRON)
    for k, color in enumerate((rgb('#478A64'), PALE['hi'], rgb('#E6A05D'))):
        poly(s, [P(s, i + k * .35, j, z + 16), P(s, i + (k + 1) * .35, j, z + 16),
                 P(s, i + (k + 1) * .35, j, z + 9), P(s, i + k * .35, j, z + 9)], lambda x, y, c=color: c)


def georgian_house(scene, i, j, wi=2.5, wj=3, floors=3, seed=0):
    """Dublin brick terrace: tall sashes, coloured door and radial fanlight, basement rails."""
    wall, height = palette_of(WALLS[seed % len(WALLS)]), floors * 12 + 3
    courses = stone_courses(wall, 3, 8)
    def pattern(u, v, lit):
        c, v = int(u) % 10, int(v)
        level = (v - 3) % 12
        trim = PALE['lit' if lit else 'dark']
        if v <= 2:
            return STONE['dark' if lit else 'deep']
        if v in (height - 3, height - 1):
            return trim
        if v < 14 and lit and int(u) // 10 == 0:
            fan = math.hypot(u - 4, v - 10)
            if 10 <= v <= 13 and fan <= 3:
                return trim if fan > 2.2 or abs(u - 4) < .65 or abs(v - 10 - abs(u - 4)) < .6 else GLASS['mid']
            if 1 <= c <= 7 and v < 11:
                if c in (1, 7) or v == 10:
                    return trim
                if v == 4 and c == 5:
                    return PORTLAND['hi']
                return DOORS[seed % len(DOORS)]
        if 1 <= c <= 6 and 3 <= level <= 10 and v < height - 4:
            if c in (1, 6) or level in (3, 7, 10) or c == 3:
                return trim
            return GLASS['mid' if lit else 'dark']
        if v > 14 and level == 2 and 0 <= c <= 7:
            return trim
        return courses(u, v, lit)
    def draw(s):
        block(s, i, j, wi, wj, height, wall, pattern)
        hip_roof(s, i, j, wi, wj, height, 6, roof=SLATE)
        block(s, i, j + wj - .12, wi, .23, 3, wall, z=height)
        # Stone entrance steps and thin iron basement guards, rather than French balconies.
        for step in range(3):
            block(s, i + .12, j + wj + .2 * step, .8, .25, 3 - step, GRANITE)
        for a in range(9, int(wi * 8), 3):
            seg(s, P(s, i + a / 8, j + wj + .55, 1), P(s, i + a / 8, j + wj + .55, 6), IRON)
        seg(s, P(s, i + 1.05, j + wj + .55, 6), P(s, i + wi, j + wj + .55, 6), IRON)
        block(s, i + .2, j + .4, .65, .75, 9, BRICK, z=height + 1)
        for a in (.27, .6):
            block(s, i + a, j + .55, .18, .2, 3, BRICK, z=height + 10)
        if seed % 5 == 0:
            # Occasional former shop: a glazed bay and restrained green canopy.
            block(s, i + 1.25, j + wj, .95, .25, 10, PALE, windows(PALE, 10, 7))
            hip_roof(s, i + 1.2, j + wj, 1.1, .4, 10, 2, roof=COPPER)
    scene.add(i + j + wi + wj + .9, draw)


def four_courts(scene, i, j):
    """Copper rotunda and Corinthian portico, low symmetrical wings and roof sculptures."""
    def draw(s):
        block(s, i, j, 12, 5, 25, GRANITE, windows(GRANITE, 25))
        hip_roof(s, i, j, 12, 5, 25, 7, roof=SLATE)
        for a in (0, 9):
            block(s, i + a, j + 2, 3, 4, 28, PORTLAND, windows(PORTLAND, 28, 8))
            balustrade(s, i + a, j + 6, 3, 28)
        octagon(s, i + 6, j + 2.6, 2.3, 27, 18, PORTLAND, openings=True)
        # Detached columns around the drum; dome rises behind the river-front portico.
        for n in range(12):
            angle = n * math.tau / 12
            column(s, i + 6 + 2.25 * math.cos(angle), j + 2.6 + 2.25 * math.sin(angle), 28, 17, width=.22)
        dome(s, i + 6, j + 2.6, 2.45, 46, 20, COPPER)
        block(s, i + 3.1, j + 5, 5.8, 1.7, 3, GRANITE)
        for a in (3.4, 4.45, 5.5, 6.5, 7.55, 8.6):
            column(s, i + a, j + 6.1, 3, 22)
        block(s, i + 3, j + 5.4, 6, 1.2, 4, PORTLAND, z=25)
        pediment(s, i + 3, j + 6.6, 6, 29, 10, PORTLAND)
        for a, z in ((3.2, 30), (6, 40), (8.8, 30)):
            relief(s, i + a, j + 6.5, z, PORTLAND)
    scene.add(i + j + 20, draw)


def custom_house(scene, i, j):
    """Long Gandon frontage, river-head keystones, central drum/dome and Commerce figure."""
    def draw(s):
        H, W = 26, 14
        regular = windows(PORTLAND, H, 9)
        def river_heads(u, v, lit):
            c = int(u) % 9
            if lit and 10 <= v <= 13 and 3 <= c <= 5:
                return PORTLAND['hi'] if c == 3 else PORTLAND['dark'] if v == 11 else PORTLAND['mid']
            return regular(u, v, lit)
        block(s, i, j, W, 5, H, PORTLAND, river_heads)
        hip_roof(s, i, j, W, 5, H, 8, roof=SLATE)
        for a in (0, 11):
            block(s, i + a, j + 1, 3, 4.5, 30, PORTLAND, windows(PORTLAND, 30, 8))
            balustrade(s, i + a, j + 5.5, 3, 30)
            for da in (.4, 2.4):
                relief(s, i + a + da, j + 5.5, 35, PORTLAND)
        # The rebuilt stone drum is darker than the pale Portland-stone wings.
        octagon(s, i + 7, j + 2, 1.8, 29, 21, STONE, openings=True)
        for a in (-1, 0, 1):
            column(s, i + 7 + a, j + 3.7, 30, 19, STONE, width=.24)
        dome(s, i + 7, j + 2, 2, 50, 18, COPPER)
        octagon(s, i + 7, j + 2, .45, 68, 4, STONE)
        relief(s, i + 7, j + 2, 72, PORTLAND)
        # Four-column Doric river portico and its sculpted tympanum.
        for a in (4.7, 6.2, 7.8, 9.3):
            column(s, i + a, j + 6, 1, 23, width=.5)
        block(s, i + 4.3, j + 5.3, 5.4, 1, 4, PORTLAND, z=24)
        pediment(s, i + 4.3, j + 6.3, 5.4, 28, 9, PORTLAND)
        relief(s, i + 7, j + 6.25, 29, PORTLAND)
        balustrade(s, i, j + 5, 4.2, 27)
        balustrade(s, i + 9.8, j + 5, 4.2, 27)
    scene.add(i + j + 21, draw)


def gpo(scene, i, j):
    """Granite GPO: exactly six Ionic columns, pediment, Hibernia/Mercury/Fidelity and tricolour."""
    def draw(s):
        block(s, i, j, 12, 5, 34, GRANITE, windows(GRANITE, 34, 9))
        hip_roof(s, i, j, 12, 5, 34, 6, roof=SLATE)
        balustrade(s, i, j + 5, 12, 35, GRANITE)
        block(s, i + 2.8, j + 5.1, 6.4, 1.5, 2, GRANITE)
        for a in (3.1, 4.25, 5.4, 6.6, 7.75, 8.9):
            column(s, i + a, j + 6.25, 2, 25, PORTLAND, width=.48)
            # Ionic scroll capitals project on both sides of each fluted shaft.
            for side in (-.3, .3):
                octagon(s, i + a + side, j + 6.25, .13, 25, 2.2, PORTLAND)
        block(s, i + 2.7, j + 5.5, 6.6, 1, 4, PORTLAND, z=27)
        pediment(s, i + 2.7, j + 6.5, 6.6, 31, 11, PORTLAND)
        for a, z in ((2.9, 32), (6, 43), (9.1, 32)):
            relief(s, i + a, j + 6.5, z, PORTLAND)
        flag(s, i + 6, j + 2, 41)
    scene.add(i + j + 20, draw)


def cathedral_body(s, i, j, wi, wj, height):
    block(s, i, j, wi, wj, height, STONE, gothic_windows(STONE, height, 9))
    roof_box = iso.Box(s, i, j, wi, wj, height)
    roof_box.gable_roof(SLATE['mid'], STONE['lit'], set(), rise=15)
    for a in range(1, int(wi), 2):
        block(s, i + a, j + wj, .35, .55, height - 4, STONE)
        spire(s, i + a - .05, j + wj, .45, .55, height - 4, 6, STONE)


def christ_church(scene, i, j):
    """Cruciform cathedral, broad crossing belfry, steep roof and enclosed Synod Hall bridge."""
    def draw(s):
        cathedral_body(s, i, j, 11, 4, 32)
        cathedral_body(s, i + 5.8, j - 1.2, 2.8, 6.4, 30)
        block(s, i + 5.4, j + .2, 3.4, 3.4, 23, STONE, gothic_windows(STONE, 23, 10, belfry=True), z=35)
        hip_roof(s, i + 5.3, j + .1, 3.6, 3.6, 58, 15, roof=SLATE)
        for a, b in ((5.4, .2), (8.8, .2), (5.4, 3.6), (8.8, 3.6)):
            block(s, i + a - .15, j + b - .15, .3, .3, 6, STONE, z=56)
            spire(s, i + a - .25, j + b - .25, .5, .5, 62, 5, SLATE)
        # West gable, recessed Romanesque portal, and paired corner turrets.
        def portal(u, v, lit):
            if not lit:
                opening = arch_opening(u, v, 16, 4, 9, STONE['deep'])
                if opening:return opening
            return gothic_windows(STONE, 32, 11)(u, v, lit)
        block(s, i, j, 1.3, 4, 32, STONE, portal)
        for b in (.2, 3.8):
            octagon(s, i + .4, j + b, .5, 0, 39, STONE)
            octagon(s, i + .4, j + b, .6, 39, 9, SLATE, roof=True)
        # The roofed bridge genuinely spans open roadway on a curved masonry arch.
        for a in (-3.4, -.6):
            block(s, i + a, j + 3.3, .65, 1.4, 16, STONE)
        for n in range(16):
            a = -2.8 + n * 2.2 / 15
            z = 7 + 6 * math.sqrt(max(0, 1 - ((a + 1.7) / 1.1) ** 2))
            block(s, i + a, j + 3.3, .18, 1.4, 2, STONE, z=z)
        block(s, i - 3.4, j + 3.3, 3.4, 1.4, 10, STONE, windows(STONE, 10, 5, True), z=16)
        hip_roof(s, i - 3.4, j + 3.3, 3.4, 1.4, 26, 5, roof=SLATE)
    scene.add(i + j + 20, draw)


def st_patricks(scene, i, j):
    """Long buttressed nave, transepts, east Lady Chapel and Minot's northwest tower/spire."""
    def draw(s):
        cathedral_body(s, i + 1, j + .5, 10, 4.5, 35)
        cathedral_body(s, i + 6, j - 1, 2.5, 7, 32)
        cathedral_body(s, i + 11, j + 1.3, 3.2, 2.8, 24)
        tower_windows = gothic_windows(STONE, 68, 10, belfry=True)
        def tower_pattern(u, v, lit):
            c = int(u) % 8
            if 50 < v < 63 and 2 <= c <= 6:
                return STONE['deep'] if c != 4 else STONE['mid']
            # Copper west clock, clipped to the shaded west-facing wall.
            r = math.hypot(u - 10, v - 40)
            if not lit and r < 4:
                if r > 3.2:return PORTLAND['lit']
                return PALE['lit'] if abs(u - 10) < .6 or abs(v - 40) < .6 else COPPER['deep']
            return tower_windows(u, v, lit)
        block(s, i, j, 2.5, 2.5, 68, STONE, tower_pattern)
        crenellate(s, i, j, 2.5, 2.5, 68, STONE, set(), step=4, height=3)
        octagon(s, i + 1.25, j + 1.25, 1.2, 69, 34, GRANITE, roof=True)
        for a, b in ((0, 0), (2.5, 0), (0, 2.5), (2.5, 2.5)):
            spire(s, i + a - .2, j + b - .2, .4, .4, 69, 7, STONE)
    scene.add(i + j + 22, draw)


def dublin_castle(scene, i, j):
    """Georgian Upper Yard and Bedford Tower, round medieval Record Tower and Chapel Royal."""
    def draw(s):
        brick_windows = windows(BRICK, 30, 8)
        for a, b, w, d in ((0, 0, 11, 2), (0, 2, 2, 5.5), (2, 6, 5.5, 1.5)):
            block(s, i + a, j + b, w, d, 30, BRICK, brick_windows)
            hip_roof(s, i + a, j + b, w, d, 30, 7, roof=SLATE)
        # Clock-faced Bedford Tower in the north range.
        def clock(u, v, lit):
            r = math.hypot(u - 8, v - 12)
            if r <= 3.3:
                return IRON if r > 2.6 or abs(u - 8) < .6 or abs(v - 12) < .6 else PALE['hi']
            return windows(PORTLAND, 20, 8)(u, v, lit)
        block(s, i + 4.5, j, 2, 2, 20, PORTLAND, clock, z=30)
        octagon(s, i + 5.5, j + 1, .75, 50, 9, PORTLAND, openings=True)
        dome(s, i + 5.5, j + 1, .85, 59, 7, COPPER)
        flag(s, i + 5.5, j + 1, 67)
        # Medieval round volume, shaded facet by facet and topped by individual merlons.
        round_tower(s, i + 8.5, j + 6.4, 1.7, 42)
        # Perpendicular Gothic Chapel Royal east of the Record Tower.
        block(s, i + 10.4, j + 3, 3.2, 4.8, 27, STONE, gothic_windows(STONE, 27, 7))
        hip_roof(s, i + 10.4, j + 3, 3.2, 4.8, 27, 10, roof=SLATE)
        for b in (3, 4.5, 6, 7.6):
            block(s, i + 13.6, j + b, .3, .4, 31, STONE)
            spire(s, i + 13.5, j + b - .1, .5, .6, 31, 5, STONE)
        # Carved heads, at a coarse but visible 2×2-pixel scale beneath the chapel cornice.
        for b in (3.5, 5, 6.5):
            block(s, i + 13.65, j + b, .25, .25, 2, PORTLAND, z=23)
    scene.add(i + j + 24, draw)


def trinity(scene, i, j):
    """Front Square setting with an open Campanile arch, four figures, belfry and copper cap."""
    def draw(s):
        for a, b, w, d in ((0, 0, 11, 1.8), (0, 1.8, 1.8, 7)):
            block(s, i + a, j + b, w, d, 22, GRANITE, windows(GRANITE, 22, 8))
            hip_roof(s, i + a, j + b, w, d, 22, 7, roof=SLATE)
        ci, cj = i + 6.5, j + 5
        block(s, ci - 1.7, cj - 1.7, 3.4, 3.4, 3, GRANITE)
        # Four independent piers leave the two axis-aligned passages genuinely open.
        for a, b in ((-1.3, -1.3), (.7, -1.3), (-1.3, .7), (.7, .7)):
            block(s, ci + a, cj + b, .6, .6, 23, GRANITE)
        for n in range(15):
            t = -1 + n / 7
            z = 12 + 8 * math.sqrt(max(0, 1 - t * t))
            block(s, ci + t, cj + 1, .18, .6, 3, GRANITE, z=z)
            block(s, ci + 1, cj + t, .6, .18, 3, GRANITE, z=z)
        block(s, ci - 1.4, cj - 1.4, 2.8, 2.8, 5, PORTLAND, z=23)
        octagon(s, ci, cj, 1.15, 28, 23, PORTLAND, openings=True)
        for a, b in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
            relief(s, ci + a * 1.2, cj + b * 1.2, 28, PORTLAND)
        dome(s, ci, cj, 1.35, 51, 13, GRANITE)
        octagon(s, ci, cj, .25, 64, 5, PORTLAND)
        block(s, ci - .08, cj - .08, .16, .16, 6, STONE, z=69)
        block(s, ci - .4, cj - .08, .8, .16, 1, STONE, z=73)
        # The bell is visible through the shaded opening of the circular upper belfry.
        block(s, ci + .9, cj, .3, .4, 4, BRICK, z=37)
    scene.add(i + j + 22, draw)


def hapenny_bridge(scene, i, j):
    """Single elliptical iron arch: three structural ribs, open spandrels, rails and lamp arches."""
    length, width = 8.5, 2.2
    def draw(s):
        def height(t):return 5 + 7 * math.sqrt(max(0, 1 - (2 * t - 1) ** 2))
        # Three separate curved iron ribs; decking is a thin projected 3D ribbon.
        for a in (0, width / 2, width):
            for n in range(40):
                t, u = n / 40, (n + 1) / 40
                seg(s, P(s, i + a, j + t * length, height(t) - 2),
                    P(s, i + a, j + u * length, height(u) - 2), PALE['dark'], 2)
        for n in range(40):
            t, u = n / 40, (n + 1) / 40
            poly(s, [P(s, i, j + t * length, height(t)), P(s, i + width, j + t * length, height(t)),
                     P(s, i + width, j + u * length, height(u)), P(s, i, j + u * length, height(u))],
                 lambda x, y: GRANITE['mid'] if (int(x) + int(y)) % 5 else GRANITE['lit'])
        for a in (0, width):
            for n in range(23):
                t = n / 22
                seg(s, P(s, i + a, j + t * length, height(t)),
                    P(s, i + a, j + t * length, height(t) + 5), PALE['lit' if a == 0 else 'dark'])
            for n in range(40):
                t, u = n / 40, (n + 1) / 40
                seg(s, P(s, i + a, j + t * length, height(t) + 5),
                    P(s, i + a, j + u * length, height(u) + 5), PALE['hi' if a == 0 else 'mid'])
        # Three distinctive overhead lamp arches, open between the side posts.
        for t in (.12, .5, .88):
            z = height(t) + 6
            for n in range(16):
                a, b = n / 16, (n + 1) / 16
                seg(s, P(s, i + a * width, j + t * length, z + math.sin(a * math.pi) * 6),
                    P(s, i + b * width, j + t * length, z + math.sin(b * math.pi) * 6), PALE['lit'])
            block(s, i + width / 2 - .12, j + t * length, .24, .25, 3, IRON_PALETTE,
                  lambda u, v, lit: LAMP_GLASS if 1 <= v <= 2 and u > .3 else None, z=z + 3)
    scene.add(i + j + length + width + 1, draw)


IRON_PALETTE = palette_of(IRON)
LANDMARKS = [
    ('four-courts', four_courts), ('gpo', gpo), ('custom-house', custom_house),
    ('christ-church', christ_church), ('st-patricks', st_patricks),
    ('castle', dublin_castle), ('trinity', trinity), ('hapenny-bridge', hapenny_bridge),
]

if __name__ == '__main__':
    for name, builder in LANDMARKS:
        print(preview([lambda s, builder=builder: builder(s, 3, 3)], 'dublin-' + name,
                      size=(260, 230), origin=(115, 100), tiles=21))
    print(preview([lambda s: [georgian_house(s, 3 + k * 3, 4, floors=2 + k % 2, seed=k) for k in range(5)]],
                  'dublin-houses', size=(260, 210), origin=(85, 55), tiles=21))
