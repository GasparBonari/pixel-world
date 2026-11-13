"""Reykjavík in painted corrugated iron, basalt, pale concrete and prismatic glass.

Architecture and sculpture use projected (i, j, height) geometry, lit on +j.
Run directly for eight isolated 4× landmarks and a house study. Geographic
anchors and architectural references are recorded in DEVELOPMENT_PLAN.md.
"""
import math

import iso
from iso import rgb, h01
from landmarks_paris import P, seg, poly, corners, facade, preview, GLASS
from landmarks_iberia import hip_roof, stone_courses, arch_opening, palette_of, tones
from landmarks_italy import cylinder, ellipse, cross
from landmarks_belgium import dome, pediment

CONCRETE = tones('#FAF7E9', '#DDDCD0', '#C2C6BD', '#9FAAA4', '#6D807C', '#B1BBB1', '#445A56')
BASALT = tones('#ADB4AE', '#818F89', '#687771', '#4C605C', '#334844', '#5B7068', '#283C38')
WHITE = tones('#FFFFF3', '#F1EFDA', '#D8DDCD', '#BAC5B9', '#8B9F94', '#CBD2C2', '#4B6057')
STEEL = tones('#F6FFFF', '#C9DFDE', '#A2C3C8', '#708E9D', '#45616F', '#89ADB6', '#2F4C59')
GLAZING = tones('#D5F5E4', '#82BEBD', '#5B989F', '#366B7F', '#23485F', '#487C8B', '#243F51')
PEARL = tones('#EFF8F4', '#C5DEDD', '#9BBFC5', '#7297A5', '#496B7D', '#8AAEB7', '#365766')
RED = tones('#F3B095', '#BE6656', '#A35147', '#7D3E3A', '#502D2D', '#965349', '#452A2B')
GREEN = tones('#BCD1AF', '#779D87', '#608572', '#406358', '#2A473F', '#537C67', '#263C34')
SLATE = tones('#AFBABA', '#7D9295', '#617A81', '#425D69', '#2B424E', '#526D76', '#253945')
WOOD = tones('#DBB88C', '#B38F66', '#8F704C', '#685139', '#483C2D', '#8C7050', '#352D25')
BRONZE = tones('#B3B99B', '#85977B', '#617A63', '#425C4A', '#2C4235', '#5A7258', '#26392D')
WALLS = [rgb(c) for c in ('#B9574B', '#DFCB93', '#ABC7CB', '#89AA94', '#E1DCD0', '#707F91', '#C89776')]
WATER = (rgb('#4B8296'), rgb('#355F78'), rgb('#C5E5E5'))
IRON, FLAG_BLUE, FLAG_RED = rgb('#304849'), rgb('#315B82'), rgb('#C16154')
AMBER = rgb('#CFB97B')


def block(s, i, j, wi, wj, height, material=CONCRETE, pattern=None, z=0):
    cover = facade(s, i, j, wi, wj, height,
                   pattern or stone_courses(material, 5, 11), palette=material, z0=z)
    iso.fill(s, list(corners(s, i, j, wi, wj, z+height)), lambda x, y: material['mid'], cover)
    iso.outline(s, cover, material['outline'])
    return cover


