"""Ljubljana: Plečnik's river city, Baroque churches and the castle hill in true projected (i, j, z).

Eight landmark studies and a house study precede integration; north-up anchors and references are
recorded in DEVELOPMENT_PLAN.md. The Ljubljanica runs along the j axis, so both bridges cross it
along i. Art is original, rendered at native resolution.

    .venv/bin/python scripts/art/landmarks_slovenia.py  ->  docs/art/capitals/ljubljana-*.png
"""
import math
from pathlib import Path

import iso
from iso import rgb, h01
from landmarks_paris import P, seg, poly, corners, facade, preview, GLASS
from landmarks_iberia import hip_roof, crenellate, stone_courses, arch_opening, palette_of, tones
from landmarks_amsterdam import gable_roof
from landmarks_italy import cylinder, ellipse
from landmarks_slovakia import block, band, pediment

STONE = tones('#F3EEE2', '#DAD3C1', '#C3BBA6', '#A29A84', '#716A58', '#B4AB93', '#46402F')
WHITE = tones('#FFFCF2', '#F1EADA', '#DDD4BF', '#BEB39B', '#877C66', '#CEC3AA', '#524836')
YELLOW = tones('#FCEBC0', '#EED59E', '#DABD82', '#B99A60', '#86693D', '#C9A970', '#544022')
SALMON = tones('#F4AE9A', '#D97260', '#C55D4D', '#A0443A', '#6F2D29', '#B45045', '#4B1E1C')
CASTLE = tones('#F5EEDB', '#E3D8BD', '#CDBF9F', '#AE9E7D', '#7A6C52', '#BCAB89', '#4C412E')
CLAY = tones('#F3A97B', '#D27143', '#B85B36', '#8F432A', '#62301F', '#A54F31', '#4E261A')
COPPER = tones('#C4E0CD', '#86B8A0', '#679C86', '#467A66', '#2F5748', '#5C8E79', '#24423A')
CONCRETE = tones('#F0EFE8', '#D5D4CB', '#BFBEB4', '#9E9D93', '#6D6C64', '#B0AFA5', '#403F3A')
BRONZE = tones('#CFC48F', '#978C5F', '#7B7250', '#5C563D', '#3E3A29', '#6E6747', '#25231A')
ROCK = tones('#D2C9AE', '#ADA48A', '#948B72', '#746C57', '#544E3E', '#867E67', '#39352A')
GOLD = tones('#FFF1A8', '#E8C35F', '#C99E3E', '#A2782B', '#6E5022', '#B88B32', '#514022')
PINKSTONE = tones('#F2D9CF', '#D9B5A8', '#C49A8D', '#A07A6F', '#6E5048', '#B28A7E', '#46302B')
ROOF = tones('#E4A07C', '#BF6E4B', '#A65A3B', '#80432D', '#58301F', '#934D33', '#45251A')  # Plečnik's tiles
WALLS = [rgb(c) for c in ('#EFD9A7', '#E7AE92', '#C7D8C1', '#F2E7CF', '#D8C3D0', '#E3C27E', '#B9CCD6',
                          '#DD9C84')]
IRON, WOOD, LEAF = rgb('#33393A'), rgb('#6A452D'), rgb('#5E8A4A')
WATER = (rgb('#4F8A7A'), rgb('#3C6E63'), rgb('#BFE0D2'))


# ------------------------------------------------------------- primitives --

def windows(material, height, bay=10, floor=12, arched=False, pilasters=False, hood=False, width=5):
    """Framed two-pane windows with sills, centred in each bay; arched heads, pilaster strips and
    pediment hoods. width is the opening including its frame, in pixels."""
    joints = stone_courses(material, 4, 10)
    def pattern(u, v, lit):
        c, level = int(u) % bay, int(v) % floor
        trim = WHITE['lit' if lit else 'dark']
        if v < 2 or int(v) in (height-1, height-3):
            return trim
        if pilasters and c == 0:
            return WHITE['hi' if lit else 'mid']
        d = c - (bay-1)/2
        half = (width-1)/2
        top = floor-3 + (math.sqrt(max(0, half*half-d*d))*.6 if arched else 0)
        if abs(d) <= half and 3 <= level <= top and v < height-4:
            if abs(d) >= half-.01 or abs(d) < .6 and width >= 5 or level in (3, 7) or level >= int(top):
                return trim
            return GLASS['mid'] if lit and d < 0 and level == int(top)-1 else GLASS['mid' if lit else 'dark']
        if level == 2 and abs(d) <= half+1 and v < height-4:
            return WHITE['hi' if lit else 'mid']  # sill
        if hood and int(top)+1 <= level <= int(top)+1 and abs(d) <= half+1 and v < height-4:
            return WHITE['hi' if lit else 'mid']
        return joints(u, v, lit) if material in (STONE, ROCK, CONCRETE) else None
    return pattern


def revolve(s, ci, cj, radius, base, rise, profile, material, ribs=4, segments=24):
    """Depth-sorted revolved roof mesh (domes, Baroque helmets) with raised ribs."""
    faces = []
    for (t, r), (nt, nr) in zip(profile, profile[1:]):
        for n in range(segments):
            a, b = n*math.tau/segments, (n+1)*math.tau/segments
            pts = [P(s, ci+rr*radius*math.cos(ang), cj+rr*radius*math.sin(ang), base+tt*rise)
                   for tt, rr, ang in ((t, r, a), (t, r, b), (nt, nr, b), (nt, nr, a))]
            key = 'lit' if math.sin((a+b)/2)-.5*math.cos((a+b)/2) > .05 else 'dark'
            faces.append((math.cos(a)+math.sin(a)+math.cos(b)+math.sin(b), n, pts, key))
    for _, n, pts, key in sorted(faces, key=lambda f: (f[0], f[1])):
        poly(s, pts, lambda x, y, k=key: material['line'] if int(y) % 5 == 0 else material[k])
        if ribs and n % ribs == 0:
            seg(s, pts[0], pts[3], material['hi' if key == 'lit' else 'deep'])


DOME = [(0, 1), (.15, .99), (.38, .9), (.62, .7), (.82, .42), (1, .1)]
HELMET = [(0, 1), (.12, 1.1), (.3, .86), (.42, .52), (.5, .42), (.6, .62), (.72, .52), (.86, .2), (1, .06)]


def apple(s, i, j, z, size=.3):
    """Gilded ball finial with a small cross."""
    cylinder(s, i, j, .06, .06, z, 3, GOLD)
    for k, (r, h) in enumerate(((size*.7, 1.2), (size, 1.6), (size*.7, 1.2))):
        cylinder(s, i, j, r, r, z+3+k*1.3, h, GOLD)
    seg(s, P(s, i, j, z+7), P(s, i, j, z+12), GOLD['dark'])
    seg(s, P(s, i-.22, j, z+10), P(s, i+.22, j, z+10), GOLD['lit'])


