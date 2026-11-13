"""Zagreb: the Upper Town on its hill, Kaptol's twin-spired cathedral and the Habsburg Lower Town,
in true projected (i, j, z).

Eight landmark studies and a house study precede integration; north-up anchors and references are
recorded in DEVELOPMENT_PLAN.md. Gradec (St Mark's, Lotrščak, the Stone Gate) stands on a raised
plateau; Ilica runs along its southern foot on the i axis into Ban Jelačić Square. Art is original,
rendered at native resolution.

    .venv/bin/python scripts/art/landmarks_croatia.py  ->  docs/art/capitals/zagreb-*.png
"""
import math
from pathlib import Path

import iso
from iso import rgb, h01
from landmarks_paris import P, seg, poly, corners, preview, GLASS
from landmarks_iberia import hip_roof, crenellate, stone_courses, arch_opening, palette_of, tones
from landmarks_italy import cylinder, ellipse
from landmarks_slovakia import block, band, pediment
from landmarks_slovenia import (windows, revolve, apple, statue, lamp, balustrade, slab, DOME, HELMET,
                                WHITE, CLAY, COPPER, BRONZE, GOLD)

STONE = tones('#F6F3EC', '#E2DDD2', '#CDC7BA', '#ABA597', '#78736A', '#BBB4A6', '#45423B')  # cathedral
TOWER = tones('#F4EEDF', '#E0D6C0', '#CABEA4', '#A79A7E', '#766B55', '#B8AA8E', '#463E2F')  # Lotrščak
YELLOW = tones('#FCE7A8', '#F0CB6B', '#DDB457', '#BD943D', '#85672A', '#CBA049', '#4E3B18')  # Habsburg
OCHRE = tones('#F6DCA2', '#E4BC6F', '#CFA55B', '#AD8541', '#7A5C2B', '#BE9550', '#4A3719')
SLATE = tones('#AEBBB7', '#82928D', '#6E7D79', '#586562', '#3B4543', '#626F6C', '#252C2B')  # cathedral roof
ROCK = tones('#D3CDB8', '#B0A890', '#988F77', '#78705B', '#575141', '#8A826B', '#3A362C')
BLUE = tones('#8FB2E6', '#3A68B4', '#2F5BA3', '#244A88', '#183461', '#29529A', '#101F3C')  # ZET tram
RED, NAVY, GREEN = rgb('#C8322E'), rgb('#2D4F9E'), rgb('#4E7A3E')
IRON, WOOD, LEAF = rgb('#33393A'), rgb('#6A452D'), rgb('#5E8A4A')
WALLS = [rgb(c) for c in ('#E9C77E', '#EFE3C8', '#CFCAC0', '#C3D2B6', '#E5BBA9', '#B9C6CF', '#F0D58A',
                          '#D9C2A3')]
WATER = (rgb('#5B95B8'), rgb('#4479A0'), rgb('#D8EEF6'))


# ------------------------------------------------------------- primitives --

def surface(s, a, e1, e2, color):
    """Paint the parallelogram a, a+e1, a+e1+e2, a+e2 (3D (i, j, z) vectors) with color(u, t), where
    (u, t) in [0, 1]^2 are its own coordinates: tiled roofs with heraldry follow the slope."""
    p0 = P(s, *a)
    pu = P(s, a[0]+e1[0], a[1]+e1[1], a[2]+e1[2])
    pt = P(s, a[0]+e2[0], a[1]+e2[1], a[2]+e2[2])
    m00, m01 = pu[0]-p0[0], pt[0]-p0[0]
    m10, m11 = pu[1]-p0[1], pt[1]-p0[1]
    det = m00*m11-m01*m10
    pts = [p0, pu, (pu[0]+pt[0]-p0[0], pu[1]+pt[1]-p0[1]), pt]
    for x, y in iso.polygon_pixels(pts):
        dx, dy = x+.5-p0[0], y+.5-p0[1]
        u, t = (m11*dx-m01*dy)/det, (m00*dy-m10*dx)/det
        s.put(x, y, color(min(max(u, 0), .999), min(max(t, 0), .999)))


def lancet(u, v, centre, half, spring, colour):
    """Pointed (Gothic) opening centred at u=centre, `half` wide, springing at `spring`."""
    du = abs(u-centre)
    if du <= half and v < spring + (half-du)*1.6:
        return colour
    return None


def gable(s, i, j, wi, z, rise, material, along_i=True, crockets=True):
    """Triangular wimperg gable on the +j face (along_i) or +i face, with crockets and a finial."""
    if along_i:
        a, b, apex = P(s, i, j, z), P(s, i+wi, j, z), P(s, i+wi/2, j, z+rise)
    else:
        a, b, apex = P(s, i, j, z), P(s, i, j-wi, z), P(s, i, j-wi/2, z+rise)
    poly(s, [a, b, apex], lambda x, y: material['lit' if along_i else 'dark'] if int(y) % 4 else material['line'])
    seg(s, a, apex, material['hi']); seg(s, apex, b, material['hi'] if along_i else material['mid'])
    if crockets:
        for k in range(1, 4):
            for p, q in ((a, apex), (b, apex)):
                x, y = p[0]+(q[0]-p[0])*k/4, p[1]+(q[1]-p[1])*k/4
                s.put(x, y-1, material['hi'])
    seg(s, apex, (apex[0], apex[1]-3), material['hi'])


def pinnacle(s, i, j, z, height, material, r=.2):
    """Slim Gothic pinnacle: shaft and a pointed cap with a finial."""
    block(s, i-r, j-r, 2*r, 2*r, height*.55, material, lambda u, v, lit: None, z=z)
    T, R, B, L = corners(s, i-r, j-r, 2*r, 2*r, z+height*.55)
    apex = P(s, i, j, z+height)
    poly(s, [L, B, apex], lambda x, y: material['lit'])
    poly(s, [B, R, apex], lambda x, y: material['dark'])
    seg(s, B, apex, material['hi'])


def spire(s, ci, cj, r, base, height, material):
    """Octagonal openwork neo-Gothic spire: tracery openings in every face, crockets along the
    ribs, a moulded collar and a gilded cross."""
    sides = 8
    faces = []
    for n in range(sides):
        a, b = (n+.5)*math.tau/sides, (n+1.5)*math.tau/sides
        key = 'lit' if math.sin((a+b)/2)-.5*math.cos((a+b)/2) > .05 else 'dark'
        faces.append((math.cos(a)+math.sin(a)+math.cos(b)+math.sin(b), a, b, key))
    apex = P(s, ci, cj, base+height)
    for _, a, b, key in sorted(faces):
        pa = P(s, ci+r*math.cos(a), cj+r*math.sin(a), base)
        pb = P(s, ci+r*math.cos(b), cj+r*math.sin(b), base)
        def color(x, y, pa=pa, pb=pb, key=key):
            t = (pa[1]-y)/(pa[1]-apex[1]+1e-6)          # 0 at the base, 1 at the apex
            mx = (pa[0]+pb[0])/2*(1-t)+apex[0]*t
            w = abs(pb[0]-pa[0])/2*(1-t)+.01
            k = (x-mx)/w
            band_ = int(t*14)
            if band_ % 2 == 1 and abs(k) < .3 and t < .75 and int(t*42) % 3:
                return material['deep'] if key == 'dark' else rgb('#6A665D')  # tracery slit
            if int(t*14*3) % 3 == 0 and band_ % 2 == 0 and t < .75:
                return material['line']
            return material[key]
        poly(s, [pa, pb, apex], color)
        seg(s, pa, apex, material['hi' if key == 'lit' else 'mid'])
        for k in range(1, 9):
            x = pa[0]+(apex[0]-pa[0])*k/9
            y = pa[1]+(apex[1]-pa[1])*k/9
            s.put(x+(1 if pa[0] > apex[0] else -1), y, material['hi'])  # crockets
    x, y = apex
    seg(s, (x, y), (x, y-7), GOLD['dark'])
    seg(s, (x-2, y-5), (x+2, y-5), GOLD['lit'])


