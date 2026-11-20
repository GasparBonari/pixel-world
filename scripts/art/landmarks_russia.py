"""Moscow's brick, white-stone and gilded landmarks, built in projected (i, j, z).

Two-source coordinates, settings, facade decisions and model limits: DEVELOPMENT_PLAN.md.
Run directly for six isolated 4× landmark studies, Moscow houses and Mount Elbrus.
"""
import math
from pathlib import Path

import iso
from iso import rgb
from landmarks_paris import P, seg, poly, facade, preview, GLASS
from landmarks_iberia import hip_roof, crenellate, stone_courses, arch_opening, palette_of, tones
from landmarks_slovakia import block, band, pediment
from landmarks_bosnia import cylinder
from landmarks_greece import column
from landmarks_slovenia import windows
from landmarks_ukraine import roof_mesh

WHITE = tones('#FFFEF0', '#F0EADD', '#DBD5C5', '#B9B4A5', '#827D70', '#CAC3B2', '#514B3F')
BRICK = tones('#E7AA88', '#BF6A52', '#A84F3D', '#813A31', '#572720', '#954331', '#43251F')
RED = tones('#EDA18A', '#CE725A', '#B54F40', '#8F3833', '#612827', '#A64636', '#472321')
STONE = tones('#E6E1CF', '#C8C4B0', '#ADAA96', '#8D907F', '#626B60', '#9FA08D', '#414B43')
OCHRE = tones('#FFEBBE', '#E9D19C', '#D5B781', '#B39461', '#7D653F', '#C4A572', '#54432F')
GREEN = tones('#B1CAB0', '#73967B', '#54795F', '#385B48', '#284131', '#486B55', '#21362B')
BLUE = tones('#D3E4EA', '#92B9CF', '#6D94B6', '#48668B', '#32465E', '#5D7D9E', '#26374B')
GOLD = tones('#FFF6BB', '#F0D17A', '#CEA74B', '#A37B2D', '#72551E', '#BB923D', '#51401D')
METAL = tones('#C6CEC6', '#929E96', '#74867E', '#53685F', '#394A43', '#65796E', '#2C3B35')
BRONZE = tones('#C0B283', '#8F9470', '#6F7D5C', '#4B6249', '#334632', '#607653', '#263A29')
WOOD = tones('#D1B08A', '#A5845F', '#896543', '#67482F', '#483222', '#7A573A', '#35281E')
ROCK = tones('#D5C8AE', '#B5A78C', '#978A70', '#766B54', '#554C3C', '#897D65', '#40392F')
SNOW = tones('#FFFFFF', '#EDF2EB', '#D0DDD9', '#A6BFC4', '#728E9E', '#BCCFD1', '#456576')
IRON, DARK_GLASS, RUBY = rgb('#354039'), rgb('#344A52'), rgb('#BE3D3C')
WALLS = [rgb(c) for c in ('#E6D3A8', '#D4DFCB', '#E4BEB2', '#BFD1D4', '#EDE1C5', '#CEBED1')]
GROUND = {k: rgb(v) for k, v in {
    'pave': '#C8BFB0', 'square': '#DDCCB6', 'joint': '#B3A38E', 'red_square': '#BCA79B',
    'cobble': '#ADB0A6', 'cobble_joint': '#8D958B', 'garden': '#78945D',
    'garden_hi': '#98AF73', 'flower': '#E6C3B1', 'water': '#548B95',
    'water_dark': '#3B6C7F', 'water_hi': '#BDDCDB',
}.items()}


def cross(s, i, j, z, size=7):
    """Orthodox three-bar cross, with a tilted foot bar, projected into its own plane."""
    seg(s, P(s, i, j, z), P(s, i, j, z+size), GOLD['deep'])
    for span, level in ((.19, .8), (.32, .58)):
        seg(s, P(s, i-span, j, z+size*level), P(s, i+span, j, z+size*level), GOLD['hi'])
    seg(s, P(s, i-.2, j, z+size*.22), P(s, i+.2, j, z+size*.35), GOLD['lit'])