def statue(s, i, j, z, height=9, material=WHITE, arm=0):
    """Slim draped figure: plinth, flaring robe with folds, narrow shoulders, head with darker hair,
    one arm raised (arm>0) or bent across the body."""
    k = height/9
    block(s, i-.2, j-.17, .4, .34, 1.5, material, z=z)
    z += 1.5
    for r, h in ((.17, 2.2), (.14, 1.8), (.12, 1.4)):
        cylinder(s, i, j, r, r*.85, z, h*k, material,
                 lambda u, v, lit: material['line'] if int(u) % 3 == 0 else None)
        z += h*k
    block(s, i-.15, j-.1, .3, .2, 1.3*k, material, z=z)  # shoulders
    z += 1.3*k
    cylinder(s, i, j, .1, .09, z, 1.7*k, material, lambda u, v, lit: material['hi'] if lit else None)
    ellipse(s, i, j, .1, .09, z+1.7*k, material['dark'])
    sh = P(s, i+.13, j+.1, z-.8*k)
    if arm > 0:
        seg(s, sh, P(s, i+.3, j+.12, z+2*k), material['lit'])
        seg(s, (sh[0]+1, sh[1]), P(s, i+.33, j+.12, z+2*k), material['dark'])
    else:
        seg(s, sh, P(s, i-.03, j+.16, z-3*k), material['dark'])


def flag(s, i, j, z, height=20):
    """Slovenian tricolour (white, blue, red) with the coat of arms near the hoist."""
    seg(s, P(s, i, j, z), P(s, i, j, z+height), IRON)
    for n, c in enumerate((WHITE['hi'], rgb('#2F5BA8'), rgb('#D2463C'))):
        poly(s, [P(s, i+a, j, z+height-1-n*2.2-b) for a, b in ((0, 0), (1.7, 0), (1.7, 2.2), (0, 2.2))],
             lambda x, y, c=c: c)
    poly(s, [P(s, i+a, j, z+height-b) for a, b in ((.25, 2.5), (.65, 2.5), (.65, 5), (.45, 6), (.25, 5))],
         lambda x, y: rgb('#2F5BA8') if int(y) % 2 else WHITE['hi'])


def lamp(s, i, j, z, height=11, globe=WHITE):
    """Plečnik-style lamp: slender dark post on a base, collar and a pale globe lantern."""
    x, y = P(s, i, j, z)
    s.put(x-1, y, IRON); s.put(x, y, IRON); s.put(x+1, y, IRON)
    for dz in range(1, int(height)):
        s.put(x, y-dz, IRON)
    s.put(x-1, y-height, IRON); s.put(x+1, y-height, IRON)
    for dx, dy, c in ((-1, -1, 'lit'), (0, -1, 'hi'), (1, -1, 'mid'), (-1, -2, 'hi'), (0, -2, 'hi'),
                      (1, -2, 'mid'), (0, -3, 'lit')):
        s.put(x+dx, y-height+dy, globe[c])


def balustrade(s, a, b, z, height=4, material=WHITE, step=2):
    """Row of turned balusters between two ground points (i, j) under a top rail."""
    (ai, aj), (bi, bj) = a, b
    pa, pb = P(s, ai, aj, z), P(s, bi, bj, z)
    n = max(2, int(max(abs(pb[0]-pa[0]), abs(pb[1]-pa[1]))/step))
    for k in range(n+1):
        t = k/n
        p = P(s, ai+(bi-ai)*t, aj+(bj-aj)*t, z)
        s.put(p[0], p[1]-1, material['dark'])
        for dz in range(1, height):
            s.put(p[0], p[1]-dz, material['lit'] if dz in (1, height-1) else material['mid'])
    for dz, c in ((height, material['hi']), (height+1, material['dark'])):
        seg(s, P(s, ai, aj, z+dz), P(s, bi, bj, z+dz), c)


def slab(s, quad, z0, z1, material, pattern=None):
    """Prism over an arbitrary ground quad (i, j) between heights z0 and z1: lit/shaded sides."""
    sides = []
    area = sum(quad[k][0]*quad[(k+1) % len(quad)][1]-quad[(k+1) % len(quad)][0]*quad[k][1] for k in range(len(quad)))
    sign = 1 if area > 0 else -1
    for k in range(len(quad)):
        (ai, aj), (bi, bj) = quad[k], quad[(k+1) % len(quad)]
        ni, nj = sign*(bj-aj), -sign*(bi-ai)  # outward normal in the (i, j) plane
        if ni+nj <= 1e-9:
            continue
        sides.append(((ai+bi+aj+bj), (ai, aj), (bi, bj), nj > ni))
    for _, (ai, aj), (bi, bj), lit in sorted(sides):
        pts = [P(s, ai, aj, z0), P(s, bi, bj, z0), P(s, bi, bj, z1), P(s, ai, aj, z1)]
        def color(x, y, pts=pts, lit=lit):
            v = pts[0][1] + (x-pts[0][0])*((pts[1][1]-pts[0][1])/(pts[1][0]-pts[0][0]) if abs(pts[1][0]-pts[0][0]) > .01 else 0) - y
            u = x-min(pts[0][0], pts[1][0])
            return (pattern(u, v, lit) if pattern else None) or material['lit' if lit else 'dark']
        poly(s, pts, color)
        seg(s, pts[2], pts[3], material['hi' if lit else 'line'])
    poly(s, [P(s, a, b, z1) for a, b in quad], lambda x, y: material['mid'])


# ------------------------------------------------------------- landmarks --