def chequy(a, b, n=5):
    """Croatian chequy (šahovnica): red first, n x n."""
    return RED if (int(a*n)+int(b*n)) % 2 == 0 else WHITE['hi']


def shield(a, b):
    """Inside a heater shield, a across, b from the top."""
    if not (0 <= a <= 1 and 0 <= b <= 1):
        return False
    if b < .55:
        return True
    return abs(a-.5) < .5*math.sqrt(max(0, 1-((b-.55)/.45)**2))


def flag(s, i, j, z, height=20):
    """Croatian tricolour (red, white, blue) with the chequy shield across the white."""
    seg(s, P(s, i, j, z), P(s, i, j, z+height), IRON)
    for n, c in enumerate((RED, WHITE['hi'], NAVY)):
        poly(s, [P(s, i+a, j, z+height-1-n*2.2-b) for a, b in ((0, 0), (1.8, 0), (1.8, 2.2), (0, 2.2))],
             lambda x, y, c=c: c)
    x, y = P(s, i+.9, j, z+height-3)
    for dx in range(-1, 2):
        for dy in range(-2, 2):
            s.put(x+dx, y+dy, RED if (dx+dy) % 2 else WHITE['hi'])


# ------------------------------------------------------------- landmarks --

def cathedral(scene, i, j):
    """Assumption Cathedral on Kaptol: Bollé's twin neo-Gothic towers with clocks, gabled belfry
    stages, corner pinnacles and openwork octagonal spires; portal under a wimperg, the great
    pointed west window, buttressed nave and steep roof, the Kaptol rampart's round tower and the
    gilded Virgin on her column with four angels in front."""
    W, D, H = 6.6, 15, 36
    TH = 92
    def draw(s):
        # Apse and choir at the east end, then the hall nave with buttresses and lancets.
        block(s, i+.9, j, W-1.8, 2.4, H-6, STONE,
              lambda u, v, lit: lancet(int(u) % 10, v, 5, 1.6, 22, GLASS['dark']) if 8 < v else None)
        hip_roof(s, i+.8, j-.1, W-1.6, 2.6, H-6, 14, SLATE)
        def side(u, v, lit):
            c = int(u) % 12
            if c in (0, 1):
                return STONE['hi' if lit else 'mid'] if int(v) % 9 else STONE['line']  # buttress
            o = lancet(c, v, 6.5, 2, 26, GLASS['dark'])
            if o and v > 8:
                return o if int(v) % 6 else STONE['mid']   # tracery transom
            if int(v) in (6, H-3):
                return STONE['lit' if lit else 'dark']
            return stone_courses(STONE, 4, 12)(u, v, lit)
        block(s, i, j+2.3, W, D-4.4, H, STONE, side)
        band(s, i, j+2.3, W, D-4.4, H-2, STONE, 2)
        # Steep nave roof in patinated sheet with a ridge cresting and a slim ridge turret.
        T, R, B, L = corners(s, i-.1, j+2.2, W+.2, D-4.2, H)
        a, b = P(s, i+W/2, j+2.2, H+26), P(s, i+W/2, j+D-1.9, H+26)
        poly(s, [T, a, b, L], lambda x, y: SLATE['mid'] if int(y) % 3 else SLATE['line'])
        poly(s, [R, B, b, a], lambda x, y: SLATE['dark'] if int(y) % 3 else SLATE['deep'])
        seg(s, a, b, SLATE['hi'])
        for k in range(12):
            x, y = a[0]+(b[0]-a[0])*k/11, a[1]+(b[1]-a[1])*k/11
            s.put(x, y-1, SLATE['hi'])
        x, y = P(s, i+W/2, j+5, H+26)
        seg(s, (x, y), (x, y-12), SLATE['dark']); seg(s, (x+1, y), (x+1, y-9), SLATE['deep'])
        # Flying buttress pinnacles along the visible (south) flank.
        for k in range(4):
            pinnacle(s, i+W+.15, j+3.2+k*2.6, H-4, 12, STONE, .22)
        # West front: the twin towers either side of the gabled centre.
        def belfry(u, v, lit):
            c = int(u)
            span = 17 if lit else 19
            if c in (0, 1) or c in (span-2, span-1):
                return STONE['hi' if lit else 'mid'] if int(v) % 10 else STONE['line']   # angle buttress
            if int(v) in (H, H+1, 62, 63, TH-2, TH-1):
                return STONE['lit' if lit else 'dark']
            if 50 <= v < 60:                                    # clock stage
                dx, dy = u-span/2, v-55
                if dx*dx+dy*dy < 14:
                    if dx*dx+dy*dy < 9:
                        if abs(dx) < .7 and 0 <= dy < 3 or abs(dy) < .7 and 0 <= dx < 2.5:
                            return GOLD['dark']
                        return WHITE['hi']
                    return GOLD['lit']
            if v > 64:                                          # paired belfry lancets
                o = lancet(u, v, span/2-2.5, 1.5, 80, rgb('#4A463F')) or lancet(u, v, span/2+2.5, 1.5, 80, rgb('#4A463F'))
                if o:
                    return o
            elif v > H+3:
                o = lancet(u, v, span/2, 1.6, 44, GLASS['dark'])
                if o:
                    return o
            elif v > 8:
                o = lancet(u, v, span/2, 1.5, 24, GLASS['dark'])
                if o:
                    return o
            return stone_courses(STONE, 4, 12)(u, v, lit)
        def tower(a):
            b = j+D-2.4
            block(s, a, b, 2.2, 2.4, TH, STONE, belfry)
            for k, zz in enumerate((H, 62)):
                band(s, a, b, 2.2, 2.4, zz, STONE, 2)
            # Gabled belfry crown: wimpergs on both faces, corner pinnacles, then the spire.
            band(s, a, b, 2.2, 2.4, TH, STONE, 2)
            gable(s, a+.15, b+2.4, 1.9, TH+2, 14, STONE)
            gable(s, a+2.2, b+2.25, 2.1, TH+2, 14, STONE, along_i=False)
            for pa, pb in ((a, b), (a+2.2, b), (a, b+2.4), (a+2.2, b+2.4)):
                pinnacle(s, pa, pb, TH+2, 13, STONE)
            spire(s, a+1.1, b+1.2, 1.0, TH+2, 74, STONE)
        tower(i-.1)
        a, fw = i+2.1, W-4.2
        def front(u, v, lit):
            if not lit:
                return None
            mid = fw*4
            du = abs(u-mid)
            # Portal with stepped jambs, tympanum and wimperg.
            if du < 5.5 and v < 14+(5.5-du)*1.5:
                if du > 4 or v > 14+(4-du)*1.5:
                    return STONE['hi'] if int(du) % 2 else STONE['dark']
                if v > 11:
                    return GOLD['mid'] if (int(u)+int(v)) % 3 == 0 else STONE['mid']  # tympanum figures
                return WOOD if int(u) % 3 else rgb('#4A3020')
            # Great pointed window with mullions above.
            if du < 4 and 27 < v < 46+(4-du)*1.6:
                if du > 3.1 or int(u) % 3 == 0 and v < 46:
                    return STONE['lit']
                return GLASS['dark'] if int(v) % 5 else STONE['mid']
            if int(v) in (24, 25):
                return STONE['hi']
            return stone_courses(STONE, 4, 12)(u, v, lit)
        block(s, a, j+D-1.8, fw, 1.9, H+6, STONE, front)
        gable(s, a, j+D+.1, fw, H+6, 22, STONE)
        gable(s, a+fw/2-1.1, j+D+.12, 2.2, 21, 14, STONE)        # portal wimperg
        statue(s, a+fw/2, j+D-.4, H+6+13, 6, STONE, 0)
        tower(i+W-2.1)
        for k in range(3):
            block(s, a-.6, j+D+.1+k*.3, fw+1.2, .35, 3-k, STONE)
        # Kaptol rampart: a stretch of wall and a round tower south-east of the church.
        wi_ = i+W+1.4
        cover = block(s, wi_, j+5, .8, 8, 14, TOWER, stone_courses(TOWER, 4, 10))
        crenellate(s, wi_, j+5, .8, 8, 14, TOWER, cover, step=4, height=3)
        cylinder(s, wi_+.4, j+13.5, 1.5, 1.5, 0, 22, TOWER,
                 lambda u, v, lit: rgb('#3A352C') if int(u) % 10 in (4, 5) and 12 < v < 16 else stone_courses(TOWER, 4, 9)(u, v, lit))
        revolve(s, wi_+.4, j+13.5, 1.65, 22, 14, [(0, 1), (1, .04)], CLAY, ribs=3)
    scene.add(i+j+W+D+4, draw)

    # The Virgin's column in front: fountain basin, four gilded angels, the gilded Virgin.
    fi, fj = i+W/2, j+D+3.6
    def column(s):
        slab(s, [(fi+1.4*math.cos(t*math.tau/24), fj+1.4*math.sin(t*math.tau/24)) for t in range(24)], 0, 2, STONE)
        poly(s, [P(s, fi+1.15*math.cos(t*math.tau/24), fj+1.15*math.sin(t*math.tau/24), 2.2) for t in range(24)],
             lambda x, y: WATER[2] if h01(x//2, y, 5101) < .15 else WATER[0])
        block(s, fi-.35, fj-.35, .7, .7, 6, STONE, z=2)
        for t in (math.pi/4, 3*math.pi/4, 5*math.pi/4, 7*math.pi/4):
            ai, aj = fi+.6*math.cos(t), fj+.6*math.sin(t)
            cylinder(s, ai, aj, .12, .12, 8, 3, GOLD)
            x, y = P(s, ai, aj, 11)
            s.put(x, y, GOLD['hi']); s.put(x-1, y+1, GOLD['lit']); s.put(x+1, y+1, GOLD['lit'])  # wings
        cylinder(s, fi, fj, .17, .17, 8, 22, STONE, lambda u, v, lit: STONE['hi'] if lit and int(u) % 3 == 0 else None)
        cylinder(s, fi, fj, .26, .26, 30, 1.5, STONE)
        statue(s, fi, fj, 31, 7, GOLD, 0)
    scene.add(fi+fj+1.5, column)


def st_mark(scene, i, j, z=0):
    """St Mark's Church: low Gothic nave whose steep lit slope is laid in glazed tiles showing the
    arms of the Triune Kingdom (chequy, Dalmatia's leopards, Slavonia's marten) and Zagreb's white
    castle on red; the bell tower with clock and tiled pyramid, the sculpted south portal under its
    canopy, buttresses, lancets and the polygonal east end."""
    W, D, H = 8.4, 4.4, 20
    def triune(a, b):
        if b < .14:                                            # crown
            return GOLD['lit'] if int(a*10) % 2 == 0 and b > .05 or b > .1 else None
        a2, b2 = a, (b-.14)/.86
        if not shield(a2, b2):
            return None
        if b2 < .45:
            if a2 < .5:
                return chequy(a2*2, b2/.45)
            if (round(a2*6) in (4, 5, 6) and abs(b2-.22) < .06) or (round(a2*6) == 5 and abs(b2-.36) < .06):
                return GOLD['lit']                             # three leopard heads
            return NAVY
        if abs(b2-.68) < .07:
            return RED if abs(b2-.68) < .04 else WHITE['hi']  # Slavonia's band (Drava and Sava)
        if abs(b2-.68) < .14 and abs(a2-.5) < .18:
            return rgb('#6A4A2A')                              # the marten
        if b2 < .55 and abs(a2-.5) < .06:
            return GOLD['lit']                                 # six-pointed star
        return NAVY
    def zagreb(a, b):
        if not shield(a, b):
            return None
        # White castle with three towers and an open gate; star and crescent above.
        if .12 < b < .22 and (abs(a-.3) < .05 or abs(a-.72) < .05):
            return GOLD['lit'] if a < .5 else WHITE['hi']
        if b > .62 and abs(a-.5) < .1:
            return rgb('#3A2A22') if b < .9 else RED
        if b > .5 and .14 < a < .86 or b > .3 and any(abs(a-c) < .1 for c in (.24, .5, .76)):
            if b < .34 and int(a*30) % 2:
                return RED                                     # merlons
            return WHITE['hi'] if int(b*20) % 4 else WHITE['mid']
        return RED
    def roof(u, t):
        # Shields sit with their tops near the ridge; the rest is a chevron of glazed tiles.
        for left, art in ((.06, triune), (.53, zagreb)):
            a, b = (u-left)/.41, (1-t)/.92
            if 0 <= a <= 1 and .02 <= b <= 1:
                c = art(a, b-.02)
                if c is not None:
                    return c
        k = (int(u*64)//3 + abs(int(t*24) % 6-3)) % 4
        return (rgb('#3E6B4A'), rgb('#9A4A2E'), WHITE['lit'], rgb('#2F5B98'))[k] if int(t*24) % 2 else rgb('#6B3A26')
    def draw(s):
        def wall(u, v, lit):
            c = int(u) % 13
            if c in (0, 1):
                return WHITE['hi' if lit else 'mid'] if int(v) % 7 else WHITE['line']
            o = lancet(c, v, 7, 1.5, 12, GLASS['dark'])
            if o and v > 4:
                return o
            return stone_courses(WHITE, 4, 9)(u, v, lit)
        # Bell tower at the west end, drawn first so the heraldic slope stays clear of it.
        a, b = i-2.0, j+.3
        TH = 52
        def bell(u, v, lit):
            c = int(u)
            if c in (0, 1) or int(v) in (24, 25, 38, 39, TH-1):
                return WHITE['hi' if lit else 'mid']
            if 27 <= v <= 35:
                dx, dy = u-9, v-31
                if dx*dx+dy*dy < 12:
                    if abs(dx) < .7 and 0 <= dy < 3 or abs(dy) < .7 and 0 <= dx < 2:
                        return IRON
                    return WHITE['hi'] if dx*dx+dy*dy < 7 else GOLD['lit']
            if v > 40:
                return arch_opening(u, v, 9, 2.4, 46, rgb('#3F3A33'))
            o = lancet(u, v, 9, 1, 16, GLASS['dark'])
            return o if v > 10 else None
        block(s, a, b, 2.2, 2.2, TH, WHITE, bell, z=z)
        band(s, a, b, 2.2, 2.2, z+TH, WHITE, 2)
        T, R, B, L = corners(s, a-.1, b-.1, 2.4, 2.4, z+TH+2)
        apex = P(s, a+1.1, b+1.1, z+TH+26)
        poly(s, [L, B, apex], lambda x, y: (GREEN, rgb('#9A4A2E'), WHITE['lit'])[(int(x)//2+int(y)//2) % 3] if int(y) % 2 else CLAY['dark'])
        poly(s, [B, R, apex], lambda x, y: CLAY['dark'] if int(y) % 2 else CLAY['deep'])
        seg(s, B, apex, CLAY['hi'])
        apple(s, a+1.1, b+1.1, z+TH+26, .22)
        # Polygonal east end, lower and narrower.
        block(s, i+W-.4, j+.8, 1.6, D-1.6, H-2, WHITE, wall, z=z)
        hip_roof(s, i+W-.5, j+.7, 1.8, D-1.4, z+H-2, 9, CLAY)
        block(s, i, j, W, D, H, WHITE, wall, z=z)
        band(s, i, j, W, D, z+H-1, WHITE, 1)
        # Steep gabled roof along i; the lit (+j) slope carries the heraldry.
        rise = 30
        surface(s, (i, j+D+.1, z+H), (W, 0, 0), (0, -D/2-.1, rise), roof)
        T, R, B, L = corners(s, i, j-.1, W, D+.2, z+H)
        ridge_a, ridge_b = P(s, i, j+D/2, z+H+rise), P(s, i+W, j+D/2, z+H+rise)
        poly(s, [B, R, ridge_b], lambda x, y: WHITE['dark'] if int(y) % 6 else WHITE['line'])  # east gable
        seg(s, ridge_a, ridge_b, rgb('#E9E1CF'))
        seg(s, L, B, rgb('#4A2A1C')); seg(s, B, ridge_b, rgb('#4A2A1C'))
        # The south portal: canopy, niches of figures and the wooden doors.
        pa = i+3.4
        def portal(u, v, lit):
            if not lit:
                return None
            du = abs(u-8)
            if du < 7.5 and v < 22:
                if du < 3 and v < 9+(3-du):
                    return WOOD if int(u) % 3 else rgb('#4A3020')
                if v > 10 and int(u) % 3 == 1 and int(v) % 5 in (1, 2, 3):
                    return GOLD['dark'] if int(v) > 17 else TOWER['deep']  # figures in niches
                return TOWER['lit'] if int(v) % 4 else TOWER['line']
            return None
        block(s, pa, j+D, 2, .6, 22, TOWER, portal, z=z)
        gable(s, pa, j+D+.6, 2, z+22, 9, TOWER)
        for k in range(2):
            block(s, pa+.1, j+D+.6+k*.3, 1.8, .35, 2-k, TOWER, z=z)
    scene.add(i+j+W+D+3, draw)


def lotrscak(scene, i, j, z=0):
    """Lotrščak Tower: square Romanesque tower of pale rubble stone with dressed quoins, small
    arched windows, the noon-gun window with the Grič cannon, battlemented viewing platform and
    the timber shop door; Strossmayer promenade railing and a gas lamp at its foot."""
    S, H = 2.8, 58
    def draw(s):
        def wall(u, v, lit):
            c = int(u)
            w = S*8
            if c < 3 and int(v) % 6 < 3 or c > w-4 and int(v) % 6 >= 3 or c in (0, int(w)-1):
                return TOWER['hi' if lit else 'mid']                 # quoins
            if v < 11 and lit:
                o = arch_opening(u, v, w/2, 2.6, 6, WOOD)
                if o:
                    return o if int(u) % 3 else rgb('#4A3020')
                if abs(u-w/2) < 3.6 and v < 10:
                    return TOWER['hi']
            for level, half in ((20, 1.6), (32, 1.6), (44, 2.2)):
                o = arch_opening(u, v, w/2, half, level, rgb('#3A352C'))
                if o and v > level-4:
                    if level == 44 and not lit and abs(u-w/2) < 1.1 and level-2 < v < level:
                        return IRON                                  # the Grič cannon's muzzle
                    return o
            if int(v) in (H-6, H-5):
                return TOWER['lit' if lit else 'dark']
            if h01(int(u)//2, int(v)//2, 6101) < .12:
                return TOWER['mid' if lit else 'line']               # rubble texture
            return stone_courses(TOWER, 5, 8)(u, v, lit)
        cover = block(s, i, j, S, S, H, TOWER, wall, z=z)
        # Corbel table and the battlemented platform.
        block(s, i-.15, j-.15, S+.3, S+.3, 3, TOWER,
              lambda u, v, lit: TOWER['deep'] if int(u) % 4 == 0 and v < 2 else None, z=z+H)
        cover = block(s, i-.15, j-.15, S+.3, S+.3, 2, TOWER, z=z+H+3)
        crenellate(s, i-.15, j-.15, S+.3, S+.3, z+H+5, TOWER, cover, step=4, height=4)
        # Promenade railing and a lamp beside the tower.
        for k in range(6):
            seg(s, P(s, i+S+.6, j-1+k*.7, z), P(s, i+S+.6, j-1+k*.7, z+4), IRON)
        seg(s, P(s, i+S+.6, j-1, z+4), P(s, i+S+.6, j+2.5, z+4), IRON)
        lamp(s, i+S+.6, j+S+.4, z, 12, WHITE)
    scene.add(i+j+2*S+1, draw)


def stone_gate(scene, i, j, z=0):
    """Kamenita vrata: the last town gate, a squat tower of rusticated stone pierced by a tall
    round-arched passage with the candle-lit shrine behind its wrought-iron grille, a plastered
    upper storey with a curved Baroque gable and niche, a steep clay hip, the lower gatehouse wing,
    and St George slaying the dragon on his pillar beside it."""
    W, D, H = 3.6, 3.4, 36
    def draw(s):
        # Lower gatehouse wing on the east.
        block(s, i+W, j+.5, 2.6, D-.5, 22, OCHRE,
              lambda u, v, lit: WHITE['lit' if lit else 'dark'] if int(v) in (1, 20, 21) else
              windows(OCHRE, 22, 9, 10, hood=True)(u, v, lit), z=z)
        hip_roof(s, i+W-.1, j+.4, 2.8, D-.3, z+22, 10, CLAY)
        def wall(u, v, lit):
            mid = (W*8 if lit else D*8)/2
            du = abs(u-mid)
            if lit and du < 9.5 and v < 16+math.sqrt(max(0, 9.5**2-du*du)):
                if du > 7.5 or v > 16+math.sqrt(max(0, 7.5**2-du*du)):
                    return TOWER['hi'] if int(math.atan2(v-16, u-mid)*9) % 2 else TOWER['dark']  # voussoirs
                # Into the dark passage: the shrine grille glows with candles.
                if 5 < v < 17 and du < 4.5:
                    if int(u) % 2 == 0 or int(v) % 4 == 0:
                        return IRON
                    return GOLD['lit'] if h01(int(u), int(v), 6202) < .5 else rgb('#E8873A')
                return rgb('#2E2A26') if v > 1 else TOWER['deep']
            if v < 22:
                if int(v) % 5 == 0 or (int(u)+(int(v)//5)*4) % 8 == 0:
                    return TOWER['line' if lit else 'deep']                       # rustication
                return TOWER['lit' if lit else 'dark']
            if int(v) in (22, 23, H-2, H-1):
                return WHITE['hi' if lit else 'mid']
            o = arch_opening(u, v, mid, 2, 30, OCHRE['deep'] if lit else GLASS['dark'])
            if o and v > 25:
                return o
            return None
        block(s, i, j, W, D, H, OCHRE, wall, z=z)
        hip_roof(s, i-.1, j-.1, W+.2, D+.2, z+H, 16, CLAY)
        apple(s, i+W/2, j+D/2, z+H+16, .18)
        # Curved Baroque gable over the passage, with a niche and scrolls.
        n = 12
        crest = [P(s, i+.5+(W-1)*k/n, j+D+.05, z+H+9*math.sin(math.pi*k/n)**.7) for k in range(n+1)]
        poly(s, [P(s, i+.5, j+D+.05, z+H)]+crest+[P(s, i+W-.5, j+D+.05, z+H)], lambda x, y: OCHRE['lit'])
        for p0, p1 in zip(crest, crest[1:]):
            seg(s, p0, p1, WHITE['hi'])
        x, y = P(s, i+W/2, j+D+.05, z+H+4)
        for dy in range(-2, 3):
            s.put(x, y+dy, OCHRE['deep']); s.put(x+1, y+dy, OCHRE['deep'])
        # St George on his pillar, lance down into the dragon.
        gi, gj = i-.9, j+D+.4
        block(s, gi-.35, gj-.35, .7, .7, 14, TOWER, stone_courses(TOWER, 3, 6), z=z)
        band(s, gi-.35, gj-.35, .7, .7, z+13, TOWER, 1)
        horse_rider(s, gi, gj-.1, z+15, BRONZE, .6, lance=True)
        x, y = P(s, gi+.1, gj+.7, z+15)
        for dx in range(-2, 3):
            s.put(x+dx, y, rgb('#4E7A5E')); s.put(x+dx//2, y-1, rgb('#6E9A7E'))     # dragon
    scene.add(i+j+W+D+3, draw)


def umbrella(s, i, j, z, seed=0):
    """Dolac's red Šestine umbrella over a laden stall."""
    block(s, i-.45, j-.35, .9, .7, 4, palette_of(rgb('#9C7A58')), z=z)
    for k in range(5):
        x, y = P(s, i-.3+k*.15, j+.1, z+4.5)
        s.put(x, y, (rgb('#E5533C'), rgb('#F2C14E'), LEAF, rgb('#8A3A6A'))[(k+seed) % 4])
    seg(s, P(s, i, j, z+4), P(s, i, j, z+12), WOOD)
    cx, cy = P(s, i, j, z+12)
    for dy in range(0, 5):
        r = 1.5+dy*1.6
        for dx in range(-int(r*1.8), int(r*1.8)+1):
            ang = math.atan2(dy*2, dx)
            edge = dy == 4
            c = WHITE['hi'] if edge and dx % 3 == 0 else rgb('#B82A26') if dx > 0 else rgb('#D8403A')
            if int((ang*8/math.pi)) % 2 and not edge:
                c = rgb('#A02420') if dx > 0 else rgb('#C93530')        # gores
            s.put(cx+dx, cy-4+dy, c)
    s.put(cx, cy-5, WOOD)


def dolac(scene, i, j):
    """Dolac Market: the raised terrace over its arcaded hall, a grid of red Šestine umbrellas over
    stalls of produce, the double stair down to Ban Jelačić Square and Kumica Barica in bronze."""
    W, D, Z = 9, 7, 12
    def draw(s):
        def hall(u, v, lit):
            c = int(u) % 9
            if c in (0, 1) or v < 2 or int(v) >= Z-2:
                return TOWER['hi' if lit else 'mid']
            if 2 < v < Z-2:
                return arch_opening(c, v, 5, 2.4, 6, GLASS['dark'] if lit else rgb('#3F3A33'))
            return None
        block(s, i, j, W, D, Z, TOWER, hall)
        poly(s, list(corners(s, i, j, W, D, Z)),
             lambda x, y: rgb('#C9BFAF') if (int(x)+2*(int(y) % 2)) % 5 else rgb('#B3A996'))
        balustrade(s, (i+.1, j+D-.1), (i+2.6, j+D-.1), Z, 3, WHITE)
        balustrade(s, (i+5.4, j+D-.1), (i+W-.1, j+D-.1), Z, 3, WHITE)
        balustrade(s, (i+W-.1, j+.1), (i+W-.1, j+D-.1), Z, 3, WHITE)
        n = 0
        for b in (1.2, 3.1, 5.0):
            for a in (1.1, 3.0, 4.9, 6.8):
                umbrella(s, i+a+(.5 if b == 3.1 else 0), j+b, Z, n)
                n += 1
        # Kumica Barica with her basket at the stair head.
        statue(s, i+4, j+D-.6, Z, 7, BRONZE, 0)
        x, y = P(s, i+4.2, j+D-.4, Z+6)
        for dx in range(-1, 2):
            s.put(x+dx, y, rgb('#A07A40')); s.put(x+dx, y-1, rgb('#E5533C') if dx else LEAF)
        # The stair down to the square, between the balustrades.
        for k in range(6):
            block(s, i+2.7, j+D+k*.4, 2.6, .4, Z-k*2, TOWER, lambda u, v, lit: TOWER['line'] if int(v) % 2 == 0 else None)
    scene.add(i+j+W+D+2, draw)


def horse_rider(s, i, j, z, material=BRONZE, k=1.0, lance=False):
    """Equestrian bronze facing +j at scale k: four legs (one foreleg raised), barrel, arched neck,
    head with ears, flowing tail; the rider's coat, head and busby, and the sabre held out ahead
    (or a lance pointing down for St George)."""
    m = material
    for di, dj, lift in ((-.2, -.5, 0), (.2, -.5, 0), (-.2, .5, 0), (.2, .55, 4)):
        top = P(s, i+di*k, j+dj*k*.9, z+7*k)
        foot = P(s, i+di*k, j+dj*k+(.25*k if lift else 0), z+lift*k)
        seg(s, foot, top, m['dark'] if di > 0 else m['lit'], 2 if k > .8 else 1)
    cylinder(s, i, j, .34*k, .75*k, z+6*k, 4.5*k, m,
             lambda u, v, lit: m['hi'] if lit and int(v) == int(3*k) else None)
    # Neck rising forward and the head with ears.
    for n in range(6):
        x, y = P(s, i, j+(.55+n*.09)*k, z+(9+n*1.3)*k)
        for dx in range(-1, 2):
            s.put(x+dx, y, m['lit'] if dx < 1 else m['dark'])
    block(s, i-.13*k, j+.95*k, .26*k, .6*k, 2.2*k, m, z=z+(15.5-2)*k)
    x, y = P(s, i, j+1.0*k, z+16.5*k)
    s.put(x, y-1, m['dark']); s.put(x+1, y-1, m['dark'])
    for n in range(5):                                                       # tail
        x, y = P(s, i+.02*n*k, j-(.75+.06*n)*k, z+(10-n*1.6)*k)
        s.put(x, y, m['dark']); s.put(x+1, y, m['deep'])
    # Rider: saddle cloth, coat, head, busby.
    block(s, i-.3*k, j-.2*k, .6*k, .5*k, 1.5*k, m, lambda u, v, lit: m['hi'] if lit and int(v) == 0 else None, z=z+10*k)
    cylinder(s, i, j, .22*k, .27*k, z+11.5*k, 3*k, m, lambda u, v, lit: m['line'] if int(u) % 4 == 0 else None)
    cylinder(s, i, j, .17*k, .2*k, z+14.5*k, 3*k, m)
    cylinder(s, i, j+.02*k, .1*k, .1*k, z+17.5*k, 2*k, m, lambda u, v, lit: m['hi'] if lit else None)
    cylinder(s, i, j+.02*k, .13*k, .13*k, z+19.5*k, 1.8*k, m)
    sh = P(s, i+.18*k, j+.15*k, z+16.5*k)
    hand = P(s, i+.3*k, j+.65*k, z+(18 if not lance else 14)*k)
    seg(s, sh, hand, m['lit'], 2 if k > .8 else 1)
    if lance:
        seg(s, hand, P(s, i+.15*k, j+1.6*k, z), rgb('#C9B98A'))
    else:
        seg(s, hand, P(s, i+.4*k, j+1.7*k, z+23*k), rgb('#ECEAE2'))           # sabre


def jelacic(scene, i, j):
    """Ban Jelačić Square: Fernkorn's equestrian bronze on its stepped granite pedestal, and the
    Manduševac fountain's flush basin with the uncovered stream to the east."""
    def draw(s):
        for k, r in enumerate((1.2, 1.0)):
            block(s, i+1.2-r, j+1.2-r, 2*r, 2*r, 2, TOWER, z=k*2)
        def ped(u, v, lit):
            if int(v) in (1, 2, 13, 14):
                return WHITE['hi' if lit else 'mid']
            if 5 < v < 11 and 3 < u < 11:
                return BRONZE['mid'] if lit else BRONZE['dark']     # inscription plaque
            return None
        block(s, i+.4, j+.4, 1.6, 1.6, 15, TOWER, ped, z=4)
        horse_rider(s, i+1.2, j+1.0, 19, BRONZE, 1.6)
    scene.add(i+j+4, draw)
    fi, fj = i+5.2, j-2.4
    def fountain(s):
        ring = [(fi+1.5*math.cos(t*math.tau/32), fj+1.5*math.sin(t*math.tau/32)) for t in range(32)]
        slab(s, ring, 0, 1.5, TOWER)
        poly(s, [P(s, fi+1.25*math.cos(t*math.tau/32), fj+1.25*math.sin(t*math.tau/32), 1.6) for t in range(32)],
             lambda x, y: WATER[2] if h01(x//2, y, 6301) < .14 else WATER[1] if (x+y) % 7 == 0 else WATER[0])
        x, y = P(s, fi, fj, 1.6)
        for k in range(5):
            s.put(x, y-k, WATER[2]); s.put(x-1+(k % 3), y-k-1, WATER[2])
    scene.add(fi+fj+1, fountain)


def theatre(scene, i, j):
    """Croatian National Theatre: Fellner & Helmer's ochre-yellow neo-Baroque house, white
    pilasters and window aediculae, the projecting columned entrance with balcony and pediment
    statues, corner pavilions under copper cupolas, the green dome over the auditorium and the
    stage house; Meštrović's Well of Life sunk in the square before it."""
    W, D, H = 7.4, 10, 30
    def draw(s):
        def wall(u, v, lit):
            c = int(u) % 10
            if c in (0, 1):
                return WHITE['hi' if lit else 'mid']
            if v < 11:
                if int(v) % 3 == 0:
                    return YELLOW['mid'] if lit else YELLOW['line']   # rusticated ground floor
                return arch_opening(c, v, 5.5, 1.8, 6, GLASS['dark'])
            if int(v) in (11, 12, H-3, H-2):
                return WHITE['lit' if lit else 'dark']
            return windows(YELLOW, H, 10, 19, arched=True, hood=True)(u, v-11, lit)
        # Stage house at the back, the auditorium drum, then the front block.
        block(s, i+.6, j, W-1.2, 3.4, H+12, YELLOW, wall)
        band(s, i+.6, j, W-1.2, 3.4, H+10, WHITE, 2)
        hip_roof(s, i+.5, j-.1, W-1, 3.6, H+12, 8, SLATE)
        block(s, i, j+3.2, W, D-3.2, H, YELLOW, wall)
        band(s, i, j+3.2, W, D-3.2, H-2, WHITE, 2)
        hip_roof(s, i-.1, j+3.1, W+.2, D-3, H, 10, SLATE)
        ci, cj = i+W/2, j+5.4
        cylinder(s, ci, cj, 2.1, 2.1, H+4, 7, YELLOW,
                 lambda u, v, lit: WHITE['hi' if lit else 'mid'] if int(u) % 8 == 0 else
                 GLASS['dark'] if int(u) % 8 in (3, 4, 5) and 2 < v < 6 else None)
        revolve(s, ci, cj, 2.25, H+11, 12, DOME, COPPER, ribs=3, segments=32)
        cylinder(s, ci, cj, .45, .45, H+23, 4, WHITE)
        revolve(s, ci, cj, .55, H+27, 4, DOME, COPPER, ribs=2)
        apple(s, ci, cj, H+30, .2)
        # Corner pavilions on the front with cupolas and lanterns.
        for a in (i-.2, i+W-2.2):
            b = j+D-2.4
            block(s, a, b, 2.4, 2.6, H+5, YELLOW, wall)
            band(s, a, b, 2.4, 2.6, H+3, WHITE, 2)
            cylinder(s, a+1.2, b+1.3, .85, .85, H+5, 5, YELLOW,
                     lambda u, v, lit: WHITE['hi' if lit else 'mid'] if int(u) % 5 == 0 else GLASS['dark'] if 1 < v < 4 else None)
            revolve(s, a+1.2, b+1.3, 1.0, H+10, 10, HELMET, COPPER, ribs=4)
            apple(s, a+1.2, b+1.3, H+20, .2)
        # Entrance portico: paired columns, balcony and a pediment crowned by statues.
        a, fw = i+2.3, W-4.6
        def portico(u, v, lit):
            if not lit:
                return None
            c = int(u) % 6
            if v < 22:
                if c in (0, 1):
                    return WHITE['hi'] if c == 0 else WHITE['lit']
                if v > 18:
                    return WHITE['lit']
                return rgb('#5A4630') if v < 12 else GLASS['dark'] if int(v) % 4 else WHITE['mid']
            return WHITE['lit'] if int(v) % 4 else WHITE['mid']
        block(s, a, j+D, fw, .9, 28, YELLOW, portico)
        for k in range(8):
            seg(s, P(s, a+k*fw/7, j+D+.9, 22), P(s, a+k*fw/7, j+D+.9, 25), WHITE['dark'])
        seg(s, P(s, a, j+D+.9, 25), P(s, a+fw, j+D+.9, 25), WHITE['hi'])
        pediment(s, a-.1, j+D, fw+.2, .9, 28, 9, WHITE)
        statue(s, a+fw/2, j+D+.4, 36, 5, WHITE, 1)               # crowning figure
        for t in (0, 1):
            x, y = P(s, a+fw*t, j+D+.5, 29)
            for dy in range(4):
                s.put(x, y-dy, GOLD['lit'] if dy < 3 else GOLD['hi']); s.put(x+1, y-dy, GOLD['dark'])
        for k in range(3):
            block(s, a-.3, j+D+.9+k*.3, fw+.6, .35, 3-k, STONE)
    scene.add(i+j+W+D+3, draw)
    # The Well of Life: a sunken round basin ringed by bronze figures.
    fi, fj = i+W/2, j+D+4.2
    def well(s):
        ring = [(fi+1.6*math.cos(t*math.tau/32), fj+1.6*math.sin(t*math.tau/32)) for t in range(32)]
        slab(s, ring, 0, 1.5, STONE)
        poly(s, [P(s, fi+1.35*math.cos(t*math.tau/32), fj+1.35*math.sin(t*math.tau/32), 1.6) for t in range(32)],
             lambda x, y: rgb('#3E5E6E') if (x+y) % 5 else WATER[0])
        # Ring of bronze figures leaning in over the water.
        for n in range(7):
            t = n*math.tau/7+.3
            gi, gj = fi+1.0*math.cos(t), fj+1.0*math.sin(t)
            hi_, hj_ = fi+.7*math.cos(t), fj+.7*math.sin(t)
            seg(s, P(s, gi, gj, 1.5), P(s, hi_, hj_, 5), BRONZE['lit' if math.sin(t) > 0 else 'dark'], 2)
            x, y = P(s, hi_, hj_, 6)
            s.put(x, y, BRONZE['hi']); s.put(x+1, y, BRONZE['mid']); s.put(x, y-1, BRONZE['deep'])
    scene.add(fi+fj+1.5, well)


def pavilion(scene, i, j):
    """Art Pavilion: long yellow exhibition hall of Art Nouveau classicism, end pavilions with
    arched windows, the domed centre on a glazed drum, the pedimented entrance with paired
    columns and statues, busts of painters in roundels along the flanks."""
    W, D, H = 10, 4.4, 26
    def draw(s):
        def wall(u, v, lit):
            c = int(u) % 12
            if c in (0, 1):
                return WHITE['hi' if lit else 'mid']
            if int(v) in (1, 2, H-3, H-2):
                return WHITE['lit' if lit else 'dark']
            if 4 < v < 20:
                o = arch_opening(c, v, 6.5, 2.4, 14, GLASS['dark'])
                if o:
                    return o if int(v) % 5 else WHITE['mid']
            if 20 < v < 24 and abs(c-6.5) < 1.6:
                return BRONZE['lit'] if lit else BRONZE['dark']           # painters' busts
            return None
        block(s, i, j, W, D, H, YELLOW, wall)
        band(s, i, j, W, D, H-1, WHITE, 2)
        hip_roof(s, i-.1, j-.1, W+.2, D+.2, H+1, 7, SLATE)
        for a in (i-.3, i+W-2.3):
            block(s, a, j-.3, 2.6, D+.6, H+4, YELLOW, wall)
            band(s, a, j-.3, 2.6, D+.6, H+2, WHITE, 2)
            hip_roof(s, a-.1, j-.4, 2.8, D+.8, H+4, 8, SLATE)
        ci, cj = i+W/2, j+D/2
        cylinder(s, ci, cj, 1.9, 1.9, H+1, 7, YELLOW,
                 lambda u, v, lit: WHITE['hi' if lit else 'mid'] if int(u) % 6 == 0 else GLASS['mid' if lit else 'dark'] if 2 < v < 6 else None)
        revolve(s, ci, cj, 2.05, H+8, 14, DOME, rgb_tones_glass(), ribs=2, segments=32)
        cylinder(s, ci, cj, .4, .4, H+21, 3, WHITE)
        apple(s, ci, cj, H+24, .18)
        # Entrance: projecting porch with paired columns under a pediment and statues.
        a, fw = i+W/2-1.6, 3.2
        def porch(u, v, lit):
            if not lit:
                return None
            c = int(u)
            if c in (1, 2, 5, 6, 19, 20, 23, 24):
                return WHITE['hi'] if c % 2 else WHITE['lit']
            if v < 16 and 8 <= c <= 17:
                return arch_opening(u, v, 12.8, 4, 10, rgb('#4A3828')) or YELLOW['lit']
            if int(v) in (17, 18, 26, 27):
                return WHITE['lit']
            return None
        block(s, a, j+D, fw, .9, 28, YELLOW, porch)
        pediment(s, a-.1, j+D, fw+.2, .9, 28, 8, WHITE)
        for t in (0, 1):
            statue(s, a+fw*t, j+D+.45, 29, 6, WHITE, t)
        for k in range(3):
            block(s, a-.6, j+D+.9+k*.3, fw+1.2, .35, 3-k, STONE)
    scene.add(i+j+W+D+3, draw)


def rgb_tones_glass():
    """Iron-and-glass dome: pale sky glass between dark green ribs."""
    return tones('#DDEFF2', '#A9CFD8', '#8DBAC6', '#6D9AA8', '#4A6F7C', '#3E5E58', '#243A36')


def funicular(scene, i, j, length, top, z0=0):
    """Uspinjača: the short funicular down the Gradec slope along +j from the upper station by
    Lotrščak to Tomićeva street, with stone bed, rails, sleepers and one blue car part-way."""
    def draw(s):
        bed = [P(s, i, j, z0+top), P(s, i, j+length, z0), P(s, i+1, j+length, z0), P(s, i+1, j, z0+top)]
        poly(s, bed, lambda x, y: rgb('#8C7A62') if (int(x)+int(y)) % 4 else rgb('#6E5E4A'))
        seg(s, bed[1], bed[2], rgb('#4A3E30')); seg(s, bed[0], bed[1], TOWER['hi'])
        for k in range(int(length*3)):
            t = k/(length*3)
            seg(s, P(s, i+.15, j+length*t, z0+top*(1-t)+.5), P(s, i+.85, j+length*t, z0+top*(1-t)+.5), WOOD)
        for a in (.3, .7):
            seg(s, P(s, i+a, j, z0+top+1), P(s, i+a, j+length, z0+1), IRON)
        t = .5
        b, zz = j+length*t, z0+top*(1-t)
        block(s, i+.1, b-.7, .8, 1.4, 9, BLUE,
              lambda u, v, lit: GLASS['mid' if lit else 'dark'] if 4 < v < 8 and int(u) % 3 else
              WHITE['hi'] if int(v) == 2 else None, z=zz+1)
    scene.add(i+j+length+1, draw)


def tram(scene, i, j, seed=0):
    """Zagreb's blue ZET low-floor tram along i: three articulated sections, ribbon glazing,
    white band, doors, pantograph."""
    L = 4.6
    def body(u, v, lit):
        u, v = int(u), int(v)
        if v <= 1:
            return rgb('#2E2A28')
        if 4 <= v <= 8 and u % 12 not in (0, 6, 7):
            return GLASS['glint'] if v == 8 and u % 5 == 0 else rgb('#2E3C58')
        if v == 3:
            return WHITE['hi']
        if u % 12 in (6, 7) and v < 9:
            return rgb('#1E2E50')                                         # doors
        if v >= 10:
            return BLUE['hi'] if lit else BLUE['lit']
        return None
    def draw(s):
        cover = block(s, i, j, L, 1.1, 11, BLUE, body)
        x, y = P(s, i+L/2, j+.55, 11)
        seg(s, (x-2, y), (x+2, y-5), IRON); seg(s, (x+2, y-5), (x-2, y-8), IRON)
    scene.add(i+j+L+1.1, draw)


def townhouse(scene, i, j, wi=2.5, wj=3, floors=3, seed=0, z=0):
    """Zagreb Lower Town historicist houses: rusticated shop floors, stucco window pediments and
    hoods, a first-floor balcony on consoles, attic cornice, red clay hips with lucarnes and
    chimneys; some corner houses carry a tin-grey cupola, Upper Town houses stay low Baroque."""
    wall, height = palette_of(WALLS[seed % len(WALLS)]), floors*10+5
    base = windows(wall, height, 9, 10, hood=seed % 2 == 0)
    cupola = seed % 11 == 3 and floors >= 3
    def pattern(u, v, lit):
        c, level = int(u) % 9, int(v) % 10
        trim = WHITE['lit' if lit else 'dark']
        if v < 9:
            if 2 <= c <= 6:
                if c in (2, 6) or int(v) == 8:
                    return trim
                if (int(u)//9+seed) % 3 == 0:
                    return WOOD if v < 7 or c == 4 else trim
                return GLASS['dark'] if v > 2 else wall['deep']
            return wall['mid'] if int(v) % 3 == 0 else None
        if level == 9 and 10 < v < 20 and 2 <= c <= 6 and seed % 3 != 1:
            return WHITE['hi' if lit else 'mid']                          # pediment hoods
        if seed % 3 == 0 and 10 <= v <= 11 and 1 <= c <= 7:
            return IRON                                                   # balcony
        return base(u, v, lit)
    def draw(s):
        block(s, i, j, wi, wj, height, wall, pattern, z=z)
        band(s, i, j, wi, wj, z+1, TOWER, 2)
        band(s, i, j, wi, wj, z+height-2, WHITE, 2)
        hip_roof(s, i-.05, j-.05, wi+.1, wj+.1, z+height, 12 if seed % 3 else 15, CLAY)
        # Lucarne on the lit slope.
        x, y = P(s, i+wi/2, j+wj-.6, z+height+4)
        for dx in range(-2, 3):
            for dy in range(0, 4):
                s.put(x+dx, y-dy, WHITE['lit'] if abs(dx) == 2 or dy == 3 else GLASS['dark'])
        s.put(x, y-4, CLAY['hi'])
        block(s, i+wi-.7, j+.45, .4, .45, 9, TOWER, z=z+height+5)
        band(s, i+wi-.7, j+.45, .4, .45, z+height+13, CLAY, 2)
        if cupola:
            block(s, i+wi-1.1, j+wj-1.1, 1.2, 1.2, 6, wall, windows(wall, 6, 9, 6), z=z+height)
            revolve(s, i+wi-.5, j+wj-.5, .75, z+height+6, 10, DOME, tones('#B8C2C6', '#8E9AA0', '#7A868C', '#626D73', '#434C51', '#6B767C', '#2A3034'), ribs=4)
            apple(s, i+wi-.5, j+wj-.5, z+height+16, .15)
    scene.add(i+j+wi+wj, draw)


def gazebo(scene, i, j):
    """Zrinjevac's cast-iron music pavilion: octagonal deck, slender columns, lace frieze, roof."""
    def draw(s):
        cylinder(s, i, j, 1.3, 1.3, 0, 3, STONE)
        for n in range(8):
            t = n*math.tau/8
            seg(s, P(s, i+1.1*math.cos(t), j+1.1*math.sin(t), 3), P(s, i+1.1*math.cos(t), j+1.1*math.sin(t), 13),
                rgb('#3E5A4A'))
        cylinder(s, i, j, 1.35, 1.35, 13, 2, tones('#9FC2AA', '#6E9A80', '#5C8670', '#476A58', '#2F4A3C', '#557E68', '#1E3027'),
                 lambda u, v, lit: WHITE['lit'] if int(u) % 2 == 0 and v < 1 else None)
        revolve(s, i, j, 1.5, 15, 7, [(0, 1), (.5, .6), (1, .05)], COPPER, ribs=4)
    scene.add(i+j+2, draw)


# name, builder, footprint, real (longitude, latitude), compressed north-up ground anchor, elevation.
SITES = [
    ('st-mark', st_mark, (9.5, 5.4), (15.97389, 45.81639), (178, 140), 14),
    ('stone-gate', stone_gate, (5.2, 4), (15.97530, 45.81580), (300, 176), 14),
    ('lotrscak', lotrscak, (3.6, 3.6), (15.97306, 45.81472), (124, 228), 14),
    ('cathedral', cathedral, (9, 19), (15.97972, 45.81444), (598, 238), 0),
    ('dolac', dolac, (9, 9.4), (15.97750, 45.81417), (420, 284), 0),
    ('jelacic', jelacic, (2.4, 2.4), (15.97722, 45.81306), (400, 366), 0),
    ('theatre', theatre, (7.4, 14), (15.97000, 45.80944), (98, 400), 0),
    ('pavilion', pavilion, (10, 5.5), (15.97861, 45.80722), (520, 452), 0),
]


def main():
    for name, builder, (wi, wj), _, _, _ in SITES:
        print(preview([lambda s, b=builder: b(s, 4, 4)], 'zagreb-'+name,
                      size=(300, 300), origin=(150, 140), tiles=24))
    print(preview([lambda s, n=n, seed=seed: townhouse(s, 3+n*3, 3, 2.5, 3, 2+n % 3, seed)
                   for n, seed in enumerate((0, 1, 2, 3, 4, 10))]
                  + [lambda s: tram(s, 4, 8), lambda s: gazebo(s, 14, 10), lambda s: funicular(s, 6, 10, 5, 12)],
                  'zagreb-houses', size=(300, 240), origin=(80, 90), tiles=24))
    import sprites
    if hasattr(sprites, 'plitvice'):
        sprite = sprites.plitvice()
        path = Path(__file__).resolve().parents[2]/'docs/art/capitals/croatia-plitvice.png'
        sprite.resize((sprite.width*4, sprite.height*4), 0).save(path)
        print(path)


if __name__ == '__main__':
    main()
