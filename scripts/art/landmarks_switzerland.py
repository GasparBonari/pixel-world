"""Bern: green-grey sandstone, arcaded townhouses and brown-red tiled roofs.

All buildings use projected (i, j, height) geometry. Run directly for eight
isolated 4× landmark studies and a house study before scene integration.
Coordinates, composition and architectural references: DEVELOPMENT_PLAN.md.
"""
import math

import iso
from iso import rgb, h01
from landmarks_paris import P, seg, poly, corners, facade, preview, GLASS
from landmarks_iberia import hip_roof, stone_courses, arch_opening, palette_of, tones
from landmarks_belgium import dome
from landmarks_italy import cylinder
from landmarks_denmark import spire

SAND = tones('#E8E6CF', '#C0C5A9', '#A6AF96', '#808F7A', '#566751', '#98A48B', '#3B4D3B')
PALE = tones('#FFF2D7', '#DED4B8', '#C6B99C', '#A4997F', '#756D54', '#B3A88E', '#4D4736')
CLAY = tones('#E9AB7D', '#B57855', '#985C40', '#75412F', '#522D24', '#8C533C', '#42271F')
SLATE = tones('#B1B8AF', '#84938C', '#697D75', '#4A625A', '#30483F', '#5E756A', '#273C34')
COPPER = tones('#C1D3AB', '#88AF91', '#688E75', '#466D59', '#2C4A3B', '#5C8268', '#263C30')
STEEL = tones('#F3F2DF', '#CBD2C8', '#ADBDB5', '#7A9390', '#526E6C', '#97ABA1', '#354F4C')
GOLD = tones('#FFF2AA', '#E7C363', '#C79E43', '#9E732D', '#6F4E23', '#B18D36', '#4F3920')
WOOD = tones('#D2B08A', '#9F7954', '#805B3D', '#5D412E', '#3E2F25', '#76563A', '#30271F')
WALLS = [rgb(c) for c in ('#C0C5A9', '#B5BEA6', '#CFC9AC', '#ADB9A5', '#D7CEB5', '#B9B5A0')]
WATER = (rgb('#4B9F91'), rgb('#35796F'), rgb('#C0E6CF'))
IRON, RED, SHUTTER = rgb('#344B3E'), rgb('#B7473D'), rgb('#4F6D56')


def block(s, i, j, wi, wj, height, material=SAND, pattern=None, z=0):
    cover = facade(s, i, j, wi, wj, height,
                   pattern or stone_courses(material, 4, 10), palette=material, z0=z)
    iso.fill(s, list(corners(s, i, j, wi, wj, z+height)), lambda x, y: material['mid'], cover)
    iso.outline(s, cover, material['outline'])
    return cover