def castle(scene, i, j):
    """Hilltop castle: crenellated Outlook Tower and flag, ranges, round Archers' Tower,
    Pentagonal gate tower, St George's Chapel with bell turret, walls and terrace."""
    W, D, Z = 15, 11, 20
    def draw(s):
        # Retaining masonry of the hilltop platform and a court of beaten gravel.
        block(s, i, j, W, D, Z, ROCK, stone_courses(ROCK, 4, 9))
        poly(s, list(corners(s, i+.3, j+.3, W-.6, D-.6, Z)),
             lambda x, y: ROCK['lit'] if h01(x, y, 4401) < .2 else CASTLE['mid'])
        # Far ranges (north-east and north-west) with clay hips.
        for a, b, w, d, h in ((i+1, j+.6, 12.5, 2.2, 27), (i+.6, j+.6, 2.2, 8.6, 24)):
            block(s, a, b, w, d, h, CASTLE, windows(CASTLE, h, 10, 12, hood=True), z=Z)
            band(s, a, b, w, d, Z+h-2, WHITE, 2)
            hip_roof(s, a-.08, b-.08, w+.16, d+.16, Z+h, 9, CLAY)
        # Round Archers' Tower at the northern corner, conical clay roof.
        cylinder(s, i+1.6, j+1.6, 1.5, 1.5, Z, 36, CASTLE,
                 lambda u, v, lit: CASTLE['deep'] if int(u) % 9 in (4, 5) and int(v) % 14 in (7, 8, 9, 10)
                 else stone_courses(CASTLE, 5, 12)(u, v, lit))
        cylinder(s, i+1.6, j+1.6, 1.62, 1.62, Z+34, 2, WHITE)
        revolve(s, i+1.6, j+1.6, 1.75, Z+36, 16, [(0, 1), (1, .05)], CLAY, ribs=3)
        # St George's Chapel in the court: Gothic nave, buttresses, Baroque bell turret.
        a, b = i+7.5, j+3.6
        block(s, a, b, 3.6, 2.2, 20, WHITE,
              lambda u, v, lit: arch_opening(int(u) % 9, v, 4.5, 1.6, 12, GLASS['dark']) if 5 < v < 17 else None, z=Z)
        for k in range(4):
            block(s, a+.4+k*.95, b+2.2, .3, .3, 13, CASTLE, z=Z)
        hip_roof(s, a-.08, b-.08, 3.76, 2.36, Z+20, 9, CLAY)
        block(s, a+.4, b+.75, .8, .8, 9, WHITE,
              lambda u, v, lit: arch_opening(u, v, 3.2, 1.5, 4, IRON), z=Z+25)
        revolve(s, a+.8, b+1.15, .7, Z+34, 10, HELMET, COPPER, ribs=6)
        apple(s, a+.8, b+1.15, Z+44, .22)
        # Near curtain walls with merlons; the court stays visible above them.
        for a2, b2, w, d in ((i+W-1.2, j+2.8, 1, D-3.6), (i+2.8, j+D-1.2, W-5.2, 1)):
            cover = block(s, a2, b2, w, d, 12, CASTLE, stone_courses(CASTLE, 4, 11), z=Z)
            crenellate(s, a2, b2, w, d, Z+12, CASTLE, cover, step=4, height=3)
        # Pentagonal Tower over the entrance on the south-east side; drawbridge gate.
        a, b = i+W-2.2, j+D-2.2
        block(s, a, b, 2.4, 2.4, 26, CASTLE,
              lambda u, v, lit: arch_opening(u, v, 9.6, 3.2, 7, WOOD) if lit and v < 12 else
              CASTLE['deep'] if int(u) % 8 in (3, 4) and 15 < v < 20 else stone_courses(CASTLE, 4, 10)(u, v, lit), z=Z)
        poly(s, [P(s, a+1.2, b+2.4+.5, Z+26), P(s, a+2.4+.5, b+1.2, Z+26), P(s, a+1.2, b+1.2, Z+38)],
             lambda x, y: CLAY['dark'])
        hip_roof(s, a-.1, b-.1, 2.6, 2.6, Z+26, 11, CLAY)
        # Outlook Tower at the western corner, facing the Old Town.
        a, b = i+.5, j+D-2.6
        def tower(u, v, lit):
            c = int(u) % 9
            if 3 <= c <= 5 and int(v) % 15 in range(5, 11) and v < 66:
                return GLASS['dark'] if c != 4 else WHITE['lit' if lit else 'dark']
            if c == 0 or int(v) in (24, 25, 48, 49):
                return WHITE['hi' if lit else 'mid']
            return stone_courses(CASTLE, 5, 12)(u, v, lit)
        block(s, a, b, 2.3, 2.3, 70, CASTLE, tower, z=Z)
        # Corbelled viewing gallery with battlements and a flag.
        block(s, a-.25, b-.25, 2.8, 2.8, 3, WHITE, lambda u, v, lit: CASTLE['deep'] if int(u) % 4 == 0 and v < 2 else None, z=Z+70)
        cover = block(s, a-.25, b-.25, 2.8, 2.8, 3, CASTLE, z=Z+73)
        crenellate(s, a-.25, b-.25, 2.8, 2.8, Z+76, CASTLE, cover, step=3, height=4)
        flag(s, a+1.15, b+1.15, Z+77, 22)
        # Front terrace wall (panoramic terrace) with a parapet along the near corner.
        cover = block(s, i-.4, j+D-.6, 5, .8, 4, CASTLE, z=Z-4)
        crenellate(s, i-.4, j+D-.6, 5, .8, Z, CASTLE, cover, step=3, height=2)
    scene.add(i+j+W+D+4, draw)


def cathedral(scene, i, j):
    """St Nicholas: twin west belfries with copper helmets and gilded apples, crossing dome on an
    octagonal drum, transept, pilastered yellow walls, bronze portal, niche saint and curved gable."""
    W, D, H = 6.4, 13, 32
    def draw(s):
        side = windows(YELLOW, H, 12, 16, arched=True, pilasters=True, width=5)
        # Apse end, transept, crossing dome, then the long nave and west front.
        block(s, i+.7, j, W-1.4, 2.6, H-4, YELLOW, windows(YELLOW, H-4, 12, 14, arched=True, pilasters=True))
        hip_roof(s, i+.6, j-.1, W-1.2, 2.8, H-4, 10, CLAY)
        block(s, i-1.2, j+2.4, W+2.4, 3.6, H, YELLOW, side)
        band(s, i-1.2, j+2.4, W+2.4, 3.6, H-2, WHITE, 2)
        hip_roof(s, i-1.3, j+2.3, W+2.6, 3.8, H, 12, CLAY)
        ci, cj = i+W/2, j+4.2
        def drum(u, v, lit):
            c = int(u) % 7
            if c == 0:
                return WHITE['hi' if lit else 'mid']
            d = abs(c-3.5)
            if d < 1.6 and 3 < v < 9 + math.sqrt(max(0, 2.6-d*d)):
                return WHITE['mid'] if d > 1 else GLASS['dark']
            return None
        cylinder(s, ci, cj, 2.2, 2.2, H+6, 13, YELLOW, drum)
        cylinder(s, ci, cj, 2.35, 2.35, H+18, 2, WHITE)
        revolve(s, ci, cj, 2.4, H+20, 19, DOME, COPPER, ribs=3, segments=32)
        cylinder(s, ci, cj, .5, .5, H+38, 6, WHITE,
                 lambda u, v, lit: GLASS['dark'] if int(u) % 3 == 1 and 1 < v < 5 else None)
        revolve(s, ci, cj, .65, H+44, 5, DOME, COPPER, ribs=2)
        apple(s, ci, cj, H+48, .25)
        block(s, i, j+6, W, D-7.4, H, YELLOW, side)
        band(s, i, j+6, W, D-7.4, H-2, WHITE, 2)
        hip_roof(s, i-.1, j+5.9, W+.2, D-7.2, H, 12, CLAY)
        # Twin west towers either side of the façade.
        TH = H+25
        def belfry(u, v, lit):
            c = int(u)
            if c in (0, 1) or abs(u-15.2*(1 if lit else 1.16)) < 1.5:
                return WHITE['hi' if lit else 'mid']
            if int(v) in (16, 17, H, H+1, TH-2, TH-1):
                return WHITE['lit' if lit else 'dark']
            if v > H+3:
                return arch_opening(u, v, 7.6 if lit else 8.8, 2.6, H+13, IRON)
            return windows(YELLOW, H, 15 if lit else 18, 16, arched=True, width=5)(u, v, lit)
        def tower(a):
            block(s, a, j+D-2.2, 1.9, 2.2, TH, YELLOW, belfry)
            band(s, a, j+D-2.2, 1.9, 2.2, TH, WHITE, 2)
            revolve(s, a+.95, j+D-1.1, 1.15, TH+2, 20, HELMET, COPPER, ribs=4)
            apple(s, a+.95, j+D-1.1, TH+22)
        tower(i-.1)
        a, fw = i+1.8, W-3.6
        def front(u, v, lit):
            if not lit:
                return None
            mid = fw*4
            du = abs(u-mid)
            if du < 4.5 and v < 11 + math.sqrt(max(0, 4.5**2-du*du)):
                if du > 3.3 or v > 11 + math.sqrt(max(0, 3.3**2-du*du)):
                    return STONE['lit'] if int(v) % 3 else STONE['dark']
                return BRONZE['mid'] if (int(u)+int(v)) % 4 else BRONZE['hi']
            if du < 2.6 and 18 < v < 26 + math.sqrt(max(0, 2.6**2-du*du)):
                return YELLOW['deep'] if du < 2 else WHITE['mid']
            if int(v) in (16, 17, H-2, H-1):
                return WHITE['lit']
            if int(u) in (0, 1, int(fw*8)-2, int(fw*8)-1):
                return WHITE['hi']
            return None
        block(s, a, j+D-1.6, fw, 1.75, H, YELLOW, front)
        # Curved Baroque gable between the towers, with an oculus and a cross.
        n = 16
        crest = [P(s, a+fw*k/n, j+D+.15, H+11*math.sin(math.pi*k/n)**.8) for k in range(n+1)]
        poly(s, [P(s, a, j+D+.15, H)]+crest+[P(s, a+fw, j+D+.15, H)],
             lambda x, y: YELLOW['lit'])
        for p, q in zip(crest, crest[1:]):
            seg(s, p, q, WHITE['hi'], 2)
        ox, oy = P(s, a+fw/2, j+D+.15, H+5)
        for t in range(16):
            s.put(ox+2.2*math.cos(t*math.tau/16), oy+2.2*math.sin(t*math.tau/16), WHITE['hi'])
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                s.put(ox+dx, oy+dy, GLASS['dark'])
        seg(s, P(s, a+fw/2, j+D+.15, H+11), P(s, a+fw/2, j+D+.15, H+19), GOLD['dark'])
        seg(s, P(s, a+fw/2-.28, j+D+.15, H+16), P(s, a+fw/2+.28, j+D+.15, H+16), GOLD['lit'])
        tower(i+W-1.8)
        for k in range(3):
            block(s, a-.1, j+D+.15+k*.3, fw+.2, .35, 3-k, STONE)
    scene.add(i+j+W+D+3, draw)


