"""Vienna's stone, stucco, glazed tiles and patinated copper, in true isometric 3D.

Run directly for eight isolated 4× landmark studies and a Gründerzeit house study.
Real sites, north-up layout and architectural sources are in DEVELOPMENT_PLAN.md.
"""
import math

import iso
from iso import rgb
from landmarks_paris import P, seg, poly, corners, facade, mansard, preview, GLASS
from landmarks_iberia import hip_roof, stone_courses, arch_opening, palette_of, tones
from landmarks_belgium import dome
from landmarks_italy import cylinder
from landmarks_denmark import spire

STONE = tones('#FFF2D8', '#E5D6B8', '#CDBD9C', '#AA987B', '#7D6C53', '#B3A183', '#4A3C2B')
PALE = tones('#FFF6E2', '#F0E3C9', '#DDCEAE', '#B8A78A', '#85765B', '#C3B497', '#504432')
YELLOW = tones('#FFE4A5', '#E9C57C', '#CDA564', '#AD864D', '#795D36', '#BB965A', '#503B25')
COPPER = tones('#BED7B5', '#86AF98', '#6A907D', '#486E60', '#2C4B41', '#5E8270', '#263C32')
SLATE = tones('#B7BBC0', '#8A9299', '#707C85', '#505F6B', '#34434F', '#62727B', '#2C3641')
CLAY = tones('#DCA083', '#B97F65', '#9E6650', '#7D493A', '#543129', '#8E5947', '#3F2A24')
STEEL = tones('#E1DDD1', '#A6AFA8', '#82938F', '#5A706F', '#374E50', '#6C8280', '#293D40')
RED = tones('#E8AD91', '#BB614B', '#9B493B', '#713A34', '#4D2827', '#A45242', '#392624')
GOLD = tones('#FFF1B3', '#E8C568', '#CBA04A', '#A37731', '#715124', '#B48C3A', '#503A20')
BRONZE = tones('#A1B18D', '#788B6D', '#5D7057', '#3D5344', '#29392F', '#53694F', '#213028')
WALLS = [rgb(c) for c in ('#E8D5AD', '#D8C2A5', '#DDB8A8', '#D7DCC5', '#ECE1C9', '#C6D0CF')]
WATER = (rgb('#4F8C91'), rgb('#3A6F7B'), rgb('#C1DFD4'))
IRON = rgb('#3E4947')
TILES = [rgb(c) for c in ('#E5C875', '#436C53', '#F0E4BB', '#3E5050', '#9C8258')]


def block(s, i, j, wi, wj, height, material=STONE, pattern=None, z=0):
    cover = facade(s, i, j, wi, wj, height,
                   pattern or stone_courses(material, 4, 11), palette=material, z0=z)
    iso.fill(s, list(corners(s, i, j, wi, wj, z+height)), lambda x, y: material['mid'], cover)
    iso.outline(s, cover, material['outline'])