def onion(s, ci, cj, radius, base, rise, material=GOLD, accent=None, twist=0):
    """Faceted bulb with convex shoulders, tapering tip and optional spiral ceramic ribs."""
    profile = [(0, .65), (.12, .91), (.32, 1), (.52, .83), (.72, .5), (.9, .15), (1, .025)]
    faces = []
    for k, ((t, r), (nt, nr)) in enumerate(zip(profile, profile[1:])):
        for n in range(32):
            a, b = n*math.tau/32, (n+1)*math.tau/32
            mid = (a+b)/2 + (t+nt)/2*twist
            light = (math.sin(mid)-math.cos(mid))/math.sqrt(2)
            key = 'hi' if light > .82 else 'lit' if light > .05 else 'mid' if light > -.6 else 'dark'
            pts = [P(s, ci+rr*radius*math.cos(ang+tt*twist),
                     cj+rr*radius*math.sin(ang+tt*twist), base+tt*rise)
                   for tt, rr, ang in ((t, r, a), (t, r, b), (nt, nr, b), (nt, nr, a))]
            mat = accent if accent and n % 8 < 3 else material
            faces.append((math.cos(mid)+math.sin(mid), k, n, pts, mat, key))
    for _, _, n, pts, mat, key in sorted(faces, key=lambda f: (f[0], f[1], f[2])):
        poly(s, pts, lambda x, y, mat=mat, key=key: mat[key])
        if n % 8 == 0:seg(s, pts[0], pts[3], mat['hi' if key in ('hi', 'lit') else 'deep'])
    cross(s, ci, cj, base+rise, 6 if radius < 1 else 8)


def church_wall(material, height, bay=13):
    joints = stone_courses(material, 4, 12)
    def pattern(u, v, lit):
        c = u % bay
        trim = WHITE['lit' if lit else 'dark']
        if int(v) in (1, 2, height-3, height-1):return trim
        if int(c) == 0:return material['hi' if lit else 'mid']
        level = v % 19
        framed = arch_opening(c, level-5, bay/2, 2.8, 7, trim)
        opening = arch_opening(c, level-6, bay/2, 1.5, 6, DARK_GLASS)
        if opening:return IRON if int(v) % 8 == 0 or abs(c-bay/2) < .5 else opening
        if framed:return framed
        return joints(u, v, lit)
    return pattern