def franciscan(scene, i, j):
    """Church of the Annunciation: red-pink Baroque screen front, two tiers of white Ionic and
    Corinthian pilasters, side volutes, three statue niches, portal stair, Madonna on the crest."""
    W, D, H = 6, 9, 28
    def draw(s):
        block(s, i+.4, j, W-.8, D-1.2, H, SALMON, windows(SALMON, H, 12, 14, arched=True, pilasters=True, width=5))
        band(s, i+.4, j, W-.8, D-1.2, H-2, WHITE, 2)
        gable_roof(s, i+.4, j, W-.8, D-1.3, H, 20, CLAY, SALMON)
        # Small bell turret over the east end.
        block(s, i+2.4, j+.6, 1.2, 1.2, 12, SALMON,
              lambda u, v, lit: arch_opening(int(u) % 5, v, 2.5, 1.2, 6, IRON) if v > 3 else None, z=H+8)
        revolve(s, i+3, j+1.2, .9, H+20, 11, HELMET, COPPER, ribs=4)
        apple(s, i+3, j+1.2, H+31, .2)
        fj, LH = j+D, 34
        def lower(u, v, lit):
            if not lit:
                return windows(SALMON, LH, 9, LH)(u, v, lit)
            c = int(u)
            if c in (0, 1, 9, 10, 37, 38, 46, 47):
                if v > LH-6:
                    return GOLD['hi'] if int(v) % 2 else WHITE['hi']  # Ionic capitals
                return WHITE['hi'] if c in (0, 9, 37, 46) else WHITE['mid']
            if int(v) in (2, LH-3, LH-2, LH-1):
                return WHITE['lit']
            du = abs(u-24)
            if du < 5.5 and v < 14 + math.sqrt(max(0, 5.5**2-du*du)):
                if du > 4.2 or v > 14 + math.sqrt(max(0, 4.2**2-du*du)):
                    return STONE['lit'] if int(v) % 3 else STONE['dark']
                return WOOD if int(u) % 4 else rgb('#8A603F')
            for nu in (5, 42):
                d = abs(u-nu)
                if d < 2.6 and 8 < v < 21 + math.sqrt(max(0, 2.6**2-d*d)):
                    return SALMON['deep'] if d < 1.9 else WHITE['mid']
            if du < 2.6 and 21 < v < 28 + math.sqrt(max(0, 2.6**2-du*du)):
                return SALMON['deep'] if du < 1.9 else WHITE['mid']
            return None
        block(s, i, fj-1.2, W, 1.3, LH, SALMON, lower)
        band(s, i, fj-1.2, W, 1.3, LH-1, WHITE, 2)
        statue(s, i+.69, fj+.1, 9, 10, WHITE, 0)
        statue(s, i+5.25, fj+.1, 9, 10, WHITE, 1)
        statue(s, i+3, fj+.1, 22, 7, WHITE, 1)
        # Upper tier with Corinthian pilasters, arched window, volutes and pediment.
        a, uw = i+1.25, W-2.5
        def upper(u, v, lit):
            if not lit:
                return None
            c = int(u)
            if c in (0, 1, 27, 28):
                return GOLD['hi'] if v > 11 and int(v) % 2 else WHITE['hi']
            du = abs(u-14)
            if du < 3.5 and 2 < v < 8 + math.sqrt(max(0, 3.5**2-du*du)):
                return WHITE['mid'] if du > 2.5 else GLASS['dark'] if int(u) != 14 else WHITE['mid']
            if int(v) in (13, 14):
                return WHITE['lit']
            return None
        block(s, a, fj-1.1, uw, 1.15, 15, SALMON, upper, z=LH)
        for sgn, u0 in ((-1, a), (1, a+uw)):
            pts = [P(s, u0-sgn*.9*(1-math.sin(t*math.pi/2)), fj+.08, LH+15*t) for t in [k/10 for k in range(11)]]
            poly(s, [P(s, u0, fj+.08, LH)]+pts+[P(s, u0, fj+.08, LH+15)], lambda x, y: SALMON['lit'])
            for p, q in zip(pts, pts[1:]):
                seg(s, p, q, WHITE['hi'])
            cx, cy = pts[0]
            for k in range(12):
                t = k*math.tau/11
                r = 2.2*(1-k/14)
                s.put(cx+sgn*1+r*math.cos(t), cy-2+r*math.sin(t), WHITE['hi'])
        pediment(s, a-.15, fj-1.1, uw+.3, 1.2, LH+15, 9, WHITE)
        # Copper Our Lady of Loreto with the Child on the gable crest.
        block(s, i+2.75, fj-.6, .5, .5, 3, WHITE, z=LH+23)
        statue(s, i+3, fj-.35, LH+26, 10, COPPER, 1)
        x, y = P(s, i+3.25, fj-.2, LH+33)
        for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1), (0, -1)):
            s.put(x+dx, y+dy, COPPER['hi'])
        for k in range(4):
            block(s, i+1.4, fj+.1+k*.3, W-2.8, .35, 4-k, STONE)
    scene.add(i+j+W+D+2, draw)


