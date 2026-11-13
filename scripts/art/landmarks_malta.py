"""Valletta: honey limestone, gallariji, bastions and eight projected 3D landmarks.

Run directly for individual 4× studies. Real sites, composition and references are
recorded in DEVELOPMENT_PLAN.md. Every architectural detail follows its wall plane.
"""

import math

import iso
from iso import rgb, h01
from landmarks_paris import P, seg, poly, corners, facade, preview
from landmarks_iberia import hip_roof, stone_courses, arch_opening, palette_of, tones
from landmarks_belgium import dome
from landmarks_italy import cylinder


STONE = tones('#FFF0C9', '#E8CF99', '#CFB57F', '#AD9363', '#7D6849', '#B8A06E', '#51412C')
PALE = tones('#FFF6DA', '#F2DEB2', '#DEC593', '#BDA372', '#8C744F', '#C7AD7D', '#59472E')
ROOF = tones('#F6E5BD', '#D7C397', '#BCAA82', '#978663', '#716044', '#AE9A72', '#4E422F')
GREEN = tones('#9EB995', '#527B59', '#3D6047', '#294737', '#1E332B', '#3F624A', '#182D24')
RED = tones('#D89C83', '#A34F3C', '#874331', '#653328', '#48291F', '#8D4B36', '#36251F')
BLUE = tones('#A6BEC3', '#5D8793', '#456875', '#304D5D', '#233B49', '#4C727E', '#1C303D')
IRON = rgb('#3B4138')
BRONZE = tones('#A5AB87', '#7A8667', '#5D6B51', '#3F503F', '#2D3A2E', '#627052', '#243026')
WALLS = [rgb(c) for c in ('#E4CB99', '#D8BD87', '#EBD9B1', '#D3B57D', '#E2C79E', '#CDB78E')]
WATER = (rgb('#3C8092'), rgb('#2C647D'), rgb('#B6DDE0'))
GLASS = {'mid': rgb('#668389'), 'dark': rgb('#344D54'), 'hi': rgb('#A7C6C5')}


def block(s, i, j, wi, wj, height, material=STONE, pattern=None, z=0):
    cover = facade(s, i, j, wi, wj, height,
                   pattern or stone_courses(material, 5, 11), palette=material, z0=z)
    iso.fill(s, list(corners(s, i, j, wi, wj, z+height)),
             lambda x, y: material['mid'] if (int(x)+int(y)) % 13 else material['line'], cover)
    iso.outline(s, cover, material['outline'])


def band(s, i, j, wi, wj, z, material=PALE, height=2):
    facade(s, i, j, wi, wj, height,
           lambda u, v, lit: material['hi' if lit else 'mid'] if v > height-1
           else material['lit' if lit else 'dark'], palette=material, z0=z)


def flat_roof(s, i, j, wi, wj, z):
    """Maltese deffun roof: warm mottled surface, low parapets and stone copings."""
    poly(s, list(corners(s, i, j, wi, wj, z)),
         lambda x, y: ROOF['lit'] if h01(x, y, 421) > .17 else ROOF['line'])
    for a, b, w, d in ((i, j, wi, .16), (i, j, .16, wj),
                        (i, j+wj-.16, wi, .16), (i+wi-.16, j, .16, wj)):
        block(s, a, b, w, d, 2, PALE, z=z)
        band(s, a-.03, b-.03, w+.06, d+.06, z+2, height=1)


