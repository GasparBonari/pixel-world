"""Prague's Gothic sandstone, Baroque stucco and red tiles, built in (i, j, z).

Run directly for eight landmark studies and a house study, each at integer 4×.
Geographic anchors and architectural references are recorded in DEVELOPMENT_PLAN.md.
"""
import math

import iso
from iso import rgb
from landmarks_paris import P, seg, poly, corners, facade, egg_dome, stone_bridge, preview, GLASS
from landmarks_iberia import hip_roof, stone_courses, arch_opening, palette_of, tones
from landmarks_denmark import spire
from landmarks_italy import cylinder

STONE = tones('#F2E5C9', '#D4C4A4', '#B6A586', '#92836B', '#625747', '#A79779', '#40392F')
PALE = tones('#FFF2D9', '#EAD9B6', '#D2BD96', '#AC9571', '#796647', '#BEAA86', '#4C402F')
GOTHIC = tones('#C4BAB0', '#9E9386', '#81766C', '#60574F', '#403C38', '#73695E', '#302D2A')
CLAY = tones('#F2AF83', '#D1805C', '#B46044', '#8C4434', '#60302A', '#A1553D', '#492923')
SLATE = tones('#ABAEB8', '#79818C', '#606975', '#434C59', '#303843', '#56606D', '#272F39')
COPPER = tones('#BDD4B8', '#89AF97', '#6B927C', '#4B6E5E', '#304D40', '#5F806D', '#263B31')
GOLD = tones('#FFF3B8', '#EBC76B', '#CBA24E', '#A27732', '#715124', '#B58C3D', '#503B22')
STEEL = tones('#E2E7E3', '#BCCDD0', '#94ADB4', '#63838F', '#3E5B6A', '#7E9BA5', '#2C424D')
WALLS = [rgb(c) for c in ('#E5C38C', '#D3A59B', '#D9DEC1', '#ECDCC2', '#B7CCC8', '#DBAE78')]
WATER = (rgb('#4B8790'), rgb('#386C7C'), rgb('#C3E0DA'))
IRON, WOOD = rgb('#333B3B'), rgb('#674736')


def block(s, i, j, wi, wj, height, material=STONE, pattern=None, z=0):
    cover = facade(s, i, j, wi, wj, height, pattern or stone_courses(material, 4, 11),
                   palette=material, z0=z)
    iso.fill(s, list(corners(s, i, j, wi, wj, z+height)), lambda x, y: material['mid'], cover)
    iso.outline(s, cover, material['outline'])