def preseren(scene, i, j):
    """Prešeren Monument: three tonalite steps, inscribed block, bronze poet holding his book,
    granite pedestal with the stylised lime tree, and the muse holding a laurel branch above him."""
    TONALITE = tones('#C3C3BE', '#9A9A96', '#85857F', '#6A6A65', '#484845', '#7B7B76', '#2E2E2C')
    GRANITE = tones('#F2EEE6', '#D9D3C6', '#C4BDAE', '#A39C8C', '#716B5E', '#B4AD9D', '#45403A')
    B = BRONZE
    def draw(s):
        for k, r in enumerate((1.6, 1.32, 1.04)):
            block(s, i+1.6-r, j+1.6-r, 2*r, 2*r, 2, TONALITE, z=k*2)
        # Granite pedestal behind; lime-tree relief on its shaded face.
        def lime(u, v, lit):
            if lit:
                return None
            if abs(u-5.5) < 1 and 3 < v < 14:
                return B['mid']
            if (u-5.5)**2/14+(v-14)**2/16 < 1 and (int(u)+int(v)) % 2 == 0:
                return B['lit'] if int(v) % 3 else LEAF
            return GRANITE['line'] if int(v) % 6 == 0 else None
        block(s, i+.9, j+.75, 1.4, 1.05, 22, GRANITE, lime, z=6)
        band(s, i+.85, j+.7, 1.5, 1.15, 27, GRANITE, 2)
        # Seated muse on the summit, bronze, half-draped, laurel held out over the poet.
        block(s, i+1.05, j+.85, 1.1, .8, 3, ROCK, z=29)
        block(s, i+1.2, j+.95, .8, .55, 3, B, z=32)                                   # lap/drapery
        block(s, i+1.25, j+1.45, .7, .35, 2, B, lambda u, v, lit: B['line'] if int(u) % 3 == 0 else None, z=30)
        cylinder(s, i+1.6, j+1.15, .25, .2, 35, 6, B, lambda u, v, lit: B['hi'] if lit and int(v) == 4 else None)
        cylinder(s, i+1.6, j+1.15, .14, .13, 41, 3, B)
        ellipse(s, i+1.6, j+1.15, .15, .14, 44, B['deep'])
        seg(s, P(s, i+1.42, j+1.3, 39), P(s, i+1.3, j+2.0, 41), B['lit'], 2)          # raised arm
        for k in range(7):
            x, y = P(s, i+1.3+k*.03, j+2.0+k*.08, 41-k*.9)
            s.put(x, y, LEAF); s.put(x+1, y, rgb('#86A85A')); s.put(x-1, y+1, rgb('#3E6233'))
        # Cut block inscribed PREŠEREN.
        block(s, i+.85, j+1.75, 1.5, .85, 8, TONALITE,
              lambda u, v, lit: GOLD['dark'] if lit and 3 <= v <= 4 and int(u) % 2 and 2 < u < 10 else None, z=6)
        # The poet: legs, open frock coat, waistcoat, shoulders, head, the book in his hand.
        pi_, pj = i+1.6, j+2.2
        for d in (-.13, .05):
            block(s, pi_+d, pj-.08, .1, .16, 5, B, z=14)
        cylinder(s, pi_, pj, .3, .22, 18, 3, B, lambda u, v, lit: B['line'] if int(u) % 4 == 0 else None)
        cylinder(s, pi_, pj, .24, .19, 21, 4, B)
        block(s, pi_-.07, pj+.12, .14, .08, 4, B, lambda u, v, lit: B['hi'], z=20)    # waistcoat
        block(s, pi_-.27, pj-.13, .54, .26, 2, B, z=25)
        cylinder(s, pi_, pj, .13, .12, 27, 3, B, lambda u, v, lit: B['hi'] if lit else None)
        ellipse(s, pi_, pj, .14, .13, 30, B['deep'])
        seg(s, P(s, pi_+.25, pj+.1, 25), P(s, pi_+.2, pj+.35, 21), B['dark'], 2)
        x, y = P(s, pi_+.15, pj+.4, 21)
        for dx in range(3):
            for dy in range(2):
                s.put(x+dx, y+dy, rgb('#D8CFA6') if dy else B['hi'])
    scene.add(i+j+5, draw)


def triple_bridge(scene, i, j):
    """Tromostovje: the stone central bridge with two arches and Plečnik's two splayed side
    footbridges, white balustrades of turned balusters, lamps and riverside piers."""
    L = 11
    def draw(s):
        bridges = [
            ([(i, j-.2), (i, j+1.3), (i+L, j+2), (i+L, j+.6)], False),        # eastern footbridge
            ([(i, j+2.7), (i, j+4.5), (i+L, j+4.5), (i+L, j+2.7)], True),     # central stone bridge
            ([(i, j+5.9), (i, j+7.4), (i+L, j+6.6), (i+L, j+5.2)], False),     # western footbridge
        ]
        deck = 9
        for quad, central in bridges:
            (a0, b0), (a1, b1), (a2, b2), (a3, b3) = quad
            # Visible +j face: arches open over the water.
            def face(u, v, lit, central=central):
                span = L*8/(2 if central else 1)
                k = (u % span) - span/2
                r = span/2-(4 if central else 8)
                rise = deck-(2.5 if central else 3.5)
                if v < rise and abs(k) < r and v < rise*math.sqrt(max(0, 1-(k/r)**2)):
                    return WATER[1] if v < 2 else rgb('#2C4A44')
                if central and int(v) % 3 == 0:
                    return STONE['line' if lit else 'deep']
                if not central and v > deck-3:
                    return WHITE['hi' if lit else 'mid']
                return None
            slab(s, [(a0, b0), (a1, b1), (a2, b2), (a3, b3)], 0, deck, STONE if central else WHITE, face)
            poly(s, [P(s, a, b, deck) for a, b in quad],
                 lambda x, y: STONE['mid'] if (int(x)+2*(int(y) % 2)) % 5 else STONE['dark'])
            # Far balustrade, lamps on the parapet, near balustrade.
            balustrade(s, (a0+.1, b0+.1), (a3-.1, b3+.1), deck, 4, WHITE)
            for t in ((.08, .5, .92) if central else (.25, .75)):
                for (pa, pb), (qa, qb) in (((a0, b0+.15), (a3, b3+.15)), ((a1, b1-.15), (a2, b2-.15))):
                    lamp(s, pa+(qa-pa)*t, pb+(qb-pb)*t, deck+4, 9 if central else 7)
            balustrade(s, (a1+.1, b1-.1), (a2-.1, b2-.1), deck, 4, WHITE)
        # Abutment lamps where the bridges land on the quays.
        for a in (i-.3, i+L+.3):
            for b in (j+2.45, j+4.75):
                lamp(s, a, b, 0, 15)
    scene.add(i+j+L+8, draw)