def windows(material, height, bay=11, floor=14, gothic=False, timber=False):
    courses = stone_courses(material, 5, 10)
    def pattern(u, v, lit):
        c, v = int(u) % bay, int(v)
        level, trim = v % floor, WHITE['lit' if lit else 'dark']
        if v < 2 or v in (height-1, height-3):
            return material['hi' if lit else 'mid']
        top = floor-3-(abs(c-bay/2)*1.15 if gothic else 0)
        if 3 <= c <= bay-3 and 4 <= level <= top and v < height-4:
            if c in (3, bay-3, bay//2) or level in (4, 8, int(top)):
                return trim
            return GLASS['mid' if lit else 'dark']
        if level == 3 and 2 <= c <= bay-2:
            return trim
        if timber:
            return material['line' if lit else 'deep'] if v % 3 == 0 else None
        return courses(u, v, lit)
    return pattern


def metal_roof(s, i, j, wi, wj, base, rise, roof=RED, wall=WHITE):
    """Gable volume, folded metal seams following the j-axis, white verge boards."""
    T, R, B, L = corners(s, i, j, wi, wj, base)
    back, front = P(s, i+wi/2, j, base+rise), P(s, i+wi/2, j+wj, base+rise)
    for pts, key in (([T, L, front, back], 'lit'), ([back, front, B, R], 'dark')):
        poly(s, pts, lambda x, y, key=key: roof[key])
    # Metal standing seams are parallel 3D lines, never screen-space stripes.
    for n in range(1, int(wi*5)):
        a = n/(wi*5)
        z = base+rise*(1-abs(2*a-1))
        seg(s, P(s, i+wi*a, j, z), P(s, i+wi*a, j+wj, z), roof['line'])
        seg(s, P(s, i+wi*a+.025, j, z), P(s, i+wi*a+.025, j+wj, z), roof['hi' if a < .5 else 'mid'])
    front_foot = P(s, i, j+wj+.05, base)
    def gable(x, y):
        u = x-front_foot[0]
        v = front_foot[1]+u*.5-y
        if abs(u-wi*4) <= 2 and 2 < v < min(9, rise-2):
            return WHITE['lit'] if abs(u-wi*4) > 1 or v < 4 or v > 7 else GLASS['dark']
        return wall['line'] if int(v) % 3 == 0 else wall['lit']
    poly(s, [L, B, front], gable)
    seg(s, back, front, roof['hi'])
    seg(s, L, front, WHITE['hi'])
    seg(s, front, B, WHITE['mid'])
    seg(s, L, B, roof['outline'])


def flag(s, i, j, z):
    seg(s, P(s, i, j, z), P(s, i, j, z+19), IRON)
    for a, b, low, high, color in ((0, 1.9, 10, 19, FLAG_BLUE),
                                  (.5, .9, 10, 19, WHITE['hi']),
                                  (0, 1.9, 13, 16, WHITE['hi']),
                                  (.62, .78, 10, 19, FLAG_RED),
                                  (0, 1.9, 14, 15, FLAG_RED)):
        poly(s, [P(s, i+a, j, z+low), P(s, i+b, j, z+low),
                 P(s, i+b, j, z+high), P(s, i+a, j, z+high)], lambda x, y, color=color: color)


def house(scene, i, j, wi=2.5, wj=3, floors=2, seed=0):
    """Low Reykjavík iron-clad houses: timber sash frames, doors, gables, metal roofs."""
    wall, height = palette_of(WALLS[seed % len(WALLS)]), floors*11+3
    def cladding(u, v, lit):
        c, v = int(u) % 10, int(v)
        level, trim = v % 11, WHITE['lit' if lit else 'dark']
        if v < 3:
            return BASALT['lit' if lit else 'dark']
        if v in (height-1, height-2):
            return trim
        if 2 <= c <= 8 and 4 <= level <= 9 and v < height-3:
            if c in (2, 5, 8) or level in (4, 7, 9):
                return trim
            if v < 11 and (int(u)//10+seed) % 3 == 0:
                return WOOD['deep'] if c == 5 else WOOD['lit' if lit else 'dark']
            return GLASS['mid' if lit else 'dark']
        if level == 3 and 1 <= c <= 9:
            return trim
        return wall['mid' if lit else 'deep'] if int(u) % 3 == 0 else None
    def draw(s):
        block(s, i, j, wi, wj, height, wall, cladding)
        roof = (RED, GREEN, SLATE)[seed % 3]
        metal_roof(s, i-.08, j-.08, wi+.16, wj+.16, height, 12, roof, wall)
        if seed % 4 == 0:
            # Small glazed entrance porch; historic houses seldom have broad balconies.
            block(s, i+.65, j+wj, 1.1, .65, 10, wall,
                  windows(wall, 12, bay=8, floor=12, timber=True))
            metal_roof(s, i+.58, j+wj, 1.24, .7, 10, 5, roof, wall)
        if seed % 5 == 0:
            block(s, i+.3, j+wj-.6, .75, .7, 6, wall,
                  windows(wall, 10, bay=6, floor=10), z=height+3)
            metal_roof(s, i+.25, j+wj-.65, .85, .8, height+9, 4, roof, wall)
        block(s, i+.4, j+.55, .4, .5, 8, BASALT, z=height+5)
        block(s, i+.35, j+.5, .5, .6, 1.5, CONCRETE, z=height+12)
    scene.add(i+j+wi+wj+1, draw)


def dial(s, i, j, z, lit=True):
    def point(u, v):
        return P(s, i+u/8 if lit else i, j if lit else j-u/8, z+v)
    ring = [point(math.cos(n*math.tau/32)*6, math.sin(n*math.tau/32)*6) for n in range(32)]
    poly(s, ring, lambda x, y: WHITE['lit' if lit else 'dark'])
    for a, b in zip(ring, ring[1:]+ring[:1]):
        seg(s, a, b, BASALT['dark'])
    for n in range(12):
        a = n*math.tau/12
        seg(s, point(math.cos(a)*4.5, math.sin(a)*4.5), point(math.cos(a)*5.5, math.sin(a)*5.5), BASALT['deep'])
    seg(s, point(0, 0), point(-3, 1), IRON)
    seg(s, point(0, 0), point(1, 4), IRON)


def leif(s, i, j):
    """Filled bronze cloak, helmet, bent arm and axe on a basalt plinth."""
    block(s, i-.45, j-.4, .9, .8, 7, BASALT)
    profile = [(-.35, 7), (.3, 7), (.23, 14), (.45, 17), (.12, 19), (-.22, 18), (-.4, 14)]
    front = [P(s, i+a, j+.15, z) for a, z in profile]
    rear = [P(s, i+a, j-.2, z) for a, z in profile]
    for n in range(len(profile)):
        m = (n+1) % len(profile)
        poly(s, [rear[n], rear[m], front[m], front[n]], lambda x, y: BRONZE['dark'])
    poly(s, front, lambda x, y: BRONZE['hi'] if int(x) % 4 == 0 else BRONZE['lit'])
    cylinder(s, i, j, .2, .2, 19, 4, BRONZE)
    seg(s, P(s, i+.45, j+.1, 8), P(s, i+.45, j+.1, 20), WOOD['deep'], 2)
    block(s, i+.1, j+.05, .6, .15, 3, STEEL, z=17)


def hallgrimskirkja(scene, i, j):
    """Basalt-column wings rising to the clock tower, nave, lancets and Leif Erikson."""
    def lancets(u, v, lit):
        c, v = int(u) % 11, int(v)
        if 3 <= c <= 7 and 7 < v < 35-abs(c-5)*1.4:
            return CONCRETE['hi' if lit else 'mid'] if c in (3, 5, 7) or v == 8 else GLAZING['dark']
        return CONCRETE['line' if lit else 'deep'] if c == 0 or v == 3 else None
    def draw(s):
        block(s, i-.3, j-.3, 8.6, 10.5, 3, BASALT)
        block(s, i+1.6, j, 4.8, 7.5, 39, CONCRETE, lancets, z=3)
        metal_roof(s, i+1.6, j, 4.8, 7.5, 42, 24, SLATE, CONCRETE)
        # The famous rising organ-pipe façade consists of actual depth-bearing columns.
        for n in range(5):
            for side in (0, 1):
                a = .05+n*.55 if side == 0 else 7.4-n*.55
                h = (24, 34, 47, 63, 80)[n]
                block(s, i+a, j+7.1, .5, 1.4, h, CONCRETE,
                      lambda u, v, lit: CONCRETE['hi' if lit else 'mid'] if int(u) % 4 == 0 else None, z=3)
        def tower(u, v, lit):
            c, v = int(u) % 6, int(v)
            if 32 < v < 86 or 106 < v < 116:
                if c in (2, 3):
                    return BASALT['dark']
                return CONCRETE['hi' if lit else 'mid'] if c == 0 else None
            if v in (3, 27, 103, 116):
                return CONCRETE['hi' if lit else 'mid']
            return None
        block(s, i+2.8, j+7, 2.4, 2.3, 116, CONCRETE, tower, z=3)
        metal_roof(s, i+2.8, j+7, 2.4, 2.3, 119, 29, CONCRETE, CONCRETE)
        cross(s, i+4, j+8.1, 149, STEEL)
        dial(s, i+4, j+9.31, 98)
        dial(s, i+5.21, j+8.15, 98, False)
        # Recessed three-door portal stays on the entrance face.
        block(s, i+2.7, j+9.3, 2.6, .35, 21, CONCRETE,
              lambda u, v, lit: BASALT['deep'] if lit and 2 < int(u) < 19 and 2 < v < 18
              and int(u) % 6 not in (0, 1) else None, z=3)
        for n in range(4):
            block(s, i+2.4, j+9.65+n*.25, 3.2, .27, 4-n, CONCRETE)
        leif(s, i+1.4, j+10.4)
    scene.add(i+j+23, draw)


def harpa(scene, i, j):
    """Asymmetric crystalline hall with projected hexagonal quasi-brick glazing."""
    def glass(u, v, lit):
        row = math.floor(v/9)
        c, level = (u+(row % 2)*5) % 10, v % 9
        edge = (c < 1 and 2 < level < 7 or level < 1 and 2 < c < 8
                or abs(abs(c-5)*.55+abs(level-4.5)-5.5) < .6)
        if edge:
            return GLAZING['deep' if lit else 'outline']
        value = h01(math.floor((u+(row % 2)*5)/10), row, 271)
        if lit and value < .13:
            return AMBER
        return GLAZING['hi' if value > .93 and lit else 'lit' if lit and value > .6 else 'mid' if lit else 'dark']
    def prism(s, a, b, wi, wj, heights):
        foot = corners(s, a, b, wi, wj, 3)
        top = [P(s, x, y, z) for (x, y), z in zip(
            ((a, b), (a+wi, b), (a+wi, b+wj), (a, b+wj)), heights)]
        for n, m, lit in ((0, 1, False), (0, 3, False), (3, 2, True), (2, 1, False)):
            start, end = foot[n], foot[m]
            slope = (end[1]-start[1])/(end[0]-start[0] or .001)
            def surface(x, y, start=start, slope=slope, lit=lit):
                u = x-start[0]
                v = start[1]+u*slope-y
                return glass(u, v, lit)
            poly(s, [foot[n], foot[m], top[m], top[n]], surface)
            seg(s, foot[n], top[n], STEEL['hi' if lit else 'deep'])
        poly(s, top, lambda x, y: SLATE['mid'] if int(x-y) % 13 else SLATE['line'])
        for a, b in zip(top, top[1:]+top[:1]):
            seg(s, a, b, STEEL['lit'])
    def draw(s):
        block(s, i-.3, j-.3, 10, 6.2, 3, BASALT)
        prism(s, i, j, 5.5, 5.4, (53, 56, 53, 50))
        prism(s, i+5.5, j+.7, 4, 4.7, (56, 42, 39, 53))
        # Recessed entrance, lintel and individual revolving-door panes.
        block(s, i+2.2, j+5.42, 5, .18, 10, STEEL,
              lambda u, v, lit: STEEL['deep'] if int(u) % 6 == 0 or int(v) == 9 else GLAZING['dark'], z=3)
        block(s, i+1.7, j+5.35, 6, .9, 2, STEEL, z=13)
    scene.add(i+j+18, draw)


def tube(s, points, material=STEEL, width=3):
    for a, b in zip(points, points[1:]):
        seg(s, P(s, *a), P(s, *b), material['outline'], width+1)
        seg(s, P(s, *a), P(s, *b), material['mid'], width)
        pa, pb = P(s, *a), P(s, *b)
        seg(s, (pa[0]-1, pa[1]-1), (pb[0]-1, pb[1]-1), material['hi'])


def sun_voyager(scene, i, j):
    """Open stainless-steel dream boat: curved keel, paired ribs and soaring end prongs."""
    def draw(s):
        cylinder(s, i+3.7, j+2.1, 4.5, 2.5, 0, 2, BASALT)
        ellipse(s, i+3.7, j+2.1, 4.4, 2.4, 2, lambda x, y: CONCRETE['line'] if (int(x)+int(y)) % 13 == 0 else CONCRETE['lit'])
        # Far rail and ribs first, then the near side: each curve is a spatial polyline.
        for side in (-1, 1):
            tube(s, [(i+.2+n*.37, j+2+side*(.2+1.05*math.sin(n*math.pi/20)),
                      5+5*abs(1-n/10)**2) for n in range(21)])
            for a in (1.3, 2.7, 4.1, 5.5):
                tube(s, [(i+a+.35*t, j+2+side*(.15+1.45*t), 5+19*t*t)
                         for t in (0, .2, .4, .6, .8, 1)], width=3)
        tube(s, [(i+.2+n*.37, j+2, 4+7*abs(1-n/10)**2) for n in range(21)], width=4)
        for a, direction in ((.3, -1), (7.4, 1)):
            for side in (-1, 1):
                tube(s, [(i+a+direction*.7*t, j+2+side*.35*t, 9+26*t*t)
                         for t in (0, .2, .4, .6, .8, 1)], width=3)
        for a in (1.5, 5.7):
            block(s, i+a, j+1.8, .24, .4, 4, STEEL, z=2)
    scene.add(i+j+16, draw)


def perlan(scene, i, j):
    """Six cylindrical hot-water tanks, observation deck and steel-ribbed glass dome."""
    def tank(u, v, lit):
        if int(v) in (2, 17, 20) or int(u) % 13 == 0:
            return STEEL['hi' if lit else 'line']
        return CONCRETE['lit' if lit else 'dark']
    def draw(s):
        cylinder(s, i+4, j+4, 4.5, 4.3, 0, 5, BASALT)
        sites = [(i+4+2.7*math.cos(n*math.tau/6), j+4+2.7*math.sin(n*math.tau/6)) for n in range(6)]
        # Rear three tanks, central glazed atrium, then the front tanks.
        for a, b in sorted(sites, key=lambda p: sum(p))[:3]:
            cylinder(s, a, b, 1.45, 1.45, 5, 23, CONCRETE, tank)
            cylinder(s, a, b, 1.51, 1.51, 27, 2, STEEL)
        cylinder(s, i+4, j+4, 2.65, 2.65, 7, 23, GLAZING,
                 lambda u, v, lit: STEEL['mid'] if int(u) % 5 == 0 else None)
        for a, b in sorted(sites, key=lambda p: sum(p))[3:]:
            cylinder(s, a, b, 1.45, 1.45, 5, 23, CONCRETE, tank)
            cylinder(s, a, b, 1.51, 1.51, 27, 2, STEEL)
        cylinder(s, i+4, j+4, 3.1, 3.1, 28, 3, STEEL)
        dome(s, i+4, j+4, 3, 31, 34, PEARL)
        for n in range(12):
            a = n*math.tau/12
            points = [P(s, i+4+3*math.cos(t)*math.cos(a), j+4+3*math.cos(t)*math.sin(a), 31+34*math.sin(t))
                      for t in [k*math.pi/24 for k in range(13)]]
            # Only the near half is visible; rear ribs must not show through the dome.
            if math.sin(a)-.5*math.cos(a) < 0:
                continue
            for p, q in zip(points, points[1:]):
                seg(s, p, q, STEEL['lit'])
        for n in range(32):
            a = n*math.tau/32
            seg(s, P(s, i+4+3.17*math.cos(a), j+4+3.17*math.sin(a), 31),
                P(s, i+4+3.17*math.cos(a), j+4+3.17*math.sin(a), 35), STEEL['deep'])
        for n in range(32):
            a, b = n*math.tau/32, (n+1)*math.tau/32
            seg(s, P(s, i+4+3.17*math.cos(a), j+4+3.17*math.sin(a), 35),
                P(s, i+4+3.17*math.cos(b), j+4+3.17*math.sin(b), 35), STEEL['mid'])
        for k in range(4):
            block(s, i+3, j+8+k*.25, 2, .27, 4-k, CONCRETE)
    scene.add(i+j+19, draw)


def city_hall(scene, i, j):
    """Pond-edge concrete wings, curved metal roofs, glazing and moss wall."""
    def glazing(u, v, lit):
        if int(u) % 7 == 0 or int(v) in (2, 14, 26):
            return CONCRETE['lit' if lit else 'dark']
        return GLAZING['mid' if lit else 'dark']
    def barrel(s, a, b, wi, wj, z):
        for n in range(24):
            t0, t1 = n*math.pi/24, (n+1)*math.pi/24
            x0, x1 = a+wi*(1-math.cos(t0))/2, a+wi*(1-math.cos(t1))/2
            z0, z1 = z+9*math.sin(t0), z+9*math.sin(t1)
            pts = [P(s, x0, b, z0), P(s, x1, b, z1), P(s, x1, b+wj, z1), P(s, x0, b+wj, z0)]
            poly(s, pts, lambda x, y, n=n: STEEL['lit' if n < 12 else 'dark'])
            if n % 3 == 0:
                seg(s, pts[0], pts[3], STEEL['line'])
    def draw(s):
        block(s, i, j, 8.5, 5, 3, BASALT)
        block(s, i, j, 3.2, 5, 30, CONCRETE, windows(CONCRETE, 30, bay=10, floor=15), z=3)
        block(s, i+4.8, j+.1, 3.7, 4.9, 24, CONCRETE, glazing, z=3)
        block(s, i+3.2, j+.7, 1.6, 3.5, 18, STEEL, glazing, z=3)
        barrel(s, i, j, 3.2, 5, 33)
        barrel(s, i+4.8, j+.1, 3.7, 4.9, 27)
        # The green planted wall is an architectural feature, not a decorative hedge.
        block(s, i+.3, j+5, 2.3, .17, 17, GREEN,
              lambda u, v, lit: GREEN['hi' if lit else 'dark'] if h01(int(u), int(v), 7) < .24 else None, z=3)
        # Open pond-facing colonnade and the broad glazed room behind it.
        block(s, i+4.9, j+4.85, 3.4, .2, 16, CONCRETE, glazing, z=3)
        for a in (5, 6.05, 7.1, 8.2):
            block(s, i+a, j+5.25, .18, .25, 19, CONCRETE, z=3)
        block(s, i+4.7, j+5, 3.9, .65, 2, CONCRETE, z=22)
        block(s, i+2.8, j+4.7, 2, 1.5, 2, BASALT, z=2)
    scene.add(i+j+17, draw)


def parliament(scene, i, j):
    """Hewn basalt Alþingishúsið: two storeys, dressed windows, reliefs and slate hip roof."""
    def draw(s):
        block(s, i, j, 8, 4.4, 33, BASALT, windows(BASALT, 33, bay=11, floor=15))
        hip_roof(s, i-.12, j-.12, 8.24, 4.64, 33, 13, SLATE)
        # Central entrance and small classical hood, no invented palace portico.
        block(s, i+3.2, j+4.4, 1.6, .25, 15, CONCRETE,
              lambda u, v, lit: WOOD['dark'] if lit and 2 < u < 10 and 2 < v < 12 else None)
        pediment(s, i+3, j+4.7, 2, 16, 5, CONCRETE)
        for n in range(4):
            # Four Icelandic guardian relief panels beneath the upper windows.
            a = i+.8+n*1.8
            block(s, a, j+4.42, .65, .12, 4, CONCRETE, z=18)
            seg(s, P(s, a+.12, j+4.56, 19), P(s, a+.5, j+4.56, 21), BASALT['dark'], 2)
        # Royal cypher in the central roof pediment; flag and paired roof stacks.
        pediment(s, i+2.7, j+4.4, 2.6, 33, 11, BASALT)
        seg(s, P(s, i+3.8, j+4.42, 37), P(s, i+4.2, j+4.42, 41), CONCRETE['hi'], 2)
        for a in (1.1, 6.3):
            block(s, i+a, j+1, .55, .6, 8, BASALT, z=39)
        flag(s, i+4, j+2, 47)
        for k in range(4):
            block(s, i+2.7, j+4.7+k*.25, 2.6, .27, 4-k, CONCRETE)
    scene.add(i+j+17, draw)


def landakotskirkja(scene, i, j):
    """Christ the King: square flat-topped Gothic tower, pinnacles, lancets and buttresses."""
    def gothic(u, v, lit):
        c, v = int(u) % 12, int(v)
        top = 36-abs(c-6)*1.6
        if 3 <= c <= 9 and 7 <= v <= top:
            return WHITE['lit' if lit else 'dark'] if c in (3, 6, 9) or v in (7, 18) else GLAZING['dark']
        return CONCRETE['line' if lit else 'deep'] if c == 0 or v % 9 == 0 else None
    def draw(s):
        block(s, i+.5, j, 4.7, 7, 39, CONCRETE, gothic)
        metal_roof(s, i+.5, j, 4.7, 7, 39, 24, SLATE, CONCRETE)
        # The eastern aisle has individual pointed cross-gables, rather than a
        # featureless long eave. Their profiles lie in j/z and extrude along i.
        block(s, i+5.1, j, .9, 7, 30, CONCRETE, gothic)
        for b in (.4, 2.5, 4.6):
            foot = P(s, i+6, j+b, 30)
            front = [foot, P(s, i+6, j+b+1.8, 30), P(s, i+6, j+b+.9, 46)]
            back = [P(s, i+5, j+b, 30), P(s, i+5, j+b+1.8, 30), P(s, i+5, j+b+.9, 46)]
            poly(s, [back[0], front[0], front[2], back[2]], lambda x, y: SLATE['lit'])
            poly(s, [back[2], front[2], front[1], back[1]], lambda x, y: SLATE['dark'])
            def gable(x, y, foot=foot):
                u = foot[0]-x
                v = foot[1]+u*.5-y
                if abs(u-7.2) < 2 and 2 < v < 9-abs(u-7.2):
                    return WHITE['dark'] if abs(u-7.2) > 1 else GLAZING['dark']
                return CONCRETE['dark']
            poly(s, front, gable)
            for a, c in zip(front, front[1:]+front[:1]):
                seg(s, a, c, CONCRETE['line'])
        for a in (.35, 5.1):
            for b in (.7, 2.5, 4.3, 6.1):
                block(s, i+a, j+b, .4, .5, 29, CONCRETE)
                block(s, i+a+.05, j+b+.05, .3, .4, 7, WHITE, z=29)
        def tower(u, v, lit):
            c, v = abs(u), int(v)
            centre = (3.4 if lit else 3.1)*4
            distance = abs(c-centre)
            top = 73-distance*1.4
            if distance < 8 and 49 < v < top:
                if distance > 6 or int(distance) in (2, 3) or v in (50, 51, 59, 65) or v > top-2:
                    return WHITE['lit' if lit else 'dark']
                return GLAZING['dark']
            if v in (3, 46, 73) or int(c) in (1, 25):
                return CONCRETE['hi' if lit else 'mid']
            return stone_courses(CONCRETE, 6, 11)(u, v, lit)
        block(s, i+1.2, j+5.6, 3.4, 3.1, 77, CONCRETE, tower)
        block(s, i+1.1, j+5.5, 3.6, 3.3, 3, WHITE, z=74)
        # Four corner pinnacles crown a flat tower; there is no tall invented spire.
        for a, b in ((1.15, 5.55), (4.3, 5.55), (1.15, 8.45), (4.3, 8.45)):
            block(s, i+a, j+b, .35, .35, 10, CONCRETE, z=77)
            hip_roof(s, i+a-.04, j+b-.04, .43, .43, 87, 4, CONCRETE)
        cross(s, i+2.9, j+8.7, 79, WHITE)
        block(s, i+1.8, j+8.71, 2.2, .18, 27, CONCRETE,
              lambda u, v, lit: arch_opening(u, v, 8.8, 5, 13, WOOD['deep']) if lit else None)
        pediment(s, i+1.7, j+8.92, 2.4, 24, 13, WHITE)
        for k in range(5):
            block(s, i+1.6, j+8.9+k*.24, 2.6, .26, 5-k, CONCRETE)
    scene.add(i+j+20, draw)


def hofdi(scene, i, j):
    """White timber Höfði: steep dark roof, cross gables, sash windows and entry porch."""
    def draw(s):
        block(s, i, j, 5.5, 5, 5, BASALT)
        pattern = windows(WHITE, 31, bay=11, floor=14, timber=True)
        block(s, i, j, 5.5, 5, 31, WHITE, pattern, z=5)
        hip_roof(s, i-.15, j-.15, 5.8, 5.3, 36, 25, SLATE)
        # Deep projecting central gable and an enclosed, finely framed entrance porch.
        block(s, i+1.55, j+4.8, 2.4, 1.1, 31, WHITE, pattern, z=5)
        metal_roof(s, i+1.45, j+4.7, 2.6, 1.3, 36, 22, SLATE, WHITE)
        block(s, i+1.8, j+5.9, 1.9, .9, 14, WHITE,
              windows(WHITE, 16, bay=8, floor=14, timber=True), z=5)
        hip_roof(s, i+1.7, j+5.8, 2.1, 1.1, 19, 6, SLATE)
        for a in (.6, 4.15):
            block(s, i+a, j+4.5, .8, .65, 9, WHITE,
                  windows(WHITE, 12, bay=6, floor=11), z=39)
            metal_roof(s, i+a-.1, j+4.4, 1, .85, 48, 7, SLATE, WHITE)
        for a in (.7, 4.4):
            block(s, i+a, j+1.1, .55, .65, 14, CONCRETE, z=48)
            block(s, i+a-.08, j+1.02, .71, .81, 2, BASALT, z=61)
        for k in range(4):
            block(s, i+1.7, j+6.8+k*.25, 2.1, .27, 4-k, CONCRETE)
        flag(s, i-.8, j+4, 0)
    scene.add(i+j+17, draw)


STUDIES = [('hallgrimskirkja', hallgrimskirkja), ('harpa', harpa),
           ('sun-voyager', sun_voyager), ('perlan', perlan), ('city-hall', city_hall),
           ('parliament', parliament), ('landakotskirkja', landakotskirkja), ('hofdi', hofdi)]

if __name__ == '__main__':
    for name, builder in STUDIES:
        print(preview([lambda s, b=builder: b(s, 4, 4)], 'reykjavik-'+name,
                      size=(250, 260), origin=(115, 125), tiles=19))
    print(preview([lambda s: house(s, 4, 4, seed=0), lambda s: house(s, 8, 4, seed=1),
                   lambda s: house(s, 8, 8, floors=1, seed=9)], 'reykjavik-houses',
                  size=(230, 190), origin=(105, 40), tiles=17))