def windows(material, height, bay=10, floor=13, gothic=False, arcade=False):
    joints = stone_courses(material, 4, 10)
    def pattern(u, v, lit):
        c, v = int(u) % bay, int(v)
        level, trim = v % floor, material['hi' if lit else 'mid']
        if v < 2 or v in (height-1, height-3) or level == 0:
            return trim
        if arcade and v < 10:
            opening = arch_opening(c, v, bay/2, bay/2-1.5, 5, material['deep'])
            if opening:
                return opening
        head = floor-3-(abs(c-bay/2)*.9 if gothic else 0)
        if 2 <= c <= bay-2 and 3 <= level <= head and v < height-4:
            if c in (2, bay-2, bay//2) or level in (3, 6, int(head)):
                return trim
            return GLASS['mid' if lit else 'dark']
        return joints(u, v, lit)
    return pattern


def band(s, i, j, wi, wj, z, material=PALE, height=2):
    """A string course on an existing solid; no cap can paint through the storey above."""
    facade(s, i, j, wi, wj, height,
           lambda u, v, lit: material['hi' if lit else 'mid'] if v > height-1
           else material['lit' if lit else 'dark'], palette=material, z0=z)


def dial(s, i, j, z, radius=7, lit=True, astronomical=False):
    """A clock in its wall plane; the astrolabe has zodiac ring, eccentric disc and sun arm."""
    def point(u, v):
        return P(s, i+u/8 if lit else i, j if lit else j-u/8, z+v)
    for u in range(-radius, radius+1):
        for v in range(-radius, radius+1):
            r = math.hypot(u, v)
            if r > radius:
                continue
            color = GOLD['lit'] if r > radius-1 else IRON
            if astronomical and r < radius-2:
                color = rgb('#4B8190') if v > -1 else rgb('#9A6045')
                if abs(math.hypot(u+1, v-1)-radius*.58) < .7:
                    color = GOLD['hi']
            x, y = point(u, v)
            s.put(x, y, color)
    for n in range(12):
        a = n*math.tau/12
        seg(s, point(math.cos(a)*(radius-2), math.sin(a)*(radius-2)),
            point(math.cos(a)*(radius-.6), math.sin(a)*(radius-.6)), GOLD['hi'])
    seg(s, point(0, 0), point(-radius*.6, radius*.2), GOLD['hi'])
    seg(s, point(0, 0), point(radius*.15, radius*.78), GOLD['lit'])
    if astronomical:
        x, y = point(radius*.15, radius*.78)
        for dx, dy in ((0, 0), (-1, 0), (1, 0), (0, 1), (0, -1)):
            s.put(x+dx, y+dy, GOLD['hi'])


def flag(s, i, j, z):
    seg(s, P(s, i, j, z), P(s, i, j, z+17), IRON)
    for lo, hi, bottom, top, color in ((0, 1.35, 6, 17, RED),
                                      (.53, .83, 8, 15, PALE['hi']),
                                      (.23, 1.13, 10, 13, PALE['hi'])):
        poly(s, [P(s, i+lo, j, z+bottom), P(s, i+hi, j, z+bottom),
                 P(s, i+hi, j, z+top), P(s, i+lo, j, z+top)], lambda x, y, c=color: c)


def townhouse(scene, i, j, wi=2.5, wj=3, floors=3, seed=0):
    """Bernese arcades, sandstone surrounds, green shutters and steep tiled hip roofs."""
    wall, height = palette_of(WALLS[seed % len(WALLS)]), floors*11+3
    joints = stone_courses(wall, 5, 12)
    def pattern(u, v, lit):
        c, v = int(u) % 10, int(v)
        level, trim = (v-11) % 11, PALE['lit' if lit else 'dark']
        if v < 2:
            return SAND['dark']
        if v in (10, height-1, height-3):
            return trim
        if v < 10:
            opening = arch_opening(c, v, 5, 3.3, 5.2, WOOD['deep'])
            if opening:
                if 3 <= v <= 6 and c in (3, 4, 6, 7):
                    return GLASS['dark'] if (int(u)//10+seed) % 2 else WOOD['lit']
                return trim if c == 5 and v < 7 else opening
        if v >= 11 and 3 <= c <= 7 and 2 <= level <= 8 and v < height-4:
            if c in (3, 5, 7) or level in (2, 5, 8):
                return trim
            return GLASS['mid' if lit else 'dark']
        if v >= 11 and c in (1, 2, 8, 9) and 3 <= level <= 7 and seed % 3:
            return SHUTTER if level % 2 else SAND['deep']
        if v >= 11 and level == 1 and 2 <= c <= 8:
            return trim
        if seed % 5 == 0 and v >= 11 and level == 0 and c in (3, 5, 7):
            return IRON
        return joints(u, v, lit)
    def draw(s):
        block(s, i, j, wi, wj, height, wall, pattern)
        hip_roof(s, i-.1, j-.1, wi+.2, wj+.2, height, 13, CLAY)
        # Dressed dormer with its own window, miniature roof and sill.
        if seed % 2 == 0:
            block(s, i+wi*.4, j+wj-.65, .6, .55, 7, PALE,
                  lambda u, v, lit: GLASS['dark'] if 1 < u < 4 and 1 < v < 5 else None,
                  z=height+2)
            hip_roof(s, i+wi*.4-.08, j+wj-.73, .76, .71, height+9, 3, CLAY)
        block(s, i+wi*.65, j+.65, .38, .4, 11, PALE, z=height+7)
        block(s, i+wi*.65-.06, j+.59, .5, .52, 2, SAND, z=height+18)
        if seed % 7 == 0:
            flag(s, i+wi*.7, j+wj+.1, 17)
    scene.add(i+j+wi+wj, draw)


def gate_base(s, i, j, width, depth):
    """Two piers and a curved vault, with a genuinely open passage between them."""
    for a in (0, width-.9):
        block(s, i+a, j, .9, depth, 14)
    # The intrados rises at the centre: fill only masonry above the curve.
    for a in range(17):
        u = .9+(width-1.8)*a/17
        v = (u-width/2)/(width/2-.9)
        low = 6+7*math.sqrt(max(0, 1-v*v))
        block(s, i+u, j, (width-1.8)/17+.02, depth, 15-low, z=low)


def zytglogge(scene, i, j):
    """Gate arch, gilded clocks/astrolabe, automata bay and broad tiled roof with belfry."""
    W, D = 4.4, 3.3
    def draw(s):
        gate_base(s, i, j, W, D)
        block(s, i, j, W, D, 47, SAND, stone_courses(SAND, 5, 12), z=15)
        for z in (16, 39, 59):
            band(s, i, j, W, D, z)
        # East-facing astrolabe and upper time dial; the west face has its own clock.
        dial(s, i+W/2, j+D+.03, 48, 11)
        dial(s, i+W+.03, j+D*.5, 27, 9, lit=False, astronomical=True)
        dial(s, i+W+.04, j+D*.5, 49, 9, lit=False)
        # Polychrome automata: filled robed figures with separate heads under a canopy.
        block(s, i+W+.02, j+D-.15, .35, .75, 2, GOLD, z=17)
        for n in range(3):
            a, b = i+W+.22, j+D-.26-n*.24
            block(s, a, b, .2, .19, 5, GOLD if n == 1 else CLAY, z=19)
            cylinder(s, a+.1, b+.1, .12, .12, 24, 2, PALE)
        hip_roof(s, i+W-.05, j+D-1, .7, 1.1, 29, 4, GOLD)
        hip_roof(s, i-.35, j-.35, W+.7, D+.7, 62, 22, CLAY)
        block(s, i+1.65, j+1.1, 1.1, 1.1, 8, WOOD,
              lambda u, v, lit: WOOD['deep'] if 1 < u % 5 < 4 and 2 < v < 7 else None, z=82)
        hip_roof(s, i+1.5, j+.95, 1.4, 1.4, 90, 8, SLATE)
        spire(s, i+2.2, j+1.65, .48, 96, 20, COPPER, conical=True)
    scene.add(i+j+W+D, draw)


def kafigturm(scene, i, j):
    """Baroque prison gate: open arch, rustication, gold dial, steep roof and bell lantern."""
    def draw(s):
        gate_base(s, i, j, 3.6, 3.2)
        block(s, i, j, 3.6, 3.2, 39, SAND, windows(SAND, 39, 11, 14), z=15)
        band(s, i, j, 3.6, 3.2, 52, height=3)
        dial(s, i+1.8, j+3.23, 43, 9)
        hip_roof(s, i-.23, j-.23, 4.06, 3.66, 55, 22, CLAY)
        block(s, i+1.3, j+1.1, 1, 1, 8, WOOD,
              lambda u, v, lit: WOOD['deep'] if 1 < u % 5 < 4 and 1 < v < 7 else None, z=76)
        spire(s, i+1.8, j+1.6, .85, 84, 12, SLATE, onion=True)
        # Adjacent narrow stair house has dressed windows and a separate red roof.
        block(s, i+3.6, j+.9, 1.4, 2.3, 29, PALE, windows(PALE, 29, 8))
        hip_roof(s, i+3.5, j+.8, 1.6, 2.5, 29, 12, CLAY)
    scene.add(i+j+8.2, draw)


def federal_palace(scene, i, j):
    """Symmetric sandstone wings, pilasters, arched loggia and three copper domes."""
    W, D, H = 12, 5.3, 36
    def draw(s):
        block(s, i, j, W, D, H, PALE, windows(PALE, H, 10, 12, arcade=True))
        hip_roof(s, i-.15, j-.15, W+.3, D+.3, H, 6, SLATE)
        for a in (0, W-2.3):
            block(s, i+a, j-.1, 2.3, D+.3, 41, PALE, windows(PALE, 41, 9, 13))
            cylinder(s, i+a+1.15, j+2.6, .9, .9, 41, 4, PALE, windows(PALE, 12, 5))
            dome(s, i+a+1.15, j+2.6, .95, 45, 10, COPPER)
        # Projecting central risalit, rusticated portal and paired pilasters.
        block(s, i+4, j+1, 4, D-.4, 44, PALE, windows(PALE, 44, 10, 14, arcade=True))
        for a in (4.15, 5.1, 6.75, 7.65):
            block(s, i+a, j+D+.65, .22, .24, 29, PALE, z=10)
        block(s, i+3.85, j+D+.45, 4.3, .5, 4, PALE, z=39)
        cylinder(s, i+6, j+3, 1.85, 1.85, 44, 13, PALE, windows(PALE, 13, 7, 13))
        front = [P(s, i+3.95, j+D+1.03, 43), P(s, i+8.05, j+D+1.03, 43),
                 P(s, i+6, j+D+1.03, 53)]
        poly(s, front, lambda x, y: PALE['lit'] if (int(x)+int(y)) % 9 else PALE['line'])
        for a, b in zip(front, front[1:]+front[:1]):
            seg(s, a, b, PALE['hi'])
        dome(s, i+6, j+3, 2.05, 57, 25, COPPER)
        cylinder(s, i+6, j+3, .36, .36, 82, 7, GOLD)
        dome(s, i+6, j+3, .42, 89, 4, GOLD)
        # Swiss escutcheon rather than unreadable invented lettering.
        block(s, i+5.7, j+D+.96, .65, .1, 7, palette_of(RED), z=29)
        seg(s, P(s, i+6, j+D+1.08, 30), P(s, i+6, j+D+1.08, 35), PALE['hi'])
        seg(s, P(s, i+5.8, j+D+1.08, 32.5), P(s, i+6.2, j+D+1.08, 32.5), PALE['hi'])
        for k in range(5):
            block(s, i+4, j+D+1+k*.3, 4, .32, 5-k, SAND)
        flag(s, i+1, j+.5, 44)
    scene.add(i+j+W+D+2.5, draw)


def gothic(material, height, bay=12):
    base = windows(material, height, bay, 22, gothic=True)
    def pattern(u, v, lit):
        c, v = int(u) % bay, int(v)
        if 4 <= v <= 24-abs(c-bay/2)*1.7 and 3 <= c <= bay-3:
            if c in (3, bay-3, bay//2) or v in (4, 13):
                return material['hi' if lit else 'mid']
            return GLASS['mid' if lit else 'dark']
        return base(u, v, lit)
    return pattern


def minster(scene, i, j):
    """Single soaring Gothic tower, open tracery spire, Last Judgement portal and buttresses."""
    W, D = 5.7, 9
    def draw(s):
        block(s, i+.8, j, W-1.6, D, 40, SAND, gothic(SAND, 40))
        hip_roof(s, i+.65, j-.2, W-1.3, D+.4, 40, 17, CLAY)
        for a in (i, i+W-1.25):
            block(s, a, j+.8, 1.25, D-1, 24, SAND, gothic(SAND, 24, 10))
            hip_roof(s, a-.08, j+.7, 1.4, D-.8, 24, 7, CLAY)
        # Tiered external buttresses and small pinnacles along the aisles.
        for b in (j+1, j+3, j+5.2, j+7):
            for a in (i-.3, i+W-.2):
                block(s, a, b, .5, .65, 18, SAND)
                block(s, a+.1, b, .3, .55, 13, SAND, z=18)
                spire(s, a+.25, b+.3, .26, 31, 7, SAND, conical=True)
        def tower_face(u, v, lit):
            c, v = int(u) % 14, int(v)
            if c in (0, 1, 12, 13):
                return SAND['hi' if lit else 'mid']
            if 49 < v < 68-abs(c-7)*.9 and c in (4, 5, 8, 9):
                return SAND['deep'] if v % 4 else SAND['line']
            if 29 < v < 43-abs(c-7) and c in (5, 6, 8):
                return GLASS['dark'] if v % 5 else SAND['mid']
            return stone_courses(SAND, 4, 10)(u, v, lit)
        block(s, i+1, j+D-3, 3.7, 3.8, 73, SAND, tower_face)
        dial(s, i+2.85, j+D+.82, 39, 6)
        # Deep coloured Last Judgement tympanum, clipped entirely to the west portal.
        def portal(u, v, lit):
            centre = 3.7*4
            if lit and abs(u-centre) < 8 and 2 < v < 20-abs(u-centre)*1.4:
                if abs(u-centre) > 6 or v > 17-abs(u-centre):
                    return SAND['hi']
                if v < 9:
                    return WOOD['deep'] if int(u) % 6 else PALE['lit']
                return (GOLD['lit'], RED, PALE['hi'], rgb('#5F7B8D'))[(int(u)//2+int(v)//3) % 4]
            return stone_courses(SAND, 4, 10)(u, v, lit)
        block(s, i+1, j+D+.8, 3.7, .45, 24, SAND, portal)
        # Set-back octagonal belfry and open stone crown over the square tower.
        for z in (26, 46, 71):
            band(s, i+1, j+D-3, 3.7, 3.8, z)
        cylinder(s, i+2.85, j+D-1.1, 1.45, 1.45, 73, 14, SAND,
                 lambda u, v, lit: SAND['deep'] if 2 < u % 10 < 7 and 2 < v < 12
                 else SAND['hi' if lit else 'mid'])
        cylinder(s, i+2.85, j+D-1.1, 1.52, 1.52, 86, 2, PALE)
        for a, b in ((1, D-3), (4.3, D-3), (1, D+.4), (4.3, D+.4)):
            block(s, i+a, j+b, .4, .4, 76, SAND)
            spire(s, i+a+.2, j+b+.2, .28, 76, 10, SAND, conical=True)
        # Eight tapering ribs and alternating open diagonal tracery, in projected 3D.
        ci, cj, base, rise = i+2.85, j+D-1.1, 88, 37
        for n in sorted(range(8), key=lambda n: math.cos(n*math.tau/8)+math.sin(n*math.tau/8)):
            a, b = n*math.tau/8, (n+1)*math.tau/8
            for k in range(6):
                t, tt = k/6, (k+1)/6
                point = lambda angle, t: P(s, ci+1.4*(1-t)*math.cos(angle),
                                          cj+1.4*(1-t)*math.sin(angle), base+rise*t)
                color = SAND['hi'] if math.sin(a)-.5*math.cos(a) > 0 else SAND['dark']
                seg(s, point(a, t), point(a, tt), color)
                seg(s, point(a, t), point(b, t), PALE['lit'])
                seg(s, point(a, t), point(b, tt), color)
        cylinder(s, ci, cj, .1, .1, 125, 5, GOLD)
    scene.add(i+j+W+D+1.4, draw)


def rathaus(scene, i, j):
    """Late Gothic council house: great tiled roof, lancets, loggia and twin stair flights."""
    W, D, H = 7, 5, 35
    def draw(s):
        block(s, i, j, W, D, H, SAND, windows(SAND, H, 12, 16, gothic=True, arcade=True))
        hip_roof(s, i-.2, j-.2, W+.4, D+.4, H, 23, CLAY)
        for a in (1.3, 3.2, 5.1):
            block(s, i+a, j+D-.7, .65, .6, 8, PALE, windows(PALE, 10, 5), z=39)
            hip_roof(s, i+a-.1, j+D-.8, .85, .8, 47, 4, CLAY)
        # Raised arcaded porch and two opposing flights converge at its central landing.
        block(s, i+2.2, j+D, 2.6, 1, 15, SAND,
              lambda u, v, lit: arch_opening(u % 9, v, 4.5, 2.7, 7, SAND['deep'])
              or stone_courses(SAND, 4, 10)(u, v, lit))
        hip_roof(s, i+2, j+D-.1, 3, 1.3, 15, 5, CLAY)
        for k in range(10):
            for a in (i+.1+k*.22, i+6.65-k*.22):
                block(s, a, j+D+.3, .25, .8, 1.3+k*1.3, SAND)
        for start, end in ((i+.1, i+2.4), (i+6.9, i+4.6)):
            seg(s, P(s, start, j+D+1.15, 5), P(s, end, j+D+1.15, 18), SAND['hi'], 2)
        for a in (.7, 5.8):
            flag(s, i+a, j+D+.1, 24)
    scene.add(i+j+W+D+1.8, draw)


def nydeggkirche(scene, i, j):
    """Buttressed Gothic church: tall lancets, red nave roof, square clock tower and spire."""
    def draw(s):
        block(s, i, j, 4.3, 6.7, 31, SAND, gothic(SAND, 31, 11))
        hip_roof(s, i-.15, j-.2, 4.6, 7.1, 31, 18, CLAY)
        for b in (j+.6, j+2.7, j+4.8):
            block(s, i+4.2, b, .6, .7, 19, SAND)
            block(s, i+4.2, b+.1, .4, .5, 9, SAND, z=19)
        block(s, i+.1, j+4.9, 2.2, 2.3, 55, SAND, gothic(SAND, 55, 9))
        block(s, i, j+4.8, 2.4, 2.5, 2, PALE, z=54)
        dial(s, i+1.2, j+7.23, 44, 6)
        hip_roof(s, i-.1, j+4.7, 2.6, 2.7, 56, 23, CLAY)
        cylinder(s, i+1.2, j+6.05, .09, .09, 79, 6, GOLD)
        # Two bronze door leaves with raised relief panels at the porch.
        block(s, i+2.4, j+6.65, 1.5, .35, 13, SAND,
              lambda u, v, lit: COPPER['deep'] if 2 < u < 10 and v < 10 else None)
        for a in (.4, 1):
            for z in (3, 6, 9):
                block(s, i+2.4+a, j+7.03, .25, .05, 1.5, COPPER, z=z)
    scene.add(i+j+12.5, draw)


def historical_museum(scene, i, j):
    """Castle-like museum with stepped entrance gable, polychrome mosaic and conical turrets."""
    W, D, H = 10, 5.5, 33
    def draw(s):
        block(s, i, j, W, D, H, PALE, windows(PALE, H, 11, 13))
        hip_roof(s, i-.1, j-.15, W+.2, D+.3, H, 20, CLAY)
        # Central projecting pavilion, carved portal and mosaic panels.
        block(s, i+3.25, j+3.2, 3.5, 3.2, 42, SAND, windows(SAND, 42, 12, 15, gothic=True))
        hip_roof(s, i+3.15, j+3.1, 3.7, 3.4, 42, 18, CLAY)
        for k in range(5):
            inset = k*.31
            block(s, i+3.1+inset, j+6.15, 3.8-2*inset, .4, 4, PALE, z=42+k*3.7)
        def mosaic(u, v, lit):
            if lit and 2 < u < 25 and 11 < v < 27:
                if int(u) % 7 in (1, 2) and v > 19:
                    return GOLD['hi']  # halos
                return (RED, GOLD['lit'], COPPER['dark'], PALE['hi'], SLATE['dark'])[(int(u)//3+int(v)//4) % 5]
            return arch_opening(u, v, 14, 4, 5, WOOD['deep']) or stone_courses(SAND, 4, 10)(u, v, lit)
        block(s, i+3.25, j+6.4, 3.5, .1, 29, PALE, mosaic)
        # Unequal corner towers give the historical museum its castle silhouette.
        for a, b, radius, h in ((.75, 4.8, 1.1, 50), (9.3, 4.7, .9, 43), (8.7, .6, .7, 42)):
            cylinder(s, i+a, j+b, radius, radius, 0, h, PALE, windows(PALE, h, 8, 13))
            spire(s, i+a, j+b, radius+ .15, h, 20, CLAY, conical=True)
        for k in range(5):
            block(s, i+3.4, j+6.6+k*.28, 3.2, .3, 5-k, SAND)
    scene.add(i+j+W+D+2.5, draw)


def paul_klee(scene, i, j):
    """Three undulating steel hills: curved roof meshes, exposed ribs and glazed end walls."""
    W, D = 11.4, 5
    def height(u):
        # Three independent half-sine arches, with the north hill slightly taller.
        n = min(2, int(u/3.8))
        return 3+(20, 17, 14)[n]*max(0, math.sin((u-n*3.8)/3.8*math.pi))**.75
    def draw(s):
        block(s, i-.2, j-.2, W+.4, D+.4, 2, SAND)
        # End glazing follows each actual curved roof profile; no rectangular cut-out.
        for k in range(114):
            a, b = k/10, (k+1)/10
            pts = [P(s, i+a, j+D, 2), P(s, i+b, j+D, 2),
                   P(s, i+b, j+D, 2+height(b)*.775), P(s, i+a, j+D, 2+height(a)*.775)]
            poly(s, pts, lambda x, y: GLASS['dark'] if int(x) % 6 == 0 else GLASS['mid'])
        faces = []
        for a in range(57):
            for b in range(10):
                u, v, step = a*.2, b*.5, .2
                pts = [P(s, i+x, j+y, 2+height(x)*(1-.045*y))
                       for x, y in ((u, v), (u+step, v), (u+step, v+.5), (u, v+.5))]
                key = 'lit' if height(u+step) > height(u) else 'dark'
                faces.append((u+v, pts, key, a, b))
        for _, pts, key, a, b in sorted(faces):
            poly(s, pts, lambda x, y, key=key: STEEL[key])
            if b % 2 == 0:
                seg(s, pts[0], pts[1], STEEL['hi'])
        # Curved structural ribs run from the glass frontage back into the meadow.
        for v in (0, 1, 2, 3, 4, 5):
            points = [P(s, i+k*.1, j+v, 2+height(k*.1)*(1-.045*v)) for k in range(115)]
            for a, b in zip(points, points[1:]):
                seg(s, a, b, STEEL['hi'] if v % 2 else STEEL['line'])
        for u in [k*.65 for k in range(18)]:
            seg(s, P(s, i+u, j+D+.02, 2), P(s, i+u, j+D+.02, 2+height(u)*.775), STEEL['deep'])
        for z in (7, 13):
            for k in range(114):
                u = k*.1
                if z < 2+height(u)*.775:
                    seg(s, P(s, i+u, j+D+.03, z), P(s, i+u+.1, j+D+.03, z), STEEL['lit'])
    scene.add(i+j+W+D, draw)


def kirchenfeld_bridge(scene, i, j):
    """Iron double-arch bridge along +i, crossing the Aare at right angles."""
    length, width, deck = 10, 1.6, 13
    def draw(s):
        for a in (0, length/2, length):
            block(s, i+a-.3, j-.15, .6, width+.3, 9, SAND)
        for b in (0, width):
            for a in (0, 5):
                points = [P(s, i+a+k/12*5, j+b, 3+9*math.sin(k/12*math.pi)) for k in range(13)]
                for p, q in zip(points, points[1:]):
                    seg(s, p, q, SLATE['deep'], 2)
                for k in range(1, 8):
                    u = k/8*5
                    seg(s, P(s, i+a+u, j+b, 3+9*math.sin(k/8*math.pi)),
                        P(s, i+a+u, j+b, deck), SLATE['lit'])
        block(s, i, j, length, width, 2, SLATE, z=deck)
        for b in (0, width):
            seg(s, P(s, i, j+b, deck+5), P(s, i+length, j+b, deck+5), IRON)
            for k in range(11):
                seg(s, P(s, i+k, j+b, deck+2), P(s, i+k, j+b, deck+5), IRON)
    scene.add(i+j+length+width, draw)


STUDIES = [('kafigturm', kafigturm), ('zytglogge', zytglogge),
           ('federal-palace', federal_palace), ('minster', minster), ('rathaus', rathaus),
           ('nydeggkirche', nydeggkirche), ('historical-museum', historical_museum),
           ('paul-klee', paul_klee)]

if __name__ == '__main__':
    for name, builder in STUDIES:
        print(preview([lambda s, b=builder: b(s, 4, 4)], 'bern-'+name,
                      size=(260, 250), origin=(115, 125), tiles=18))
    print(preview([lambda s: townhouse(s, 4, 4, seed=0),
                   lambda s: townhouse(s, 8, 4, seed=1),
                   lambda s: townhouse(s, 8, 8, floors=2, seed=11)], 'bern-houses',
                  size=(230, 190), origin=(105, 45), tiles=17))