def dragon(s, i, j, z, facing=-1, material=COPPER):
    """Copper dragon on its pedestal: haunches, raised chest, S-neck and open-jawed head, spread
    ribbed bat wings and a tail curling down the plinth. facing: -1 north (-i), +1 south (+i)."""
    f = facing
    block(s, i-.35, j-.4, .7, .8, 4, material, lambda u, v, lit: material['line'] if int(u+v) % 4 == 0 else None, z=z)
    cylinder(s, i+f*.1, j, .32, .32, z+3, 8, material,
             lambda u, v, lit: material['hi'] if int(v) % 3 == 0 and lit else None)
    # Wings: two ribbed membranes spreading sideways and up.
    for side in (-1, 1):
        root = (i-f*.1, j+side*.2, z+9)
        tips = [(i-f*.5, j+side*1.1, z+21), (i-f*.75, j+side*1.25, z+15), (i-f*.6, j+side*1.0, z+10)]
        membrane = [P(s, *root)] + [P(s, *t) for t in tips] + [P(s, i-f*.3, j+side*.4, z+7)]
        poly(s, membrane, lambda x, y: material['dark'] if side > 0 else material['mid'])
        for t in tips:
            seg(s, P(s, *root), P(s, *t), material['deep'])
        seg(s, P(s, *root), P(s, *tips[0]), material['hi'])
    # Neck and head, jaw open, with a crest.
    prev = None
    for k in range(9):
        t = k/8
        p = (i+f*(.15+.35*math.sin(t*2.6)), j, z+10+8*t)
        if prev:
            a, b = P(s, *prev), P(s, *p)
            seg(s, a, b, material['lit'], 3)
            seg(s, (a[0], a[1]+2), (b[0], b[1]+2), material['dark'])
        prev = p
    hi, hj, hz = prev
    block(s, hi+(f-1)*.35, hj-.17, .7, .34, 2.5, material, z=hz)
    seg(s, P(s, hi+f*.7, hj, hz+.5), P(s, hi+f*.95, hj, hz-1.5), material['dark'], 2)  # lower jaw
    s.put(*P(s, hi+f*.2, hj+.18, hz+2), rgb('#E7C85A'))  # eye
    for k in range(3):
        s.put(*P(s, hi-f*(.1+k*.15), hj, hz+3+k % 2), material['hi'])
    # Tail coiling down the pedestal.
    prev = None
    for k in range(14):
        t = k/13
        p = P(s, i-f*.35+.3*math.cos(t*5), j+.45+.25*math.sin(t*5), z+3-9*t)
        if prev:
            seg(s, prev, p, material['mid'], 2)
        prev = p


def dragon_bridge(scene, i, j):
    """Zmajski most: pale concrete three-hinged arch, panelled parapets, dragon-crowned lamps,
    and four winged copper dragons on corner pedestals."""
    L, Wd, deck = 11, 2.8, 11
    def draw(s):
        def face(u, v, lit):
            k = u-L*4
            r = L*4-9
            if v < deck-3 and abs(k) < r and v < (deck-3)*math.sqrt(max(0, 1-(k/r)**2)):
                return WATER[1] if v < 2 else rgb('#2C4A44')
            if abs(k) < r+1.5 and v < (deck-3)*math.sqrt(max(0, 1-(k/(r+1.5))**2))+1.5:
                return CONCRETE['hi' if lit else 'mid']  # arch ring
            if v > deck-2:
                return CONCRETE['lit' if lit else 'dark']
            return CONCRETE['line'] if int(u) % 12 == 0 else None
        cover = facade(s, i, j, L, Wd, deck, face, palette=CONCRETE)
        iso.outline(s, cover, CONCRETE['outline'])
        poly(s, list(corners(s, i, j+.3, L, Wd-.6, deck)), lambda x, y: rgb('#6B6B68') if (int(x)+int(y)) % 9 else rgb('#7E7E7A'))
        for b in (j, j+Wd-.3):
            block(s, i, b, L, .3, 4, CONCRETE,
                  lambda u, v, lit: CONCRETE['deep'] if int(u) % 8 in (3, 4, 5) and 1 <= v <= 2 else None, z=deck)
            for t in (.33, .67):
                lamp(s, i+L*t, b+.15, deck+4, 9, CONCRETE)
                x, y = P(s, i+L*t, b+.15, deck+18)
                for dx, dy in ((-1, 0), (0, -1), (1, 0), (1, 1), (-1, 1)):
                    s.put(x+dx, y+dy, COPPER['mid'])
        # Pedestals and dragons: far (north) pair first, then south pair.
        for a, f in ((i-.4, -1), (i+L-.6, 1)):
            for b in (j-.3, j+Wd-.7):
                block(s, a, b, 1, 1, deck+9, CONCRETE,
                      lambda u, v, lit: CONCRETE['deep'] if 4 < v < deck+5 and int(u) % 8 in (2, 5) else None, z=0)
                band(s, a, b, 1, 1, deck+8, CONCRETE, 2)
                dragon(s, a+.5, b+.5, deck+10, f)
    scene.add(i+j+L+Wd+2, draw)