def townhouse(scene, i, j, wi=2.7, wj=3, floors=2, seed=0, z=0):
    """Moscow stucco merchant houses: nalichnik hoods, pilasters and standing-seam hips."""
    wall, height = palette_of(WALLS[seed % len(WALLS)]), floors*12+4
    base = windows(wall, height, bay=11, floor=12, hood=True, pilasters=True)
    def pattern(u, v, lit):
        c, level = int(u) % 11, int(v) % 12
        trim = WHITE['lit' if lit else 'dark']
        if v < 11:
            if c in (2, 9) or int(v) in (2, 9):return trim
            if 2 < c < 9 and 2 < v < 9:return WOOD['deep'] if (int(u)//11+seed) % 3 == 0 else GLASS['dark']
            if int(v) % 3 == 0:return wall['line']
        if 12 < v < height-4 and level == 10 and 2 <= c <= 9:return trim
        return base(u, v, lit)
    def draw(s):
        block(s, i, j, wi, wj, height, wall, pattern, z=z)
        band(s, i, j, wi, wj, z+1, STONE, 2)
        band(s, i, j, wi, wj, z+height-2, WHITE, 2)
        hip_roof(s, i-.12, j-.12, wi+.24, wj+.24, z+height+1, 9, GREEN if seed % 3 == 0 else METAL)
        if seed % 4 == 0:pediment(s, i+.45, j+wj-.1, wi-.9, .35, z+height, 7, WHITE)
        if seed % 4 == 1:
            # One substantial bracketed bay with glazing, rather than stripes over every wall.
            block(s, i+.65, j+wj, 1.2, .4, 10, wall, windows(wall, 10, bay=7, floor=14), z=z+13)
            band(s, i+.65, j+wj, 1.2, .4, z+23, WHITE)
        elif seed % 4 == 2:
            block(s, i+.6, j+wj, 1.3, .3, 1, STONE, z=z+14)
            for k in range(5):seg(s, P(s, i+.6+k*.32, j+wj+.3, z+15), P(s, i+.6+k*.32, j+wj+.3, z+20), IRON)
            seg(s, P(s, i+.6, j+wj+.3, z+20), P(s, i+1.9, j+wj+.3, z+20), IRON)
        block(s, i+.3, j+.55, .4, .45, 8, BRICK, z=z+height+5)
        band(s, i+.3, j+.55, .4, .45, z+height+12, STONE)
    scene.add(i+j+wi+wj+1, draw)


def tent(s, ci, cj, radius, base, rise, roof=GREEN, ribs=WHITE):
    roof_mesh(s, ci, cj, radius, base, rise, roof, pear=False, ribs=0,
              profile=[(0, 1), (.25, .76), (.5, .51), (.75, .26), (1, .025)])
    for n in range(8):
        a = n*math.tau/8
        seg(s, P(s, ci+radius*math.cos(a), cj+radius*math.sin(a), base), P(s, ci, cj, base+rise), ribs['lit'])
    # Small roof lozenges are points on the sloping surface, never screen-space stripes.
    for n in range(8):
        a = (n+.5)*math.tau/8
        if math.cos(a)+math.sin(a) < 0:continue
        for k in range(1, 5):
            t = k/6
            r = radius*(1-t)*.94
            s.put(*P(s, ci+r*math.cos(a), cj+r*math.sin(a), base+rise*t), roof['hi'])


def basil(scene, i, j, z=0):
    """Eight outer churches, central tent, later NW chapel and separate SE tented belfry."""
    def draw(s):
        block(s, i, j, 10, 10, 10, BRICK, church_wall(BRICK, 24), z=z)
        band(s, i, j, 10, 10, z+9, WHITE, 2)
        # Low enclosing gallery, open arcades and stepped west porch.
        for a, b, w, d in ((0, 8.7, 10, 1.3), (8.7, 0, 1.3, 10)):
            block(s, i+a, j+b, w, d, 12, RED, church_wall(RED, 25, 11), z=z+10)
            hip_roof(s, i+a-.1, j+b-.1, w+.2, d+.2, z+22, 5, GREEN)
        # A central octagon and eight unequal satellite drums in a compass ring.
        parts = [(5, 5, 1.45, 63, GOLD, None, 0, True)]
        positions = [(2, 2), (5, .8), (8, 2), (9.2, 5), (8, 8), (5, 9.2), (2, 8), (.8, 5)]
        roofs = [(GREEN, GOLD, 1.5), (RED, WHITE, 0), (BLUE, WHITE, -1.4), (GREEN, WHITE, 1.3),
                 (RED, GOLD, 0), (GREEN, GOLD, -1.3), (BLUE, WHITE, 1.5), (GREEN, WHITE, 0)]
        for n, ((a, b), (roof, accent, twist)) in enumerate(zip(positions, roofs)):
            parts.append((a, b, 1.05 if n % 2 == 0 else .85, 35 if n % 2 == 0 else 27, roof, accent, twist, False))
        # St Basil's later chapel is on the north-west, not a generic extra corner dome.
        parts.append((1, 3.4, .55, 20, GREEN, GOLD, 0, False))
        for a, b, radius, height, roof, accent, twist, central in sorted(parts, key=lambda p: p[0]+p[1]):
            ci, cj = i+a, j+b
            cylinder(s, ci, cj, radius, radius, z+10, height, RED,
                     church_wall(RED, height, 10), segments=8)
            for dz in (height-4, height):cylinder(s, ci, cj, radius+.12, radius+.12, z+10+dz, 2, WHITE, segments=8)
            # Tiered kokoshnik scallops below each crown, projected on all eight facets.
            for n in range(8):
                ang = n*math.tau/8
                cylinder(s, ci+radius*.85*math.cos(ang), cj+radius*.85*math.sin(ang), .21, .21,
                         z+height+12, 3, WHITE, segments=8)
            if central:
                tent(s, ci, cj, radius+.1, z+height+14, 27, RED, WHITE)
                onion(s, ci, cj, .33, z+height+41, 6, GOLD)
            else:
                cylinder(s, ci, cj, radius*.7, radius*.7, z+height+14, 5, WHITE, segments=16)
                onion(s, ci, cj, radius*1.12, z+height+19, 19 if radius > .9 else 15, roof, accent, twist)
        # Separate octagonal bell tower on the south-east side. No extra onion crown.
        ci, cj = i+10.8, j+5.5
        cylinder(s, ci, cj, .72, .72, z, 29, RED, church_wall(RED, 29, 8), segments=8)
        cylinder(s, ci, cj, .78, .78, z+29, 12, WHITE,
                 lambda u, v, lit: DARK_GLASS if 1 < u % 7 < 5 and 1 < v < 10 else None, segments=8)
        tent(s, ci, cj, .98, z+41, 23, GREEN, WHITE)
        cross(s, ci, cj, z+64, 6)
        # West-side porch snaps SW; the famous north-west Red Square front stays hidden.
        for k in range(5):block(s, i+1.8, j+10+k*.24, 2.7, .28, 10-k*2, STONE, z=z)
        block(s, i+1.7, j+9.5, 2.9, .5, 17, RED, church_wall(RED, 28, 11), z=z+10)
        hip_roof(s, i+1.6, j+9.4, 3.1, .8, z+27, 10, RED)
    scene.add(i+j+24, draw)


def spasskaya(scene, i, j, z=0):
    """Brick gate, white Gothic cresting, black/gold clocks, octagonal belfry and ruby star."""
    def draw(s):
        def gate(u, v, lit):
            opening = arch_opening(u, v-1, 16, 5, 16, WOOD['deep'])
            if opening:return opening
            if 23 < v < 34 and 12 < u < 20:
                return GOLD['dark'] if int(u) in (13, 19) or int(v) in (24, 33) else BRONZE['deep']
            return stone_courses(BRICK, 4, 10)(u, v, lit)
        block(s, i, j, 4, 4, 46, BRICK, gate, z=z)
        for dz in (2, 36, 44):band(s, i, j, 4, 4, z+dz, WHITE, 2)
        crenellate(s, i, j, 4, 4, z+47, BRICK, set(), step=5)
        # Set-back four-sided clock stage, with Gothic white jambs and pinnacles.
        block(s, i+.45, j+.45, 3.1, 3.1, 34, BRICK,
              church_wall(BRICK, 34, 11), z=z+47)
        for a, b in ((.45, .45), (3.55, .45), (.45, 3.55), (3.55, 3.55)):
            block(s, i+a-.14, j+b-.14, .28, .28, 27, WHITE, z=z+49)
            tent(s, i+a, j+b, .25, z+76, 10, WHITE, WHITE)
        # Dials lie on their actual SW and SE support planes; there are four in reality.
        for side in ('sw', 'se'):
            def point(u, h):
                return P(s, i+2+u/8, j+3.58, z+65+h) if side == 'sw' else P(s, i+3.58, j+2-u/8, z+65+h)
            for radius, color in ((9, GOLD['hi']), (8, IRON)):
                poly(s, [point(radius*math.cos(n*math.tau/48), radius*math.sin(n*math.tau/48)) for n in range(48)],
                     lambda x, y, color=color: color)
            for n in range(12):
                a = n*math.tau/12
                seg(s, point(6.3*math.cos(a), 6.3*math.sin(a)), point(7.4*math.cos(a), 7.4*math.sin(a)), GOLD['lit'])
            seg(s, point(0, 0), point(-4, 3), GOLD['hi'])
            seg(s, point(0, 0), point(1, 6), GOLD['hi'])
        cylinder(s, i+2, j+2, 1.6, 1.6, z+82, 16, WHITE,
                 lambda u, v, lit: DARK_GLASS if 2 < u % 9 < 7 and 2 < v < 14 else None, segments=8)
        tent(s, i+2, j+2, 1.9, z+99, 32, GREEN, WHITE)
        seg(s, P(s, i+2, j+2, z+130), P(s, i+2, j+2, z+138), GOLD['dark'])
        pts = [P(s, i+2+(.6 if n % 2 == 0 else .24)*math.sin(n*math.pi/5), j+2,
                 z+139+(5 if n % 2 == 0 else 2)*math.cos(n*math.pi/5)) for n in range(10)]
        poly(s, pts, lambda x, y: RUBY if x % 3 else RED['hi'])
    scene.add(i+j+11, draw)


def historical_museum(scene, i, j, z=0):
    """Long red Russian Revival museum; four corner tents, two dominant on the SE front."""
    w, d, h = 7.5, 11, 34
    def draw(s):
        def pattern(u, v, lit):
            c, level = u % 12, v % 16
            frame = arch_opening(c, level-3, 6, 3.2, 6, RED['hi' if lit else 'mid'])
            hole = arch_opening(c, level-4, 6, 1.8, 5, DARK_GLASS)
            if hole:return RED['lit'] if int(c) == 6 else hole
            return frame or stone_courses(BRICK, 3, 9)(u, v, lit)
        block(s, i, j, w, d, h, BRICK, pattern, z=z)
        for dz in (2, 16, 31, 34):band(s, i, j, w, d, z+dz, RED, 2)
        hip_roof(s, i-.1, j-.1, w+.2, d+.2, z+h+1, 14, GREEN)
        # Four corners retain their geographic handedness; the SE pair frames Red Square.
        for a, b in sorted(((0, 0), (0, d-1.8), (w-1.8, 0), (w-1.8, d-1.8)), key=sum):
            height = 56 if a > 0 else 46
            block(s, i+a, j+b, 1.8, 1.8, height, RED, pattern, z=z)
            for dz in (17, 33, height-3):band(s, i+a, j+b, 1.8, 1.8, z+dz, BRICK, 2)
            cylinder(s, i+a+.9, j+b+.9, .96, .96, z+height, 8, RED, pattern, segments=8)
            tent(s, i+a+.9, j+b+.9, 1.2, z+height+8, 24, RED, WHITE)
            # Small solid paired-wing gilded eagle finials, rather than flag-like sticks.
            ci, cj, zz = i+a+.9, j+b+.9, z+height+33
            for sign in (-1, 1):
                poly(s, [P(s, ci, cj, zz), P(s, ci+sign*.4, cj, zz+4), P(s, ci+sign*.3, cj, zz+1),
                         P(s, ci+sign*.46, cj, zz-2), P(s, ci, cj, zz-1)], lambda x, y: GOLD['lit'])
            cylinder(s, ci, cj, .1, .1, zz, 4, GOLD, segments=8)
        # The famous Red Square facade faces SE (+i), so decoration stays on that plane.
        fi = i+w+.04
        def front_point(u, height):return P(s, fi, j+u, z+height)
        for c in (2.8, 5.5, 8.2):
            pts = [front_point(c-.65, 0), front_point(c+.65, 0), front_point(c+.65, 12),
                   front_point(c, 18), front_point(c-.65, 12)]
            poly(s, pts, lambda x, y: WOOD['deep'])
            for a, b in zip(pts, pts[1:]+pts[:1]):seg(s, a, b, RED['hi'])
        # Stepped central kokoshnik gable and flanking small tented roof turrets.
        for n in range(4):
            span = 4.4-n*.9
            block(s, i+w-.4, j+d/2-span/2, .45, span, 5, RED,
                  stone_courses(RED, 3, 8), z=z+35+n*4)
        for b in (3.1, 7.9):
            cylinder(s, i+w-.35, j+b, .4, .4, z+36, 11, RED, segments=8)
            tent(s, i+w-.35, j+b, .55, z+47, 13, GREEN, WHITE)
        for b in (2.8, 5.5, 8.2):
            poly(s, [front_point(b-.5, 26), front_point(b+.5, 26), front_point(b+.5, 31),
                     front_point(b, 34), front_point(b-.5, 31)], lambda x, y: WHITE['dark'] if x % 3 else DARK_GLASS)
    scene.add(i+j+w+d+3, draw)


def bolshoi(scene, i, j, z=0):
    """Ochre theatre, eight white columns, pediment relief and substantial bronze quadriga."""
    w, d, h = 12, 7, 35
    def draw(s):
        block(s, i, j, w, d, h, OCHRE, windows(OCHRE, h, bay=11, floor=15, pilasters=True), z=z)
        for dz in (2, 18, 33):band(s, i, j, w, d, z+dz, WHITE, 2)
        hip_roof(s, i-.1, j-.1, w+.2, d+.2, z+h, 9, METAL)
        # Higher stage-house retains its low pediment and dressed attic windows.
        block(s, i+2.4, j+.8, 7.2, 3.4, 10, OCHRE, windows(OCHRE, 10, bay=10, floor=15), z=z+42)
        hip_roof(s, i+2.3, j+.7, 7.4, 3.6, z+52, 7, METAL)
        pediment(s, i+2.2, j+4, 7.6, .4, z+52, 7, WHITE)
        # Front faces SSW, locally snapped SW without turning the city.
        block(s, i+1.2, j+d, 9.6, 1.3, 3, STONE, z=z)
        for n in range(8):column(s, i+1.65+n*1.24, j+d+1.05, z+3, 29, .25, WHITE, order='ionic')
        block(s, i+1.1, j+d-.1, 9.8, 1.5, 4, WHITE, z=z+32)
        pediment(s, i+1, j+d-.2, 10, 1.7, z+36, 12, WHITE)
        # The tympanum has a central lyre/wing relief confined to the triangular face.
        ci, cj = i+6, j+d+1.52
        cylinder(s, ci, cj, .25, .1, z+38, 5, OCHRE, segments=12)
        for sign in (-1, 1):
            poly(s, [P(s, ci+sign*.15, cj, z+40), P(s, ci+sign*1.2, cj, z+39),
                     P(s, ci+sign*.6, cj, z+43)], lambda x, y: OCHRE['dark'])
        # Four separate volumetric horses: bodies, bent legs, arched necks, heads and tails.
        # The group faces SW; the chariot and Apollo stand behind the team.
        for n in range(4):
            a, b = i+4.35+n*1.1, j+d+.65
            cylinder(s, a, b, .32, .55, z+48, 4, BRONZE, segments=12)
            for di, dj, bend in ((-.2, -.3, -1), (.2, -.3, 1), (-.2, .33, 1), (.2, .33, -1)):
                block(s, a+di-.07, b+dj, .14, .13, 4, BRONZE, z=z+45)
                seg(s, P(s, a+di, b+dj, z+47), P(s, a+di+bend*.12, b+dj+.25, z+44), BRONZE['lit'])
            cylinder(s, a, b+.43, .18, .19, z+51, 6, BRONZE, segments=10)
            cylinder(s, a, b+.62, .19, .34, z+56, 3, BRONZE, segments=10)
            block(s, a-.16, b+.48, .12, .1, 2, BRONZE, z=z+59)
            seg(s, P(s, a, b-.4, z+51), P(s, a-.2, b-.8, z+48), BRONZE['deep'], 2)
        block(s, i+5.2, j+d-.4, 1.6, .7, 5, BRONZE, z=z+48)
        for a in (5.1, 6.9):
            # Wheel rims project on vertical i/z planes.
            pts = [P(s, i+a+.22*math.cos(n*math.tau/20), j+d+.1, z+49+2*math.sin(n*math.tau/20)) for n in range(20)]
            for p, q in zip(pts, pts[1:]+pts[:1]):seg(s, p, q, BRONZE['hi'])
        cylinder(s, i+6, j+d-.05, .24, .2, z+53, 8, BRONZE, segments=12)
        cylinder(s, i+6, j+d-.05, .22, .2, z+62, 4, BRONZE, segments=12)
        for sign in (-1, 1):
            block(s, i+6+sign*.25, j+d-.02, .2, .22, 4, BRONZE, z=z+58)
            seg(s, P(s, i+6+sign*.3, j+d, z+60), P(s, i+6+sign*.8, j+d+.5, z+63), BRONZE['lit'], 2)
        for n in range(3):block(s, i+1-n*.2, j+d+1.3+n*.25, 10+n*.4, .28, 3-n, STONE, z=z)
    scene.add(i+j+w+d+4, draw)


def ivan_bell_tower(scene, i, j, z=0):
    """The freestanding three-stage octagonal tower; adjoining Assumption belfry omitted."""
    def draw(s):
        ci, cj = i+2, j+2
        # The 81 m tower is slender: the three octagons must not read as broad stacked drums.
        for radius, base, height in ((1.4, 0, 45), (1.05, 46, 34), (.75, 81, 26)):
            def openings(u, v, lit, height=height, radius=radius):
                bay = radius*math.pi
                c = u % bay
                frame = arch_opening(c, v-height+19, bay/2, bay*.34, 10, WHITE['hi' if lit else 'mid'])
                hole = arch_opening(c, v-height+18, bay/2, bay*.23, 9, IRON)
                if hole:
                    # Bronze bells hang in dark, recessed open arches.
                    return BRONZE['lit' if lit else 'dark'] if abs(c-bay/2) < bay*.16 and height-14 < v < height-9 else hole
                if frame:return frame
                if c < .45:return WHITE['hi' if lit else 'mid']
                if 5 < v < height-23 and abs(c-bay/2) < .75:
                    return WHITE['dark' if abs(c-bay/2) < .35 else 'hi']
                if int(v) == height-22:return WHITE['mid' if lit else 'line']
                return stone_courses(WHITE, 6, 15)(u, v, lit)
            cylinder(s, ci, cj, radius, radius, z+base, height, WHITE, openings, segments=8)
            for dz in (1, height-3, height):cylinder(s, ci, cj, radius+.12, radius+.12, z+base+dz, 2, WHITE, segments=8)
        # Inscription frieze below a single gilded crown; lettering is pixel-abbreviated.
        cylinder(s, ci, cj, .8, .8, z+108, 9, WHITE,
                 lambda u, v, lit: GOLD['dark'] if 2 < v < 7 and int(u) % 3 else None, segments=16)
        onion(s, ci, cj, 1, z+118, 16, GOLD)
        # Main western doorway is on a visible SW-snapped octagonal facet.
        facade(s, ci-.45, cj+1.16, .9, .12, 17,
               lambda u, v, lit: arch_opening(u, v, 3.6, 2.6, 11, WOOD['deep']), WHITE, z0=z)
    scene.add(i+j+10, draw)


def christ_saviour(scene, i, j, z=0):
    """Broad white Greek cross, one enormous gilded crown and four corner bell domes."""
    def draw(s):
        block(s, i, j, 10, 10, 5, STONE, z=z)
        parts = []
        # Four corner belfries, and the main cross-plan body, in painter order.
        for a, b in ((.3, .3), (7.7, .3), (.3, 7.7), (7.7, 7.7)):
            parts.append((a+b+2, 'tower', a, b))
        parts.append((13, 'body', 0, 0))
        for _, kind, a, b in sorted(parts):
            if kind == 'tower':
                block(s, i+a, j+b, 2, 2, 53, WHITE, church_wall(WHITE, 53, 8), z=z+5)
                band(s, i+a, j+b, 2, 2, z+54, WHITE, 3)
                cylinder(s, i+a+1, j+b+1, .78, .78, z+58, 13, WHITE,
                         church_wall(WHITE, 26, 8), segments=8)
                onion(s, i+a+1, j+b+1, .94, z+72, 15, GOLD)
            else:
                for a, b, w, d in ((2.3, .5, 5.4, 9), (.5, 2.3, 9, 5.4)):
                    block(s, i+a, j+b, w, d, 42, WHITE, church_wall(WHITE, 42, 13), z=z+5)
                    band(s, i+a, j+b, w, d, z+45, WHITE, 3)
                    hip_roof(s, i+a, j+b, w, d, z+48, 8, METAL)
                cylinder(s, i+5, j+5, 2.2, 2.2, z+54, 24, WHITE,
                         church_wall(WHITE, 28, 9), segments=24)
                cylinder(s, i+5, j+5, 2.4, 2.4, z+78, 3, WHITE, segments=24)
                onion(s, i+5, j+5, 2.5, z+81, 30, GOLD)
        # West front locally snaps SW. Rounded zakomara gables, bronze relief and three portals.
        for a, base, radius in ((2.9, 45, .65), (5, 50, 1.3), (7.1, 45, .65)):
            pts = [P(s, i+a+radius*math.cos(n*math.pi/24), j+9.65, z+base+radius*8*math.sin(n*math.pi/24)) for n in range(25)]
            poly(s, pts, lambda x, y: WHITE['lit'])
            for p, q in zip(pts, pts[1:]):seg(s, p, q, WHITE['hi'])
            cylinder(s, i+a, j+9.7, .22, .08, z+base+2, 3, BRONZE, segments=12)
        def front(u, v, lit):
            c = u % 16
            door = arch_opening(c, v-4, 8, 4, 14, BRONZE['deep'])
            frame = arch_opening(c, v-3, 8, 5, 15, WHITE['hi' if lit else 'mid'])
            if door:return BRONZE['lit'] if int(v) % 6 == 0 or int(c) == 8 else door
            if frame:return frame
            if 26 < v < 33 and 3 < c < 13:return BRONZE['dark' if int(u+v) % 3 else 'lit']
            return church_wall(WHITE, 38, 16)(u, v, lit)
        block(s, i+2.2, j+9.3, 5.6, .4, 36, WHITE, front, z=z+5)
        for n in range(5):block(s, i+2-n*.12, j+10+n*.24, 6+n*.24, .28, 5-n, STONE, z=z)
    scene.add(i+j+24, draw)


def main():
    for name, builder, _, _, _, elevation in SITES:
        print(preview([lambda s, b=builder, z=elevation: b(s, 4, 4, z=z)], 'moscow-'+name,
                      size=(290, 290), origin=(145, 130), tiles=25))
    print(preview([lambda s: townhouse(s, 4, 4, seed=0),
                   lambda s: townhouse(s, 9, 4, floors=3, seed=1),
                   lambda s: townhouse(s, 8, 10, seed=2)], 'moscow-houses',
                  size=(240, 190), origin=(110, 50), tiles=20))
    import sprites
    if 'elbrus' in sprites.ICONS:
        im = sprites.elbrus()
        path = Path(__file__).resolve().parents[2] / 'docs/art/capitals/russia-elbrus.png'
        im.resize((im.width*4, im.height*4), 0).save(path)
        print(path)


# name, builder, footprint, real (longitude, latitude), scene ground anchor, elevation
SITES = [
    ('bolshoi', bolshoi, (12, 8.8), (37.61861, 55.76028), (430, 115), 0),
    ('historical-museum', historical_museum, (7.5, 11), (37.6177437, 55.7553192), (295, 245), 0),
    ('spasskaya', spasskaya, (4, 4), (37.621425, 55.752544), (505, 310), 12),
    ('st-basil', basil, (11.8, 11.3), (37.62306, 55.7525), (620, 365), 0),
    ('ivan-belltower', ivan_bell_tower, (4, 4), (37.6182122, 55.7507148), (390, 420), 12),
    ('christ-saviour', christ_saviour, (10, 11.3), (37.60556, 55.74444), (140, 460), 0),
]


if __name__ == '__main__':
    main()