def windows(material, height, bay=10, floor=14, gothic=False, arcade=False):
    joints = stone_courses(material, 5, 12)
    def pattern(u, v, lit):
        c, v = int(u) % bay, int(v)
        level, trim = v % floor, PALE['lit' if lit else 'dark']
        if v < 2 or v in (height-1, height-3) or level == 0:
            return trim
        if arcade and v < 11:
            opening = arch_opening(c, v, bay/2, bay/2-1.6, 6, material['deep'])
            if opening:
                return opening
        head = floor-3-abs(c-bay/2)*(1.6 if gothic else .25)
        if 2 <= c <= bay-2 and 3 <= level <= head and v < height-4:
            if c in (2, bay-2, bay//2) or level in (3, 7, int(head)):
                return trim
            return STEEL['dark' if lit else 'deep'] if gothic else GLASS['mid' if lit else 'dark']
        if gothic and c == 0:
            return trim
        return joints(u, v, lit)
    return pattern


def band(s, i, j, wi, wj, z, material=PALE, height=2):
    facade(s, i, j, wi, wj, height,
           lambda u, v, lit: material['hi' if lit else 'mid'] if v > height-1
           else material['lit' if lit else 'dark'], palette=material, z0=z)


def pediment(s, i, j, width, base, rise, material=PALE):
    """A triangular stone pediment with thickness, sloped cornices and a relief tympanum."""
    front = [P(s, i, j, base), P(s, i+width, j, base), P(s, i+width/2, j, base+rise)]
    back = [P(s, i, j-.32, base), P(s, i+width, j-.32, base), P(s, i+width/2, j-.32, base+rise)]
    poly(s, [front[1], back[1], back[2], front[2]], lambda x, y: material['dark'])
    poly(s, front, lambda x, y: material['lit'] if (int(x)+int(y)) % 7 else material['line'])
    for a, b in zip(front, front[1:]+front[:1]):
        seg(s, a, b, material['hi'])
    # Low sculpted wreath in the actual wall plane.
    for n in range(12):
        a = n*math.tau/12
        x, y = P(s, i+width/2+math.cos(a)*width*.13, j+.02, base+rise*.4+math.sin(a)*2)
        s.put(x, y, material['deep'])


def figure(s, i, j, base, material=BRONZE, height=8):
    """Filled head, shoulders, tunic, arms and separate legs, rather than a line finial."""
    cylinder(s, i, j, .18, .18, base+height*.75, height*.25, material)
    block(s, i-.23, j-.15, .46, .3, height*.48, material, z=base+height*.27)
    for a in (-.3, .22):
        block(s, i+a, j-.12, .13, .22, height*.35, material, z=base+height*.34)
    for a in (-.17, .07):
        block(s, i+a, j-.1, .12, .2, height*.28, material, z=base)


def clock(s, i, j, z, radius=6, lit=True):
    def point(u, v):
        return P(s, i+u/8 if lit else i, j if lit else j-u/8, z+v)
    for u in range(-radius, radius+1):
        for v in range(-radius, radius+1):
            r = math.hypot(u, v)
            if r <= radius:
                s.put(*point(u, v), GOLD['lit'] if r > radius-1 else IRON)
    for n in range(12):
        a = n*math.tau/12
        seg(s, point(math.cos(a)*(radius-1), math.sin(a)*(radius-1)),
            point(math.cos(a)*radius, math.sin(a)*radius), PALE['hi'])
    seg(s, point(0, 0), point(-radius*.65, radius*.25), PALE['hi'])
    seg(s, point(0, 0), point(radius*.15, radius*.8), PALE['hi'])


def townhouse(scene, i, j, wi=2.5, wj=3, floors=3, seed=0):
    """Viennese Gründerzeit stucco: moulded surrounds, window pediments, ironwork and bays."""
    wall, height = palette_of(WALLS[seed % len(WALLS)]), floors*12+3
    joints = stone_courses(wall, 6, 15)
    def pattern(u, v, lit):
        c, v = int(u) % 11, int(v)
        level, trim = (v-12) % 12, PALE['lit' if lit else 'dark']
        if v < 3:
            return STONE['mid' if lit else 'deep']
        if v in (11, height-1, height-3):
            return trim
        if v < 11:
            opening = arch_opening(c, v, 5.5, 3.3, 6.2, IRON)
            if opening:
                return GLASS['dark'] if 3 < v < 8 and c in (4, 7) else opening
        if v >= 12 and 3 <= c <= 8 and 2 <= level <= 8 and v < height-4:
            if c in (3, 5, 8) or level in (2, 5, 8):
                return trim
            return GLASS['mid' if lit else 'dark']
        if v >= 12 and (level == 9 and 2 <= c <= 9 or level == 10 and 4 <= c <= 7):
            return trim
        if v >= 12 and level == 1 and 2 <= c <= 9:
            return trim
        if seed % 3 == 0 and v >= 12 and level == 0 and c in (3, 5, 7):
            return IRON
        return joints(u, v, lit)
    def draw(s):
        block(s, i, j, wi, wj, height, wall, pattern)
        hip_roof(s, i-.12, j-.12, wi+.24, wj+.24, height, 12, SLATE if seed % 4 else CLAY)
        if seed % 3 == 1:
            block(s, i+wi*.45, j+wj-.08, .8, .55, 19, wall,
                  windows(wall, 19, 6, 10), z=12)
            hip_roof(s, i+wi*.45-.1, j+wj-.18, 1, .75, 31, 4, COPPER)
        if seed % 2 == 0:
            block(s, i+wi*.35, j+wj-.6, .6, .55, 6, PALE,
                  lambda u, v, lit: GLASS['dark'] if 1 < u < 4 and 1 < v < 5 else None, z=height+2)
            pediment(s, i+wi*.35-.08, j+wj, .76, height+8, 3)
        block(s, i+wi*.7, j+.55, .4, .4, 10, PALE, z=height+6)
        block(s, i+wi*.7-.06, j+.49, .52, .52, 2, STONE, z=height+16)
    scene.add(i+j+wi+wj+1, draw)


def gothic_tower(s, i, j, width, height, rise, material=STONE, dial=False):
    block(s, i, j, width, width, height, material, windows(material, height, 9, 21, gothic=True))
    for z in (height*.4, height-3):
        band(s, i-.08, j-.08, width+.16, width+.16, z)
    if dial:
        clock(s, i+width/2, j+width+.04, height-16, 6)
        clock(s, i+width+.04, j+width/2, height-16, 6, False)
    ci, cj, radius = i+width/2, j+width/2, width*.63
    # Faceted taper with open dark lancets, diagonal stone tracery and crockets.
    for n in sorted(range(8), key=lambda n: math.cos((n+.5)*math.pi/4)+math.sin((n+.5)*math.pi/4)):
        a, b = n*math.pi/4, (n+1)*math.pi/4
        lit = math.sin((a+b)/2)-.5*math.cos((a+b)/2) > 0
        foot = [P(s, ci+radius*math.cos(v), cj+radius*math.sin(v), height) for v in (a, b)]
        tip = P(s, ci, cj, height+rise)
        poly(s, [*foot, tip], lambda x, y: material['deep' if lit else 'outline'])
        for v in (a, b):
            seg(s, P(s, ci+radius*math.cos(v), cj+radius*math.sin(v), height),
                tip, material['hi' if lit else 'mid'])
        for k in range(1, 9):
            z0, z1 = (k-1)/9, k/9
            def point(v, z):
                return P(s, ci+radius*(1-z)*math.cos(v), cj+radius*(1-z)*math.sin(v), height+rise*z)
            seg(s, point(a, z0), point(b, z1), material['lit' if lit else 'dark'])
            seg(s, point(b, z0), point(a, z1), material['lit' if lit else 'dark'])
            if k % 2 == 0:
                x, y = point(a, z1)
                s.put(x-1, y, material['hi' if lit else 'mid'])
    for a, b in ((0, 0), (width, 0), (0, width), (width, width)):
        block(s, i+a-.1, j+b-.1, .2, .2, 7, material, z=height-3)
        poly(s, [P(s, i+a-.18, j+b, height+4), P(s, i+a+.18, j+b, height+4),
                 P(s, i+a, j+b, height+13)], lambda x, y: material['lit'])
    seg(s, P(s, ci, cj, height+rise), P(s, ci, cj, height+rise+4), material['deep'])


def cathedral_roof(s, i, j, wi, wj, base, rise):
    """Two steep roof planes: glazed chevrons and a small double-headed eagle on the south."""
    for side in (-1, 1):
        edge = i if side < 0 else i+wi
        pts = [P(s, edge, j, base), P(s, edge, j+wj, base),
               P(s, i+wi/2, j+wj, base+rise), P(s, i+wi/2, j, base+rise)]
        a, b, d = pts[0], pts[1], pts[3]
        ux, uy, vx, vy = b[0]-a[0], b[1]-a[1], d[0]-a[0], d[1]-a[1]
        det = ux*vy-uy*vx
        def color(x, y):
            u = ((x-a[0])*vy-(y-a[1])*vx)/det
            v = (ux*(y-a[1])-uy*(x-a[0]))/det
            along, across = u*wj*8, v*rise
            index = int((abs(along % 18-9)+across*.8)/3) % 4
            tone = TILES[index]
            # Crown, paired heads, outstretched wings and tail; clipped by this roof plane.
            du, dv = abs(u-.77), v-.46
            eagle = (du < .035 and -.13 < dv < .22
                     or .035 < du < .16 and abs(dv-.04-du*.6) < .07
                     or .035 < du < .095 and .19 < dv < .25
                     or du < .07 and -.22 < dv < -.12)
            if side > 0 and eagle:
                return TILES[3]
            return iso.shade(tone, -.12) if side > 0 else tone
        poly(s, pts, color)
        for a, b in zip(pts, pts[1:]+pts[:1]):
            seg(s, a, b, STONE['outline'])
    seg(s, P(s, i+wi/2, j, base+rise), P(s, i+wi/2, j+wj, base+rise), GOLD['hi'])


def stephansdom(scene, i, j):
    """Steep polychrome nave, south Steffl, short domed north tower and Romanesque westwork."""
    W, D, H = 5, 9, 38
    def draw(s):
        # Short north tower sits behind the nave, not a second matching Gothic steeple.
        block(s, i-.7, j+2.7, 1.9, 1.9, 56, STONE, windows(STONE, 56, 8, 18, gothic=True))
        dome(s, i+.25, j+3.65, 1.1, 56, 12, COPPER)
        spire(s, i+.25, j+3.65, .35, 68, 8, COPPER)
        block(s, i, j, W, D, H, STONE, windows(STONE, H, 13, 30, gothic=True))
        cathedral_roof(s, i, j, W, D, H, 35)
        for b in (1, 3, 5, 7, 8.5):
            block(s, i+W, j+b, .5, .35, 29, STONE)
            spire(s, i+W+.25, j+b+.18, .22, 29, 9, STONE)
        # Western Romanesque facade and two Heidentürme.
        block(s, i+.7, j+D-.1, 3.6, .65, 34, STONE, windows(STONE, 34, 14, 19, arcade=True))
        for a in (.1, 3.8):
            block(s, i+a, j+D-.4, 1.1, 1.1, 47, STONE, windows(STONE, 47, 7, 16))
            spire(s, i+a+.55, j+D+.15, .64, 47, 14, SLATE, conical=True)
        # Giant's Door and a circular west window remain on the lit westwork face.
        x0, y0 = i+2.5, j+D+.57
        for u in range(-7, 8):
            for v in range(19):
                if (u/6)**2+((v-7)/10)**2 < 1 and v < 17:
                    s.put(*P(s, x0+u/8, y0, v), STONE['deep'] if abs(u) < 4 else PALE['hi'])
        # Dressed circular west window, with radial tracery confined to the west wall.
        for u in range(-4, 5):
            for v in range(-4, 5):
                r = math.hypot(u, v)
                if r <= 4:
                    color = PALE['hi'] if r > 3 or u == 0 or v == 0 else STEEL['dark']
                    s.put(*P(s, x0+u/8, y0, 26+v), color)
        gothic_tower(s, i+W-.7, j+3.8, 1.8, 91, 49)
    scene.add(i+j+W+D+1.5, draw)


def rathaus(scene, i, j):
    """Neo-Gothic arcades, five spired towers, clocks and the armoured Rathausmann."""
    W, D, H = 12, 4.6, 34
    def draw(s):
        block(s, i, j, W, D, H, STONE, windows(STONE, H, 10, 17, gothic=True, arcade=True))
        hip_roof(s, i-.1, j-.1, W+.2, D+.2, H, 14, SLATE)
        # Front arcade is an open colonnade with separate piers, not black painted stripes.
        for n in range(11):
            block(s, i+n*1.08+.15, j+D+.25, .25, .45, 13, PALE)
        band(s, i, j+D, W, .7, 13, height=3)
        for a in (0, 2.5, 8.2, 10.7):
            gothic_tower(s, i+a, j+D-1.3, 1.3, 49, 23)
        gothic_tower(s, i+5.1, j+D-1.8, 1.9, 80, 35, dial=True)
        figure(s, i+6.05, j+D-.85, 119, BRONZE, 8)
        # Broad banner and halberd beside the full figure.
        seg(s, P(s, i+6.45, j+D-.85, 120), P(s, i+6.45, j+D-.85, 132), BRONZE['deep'])
        poly(s, [P(s, i+6.45, j+D-.85, 131), P(s, i+7.15, j+D-.85, 130),
                 P(s, i+6.85, j+D-.85, 126), P(s, i+6.45, j+D-.85, 127)], lambda x, y: BRONZE['lit'])
    scene.add(i+j+W+D+1, draw)


def hofburg(scene, i, j):
    """Neue Burg: concave monumental facade, paired giant columns, balustrade and statuary."""
    W, D, H = 12, 4.5, 42
    def draw(s):
        # Short wings follow a shallow arc in plan. Paint back to front, preserving the concavity.
        modules = [(n*1.5, .65-2.2*math.sin((n+.5)/8*math.pi)) for n in range(8)]
        for a, b in sorted(modules, key=lambda t: sum(t)):
            block(s, i+a, j+b, 1.55, D, H, STONE, windows(STONE, H, 9, 14, arcade=True))
            hip_roof(s, i+a-.05, j+b-.05, 1.65, D+.1, H, 7, COPPER)
            # Engaged paired columns and capitals across the curved south-west front.
            for u in (.18, 1.12):
                cylinder(s, i+a+u, j+b+D+.12, .12, .12, 13, 25, PALE)
                block(s, i+a+u-.2, j+b+D-.08, .4, .4, 2, PALE, z=37)
            band(s, i+a, j+b, 1.55, D, 40, height=3)
            for u in (.2, .6, 1, 1.4):
                block(s, i+a+u, j+b+D-.1, .09, .1, 4, PALE, z=44)
            seg(s, P(s, i+a, j+b+D, 48), P(s, i+a+1.5, j+b+D, 48), PALE['hi'])
            if int(a*2) % 3 == 0:
                figure(s, i+a+.75, j+b+D-.1, 48, PALE, 6)
        # Raised central portal and imperial double-headed eagle relief on the attic.
        block(s, i+4.6, j+D-.6, 2.8, .8, 10, PALE, z=40)
        pediment(s, i+4.4, j+D+.3, 3.2, 50, 7)
        for a in (-.45, .45):
            poly(s, [P(s, i+6, j+D+.34, 53), P(s, i+6+a*2, j+D+.34, 56),
                     P(s, i+6+a, j+D+.34, 51)], lambda x, y: BRONZE['mid'])
        for n in range(4):
            block(s, i+4.7, j+D+.4+n*.28, 2.6, .3, 4-n, STONE)
    scene.add(i+j+W+D+1, draw)


def opera(scene, i, j):
    """Renaissance opera: arcaded loggia, paired winged horses and raised copper roofs."""
    W, D = 8, 6
    def draw(s):
        block(s, i+.8, j, W-1.6, D, 37, STONE, windows(STONE, 37, 10, 13, arcade=True))
        mansard(s, i+.65, j-.15, W-1.3, D+.3, 37, 24, 1, COPPER, dormers=3, dome=True)
        for a in (0, W-1.7):
            block(s, i+a, j+D-3, 1.7, 3, 39, STONE, windows(STONE, 39, 8, 13, arcade=True))
            mansard(s, i+a-.1, j+D-3.1, 1.9, 3.2, 39, 10, .45, COPPER)
        block(s, i+1.7, j+D-1, 4.6, 1.6, 12, STONE, windows(STONE, 12, 9, 12, arcade=True))
        # Five stone arches over the entrance and five open upper loggia bays.
        for n in range(5):
            a = i+1.85+n*.88
            cylinder(s, a, j+D+.72, .1, .12, 13, 13, PALE)
            block(s, a-.15, j+D+.57, .3, .3, 2, PALE, z=25)
            for k in range(8):
                u = k*.11
                low = 6+6*math.sqrt(max(0, 1-((u-.44)/.44)**2))
                block(s, a+u, j+D+.5, .12, .35, 13-low, PALE, z=13+low)
        band(s, i+1.7, j+D-.9, 4.6, 1.7, 26, height=3)
        for a in (1.2, 6.7):
            # Pegasus: volumetric body/head, four legs, paired filled wings and mounted figure.
            block(s, i+a-.35, j+D-.7, .8, .35, 4, BRONZE, z=43)
            cylinder(s, i+a+.4, j+D-.53, .18, .18, 46, 3, BRONZE)
            for u in (-.2, .25):
                block(s, i+a+u, j+D-.6, .1, .15, 4, BRONZE, z=40)
            for v in (-.15, .15):
                poly(s, [P(s, i+a-.1, j+D-.5+v, 46), P(s, i+a-.8, j+D-.5+v, 53),
                         P(s, i+a-.35, j+D-.5+v, 52), P(s, i+a+.3, j+D-.5+v, 46)],
                     lambda x, y: BRONZE['lit'] if v > 0 else BRONZE['dark'])
            figure(s, i+a, j+D-.5, 46, BRONZE, 6)
        for n in range(4):
            block(s, i+2, j+D+.8+n*.25, 4, .3, 4-n, STONE)
    scene.add(i+j+W+D+2, draw)


def karlskirche(scene, i, j):
    """Elongated copper dome, temple portico, spiral relief columns and two pagoda belfries."""
    W, D = 8.2, 5.2
    def draw(s):
        block(s, i+1.6, j, 5, D, 31, PALE, windows(PALE, 31, 11, 16))
        hip_roof(s, i+1.5, j-.1, 5.2, D+.2, 31, 8, COPPER)
        cylinder(s, i+4.1, j+2.3, 1.7, 1.7, 35, 17, PALE, windows(PALE, 17, 8, 17))
        dome(s, i+4.1, j+2.3, 1.95, 52, 32, COPPER)
        cylinder(s, i+4.1, j+2.3, .34, .34, 84, 7, PALE, windows(PALE, 7, 4, 7))
        dome(s, i+4.1, j+2.3, .43, 91, 5, COPPER)
        seg(s, P(s, i+4.1, j+2.3, 96), P(s, i+4.1, j+2.3, 102), GOLD['lit'])
        seg(s, P(s, i+3.85, j+2.3, 100), P(s, i+4.35, j+2.3, 100), GOLD['hi'])
        for a in (0, W-1.3):
            block(s, i+a, j+D-1.9, 1.3, 2, 27, PALE, windows(PALE, 27, 8, 14, arcade=True))
            for z, width in ((27, 1.7), (32, 1.4)):
                hip_roof(s, i+a+(1.3-width)/2, j+D-1.2-width/2, width, width, z, 5, COPPER)
            spire(s, i+a+.65, j+D-1.2, .42, 37, 8, COPPER, onion=True)
        # Portico columns have full bases/capitals and a pediment in the same wall plane.
        for n in range(6):
            a = i+2.1+n*.79
            cylinder(s, a, j+D+.55, .14, .14, 3, 20, PALE)
            block(s, a-.22, j+D+.33, .44, .44, 3, PALE, z=22)
        block(s, i+1.8, j+D+.18, 4.6, .8, 3, PALE, z=25)
        pediment(s, i+1.7, j+D+1, 4.8, 28, 10)
        figure(s, i+4.1, j+D+.7, 40, PALE, 8)
        for a in (.8, 7.4):
            block(s, i+a-.5, j+D+.5, 1, 1, 6, PALE)
            cylinder(s, i+a, j+D+1, .3, .3, 6, 43, STONE)
            # Continuous spiral band winds around the actual column, clipped to its cylinder.
            for n in range(160):
                t = n*math.tau/20
                p = P(s, i+a+.32*math.cos(t), j+D+1+.32*math.sin(t), 7+n*.255)
                if math.sin(t)-.5*math.cos(t) > -.4:
                    s.put(*p, STONE['deep'])
            cylinder(s, i+a, j+D+1, .45, .45, 49, 3, PALE)
            figure(s, i+a, j+D+1, 52, PALE, 7)
        for n in range(4):
            block(s, i+1.9, j+D+1.1+n*.23, 4.4, .27, 4-n, STONE)
    scene.add(i+j+W+D+2.3, draw)


def belvedere(scene, i, j):
    """Upper Belvedere: sculpted central pavilion, rhythmic wings and four copper tent roofs."""
    W, D = 12, 4.2
    def draw(s):
        block(s, i, j, W, D, 28, PALE, windows(PALE, 28, 10, 14, arcade=True))
        hip_roof(s, i-.1, j-.1, W+.2, D+.2, 28, 8, COPPER)
        for a, b in ((0, 0), (9.8, 0), (0, D-1.6), (9.8, D-1.6)):
            block(s, i+a, j+b, 2.2, 1.8, 32, PALE, windows(PALE, 32, 8, 16))
            mansard(s, i+a-.1, j+b-.1, 2.4, 2, 32, 13, .65, COPPER, dome=True)
            spire(s, i+a+1.1, j+b+.9, .3, 45, 8, COPPER)
        block(s, i+4, j+.3, 4, D+.3, 38, PALE, windows(PALE, 38, 10, 19, arcade=True))
        mansard(s, i+3.85, j+.15, 4.3, D+.6, 38, 17, .9, COPPER, dormers=2, dome=True)
        for a in (4.2, 5.25, 6.6, 7.65):
            block(s, i+a, j+D+.65, .18, .2, 23, PALE, z=10)
        # Undulating Baroque attic, a carved central shield, crest and stone figures.
        pediment(s, i+4, j+D+.85, 4, 39, 11)
        cylinder(s, i+6, j+D+.9, .36, .12, 44, 6, GOLD)
        for a in (4.3, 7.7):
            figure(s, i+a, j+D+.8, 42, PALE, 6)
        spire(s, i+6, j+2.4, .42, 55, 8, COPPER)
        for n in range(4):
            block(s, i+4.5, j+D+1+n*.25, 3, .3, 4-n, STONE)
    scene.add(i+j+W+D+2, draw)


def schonbrunn(scene, i, j):
    """Schönbrunn-yellow wings, giant pilasters, central pediment, balustrade and double stairs."""
    W, D = 14, 4
    def draw(s):
        block(s, i, j, W, D, 31, YELLOW, windows(YELLOW, 31, 9, 15))
        hip_roof(s, i-.12, j-.12, W+.24, D+.24, 31, 9, SLATE)
        for a in (0, W-2):
            block(s, i+a, j+D-1, 2, 2.6, 34, YELLOW, windows(YELLOW, 34, 8, 16))
            hip_roof(s, i+a-.1, j+D-1.1, 2.2, 2.8, 34, 8, SLATE)
        block(s, i+5, j+D-.9, 4, 1.5, 37, YELLOW, windows(YELLOW, 37, 10, 18, arcade=True))
        for a in (5.2, 6.1, 7.7, 8.6):
            block(s, i+a, j+D+.62, .2, .24, 24, PALE, z=10)
        pediment(s, i+4.8, j+D+.9, 4.4, 38, 10)
        for a in (0, 2, 4, 9.8, 11.8, 13.8):
            block(s, i+a, j+D+.05, .18, .2, 23, PALE, z=6)
        band(s, i, j, W, D, 29, height=3)
        for n in range(23):
            block(s, i+n*.61, j+D-.1, .1, .12, 4, PALE, z=32)
        seg(s, P(s, i, j+D, 36), P(s, i+W, j+D, 36), PALE['hi'])
        for a in (1, 3, 11, 13):
            figure(s, i+a, j+D, 36, PALE, 6)
        # Two separate sweeping stairs to the garden loggia, each with a stone parapet.
        for side in (-1, 1):
            for n in range(8):
                a = i+7+side*(1+n*.33)
                block(s, a, j+D+.8+n*.13, .38, 1, 11-n, PALE)
            seg(s, P(s, i+7+side, j+D+1.8, 15), P(s, i+7+side*3.5, j+D+2.8, 6), PALE['hi'])
        hip_roof(s, i+5, j+D-1, 4, 1.6, 37, 7, SLATE)
    scene.add(i+j+W+D+3.5, draw)


def riesenrad(scene, i, j):
    """A volumetric double steel rim, 30 radial spokes, A-frames and fifteen red cabins."""
    ci, cj, radius, hub, depth = i+4.8, j+2, 4.6, 61, .9
    def point(t, face=0, radius=radius, z=hub):
        # Upright wheel plane along i; its axle runs along j.
        return P(scene, ci+radius*math.cos(t), cj+face*depth, z+radius*9*math.sin(t))
    def draw(s):
        for a in (-2.8, 2.8):
            for b in (-1.3, 1.9):
                block(s, ci+a-.4, cj+b-.4, .8, .8, 4, STONE)
                seg(s, P(s, ci+a, cj+b, 4), P(s, ci, cj+(.1 if b < 0 else .8), hub), STEEL['deep'], 2)
                seg(s, P(s, ci+a+.1, cj+b, 4), P(s, ci+.1, cj+(.1 if b < 0 else .8), hub), STEEL['lit'])
        for face in (0, 1):
            for r in (radius, radius-.25):
                ring = [point(k*math.tau/120, face, r) for k in range(121)]
                for a, b in zip(ring, ring[1:]):
                    seg(s, a, b, STEEL['lit' if face else 'deep'])
            for n in range(30):
                t = n*math.tau/30
                seg(s, point(t, face, .25), point(t, face, radius-.25), STEEL['line' if face else 'dark'])
                if n % 2 == 0:
                    seg(s, point(t, 0), point(t, 1), STEEL['hi'])
        cylinder(s, ci, cj+.45, .3, .5, hub-3, 6, STEEL)
        # Cabin boxes stay level as the wheel rotates; each has glazed sides and a roof.
        for n in sorted(range(15), key=lambda n: math.cos(n*math.tau/15)+math.sin(n*math.tau/15)):
            t = n*math.tau/15
            a, b, z = ci+radius*math.cos(t), cj+.45, hub+radius*9*math.sin(t)
            seg(s, P(s, a, b, z), P(s, a, b, z-4), STEEL['deep'])
            block(s, a-.44, b-.35, .88, .7, 8, RED,
                  lambda u, v, lit: PALE['mid'] if int(v) == 6 else GLASS['mid' if lit else 'dark']
                  if 3 < v < 6 and int(u) % 3 else None, z=z-12)
            hip_roof(s, a-.5, b-.4, 1, .8, z-4, 2, RED)
        # Low entrance pavilion; no invented amusement-park towers.
        block(s, i+2.3, j+3.2, 5, 1.5, 10, PALE, windows(PALE, 10, 8, 11, arcade=True))
        hip_roof(s, i+2.2, j+3.1, 5.2, 1.7, 10, 5, RED)
    scene.add(i+j+9.6+4, draw)


STUDIES = [('stephansdom', stephansdom), ('rathaus', rathaus), ('hofburg', hofburg),
           ('state-opera', opera), ('karlskirche', karlskirche), ('belvedere', belvedere),
           ('schonbrunn', schonbrunn), ('riesenrad', riesenrad)]

if __name__ == '__main__':
    for name, builder in STUDIES:
        print(preview([lambda s, b=builder: b(s, 4, 4)], 'vienna-'+name,
                      size=(280, 270), origin=(130, 140), tiles=22))
    print(preview([lambda s: townhouse(s, 4, 4, seed=0),
                   lambda s: townhouse(s, 8, 4, seed=1),
                   lambda s: townhouse(s, 8, 8, floors=2, seed=8)], 'vienna-houses',
                  size=(240, 200), origin=(110, 50), tiles=18))