def market(scene, i, j):
    """Plečnik's Market colonnade following the river: two storeys, Doric street colonnade,
    small upper windows, tiled hips, and two open riverside loggias between the halls."""
    W, H = 3.2, 30
    halls = [(0, 4.6), (6.4, 3.6), (11.8, 4.6)]
    loggias = [(4.6, 1.8), (10, 1.8)]
    def draw(s):
        def colonnade(u, v, lit):
            if lit:
                c = int(u) % 8
                if v < 13:
                    return STONE['hi'] if c in (0, 1) else STONE['deep'] if 2 <= c <= 6 and v > 1 else None
            else:
                c = int(u) % 10
                if v < 14:
                    if c in (0, 1):
                        return STONE['lit'] if c == 0 else STONE['mid']
                    if v > 1:
                        return rgb('#4C4840') if v < 12 else STONE['deep']
                if int(v) in (14, 15, H-2, H-1):
                    return STONE['hi'] if int(v) in (15, H-1) else STONE['mid']
                if 4 <= c <= 6 and 19 < v < 25:
                    return GLASS['dark'] if c != 5 else STONE['lit']
                return stone_courses(STONE, 5, 10)(u, v, lit)
            return None
        # From the far (north-east) end, each hall then the loggia in front of it.
        segments = sorted([(b, d, 'hall') for b, d in halls] + [(b, d, 'loggia') for b, d in loggias])
        for b, d, kind in segments:
            if kind == 'hall':
                block(s, i, j+b, W, d, H, STONE, colonnade)
                band(s, i, j+b, W, d, 14, STONE, 1)
                band(s, i, j+b, W, d, H-1, WHITE, 2)
                hip_roof(s, i-.1, j+b-.1, W+.2, d+.2, H+1, 9, ROOF)
            else:
                # Open loggia: paired columns on both storeys with the river seen through.
                def open_face(u, v, lit):
                    c = int(u) % 6
                    if c in (0, 1) or int(v) in (13, 14, 15, H-5, H-4, H-3):
                        if v > 10 and v < 13 or v > H-8 and v < H-5:
                            return STONE['hi'] if lit else STONE['lit']  # capitals
                        return STONE['hi' if c == 0 else 'lit'] if lit else STONE['lit' if c == 0 else 'mid']
                    if 3 <= c <= 4 and (3 < v < 10 or 18 < v < H-8):
                        return rgb('#9CC4B8')  # river light through the far arcade
                    return rgb('#4B4A42') if v > 1 else STONE['dark']
                block(s, i+.3, j+b, W-.6, d, H-3, STONE, open_face)
                hip_roof(s, i+.2, j+b-.05, W-.4, d+.1, H-2, 7, ROOF)
        # Steps between the colonnade and Vodnik Square.
        for k in range(2):
            block(s, i+W+k*.3, j+.4, .3, 15.2, 2-k, STONE)
    scene.add(i+j+W+16+1, draw)