def windows(material, height, bay=11, floor=15, arched=False):
    courses = stone_courses(material, 5, 12)
    def pattern(u, v, lit):
        c, v = int(u) % bay, int(v)
        level = v % floor
        trim = PALE['lit' if lit else 'dark']
        if v < 2 or v in (height-2, height-1) or level == 0:
            return trim
        head = floor-3-abs(c-bay/2)*(.65 if arched else 0)
        if 3 <= c <= bay-3 and 4 <= level <= head and v < height-3:
            if c in (3, bay//2, bay-3) or level in (4, 8, int(head)):
                return trim
            return GLASS['mid' if lit else 'dark']
        if level == 3 and 2 <= c <= bay-2:
            return trim
        return courses(u, v, lit)
    return pattern


def pediment(s, i, j, width, z, rise):
    front = [P(s, i, j, z), P(s, i+width, j, z), P(s, i+width/2, j, z+rise)]
    back = [P(s, i, j-.24, z), P(s, i+width, j-.24, z), P(s, i+width/2, j-.24, z+rise)]
    poly(s, [front[1], back[1], back[2], front[2]], lambda x, y: STONE['dark'])
    poly(s, front, lambda x, y: PALE['lit'] if (int(x)+int(y)) % 9 else STONE['line'])
    for a, b in zip(front, front[1:]+front[:1]):
        seg(s, a, b, PALE['hi'], 2)


def flag(s, i, j, z):
    seg(s, P(s, i, j, z), P(s, i, j, z+15), IRON)
    for k, color in enumerate((PALE['hi'], RED['lit'])):
        poly(s, [P(s, i+k*.35, j, z+14), P(s, i+(k+1)*.35, j, z+13.6),
                 P(s, i+(k+1)*.35, j, z+8), P(s, i+k*.35, j, z+8.4)], lambda x, y, c=color: c)
    # George Cross in the white canton.
    x, y = P(s, i+.12, j, z+12)
    seg(s, (x-1, y), (x+1, y), ROOF['dark'])
    seg(s, (x, y-1), (x, y+1), ROOF['dark'])


def gallarija(s, i, j, width, base, material=GREEN, side=False):
    """Enclosed timber balcony: projecting box, glazing, panelling and stone corbels."""
    wi, wj = (.52, width) if side else (width, .52)
    def glazed(u, v, lit):
        c, v = int(u) % 5, int(v)
        if v < 3:
            return material['mid' if lit else 'dark'] if c in (1, 3) else material['deep']
        if c in (0, 1, 4) or v in (3, 7, 11):
            return material['lit' if lit else 'dark']
        return GLASS['mid' if lit else 'dark'] if v < 11 else material['lit' if lit else 'dark']
    block(s, i, j, wi, wj, 12, material, glazed, z=base)
    band(s, i-.07, j-.07, wi+.14, wj+.14, base+12, material, 2)
    for fraction in (.15, .8):
        a, b = (i+.2, j+wj*fraction) if side else (i+wi*fraction, j+.2)
        block(s, a, b, .22, .22, 3, PALE, z=base-3)


def townhouse(scene, i, j, wi=2.5, wj=3, floors=3, seed=0):
    material, height = palette_of(WALLS[seed % len(WALLS)]), floors*11+3
    wood = (GREEN, RED, BLUE)[seed % 3]
    courses = stone_courses(material, 5, 13)
    def pattern(u, v, lit):
        c, v = int(u) % 10, int(v)
        level = (v-11) % 11
        trim = PALE['lit' if lit else 'dark']
        if v < 2:
            return STONE['mid' if lit else 'deep']
        if v in (11, height-1, height-3):
            return trim
        if v < 11:
            if 3 <= c <= 7 and v < 9:
                if v == 8 or c in (3, 7):
                    return trim
                return wood['lit' if lit else 'dark'] if seed % 3 else GLASS['dark']
            return courses(u, v, lit)
        if 3 <= c <= 7 and 2 <= level <= 8 and v < height-4:
            if c in (3, 5, 7) or level in (2, 5, 8):
                return trim
            return GLASS['mid' if lit else 'dark']
        if level == 1 and 2 <= c <= 8:
            return trim
        if seed % 4 == 0 and level == 0 and c in (3, 5, 7):
            return IRON
        return courses(u, v, lit)
    def draw(s):
        block(s, i, j, wi, wj, height, material, pattern)
        band(s, i-.08, j-.08, wi+.16, wj+.16, height-1)
        flat_roof(s, i, j, wi, wj, height)
        gallarija(s, i+.35, j+wj-.04, min(1.65, wi-.5), 12, wood)
        if seed % 3 == 0:
            gallarija(s, i+wi-.03, j+.6, min(1.4, wj-.7), 12, wood, True)
        # Small masonry flue and capped chimney; taller stair-room on selected roofs.
        block(s, i+.35, j+.4, .34, .34, 6, STONE, z=height)
        band(s, i+.3, j+.35, .44, .44, height+6, height=1)
        if seed % 4 == 1:
            block(s, i+wi-.95, j+.3, .7, .85, 6, material,
                  lambda u, v, lit: wood['dark'] if 1 < u < 4 and v < 5 else None, z=height)
            flat_roof(s, i+wi-.95, j+.3, .7, .85, height+6)
    scene.add(i+j+wi+wj+1, draw)


def st_john(scene, i, j):
    """Mannerist twin belfries, Tuscan portal balcony and three right-hand clocks."""
    def draw(s):
        block(s, i+.2, j, 5.6, 7, 37, STONE, windows(STONE, 37, 14, 19, True))
        hip_roof(s, i+.15, j-.05, 5.7, 7.1, 37, 8, ROOF)
        def front(u, v, lit):
            if not lit:
                return windows(STONE, 37, 12, 19)(u, v, lit)
            c = u-24
            if v < 22:
                portal = arch_opening(c, v, 0, 5, 14, RED['dark'])
                if portal:
                    return portal
            if abs(c) in (8, 9, 13, 14) and 3 < v < 25:
                return PALE['hi']
            if 24 <= v <= 26 and abs(c) <= 17:
                return PALE['lit'] if v != 25 else STONE['deep']
            if abs(c) <= 3 and 28 < v < 34:
                return GLASS['dark'] if abs(c) != 0 else PALE['lit']
            return stone_courses(STONE, 6, 13)(u, v, lit)
        block(s, i, j+5.8, 6, 1.4, 37, STONE, front)
        pediment(s, i+1.65, j+7.22, 2.7, 37, 7)
        for a in (i-.15, i+4.6):
            def tower_face(u, v, lit):
                c = int(u) % 12
                if v in (25, 27, 45, 47, 65, 67):
                    return PALE['lit' if lit else 'dark']
                if 48 < v < 63:
                    opening = arch_opening(c, v-48, 6, 3.3, 8, IRON)
                    if opening:
                        return opening
                if c in (1, 11):
                    return PALE['lit' if lit else 'mid']
                return stone_courses(STONE, 6, 14)(u, v, lit)
            block(s, a, j+5.6, 1.55, 1.8, 68, STONE, tower_face)
            band(s, a-.13, j+5.47, 1.81, 2.06, 67, height=3)
            # Bells are filled bronze bodies, not empty dark belfries.
            cylinder(s, a+.78, j+7.43, .2, .12, 52, 5, BRONZE)
            if a > i:
                for dx, z, radius in ((.78, 37, 4), (.28, 29, 2), (1.27, 29, 2)):
                    dial(s, a+dx, j+7.43, z, radius)
            else:
                # Small pyramidal belfry cap and cross.
                pyramid(s, a+.32, j+5.98, .9, .95, 70, 10)
                seg(s, P(s, a+.78, j+6.45, 80), P(s, a+.78, j+6.45, 86), IRON)
                seg(s, P(s, a+.55, j+6.45, 84), P(s, a+1, j+6.45, 84), IRON)
        for n in range(4):
            block(s, i+.8-n*.15, j+7.3+n*.24, 4.4+n*.3, .25, 1, PALE, z=3-n)
    scene.add(i+j+14, draw)


def dial(s, i, j, z, radius):
    def point(u, v):
        return P(s, i+u/8, j, z+v)
    for u in range(-radius, radius+1):
        for v in range(-radius, radius+1):
            if math.hypot(u, v) <= radius:
                s.put(*point(u, v), STONE['deep'] if math.hypot(u, v) > radius-.8 else PALE['hi'])
    seg(s, point(0, 0), point(-radius*.6, .3), IRON)
    seg(s, point(0, 0), point(.3, radius*.7), IRON)


def pyramid(s, i, j, wi, wj, base, rise):
    t, r, b, l = corners(s, i, j, wi, wj, base)
    apex = P(s, i+wi/2, j+wj/2, base+rise)
    for pts, tone in (([t, r, apex], 'mid'), ([t, l, apex], 'mid'),
                      ([l, b, apex], 'lit'), ([b, r, apex], 'dark')):
        poly(s, pts, lambda x, y, tone=tone: STONE['line'] if int(y) % 7 == 0 else STONE[tone])
    for p in (l, b, r):
        seg(s, apex, p, STONE['outline'])
    seg(s, apex, l, PALE['hi'])


def carmelite(scene, i, j):
    """Great ribbed stone dome, arched drum, lantern and restrained Baroque church."""
    def draw(s):
        block(s, i, j, 6, 6.4, 30, STONE, windows(STONE, 30, 13, 16, True))
        flat_roof(s, i, j, 6, 6.4, 30)
        ci, cj = i+3, j+3.1
        cylinder(s, ci, cj, 2.55, 2.55, 30, 21, STONE, windows(STONE, 21, 12, 21, True))
        cylinder(s, ci, cj, 2.7, 2.7, 49, 3, PALE)
        dome(s, ci, cj, 2.7, 52, 34, ROOF)
        # Narrow radial stone ribs distinguish the dome from a copper hemisphere.
        for n in range(12):
            a = n*math.tau/12
            points = [P(s, ci+2.72*math.cos(t)*math.cos(a),
                        cj+2.72*math.cos(t)*math.sin(a), 52+34*math.sin(t))
                      for t in [k*math.pi/24 for k in range(13)]]
            for p, q in zip(points, points[1:]):
                if math.sin(a)+math.cos(a) > -.5:
                    seg(s, p, q, PALE['lit'] if math.sin(a) > .2 else STONE['dark'])
        cylinder(s, ci, cj, .55, .55, 84, 12, STONE, windows(STONE, 12, 7, 12, True))
        dome(s, ci, cj, .65, 96, 5, PALE)
        seg(s, P(s, ci, cj, 101), P(s, ci, cj, 107), IRON)
        seg(s, P(s, ci-.25, cj, 105), P(s, ci+.25, cj, 105), IRON)
        pediment(s, i+.7, j+6.42, 4.6, 30, 8)
        block(s, i+2.45, j+6.42, 1.1, .16, 16, STONE,
              lambda u, v, lit: RED['dark'] if 1 < u < 7 and v < 13 else None)
    scene.add(i+j+13, draw)


def st_paul(scene, i, j):
    """Six-column Ionic portico and slender limestone belfry with a tall spire."""
    def draw(s):
        block(s, i, j, 5.8, 6.5, 34, STONE, windows(STONE, 34, 14, 18, True))
        hip_roof(s, i-.05, j-.05, 5.9, 6.6, 34, 8, ROOF)
        for n in range(4):
            block(s, i-.3-n*.1, j+6.5+n*.3, 6.4+n*.2, .32, 1, PALE, z=3-n)
        for n in range(6):
            ci, cj = i+.25+n*1.06, j+7
            cylinder(s, ci, cj, .18, .18, 4, 28, PALE)
            block(s, ci-.28, cj-.26, .56, .52, 2, STONE, z=3)
            block(s, ci-.28, cj-.26, .56, .52, 2, PALE, z=31)
            for dx in (-.23, .23):
                cylinder(s, ci+dx, cj+.16, .1, .12, 31, 2, STONE)
        band(s, i-.2, j+6.75, 6.2, .65, 33, height=4)
        pediment(s, i-.25, j+7.43, 6.3, 37, 12)
        a, b = i+.15, j+.1
        def tower_pattern(u, v, lit):
            c = int(u) % 14
            if v in (18, 20, 39, 41, 58, 60) or c in (1, 12):
                return PALE['lit' if lit else 'mid']
            if 5 <= c <= 9 and 23 < v < 35:
                return STONE['dark' if lit else 'deep'] if c != 7 else PALE['mid']
            return stone_courses(STONE, 6, 15)(u, v, lit)
        block(s, a, b, 1.8, 1.8, 61, STONE, tower_pattern)
        for z in (40, 60, 74):
            band(s, a-.12, b-.12, 2.04, 2.04, z, height=2)
        block(s, a+.13, b+.13, 1.54, 1.54, 13, STONE,
              lambda u, v, lit: IRON if arch_opening(int(u) % 12, v, 6, 3, 6, True) else None, z=62)
        pyramid(s, a+.05, b+.05, 1.7, 1.7, 76, 40)
        seg(s, P(s, a+.9, b+.9, 116), P(s, a+.9, b+.9, 121), IRON)
    scene.add(i+j+14, draw)


def grandmaster(scene, i, j):
    """Courtyard palace, long green corner balconies, Baroque portals and Pinto clock."""
    def draw(s):
        # Rear and side ranges leave a genuinely open central courtyard.
        for a, b, wi, wj in ((i, j, 9, 1.8), (i, j+1.8, 1.8, 4.5), (i+7.2, j+1.8, 1.8, 4.5)):
            block(s, a, b, wi, wj, 38, STONE, windows(STONE, 38, 12, 19))
            flat_roof(s, a, b, wi, wj, 38)
        poly(s, list(corners(s, i+1.8, j+1.8, 5.4, 4.4, 1)), lambda x, y: PALE['mid'])
        block(s, i, j+5.4, 9, 1.8, 38, STONE, windows(STONE, 38, 12, 19))
        flat_roof(s, i, j+5.4, 9, 1.8, 38)
        for a in (i+1.2, i+5.8):
            block(s, a, j+7.23, 1.4, .24, 18, PALE,
                  lambda u, v, lit: arch_opening(u, v, 5.6, 3.5, 11, RED['dark']))
        gallarija(s, i+.1, j+7.22, 2.6, 22, GREEN)
        gallarija(s, i+5.8, j+7.22, 3.2, 22, GREEN)
        gallarija(s, i+9.03, j+5.4, 1.65, 22, GREEN, True)
        # The low roof balustrade has small pierced panels under a continuous coping.
        facade(s,i-.02,j+7.05,9.04,.18,4,
               lambda u,v,lit: STONE['deep'] if 1 < v < 3 and int(u)%4 in (1,2)
               else PALE['lit' if lit else 'dark'],palette=PALE,z0=40)
        band(s,i-.08,j+6.99,9.16,.3,44,height=1)
        # Pinto clock tower rises from the court, with its four face panels.
        block(s, i+4, j+2, 1.7, 1.5, 20, STONE, windows(STONE, 20, 12, 20), z=37)
        band(s, i+3.9, j+1.9, 1.9, 1.7, 57, height=3)
        dial(s, i+4.85, j+3.55, 49, 4)
        flat_roof(s, i+3.9, j+1.9, 1.9, 1.7, 60)
        flag(s, i+4.85, j+2.7, 63)
    scene.add(i+j+17, draw)


def castille(scene, i, j):
    """Baroque auberge: broad steps, rusticated portal, trophies and curved crest."""
    def draw(s):
        block(s, i, j, 9.2, 5, 43, STONE, windows(STONE, 43, 12, 21))
        flat_roof(s, i, j, 9.2, 5, 43)
        # Upper window pediments, pilasters and carved aprons on the actual facade.
        for a in (i+.55, i+2.05, i+5.95, i+7.45):
            pediment(s, a, j+5.04, 1.15, 38, 4)
            band(s, a+.12, j+4.96, .91, .22, 23, height=2)
        block(s, i+3.3, j+4.98, 2.5, .48, 32, PALE,
              lambda u, v, lit: arch_opening(u, v, 10, 5, 17, RED['dark']) if lit else None)
        for a in (i+3.2, i+5.6):
            cylinder(s, a, j+5.55, .23, .24, 6, 26, PALE)
            block(s, a-.34, j+5.25, .68, .6, 3, STONE, z=30)
        band(s, i+3, j+5.1, 3.2, .75, 34, height=3)
        # Curved sculpted cartouche: an actual shield outline, crown and scrolls.
        shape=[(-.9,0),(-1.05,4),(-.75,8),(-.45,10),(0,11),(.45,10),
               (.75,8),(1.05,4),(.9,0),(.45,-2),(0,-4),(-.45,-2)]
        face=[P(s,i+4.6+a,j+5.18,48+v) for a,v in shape]
        back=[P(s,i+4.6+a,j+4.98,48+v) for a,v in shape]
        for k in range(len(face)):
            poly(s,[face[k-1],face[k],back[k],back[k-1]],lambda x,y:STONE['dark'])
        poly(s,face,lambda x,y:PALE['lit'] if h01(x,y,457)>.18 else STONE['line'])
        for a,b in zip(face,face[1:]+face[:1]):
            seg(s,a,b,PALE['hi'])
        inner=[P(s,i+4.6+a,j+5.2,50+v) for a,v in ((-.4,2),(.4,2),(.35,-2),(0,-4),(-.35,-2))]
        poly(s,inner,lambda x,y:STONE['dark'])
        for n in (-.25,0,.25):
            block(s,i+4.6+n-.08,j+4.94,.16,.24,2,PALE,z=60)
        # Filled bust above the portal and its flanking trophy reliefs.
        cylinder(s,i+4.6,j+5.55,.19,.17,32,3,PALE)
        block(s,i+4.3,j+5.4,.6,.3,3,PALE,z=29)
        for sign in (-1, 1):
            for k in range(3):
                seg(s, P(s, i+4.6+sign*(.6+k*.18), j+5.55, 48),
                    P(s, i+4.6+sign*(1.1+k*.25), j+5.55, 53+k), STONE['lit'], 2)
        for n in range(6):
            block(s, i+2.6-n*.16, j+5.5+n*.28, 4+n*.32, .3, 1, PALE, z=5-n)
        flag(s, i+4.6, j+2.8, 51)
    scene.add(i+j+17, draw)


def parliament(scene, i, j):
    """Piano's two raised stone volumes with irregular eroded limestone sun screens."""
    def draw(s):
        def screen_pattern(u, v, lit):
            c, r = int(u)//3, int(v)//3
            # Inset apertures vary in size and spacing, leaving quiet solid corner piers.
            if 6 < u < 29 and 4 < v < 22 and h01(c, r, 453) > .35:
                if int(v) % 3 == 0:
                    return PALE['hi' if lit else 'mid']
                if int(u) % 3 < 2:
                    return STONE['deep' if lit else 'outline']
            return stone_courses(PALE, 8, 20)(u, v, lit)
        for a, b, wi, wj in ((i, j, 4.4, 5.5), (i+5.2, j+.4, 4.2, 5.1)):
            block(s, a+.2, b+.2, wi-.4, wj-.4, 9, BLUE,
                  lambda u, v, lit: IRON if int(u) % 8 == 0 else GLASS['dark'])
            for x in (.25, wi-.45):
                for y in (.2, wj-.4):
                    block(s, a+x, b+y, .22, .24, 10, ROOF)
            block(s, a, b, wi, wj, 26, PALE, screen_pattern, z=10)
            band(s, a-.04, b-.04, wi+.08, wj+.08, 36, ROOF, 1)
            poly(s, list(corners(s, a+.25, b+.25, wi-.5, wj-.5, 37)),
                 lambda x, y: ROOF['dark'] if int(x) % 7 else ROOF['line'])
        block(s, i+4.4, j+1.2, .8, 2.2, 12, BLUE,
              lambda u, v, lit: IRON if int(u) % 5 == 0 else GLASS['mid'], z=15)
        # Broad stepped pedestrian approach, not a decorative perimeter cage.
        for n in range(4):
            block(s, i+5.5, j+5.65+n*.32, 3.4, .34, 1, PALE, z=3-n)
    scene.add(i+j+16, draw)


def bastion(s, vertices, height=17):
    """Battered polygonal curtain; its visible faces carry coursed masonry and embrasures."""
    center = tuple(sum(p[k] for p in vertices)/len(vertices) for k in (0, 1))
    bottom = [(a+(a-center[0])*.045, b+(b-center[1])*.045) for a, b in vertices]
    faces = []
    for n, ((a, b), (c, d)) in enumerate(zip(vertices, vertices[1:]+vertices[:1])):
        x0, y0 = P(s, a, b, height)
        x1, y1 = P(s, c, d, height)
        if x1 >= x0:
            continue
        lo, hi = P(s, *bottom[n]), P(s, *bottom[(n+1) % len(vertices)])
        faces.append(((a+b+c+d)/2, [(x1,y1), (x0,y0), lo, hi], x1, y1, x0, y0, c-a < 0))
    for _, pts, x0, y0, x1, y1, lit in sorted(faces):
        def masonry(x, y):
            v = int(y0+(x-x0)*(y1-y0)/(x1-x0)-y)
            return stone_courses(STONE, 5, 12)(x-x0, v, lit) or STONE['lit' if lit else 'dark']
        poly(s, pts, masonry)
    top = [P(s, a, b, height) for a, b in vertices]
    poly(s, top, lambda x, y: PALE['mid'] if h01(x//3, y//2, 463) > .08 else STONE['line'])
    for a, b in zip(top, top[1:]+top[:1]):
        seg(s, a, b, PALE['hi'], 2)


def fort_st_elmo(scene, i, j):
    """Low star bastions, open parade court, barracks, chapel and projecting sentry box."""
    def draw(s):
        vertices = [(i,j+2),(i+2,j+1),(i+2.7,j-1),(i+5,j+.7),(i+7.4,j-.1),
                    (i+7.2,j+2.2),(i+10,j+3.2),(i+7.8,j+5),(i+8.2,j+7),
                    (i+5.7,j+6.6),(i+4.4,j+8),(i+3,j+6),(i+.1,j+6.4),(i+.8,j+4)]
        bastion(s, vertices, 18)
        # Court level and ranges remain open above the low defensive curtain.
        for a, b, wi, wj in ((i+2,j+1.8,4.5,1.1), (i+1.5,j+2.8,1.2,2.6),
                             (i+6,j+2.5,1.3,2.4)):
            block(s, a, b, wi, wj, 14, STONE, windows(STONE,14,9,14,True), z=18)
            flat_roof(s, a, b, wi, wj, 32)
        block(s, i+3.5, j+3.5, 2, 1.4, 12, PALE, windows(PALE,12,9,14,True), z=18)
        pediment(s, i+3.45, j+4.93, 2.1, 30, 5)
        # A projecting hexagonal gardjola on the seaward bastion.
        cylinder(s, i+8.1, j+6.7, .48, .48, 18, 10, PALE, windows(PALE, 10, 6, 11, True))
        dome(s, i+8.1, j+6.7, .58, 28, 5, STONE)
        for a, b in ((i+1,j+5.8), (i+4.5,j+7), (i+7.8,j+4.8)):
            block(s, a, b, .7, .32, 2, ROOF, z=19)
            seg(s, P(s,a+.35,b+.2,22), P(s,a+.35,b+.7,23), IRON, 2)
        flag(s, i+5, j+1.8, 34)
    scene.add(i+j+18, draw)


def arcade(s, i, j, count, bay=1.3, z=22):
    """Open round arches: fill only the piers and spandrels, preserving the view through."""
    width, height = count*bay, 22
    for n in range(count+1):
        block(s,i+n*bay-.14,j,.28,.42,15,STONE,z=z)
        band(s,i+n*bay-.2,j-.05,.4,.52,z+14,height=2)
    # Wedge-shaped voussoirs have thickness and keep the arch holes genuinely empty.
    for n in range(count):
        ci = i+(n+.5)*bay
        for k in range(10):
            a,b = k*math.pi/10,(k+1)*math.pi/10
            outer,inner=bay*.5,bay*.5-.19
            pts=[P(s,ci+outer*math.cos(a),j+.43,z+14+outer*8*math.sin(a)),
                 P(s,ci+outer*math.cos(b),j+.43,z+14+outer*8*math.sin(b)),
                 P(s,ci+inner*math.cos(b),j+.43,z+14+inner*8*math.sin(b)),
                 P(s,ci+inner*math.cos(a),j+.43,z+14+inner*8*math.sin(a))]
            poly(s,pts,lambda x,y:PALE['lit'] if k%2 else STONE['lit'])
            seg(s,pts[0],pts[3],STONE['line'])
        # Fill the spandrel ABOVE the curved opening, never below it.
        for x,y in iso.polygon_pixels([P(s,ci-bay/2,j+.43,z+14),P(s,ci+bay/2,j+.43,z+14),
                                      P(s,ci+bay/2,j+.43,z+height),P(s,ci-bay/2,j+.43,z+height)]):
            anchor=P(s,ci-bay/2,j+.43,z)
            u=x-anchor[0];v=anchor[1]+u*.5-y
            if v > 14+math.sqrt(max(0,(bay*4)**2-(u-bay*4)**2)):
                s.put(x,y,STONE['lit'] if int(v)%5 else STONE['line'])
    band(s,i-.2,j-.06,width+.4,.55,z+height,height=3)
    # Return arcade along the other isometric axis.
    for n in range(3):
        block(s,i+width-.12,j-n*1.2,.28,.3,22,STONE,z=z)
    band(s,i+width-.16,j-2.4,.38,2.8,z+height,height=3)


def upper_barrakka(scene, i, j):
    """Arcaded garden on St Peter and Paul Bastion, lower Saluting Battery and guns."""
    def draw(s):
        bastion(s, [(i,j),(i+8,j),(i+8.8,j+3.5),(i+7.3,j+5.7),(i,j+5.7)], 22)
        # Garden paths and beds sit above the bastion platform, behind its arcades.
        for a,b in ((i+.8,j+1),(i+4.2,j+1)):
            poly(s,list(corners(s,a,b,2.4,1.5,23)),lambda x,y: GREEN['mid'] if (int(x)+int(y))%5 else GREEN['lit'])
        arcade(s,i+.2,j+3.2,6,z=23)
        # Lower terrace: cannons face out across the Grand Harbour.
        block(s,i+.6,j+5.8,7,1.4,5,STONE,z=4)
        for n in range(5):
            a,b=i+1+n*1.3,j+6.5
            block(s,a-.2,b,.6,.38,3,RED,z=9)
            for dx in (-.2,.3):
                cylinder(s,a+dx,b+.25,.12,.14,9,3,IRON_MATERIAL)
            seg(s,P(s,a+.1,b,14),P(s,a+.1,b+1,15),IRON,3)
            seg(s,P(s,a+.05,b,15),P(s,a+.05,b+1,16),BRONZE['lit'])
        # Basin and original small garden trees, kept below the arcade springing.
        cylinder(s,i+3.7,j+1.3,.45,.45,23,2,PALE)
        cylinder(s,i+3.7,j+1.3,.3,.3,25,1,BLUE)
        for a in (i+1.7,i+5.6):
            cylinder(s,a,j+1.8,.12,.12,23,8,STONE)
            dome(s,a,j+1.8,.65,29,7,GREEN)
    scene.add(i+j+18,draw)


IRON_MATERIAL = palette_of(IRON)


if __name__ == '__main__':
    for builder, name in ((st_john,'st-john'), (carmelite,'carmelite'), (st_paul,'st-paul'),
                          (grandmaster,'grandmaster'), (fort_st_elmo,'fort-st-elmo'),
                          (parliament,'parliament'), (castille,'castille'), (upper_barrakka,'upper-barrakka')):
        print(preview([lambda s,b=builder:b(s,3,3)],f'valletta-{name}',
                      size=(240,220),origin=(110,105),tiles=18))
    print(preview([lambda s:townhouse(s,3,3,2.5,3,3,0),
                   lambda s:townhouse(s,7,3,2.5,3,2,1),
                   lambda s:townhouse(s,7,7,2.5,3,3,2)],'valletta-houses',
                  size=(230,200),origin=(110,65),tiles=16))