def windows(material, height, bay=10, floor=13, gothic=False):
    joints = stone_courses(material, 5, 13)
    def pattern(u, v, lit):
        c, v = int(u) % bay, int(v)
        level, trim = v % floor, material['hi' if lit else 'mid']
        if v < 2 or v in (height-1, height-3) or level == 0:
            return trim
        head = floor-3-abs(c-bay/2)*(1.6 if gothic else .2)
        if 2 <= c <= bay-2 and 3 <= level <= head and v < height-4:
            if c in (2, bay-2, bay//2) or level in (3, 6, int(head)):
                return trim
            return STEEL['deep'] if gothic else GLASS['mid' if lit else 'dark']
        return joints(u, v, lit)
    return pattern


def band(s, i, j, wi, wj, z, material=PALE):
    facade(s, i-.06, j-.06, wi+.12, wj+.12, 2,
           lambda u, v, lit: material['hi' if lit else 'dark'], palette=material, z0=z)


def dial(s, i, j, z, radius=5, astronomical=False):
    """Concentric rings, zodiac and hands mapped into the lit supporting wall plane."""
    def point(u, v):
        return P(s, i+u/8, j, z+v)
    for u in range(-radius, radius+1):
        for v in range(-radius, radius+1):
            r = math.hypot(u, v)
            if r <= radius:
                color = GOLD['lit'] if r > radius-1 or astronomical and abs(r-radius*.6) < .7 else IRON
                if astronomical and r < radius*.5:
                    color = STEEL['dark'] if v > 0 else CLAY['dark']
                s.put(*point(u, v), color)
    for n in range(12):
        a = n*math.tau/12
        s.put(*point(math.cos(a)*(radius-1), math.sin(a)*(radius-1)), PALE['hi'])
    seg(s, point(0, 0), point(-radius*.6, radius*.3), GOLD['hi'])
    seg(s, point(0, 0), point(radius*.15, radius*.8), GOLD['hi'])


def figure(s, i, j, z, material=GOTHIC, height=7):
    """Solid carved saint: plinth, flared robe, head, shoulders and bent arm."""
    block(s, i-.2, j-.2, .4, .4, 2, material, z=z)
    cylinder(s, i, j, .17, .13, z+2, height*.58, material)
    cylinder(s, i, j, .13, .13, z+height*.8, height*.2, material)
    poly(s, [P(s, i-.15, j, z+height*.7), P(s, i+.28, j, z+height*.65),
             P(s, i+.25, j, z+height*.4), P(s, i, j, z+height*.5)], lambda x, y: material['lit'])


def pointed_roof(s, ci, cj, radius, base, rise, material=SLATE):
    faces = []
    for n in range(8):
        a, b = n*math.tau/8, (n+1)*math.tau/8
        lit = math.sin((a+b)/2)-.5*math.cos((a+b)/2) > 0
        points = [P(s, ci+radius*math.cos(t), cj+radius*math.sin(t), base) for t in (a, b)]
        points.append(P(s, ci, cj, base+rise))
        faces.append((math.cos(a)+math.sin(a), points, lit))
    for _, points, lit in sorted(faces):
        poly(s, points, lambda x, y, lit=lit: material['line'] if int(y) % 4 == 0 else material['lit' if lit else 'dark'])
        seg(s, points[0], points[2], material['hi' if lit else 'deep'])
    seg(s, P(s, ci, cj, base+rise), P(s, ci, cj, base+rise+7), material['outline'])


def gothic_tower(s, i, j, width, height, rise, material=GOTHIC, turrets=False, roof=SLATE):
    block(s, i, j, width, width, height, material, windows(material, height, 8, 17, True))
    for z in (height*.45, height-4):
        band(s, i, j, width, width, z, material)
    pointed_roof(s, i+width/2, j+width/2, width*.76, height, rise, roof)
    for a, b in ((0, 0), (width, 0), (0, width), (width, width)):
        block(s, i+a-.13, j+b-.13, .26, .26, 8, material, z=height-3)
        pointed_roof(s, i+a, j+b, .25 if turrets else .15, height+5, 16 if turrets else 8, roof)
    # Týn's two tiers of four roof turrets, rather than a generic single pyramid.
    if turrets:
        for a, b in ((-.36, -.36), (.36, -.36), (-.36, .36), (.36, .36)):
            pointed_roof(s, i+width/2+a, j+width/2+b, .19, height+rise*.46, 14)


def prague_castle(scene, i, j):
    """Palace courts around St Vitus: twin west spires, rose, buttresses and south clock tower."""
    W, D = 13, 8
    def draw(s):
        block(s, i-.5, j-.5, W+1, D+1, 5, STONE)
        # Low cream palace wings enclose the cathedral without hiding its lower walls.
        for a, b, wi, wj in ((i, j, W, 1.2), (i, j, 1.2, D), (i+W-1.2, j, 1.2, D)):
            block(s, a, b, wi, wj, 18, PALE, windows(PALE, 18, 8, 12), z=5)
            hip_roof(s, a-.1, b-.1, wi+.2, wj+.2, 23, 9, CLAY)
        a, b, wi, wj, H = i+3, j+1.7, 5.3, 5.6, 42
        block(s, a, b, wi, wj, H, STONE, windows(STONE, H, 9, 23, True), z=5)
        hip_roof(s, a, b, wi, wj, H+5, 19, SLATE)
        # Projected flying buttresses and pinnacles along the long south wall.
        for n in range(5):
            aa = a+.4+n*1.05
            block(s, aa, b+wj, .28, .8, 23, STONE, z=5)
            poly(s, [P(s, aa, b+wj+.8, 28), P(s, aa, b+wj, 43),
                     P(s, aa+.2, b+wj, 40), P(s, aa+.2, b+wj+.8, 25)], lambda x, y: STONE['hi'])
            spire(s, aa+.1, b+wj+.4, .17, 29, 9, STONE)
        # West front and its stone rose in its own wall plane.
        def front(u, v, lit):
            if not lit:
                return windows(STONE, 43, 8, 20, True)(u, v, lit)
            rr = math.hypot(u-21, v-29)
            if rr < 6:
                return STONE['hi'] if rr > 4.8 or int(u) == 21 or int(v) == 29 else STEEL['dark'] if int(u+v) % 3 else GOLD['mid']
            for c in (8, 21, 34):
                opening = arch_opening(u, v, c, 3.5, 11-abs(u-c), STONE['deep'])
                if opening:
                    return opening
            return stone_courses(STONE)(u, v, lit)
        block(s, a, b+wj-.6, wi, .7, 43, STONE, front, z=5)
        for aa in (a, a+wi-1.3):
            gothic_tower(s, aa, b+wj-1, 1.3, 63, 27, STONE)
        # Great South Tower's Renaissance copper crown differs from the Gothic pair.
        aa, bb = a+wi+.25, b+2.6
        block(s, aa, bb, 1.8, 1.8, 65, STONE, windows(STONE, 65, 8, 18, True))
        dial(s, aa+.9, bb+1.83, 54, 5)
        band(s, aa, bb, 1.8, 1.8, 64)
        spire(s, aa+.9, bb+.9, 1.15, 67, 24, COPPER, onion=True)
    scene.add(i+j+W+D, draw)


def st_nicholas(scene, i, j):
    """Malá Strana's Baroque church: ribbed green dome and separate onion-capped bell tower."""
    def draw(s):
        block(s, i, j, 6.8, 4.8, 30, PALE, windows(PALE, 30, 10, 15))
        hip_roof(s, i, j, 6.8, 4.8, 30, 10, CLAY)
        ci, cj = i+2.5, j+1.2
        cylinder(s, ci, cj, 1.45, 1.45, 33, 14, PALE,
                 lambda k, v, lit: STEEL['deep'] if k % 5 in (2, 3) and 3 < v < 11 else None)
        for n in range(12):
            a = n*math.tau/12
            aa, bb = ci+1.46*math.cos(a), cj+1.46*math.sin(a)
            if math.sin(a)-.5*math.cos(a) > -.4:
                seg(s, P(s, aa, bb, 36), P(s, aa, bb, 44), PALE['dark'], 2)
        x, y = P(s, ci, cj, 47)
        egg_dome(s, x, y, 17, 20, (COPPER['lit'], COPPER['dark'], COPPER['outline']))
        for f in (-.7, -.35, 0, .35, .7):
            points = [(x+17*f*math.cos(n/16*math.pi/2), y-20*math.sin(n/16*math.pi/2)) for n in range(17)]
            for p, q in zip(points, points[1:]):
                seg(s, p, q, COPPER['hi'] if f < 0 else COPPER['deep'])
        spire(s, ci, cj, .36, 67, 14, COPPER, onion=True)
        # Pilastered west entrance with scroll shoulders and round-headed door.
        def entrance(u, v, lit):
            if lit and v < 18:
                opening = arch_opening(u, v, 14, 4, 12, WOOD)
                if opening:
                    return opening
            return (PALE['hi' if lit else 'mid'] if int(u) % 9 in (0, 1) or int(v) in (21, 32)
                    else windows(PALE, 34, 9, 17)(u, v, lit))
        block(s, i+.4, j+4.1, 3.5, 1.1, 34, PALE, entrance)
        hip_roof(s, i+.4, j+4.1, 3.5, 1.1, 34, 8, COPPER)
        aa, bb = i+5.7, j+3.2
        block(s, aa, bb, 1.8, 1.8, 60, PALE, windows(PALE, 60, 8, 18))
        dial(s, aa+.9, bb+1.83, 45, 5)
        band(s, aa, bb, 1.8, 1.8, 58)
        spire(s, aa+.9, bb+.9, 1.2, 62, 26, COPPER, onion=True)
    scene.add(i+j+13, draw)


def charles_bridge(scene, i, j):
    """Stone arches, cutwaters, sculpted saints and the Old Town Gothic gateway."""
    length, width = 14, 2.3
    stone_bridge(scene, i, j, length, width, deck=10)
    def draw(s):
        for n in range(1, 6):
            b = j+n*2.2
            for a in (i+.1, i+width-.1):
                block(s, a-.18, b-.18, .36, .36, 3, GOTHIC, z=10)
                figure(s, a, b, 13, height=6)
            poly(s, [P(s, i+width, b-.4, 0), P(s, i+width+.7, b, 0),
                     P(s, i+width, b+.4, 0)], lambda x, y: STONE['dark'])
        a, b = i-.2, j-.8  # eastern, Old Town end of the +j crossing
        def gate(u, v, lit):
            if lit:
                opening = arch_opening(u, v, 10.8, 5.5, 15-abs(u-10.8)*.5, GOTHIC['deep'])
                if opening and v < 23:
                    return opening
            return windows(GOTHIC, 49, 9, 16, True)(u, v, lit)
        block(s, a, b, 2.7, 2.5, 49, GOTHIC, gate)
        band(s, a, b, 2.7, 2.5, 30, STONE)
        hip_roof(s, a-.1, b-.1, 2.9, 2.7, 49, 35, SLATE)
        for aa in (a+.2, a+2.4):
            spire(s, aa, b+2.2, .19, 49, 15, SLATE)
        for aa in (a+.6, a+1.35, a+2.1):
            figure(s, aa, b+2.52, 31, PALE, 6)
    scene.add(i+j+width+length+1, draw)


def old_town_hall(scene, i, j):
    """Gothic watchtower and oriel chapel, paired Orloj/calendar dials and apostle windows."""
    def draw(s):
        block(s, i, j, 6.5, 3.6, 27, PALE, windows(PALE, 27, 9, 13))
        hip_roof(s, i-.1, j-.1, 6.7, 3.8, 27, 12, CLAY)
        a, b = i+3.5, j+1.2
        gothic_tower(s, a, b, 2.4, 68, 27, STONE, roof=COPPER)
        dial(s, a+1.2, b+2.43, 56, 6)
        # Orloj is on the south wall near the tower foot, separate from the tower clock.
        block(s, a-.05, b+2.35, 2.5, .3, 28, GOTHIC,
              lambda u, v, lit: STONE['hi'] if int(u) in (1, 18) or int(v) in (1, 27) else None)
        dial(s, a+1.2, b+2.68, 19, 7, True)
        dial(s, a+1.2, b+2.68, 6, 5)
        for aa in (a+.75, a+1.5):
            block(s, aa, b+2.69, .4, .1, 4, PALE,
                  lambda u, v, lit: STEEL['deep'] if 1 < u < 3 and v > 1 else None, z=28)
        for aa in (a+.1, a+2.25):
            figure(s, aa, b+2.7, 18, PALE, 5)
        # Projecting Gothic chapel bay, mullions and peaked canopy.
        block(s, i+1, j+3.45, 1.2, .7, 17, STONE, windows(STONE, 17, 6, 16, True), z=9)
        hip_roof(s, i+.9, j+3.35, 1.4, .9, 26, 9, SLATE)
    scene.add(i+j+11, draw)


def tyn_church(scene, i, j):
    """Unequal Adam/Eve towers, eight-turret Gothic crowns and gilded Madonna gable."""
    def draw(s):
        block(s, i, j, 6.8, 4.6, 36, STONE, windows(STONE, 36, 10, 22, True))
        hip_roof(s, i, j, 6.8, 4.6, 36, 18, SLATE)
        for a, height in ((i, 62), (i+4.8, 66)):
            gothic_tower(s, a, j+3, 2, height, 43, STONE, True)
        # A deep traceried front window below the central, stepped and gilded gable.
        block(s, i+2, j+3.8, 2.8, .9, 40, STONE, windows(STONE, 40, 11, 29, True))
        for k in range(5):
            block(s, i+2+k*.21, j+4.4, 2.8-k*.42, .3, 3, PALE, z=40+k*3)
        figure(s, i+3.4, j+4.75, 45, GOLD, 8)
        for n in range(12):
            a = n*math.tau/12
            seg(s, P(s, i+3.4+.5*math.cos(a), j+4.76, 49+5*math.sin(a)),
                P(s, i+3.4+.65*math.cos(a), j+4.76, 49+6*math.sin(a)), GOLD['lit'])
    scene.add(i+j+13, draw)


def powder_gate(scene, i, j):
    """Soot-dark Gothic gate: pointed passage, sculptural niches, gallery and steep slate crown."""
    def draw(s):
        def wall(u, v, lit):
            centre = 15 if lit else 13
            if abs(u-centre) < 6 and v < 19-abs(u-centre)*.7:
                return GOTHIC['deep']
            return windows(GOTHIC, 57, 10, 19, True)(u, v, lit)
        block(s, i, j, 3.8, 3.2, 57, GOTHIC, wall)
        for z in (21, 40, 53, 57):
            band(s, i, j, 3.8, 3.2, z, STONE)
        hip_roof(s, i-.2, j-.2, 4.2, 3.6, 59, 38, SLATE)
        for a, b in ((i, j), (i+3.8, j), (i, j+3.2), (i+3.8, j+3.2)):
            pointed_roof(s, a, b, .25, 56, 17)
        for a in (i+.8, i+1.9, i+3):
            figure(s, a, j+3.22, 27, PALE, 8)
            spire(s, a, j+3.25, .2, 36, 6, STONE)
        # Gallery's balustrade follows the sloped wall plane.
        for n in range(15):
            a = i+n*3.8/14
            seg(s, P(s, a, j+3.25, 54), P(s, a, j+3.25, 57), GOTHIC['deep'])
    scene.add(i+j+8, draw)


def national_theatre(scene, i, j):
    """Renaissance loggia, gilded blue roof, rooftop balustrade and paired horse teams."""
    def draw(s):
        block(s, i, j, 8, 5.6, 34, PALE, windows(PALE, 34, 10, 15))
        # Deep upper arcade is drawn in the lit wall only, with piers left intact.
        block(s, i+.3, j+4.8, 7.4, 1, 30, PALE,
              lambda u, v, lit: (arch_opening(u % 10, v-17, 5, 3, 6, STONE['deep'])
                                 if lit and 17 < v < 27 else None)
              or (PALE['hi' if lit else 'mid'] if int(v) in (15, 29) or int(u) % 10 in (0, 1)
                  else windows(PALE, 30, 10, 15)(u, v, lit)))
        band(s, i, j, 8, 5.6, 34)
        # The theatre's distinctive raised barrel roof has gilded ribs and a flat ridge.
        for n in range(12):
            a, b = -math.pi/2+n*math.pi/12, -math.pi/2+(n+1)*math.pi/12
            points = [P(s, aa, j+2.8+2.3*math.sin(t), 36+17*math.cos(t))
                      for aa, t in ((i+.5, a), (i+7.5, a), (i+7.5, b), (i+.5, b))]
            poly(s, points, lambda x, y, n=n: SLATE['line'] if int(x+y) % 9 == 0 else SLATE['lit' if n > 5 else 'dark'])
        for aa in (i+.5, i+1.5, i+3, i+4.5, i+6, i+7.5):
            points = [P(s, aa, j+2.8+2.3*math.sin(-math.pi/2+n*math.pi/24),
                        36+17*math.cos(-math.pi/2+n*math.pi/24)) for n in range(25)]
            for p, q in zip(points, points[1:]):
                seg(s, p, q, GOLD['lit'])
        for edge, length, along_i in ((j+.4, 7, True), (i+7.6, 4.6, False)):
            for n in range(int(length*4)):
                a, b = (i+.5+n/4, edge) if along_i else (edge, j+.5+n/4)
                seg(s, P(s, a, b, 35), P(s, a, b, 39), GOLD['lit'])
        # Trigas: three filled horses with legs, necks, heads and a chariot driver per group.
        for a in (i+.5, i+6.5):
            for n in range(3):
                b = j+.6+n*.45
                block(s, a, b, .8, .27, 3, GOTHIC, z=41)
                for aa in (a+.1, a+.65):
                    block(s, aa, b, .12, .14, 4, GOTHIC, z=37)
                block(s, a+.6, b, .23, .25, 4, GOTHIC, z=43)
                block(s, a+.65, b-.08, .42, .27, 2, GOTHIC, z=46)
            figure(s, a-.15, j+1.1, 42, GOTHIC, 8)
        for n in range(4):
            figure(s, i+1.3+n*1.8, j+5.62, 35, PALE, 6)
    scene.add(i+j+15, draw)


def dancing_house(scene, i, j):
    """Gehry/Milunić: pinched glass Ginger, wavy Fred with offset windows and metal Medusa."""
    def draw(s):
        block(s, i+3, j-.8, 4, 2.6, 48, PALE, windows(PALE, 48, 9, 9))
        band(s, i+3, j-.8, 4, 2.6, 48)
        # Fred's irregular ring sections are faceted solids; windows follow those same faces.
        ci, cj, H = i+4.4, j+2.4, 53
        levels = [(z, 1.55+.13*math.sin(z*.23), .22*math.sin(z*.14)) for z in range(0, H+1, 6)]
        for (z0, r0, off0), (z1, r1, off1) in zip(levels, levels[1:]):
            faces = []
            for n in range(12):
                a, b = n*math.tau/12, (n+1)*math.tau/12
                points = [P(s, ci+off+r*math.cos(t), cj+r*math.sin(t), z)
                          for z, r, off, t in ((z0, r0, off0, a), (z0, r0, off0, b),
                                               (z1, r1, off1, b), (z1, r1, off1, a))]
                lit = math.sin((a+b)/2)-.5*math.cos((a+b)/2) > 0
                faces.append((math.cos(a)+math.sin(a), points, lit))
            for _, points, lit in sorted(faces):
                poly(s, points, lambda x, y, lit=lit: PALE['lit' if lit else 'dark'])
                # Offset framed windows sit fully inside each projected segment.
                def inset(f, t):
                    low = tuple(points[0][k]+f*(points[1][k]-points[0][k]) for k in (0, 1))
                    high = tuple(points[3][k]+f*(points[2][k]-points[3][k]) for k in (0, 1))
                    return tuple(low[k]+t*(high[k]-low[k]) for k in (0, 1))
                frame = [inset(f, t) for f, t in ((.2, .12), (.8, .12), (.8, .88), (.2, .88))]
                poly(s, frame, lambda x, y: STEEL['deep'])
                for p, q in zip(frame, frame[1:]+frame[:1]):
                    seg(s, p, q, PALE['hi' if lit else 'mid'])
        cylinder(s, ci, cj, 1.65, 1.65, 53, 2, STONE)
        # Irregular mesh crown, a volume with interlaced projected steel members.
        for n in range(14):
            a = n*math.tau/14
            foot = P(s, ci+.8*math.cos(a), cj+.8*math.sin(a), 55)
            tip = P(s, ci+.55*math.cos(a+.5), cj+.55*math.sin(a+.5), 64+n % 3)
            seg(s, foot, tip, STEEL['dark' if n % 2 else 'lit'])
            seg(s, tip, P(s, ci+.8*math.cos(a+1.4), cj+.8*math.sin(a+1.4), 55), STEEL['deep'])
        # Ginger leans into Fred and narrows at the waist; triangulated glass has real depth.
        ci, cj = i+1.25, j+3.4
        profile = [(7, 1.25, -.4), (18, .87, -.2), (30, .72, 0), (42, 1.05, .2), (51, 1.38, .3)]
        for (z0, r0, off0), (z1, r1, off1) in zip(profile, profile[1:]):
            faces = []
            for n in range(12):
                a, b = n*math.tau/12, (n+1)*math.tau/12
                points = [P(s, ci+off+r*math.cos(t), cj+r*math.sin(t), z)
                          for z, r, off, t in ((z0, r0, off0, a), (z0, r0, off0, b),
                                               (z1, r1, off1, b), (z1, r1, off1, a))]
                lit = math.sin((a+b)/2)-.5*math.cos((a+b)/2) > 0
                faces.append((math.cos(a)+math.sin(a), points, lit))
            for _, points, lit in sorted(faces):
                poly(s, points, lambda x, y, lit=lit: STEEL['lit' if lit else 'dark'])
                for p, q in zip(points, points[1:]+points[:1]):
                    seg(s, p, q, STEEL['deep'])
                seg(s, points[0], points[2], STEEL['hi' if lit else 'mid'])
        for n in range(6):
            a = n*math.tau/6
            seg(s, P(s, ci+1.3*math.cos(a), cj+1.3*math.sin(a), 8),
                P(s, ci+1.5*math.cos(a), cj+1.5*math.sin(a), 0), STONE['dark'], 2)
    scene.add(i+j+13, draw)


def townhouse(scene, i, j, wi, wj, floors, seed):
    """Prague stucco: framed panes, shop arches, carved hoods, iron guards and Baroque gables."""
    wall, H = palette_of(WALLS[seed % len(WALLS)]), floors*11+3
    def pattern(u, v, lit):
        c, v = int(u) % 9, int(v)
        level, trim = (v-11) % 11, PALE['lit' if lit else 'dark']
        if v < 3:
            return STONE['mid' if lit else 'deep']
        if v in (10, H-1, H-3):
            return trim
        if v < 10:
            return arch_opening(c, v, 4.5, 2.8, 5, WOOD if seed % 3 else STEEL['deep'])
        if 2 <= c <= 7 and 2 <= level <= 8 and v < H-4:
            return trim if c in (2, 4, 7) or level in (2, 5, 8) else GLASS['mid' if lit else 'dark']
        if level in (1, 9) and 1 <= c <= 8:
            return trim
        if seed % 3 == 0 and level == 0 and c in (2, 4, 6):
            return IRON
        if seed % 4 == 0 and v > 11 and int(u+v) % 13 == 0:
            return wall['line']  # restrained sgraffito
        return None
    def draw(s):
        block(s, i, j, wi, wj, H, wall, pattern)
        hip_roof(s, i-.12, j-.12, wi+.24, wj+.24, H, 13, CLAY)
        if seed % 3 == 0:
            # Curved Baroque gable profile extruded back into the roof.
            steps = [(0, 0), (.08, 2), (.23, 3), (.28, 7), (.38, 9), (.43, 13),
                     (.57, 13), (.62, 9), (.72, 7), (.77, 3), (.92, 2), (1, 0)]
            front = [P(s, i+wi*t, j+wj+.05, H+z) for t, z in steps]
            back = [P(s, i+wi*t, j+wj-.2, H+z) for t, z in steps]
            for n in range(len(steps)-1):
                poly(s, [front[n], back[n], back[n+1], front[n+1]], lambda x, y: wall['dark'])
            poly(s, front, lambda x, y: wall['lit'])
            for p, q in zip(front, front[1:]):
                seg(s, p, q, PALE['hi'])
            block(s, i+wi*.42, j+wj+.06, wi*.16, .08, 4, PALE,
                  lambda u, v, lit: STEEL['deep'] if 1 < u < 3 and v > 1 else None, z=H+4)
        else:
            block(s, i+wi*.4, j+wj-.7, .6, .55, 5, PALE,
                  lambda u, v, lit: GLASS['dark'] if 1 < u < 4 and 1 < v < 4 else None, z=H+3)
            hip_roof(s, i+wi*.4-.08, j+wj-.78, .76, .71, H+8, 4, CLAY)
        block(s, i+.5, j+.5, .4, .4, 9, PALE, z=H+6)
        block(s, i+.44, j+.44, .52, .52, 2, STONE, z=H+15)
    scene.add(i+j+wi+wj+1, draw)


if __name__ == '__main__':
    plots = [('castle', prague_castle, (300, 250), (135, 110)),
             ('st-nicholas', st_nicholas, (220, 225), (90, 110)),
             ('charles-bridge', charles_bridge, (260, 230), (170, 95)),
             ('old-town-hall', old_town_hall, (220, 220), (100, 105)),
             ('tyn', tyn_church, (230, 230), (100, 115)),
             ('powder-gate', powder_gate, (200, 220), (100, 115)),
             ('national-theatre', national_theatre, (240, 215), (100, 85)),
             ('dancing-house', dancing_house, (220, 210), (95, 90))]
    for name, builder, size, origin in plots:
        print(preview([lambda s, build=builder: build(s, 3, 3)], f'prague-{name}',
                      size=size, origin=origin, tiles=18))
    print(preview([lambda s: townhouse(s, 2, 2, 3, 3, 3, 0),
                   lambda s: townhouse(s, 7, 2, 3, 3, 4, 1),
                   lambda s: townhouse(s, 7, 7, 3, 3, 2, 3)], 'prague-houses',
                  size=(250, 220), origin=(115, 75), tiles=17))