def town_hall(scene, i, j):
    """Mestna hiša: Baroque gable front, arcaded loggia, rusticated piers, central clock tower and
    lantern; Robba's Fountain of the Three Carniolan Rivers on the square before it."""
    W, D, H = 7, 5, 31
    WALL = tones('#F3EEDC', '#E1D9C2', '#CCC3AA', '#ABA187', '#776E58', '#BCB197', '#4A4333')
    def draw(s):
        def front(u, v, lit):
            if v < 12:
                c = int(u) % 11
                o = arch_opening(c, v, 5.5, 3.5, 6, rgb('#4D463A'))
                if o and lit:
                    return o
                return stone_courses(WALL, 3, 11)(u, v, lit) or WALL['lit' if lit else 'dark']
            if int(v) in (12, 13, H-2, H-1):
                return WHITE['hi' if lit else 'mid']
            return windows(WALL, H, 11, 10, hood=True)(u, v-12, lit)
        block(s, i, j, W, D, H, WALL, front)
        hip_roof(s, i-.1, j-.1, W+.2, D+.2, H, 13, CLAY)
        # Gabled central bay with balcony, the city arms and the clock tower.
        a, b = i+2.4, j+D-.3
        block(s, a, b, 2.2, .5, H+12, WALL,
              lambda u, v, lit: (GLASS['dark'] if 6 < u < 12 and 16 < v < 25 and int(u) != 9 else
                                 WHITE['hi'] if int(v) in (14, 26, H, H+1) else None) if lit else None)
        block(s, a-.1, b+.5, 2.4, .4, 1.5, WHITE, z=14)
        for k in range(10):
            seg(s, P(s, a+k*.24, b+.9, 15.5), P(s, a+k*.24, b+.9, 18), IRON)
        seg(s, P(s, a, b+.9, 18), P(s, a+2.4, b+.9, 18), IRON)
        pediment(s, a-.1, b, 2.4, .5, H+12, 7, WHITE)
        ci, cj = a+1.1, b-.6
        block(s, ci-.7, cj-.7, 1.4, 1.4, 16, WALL, lambda u, v, lit:
              arch_opening(u, v, 5.6, 2, 9, IRON) if v > 4 else None, z=H+8)
        band(s, ci-.7, cj-.7, 1.4, 1.4, H+23, WHITE, 2)
        x0, y0 = P(s, ci-.2, cj+.71, H+14)
        for n in range(16):
            t = n*math.tau/16
            s.put(x0+2.8*math.cos(t), y0+2.8*math.sin(t), GOLD['lit'])
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if dx*dx+dy*dy <= 4:
                    s.put(x0+dx, y0+dy, WHITE['hi'])
        seg(s, (x0, y0), (x0, y0-2), IRON); seg(s, (x0, y0), (x0+2, y0), IRON)
        revolve(s, ci, cj, .95, H+25, 10, HELMET, COPPER, ribs=4)
        apple(s, ci, cj, H+35, .2)
        for fa in (i+.5, i+W-.5):
            flag(s, fa, j+D-.2, H+2, 14)
        # Three-part entrance stair.
        for k in range(2):
            block(s, i+1, j+D+k*.3, W-2, .35, 2-k, STONE)
        # Robba Fountain, north-west of the stair: three-lobed basin, three river gods pouring
        # from jugs, rose-limestone pedestal and slender obelisk.
        fi, fj = i+1.1, j+D+3.0
        lobes = []
        for k in range(36):
            t = k*math.tau/36
            r = 1.35+.35*math.cos(3*(t-math.pi/4))
            lobes.append((fi+r*math.cos(t), fj+r*math.sin(t)))
        slab(s, lobes, 0, 3, WHITE)
        poly(s, [P(s, fi+(x-fi)*.84, fj+(y-fj)*.84, 3.2) for x, y in lobes],
             lambda x, y: WATER[2] if h01(x//2, y, 4402) < .12 else WATER[0])
        block(s, fi-.5, fj-.5, 1, 1, 7, PINKSTONE, lambda u, v, lit: WHITE['lit' if lit else 'dark'] if int(v) in (1, 6) else None, z=2)
        for t in sorted((math.pi/4, math.pi/4+2.09, math.pi/4+4.19), key=lambda t: math.cos(t)+math.sin(t)):
            gi, gj = fi+.8*math.cos(t), fj+.8*math.sin(t)
            block(s, gi-.3, gj-.25, .6, .5, 2.5, WHITE, z=3)                    # reclining body
            cylinder(s, gi-.1*math.cos(t), gj-.1*math.sin(t), .2, .18, 5.5, 4, WHITE)
            cylinder(s, gi-.1*math.cos(t), gj-.1*math.sin(t), .13, .12, 9.5, 2.5, WHITE)
            ellipse(s, gi-.1*math.cos(t), gj-.1*math.sin(t), .13, .12, 12, WHITE['mid'])
            ji, jj = gi+.42*math.cos(t), gj+.42*math.sin(t)
            cylinder(s, ji, jj, .17, .17, 4, 2.5, STONE)
            x, y = P(s, ji+.15*math.cos(t), jj+.15*math.sin(t), 5)
            for k in range(4):
                s.put(x+(k % 2), y+k, WATER[2])
        def obelisk(base, h, r0, r1):
            T0, R0, B0, L0 = corners(s, fi-r0, fj-r0, 2*r0, 2*r0, base)
            T1, R1, B1, L1 = corners(s, fi-r1, fj-r1, 2*r1, 2*r1, base+h)
            poly(s, [L0, B0, B1, L1], lambda x, y: PINKSTONE['lit'] if int(y) % 7 else PINKSTONE['line'])
            poly(s, [B0, R0, R1, B1], lambda x, y: PINKSTONE['dark'] if int(y) % 7 else PINKSTONE['deep'])
            seg(s, B0, B1, PINKSTONE['hi'])
            apex = P(s, fi, fj, base+h+4)
            poly(s, [L1, B1, apex], lambda x, y: PINKSTONE['hi'])
            poly(s, [B1, R1, apex], lambda x, y: PINKSTONE['mid'])
        obelisk(9, 30, .3, .16)
    scene.add(i+j+W+D+7, draw)


def townhouse(scene, i, j, wi=2.5, wj=3, floors=3, seed=0):
    """Ljubljana plaster houses: Baroque portals, framed windows with hoods, Secession friezes,
    steep clay hips with eyebrow dormers and chimneys."""
    wall, height = palette_of(WALLS[seed % len(WALLS)]), floors*10+4
    base = windows(wall, height, 9, 10, hood=seed % 2 == 0)
    secession = seed % 13 == 1 and seed % 2 == 0
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
            return wall['mid'] if int(v) % 3 == 0 else None  # rusticated ground floor
        if secession and level == 9:
            return rgb('#4E8E8A') if int(u) % 3 else GOLD['lit']  # ceramic frieze
        if seed % 4 == 0 and v >= 10 and level == 2 and 1 <= c <= 7:
            return IRON
        return base(u, v, lit)
    def draw(s):
        block(s, i, j, wi, wj, height, wall, pattern)
        band(s, i, j, wi, wj, 1, STONE, 2)
        band(s, i, j, wi, wj, height-1, WHITE)
        hip_roof(s, i-.05, j-.05, wi+.1, wj+.1, height, 16 if seed % 3 else 12, CLAY)
        # Eyebrow dormer (frčada) on the lit slope.
        x, y = P(s, i+wi/2, j+wj-.75, height+5)
        for dx in range(-3, 4):
            for dy in range(0, 4 - abs(dx)//2):
                s.put(x+dx, y-dy, CLAY['hi'] if dy == 3-abs(dx)//2 else CLAY['lit'])
        for dx in (-1, 0, 1):
            s.put(x+dx, y+1, GLASS['dark'])
        block(s, i+wi-.7, j+.45, .4, .45, 9, STONE, z=height+6)
        band(s, i+wi-.7, j+.45, .4, .45, height+14, CLAY, 2)
        if secession:
            # Corner turret with a small copper helmet.
            block(s, i+wi-.9, j+wj-.9, 1, 1, 8, wall, windows(wall, 8, 8, 8), z=height)
            revolve(s, i+wi-.4, j+wj-.4, .6, height+8, 9, HELMET, COPPER, ribs=4)
    scene.add(i+j+wi+wj, draw)


def funicular(scene, i, j, length, top):
    """Castle funicular: stone track bed and rails climbing along +i from the town to the castle,
    with one red-and-glass car part-way up."""
    def z(t):
        return top*t
    def draw(s):
        bed = [P(s, i, j, 0), P(s, i+length, j, top), P(s, i+length, j+.9, top), P(s, i, j+.9, 0)]
        poly(s, bed, lambda x, y: STONE['dark'] if (int(x)+int(y)) % 4 else STONE['deep'])
        for k in range(int(length*3)):
            t = k/(length*3)
            seg(s, P(s, i+length*t, j+.15, z(t)+.5), P(s, i+length*t, j+.75, z(t)+.5), WOOD)
        for b in (.25, .65):
            seg(s, P(s, i, j+b, 1), P(s, i+length, j+b, top+1), IRON)
        t = .45
        a, zz = i+length*t, z(t)
        block(s, a-.6, j+.1, 1.2, .7, 6, palette_of(rgb('#C8463E')),
              lambda u, v, lit: GLASS['mid' if lit else 'dark'] if 2 < v < 5 and int(u) % 3 else None, z=zz+1)
    scene.add(i+j+length+1, draw)


def stall(scene, i, j, seed=0):
    """Vodnik Square market stall: timber counter with produce under a striped awning."""
    cloth = (rgb('#D9534A'), rgb('#3F7F9B'), rgb('#E2A13B'))[seed % 3]
    def draw(s):
        block(s, i, j, 1.4, 1, 4, palette_of(WOOD))
        for k in range(6):
            x, y = P(s, i+.2+k*.2, j+.5, 4.5)
            s.put(x, y, (rgb('#E5533C'), rgb('#F2C14E'), LEAF)[(k+seed) % 3])
        for a, b in ((i+.05, j+.05), (i+1.3, j+.05), (i+.05, j+.9), (i+1.3, j+.9)):
            seg(s, P(s, a, b, 4), P(s, a, b, 10), WOOD)
        poly(s, list(corners(s, i-.1, j-.1, 1.6, 1.2, 10)),
             lambda x, y: cloth if (int(x)//2) % 2 else WHITE['hi'])
        seg(s, P(s, i-.1, j+1.1, 10), P(s, i+1.5, j+1.1, 10), WHITE['deep'])
    scene.add(i+j+2.4, draw)


# name, builder, footprint, real (longitude, latitude), compressed north-up ground anchor.
SITES = [
    ('dragon-bridge', dragon_bridge, (11, 2.8), (14.510241, 46.051947), (620, 110)),
    ('franciscan', franciscan, (6, 9.5), (14.5060028, 46.0518389), (175, 190)),
    ('market', market, (3.5, 16.4), (14.50972, 46.05167), (575, 205)),
    ('preseren', preseren, (3.2, 3.2), (14.5063083, 46.0514083), (282, 247)),
    ('triple-bridge', triple_bridge, (11, 7.4), (14.50611, 46.05111), (240, 300)),
    ('cathedral', cathedral, (6, 14), (14.50778, 46.05056), (410, 320)),
    ('town-hall', town_hall, (7, 9.5), (14.50694, 46.049861), (300, 410)),
    ('castle', castle, (15, 11), (14.50833, 46.04889), (548, 456)),
]


def main():
    for name, builder, (wi, wj), _, _ in SITES:
        print(preview([lambda s, b=builder: b(s, 4, 4)], 'ljubljana-'+name,
                      size=(300, 300), origin=(150, 120), tiles=24))
    print(preview([lambda s, n=n, seed=seed: townhouse(s, 3+n*3, 3, 2.5, 3, 2+n % 2, seed)
                   for n, seed in enumerate((0, 1, 2, 14, 4, 5))],
                  'ljubljana-houses', size=(300, 240), origin=(80, 90), tiles=24))
    import sprites
    if hasattr(sprites, 'bled'):
        sprite = sprites.bled()
        path = Path(__file__).resolve().parents[2]/'docs/art/capitals/slovenia-bled.png'
        sprite.resize((sprite.width*4, sprite.height*4), 0).save(path)
        print(path)


if __name__ == '__main__':
    main()
