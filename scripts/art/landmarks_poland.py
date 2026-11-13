"""Warsaw's Mazovian brick, coloured Old Town stucco and royal palaces in (i, j, z).

Run directly for eight isolated landmark plots and a house study, at integer 4×.
Real geographic anchors and architectural references are in DEVELOPMENT_PLAN.md.
"""
import math

import iso
from iso import rgb
from landmarks_paris import P, seg, poly, corners, facade, mansard, preview, GLASS
from landmarks_iberia import hip_roof, crenellate, stone_courses, arch_opening, palette_of, tones
from landmarks_italy import cylinder, ellipse
from landmarks_denmark import spire
from landmarks_amsterdam import gable_roof

STONE = tones('#F7EDDA', '#DBCCAF', '#C3B397', '#A08F75', '#71624E', '#B5A286', '#493E31')
PALE = tones('#FFF4DE', '#EEE1C4', '#D7C6A6', '#B7A17F', '#827054', '#CCB896', '#514330')
BRICK = tones('#E5AC8A', '#BD775A', '#A05E47', '#7D4538', '#562F2A', '#9A5945', '#422B25')
CLAY = tones('#F3B08B', '#D08460', '#B46849', '#8C4938', '#60312A', '#A25A42', '#4D2C25')
SALMON = tones('#F7C4AA', '#DD9B7F', '#C58469', '#A56552', '#774936', '#B9755D', '#51392B')
YELLOW = tones('#FFF1AE', '#E9CE7C', '#CEAC5E', '#AA8847', '#796132', '#BD9A52', '#51412A')
COPPER = tones('#B6CBB3', '#85A590', '#698B77', '#496856', '#304A3C', '#5C7A65', '#283D32')
SLATE = tones('#ADB3B8', '#7F8B92', '#66737D', '#495761', '#303E49', '#5B6974', '#283540')
BRONZE = tones('#B6B49A', '#81947C', '#62765E', '#405B47', '#2B4132', '#53694F', '#22372A')
GRANITE = tones('#DDBEAD', '#BD9582', '#A47A68', '#815B4E', '#5C4037', '#956D5D', '#49352D')
GOLD = tones('#FFF0B3', '#E6C56F', '#C2A051', '#967738', '#6E552A', '#AF8B45', '#503D23')
WALLS = [rgb(c) for c in ('#D8B66F', '#C6856E', '#B8BF9A', '#E6D4B2', '#B6C9C5', '#DDA684', '#AB795F')]
WATER = (rgb('#528794'), rgb('#3E6D7F'), rgb('#C1DFDC'))
IRON, WOOD, FLAG_RED = rgb('#36413D'), rgb('#715140'), rgb('#C75252')


def block(s, i, j, wi, wj, height, material=STONE, pattern=None, z=0):
    cover = facade(s, i, j, wi, wj, height, pattern or stone_courses(material, 5, 12),
                   palette=material, z0=z)
    iso.fill(s, list(corners(s, i, j, wi, wj, z+height)), lambda x, y: material['mid'], cover)
    iso.outline(s, cover, material['outline'])
    return cover


def band(s, i, j, wi, wj, z, material=PALE, height=2):
    facade(s, i-.06, j-.06, wi+.12, wj+.12, height,
           lambda u, v, lit: material['hi' if lit else 'dark'], palette=material, z0=z)


def windows(material, height, bay=10, floor=13, gothic=False, pilasters=False):
    courses = stone_courses(material, 3 if material == BRICK else 5, 11)
    def pattern(u, v, lit):
        c, v = int(u) % bay, int(v)
        level, trim = v % floor, PALE['lit' if lit else 'dark']
        if v < 2 or v in (height-1, height-3) or level == 0:
            return trim
        if pilasters and c in (0, 1):
            return trim
        head = floor-3-abs(c-bay/2)*(1.25 if gothic else .2)
        if 2 <= c <= bay-2 and 3 <= level <= head and v < height-4:
            if c in (2, bay-2, bay//2) or level in (3, 6, int(head)):
                return trim if not gothic else material['hi' if lit else 'mid']
            return GLASS['mid' if lit else 'dark']
        return courses(u, v, lit)
    return pattern


def extrude(s, profile, j, thickness, material):
    """A carved i/z profile with an actual j-depth, lit front and shaded returns."""
    front = [P(s, i, j, z) for i, z in profile]
    back = [P(s, i, j-thickness, z) for i, z in profile]
    poly(s, back, lambda x, y: material['dark'])
    for n in range(len(profile)):
        k = (n+1) % len(profile)
        poly(s, [front[n], back[n], back[k], front[k]], lambda x, y: material['mid'])
        seg(s, back[n], back[k], material['outline'])
    poly(s, front, lambda x, y: material['lit'] if int(x+y) % 7 else material['mid'])
    for p, q in zip(front, front[1:]+front[:1]):
        seg(s, p, q, material['outline'])
    return front


def clock(s, i, j, z, radius=5, lit=True):
    def point(u, v):
        return P(s, i+u/8 if lit else i, j if lit else j-u/8, z+v)
    circle = [point(math.cos(n*math.tau/32)*radius, math.sin(n*math.tau/32)*radius) for n in range(32)]
    poly(s, circle, lambda x, y: PALE['hi'])
    for a, b in zip(circle, circle[1:]+circle[:1]):
        seg(s, a, b, GOLD['dark'])
    for n in range(12):
        a = n*math.tau/12
        s.put(*point(math.cos(a)*(radius-1), math.sin(a)*(radius-1)), IRON)
    seg(s, point(0, 0), point(-radius*.6, radius*.15), IRON)
    seg(s, point(0, 0), point(radius*.15, radius*.7), IRON)


def figure(s, i, j, z, height=8, material=PALE, sword=False):
    """Filled sculpted person, including head, shoulders, flared robe, bent arms and base."""
    block(s, i-.2, j-.2, .4, .4, 2, material, z=z)
    profile = [(-.22, 2), (.24, 2), (.15, height*.5), (.25, height*.65),
               (.16, height*.78), (.1, height*.81), (.12, height), (-.12, height),
               (-.16, height*.83), (-.27, height*.68), (-.15, height*.45)]
    extrude(s, [(i+a, z+b) for a, b in profile], j+.07, .22, material)
    seg(s, P(s, i-.1, j+.1, z+height*.76), P(s, i+.22, j+.13, z+height*.51), material['hi'])
    if sword:
        block(s, i+.23, j-.02, .13, .13, height*.65, material, z=z+height*.45)
        seg(s, P(s, i+.1, j+.12, z+height*.62), P(s, i+.46, j+.12, z+height*.62), material['hi'])


def townhouse(scene, i, j, wi=2.4, wj=2.8, floors=3, seed=0, ornate=False):
    """Warsaw kamienice: warm stucco, white surrounds, tiled gables, restrained sgraffito."""
    wall, height = palette_of(WALLS[seed % len(WALLS)]), floors*11+3
    def pattern(u, v, lit):
        c, v = int(u) % 10, int(v)
        level, trim = (v-11) % 11, PALE['lit' if lit else 'dark']
        if v < 3:
            return STONE['mid' if lit else 'deep']
        if v in (10, height-1, height-3):
            return trim
        if v < 10:
            opening = arch_opening(c, v, 5, 3, 5, WOOD if seed % 3 else GLASS['dark'])
            if opening:
                return trim if c in (2, 8) or v == 8 else opening
        if 2 <= c <= 8 and 2 <= level <= 8 and 11 <= v < height-4:
            return trim if c in (2, 5, 8) or level in (2, 5, 8) else GLASS['mid' if lit else 'dark']
        if ornate and v > 13 and level in (0, 10) and 1 <= c <= 9:
            return wall['deep'] if c % 3 == 0 else trim
        if seed % 4 == 0 and 11 < v < height-4 and level == 1 and 2 <= c <= 8:
            return IRON  # iron window guards on selected houses
        if ornate and int(u+v*1.3) % 19 == 0:
            return wall['line']
        return None
    def draw(s):
        block(s, i, j, wi, wj, height, wall, pattern)
        gable_roof(s, i-.05, j-.05, wi+.1, wj+.1, height, 12+seed % 3, CLAY, wall,
                   'bell' if ornate and seed % 2 else 'point')
        # Framed attic opening in the lit gable; occasionally a carved medallion.
        a, b = i+wi*.42, j+wj+.13
        block(s, a, b, wi*.18, .08, 5, PALE,
              lambda u, v, lit: GLASS['dark'] if lit and 1 < u < wi*1.4-1 and 1 < v < 4 else None,
              z=height+3)
        if ornate:
            cylinder(s, i+wi*.5, j+wj+.17, .18, .07, height+10, 3, GOLD)
        block(s, i+.3, j+.5, .4, .4, 8, BRICK, z=height+6)
        band(s, i+.3, j+.5, .4, .4, height+13, PALE, 1)
    scene.add(i+j+wi+wj+1, draw)


def barbican(scene, i, j):
    """Semicircular brick gate, four conical turrets, slit windows, battlements and bridge."""
    def draw(s):
        # Recessed gate passage and causeway stay between the curved curtain's ends.
        block(s, i+2.6, j+2.7, 2.8, 4.7, 4, STONE)
        for n in range(9):
            a, b = -math.pi*.12+n*math.pi*1.24/9, -math.pi*.12+(n+1)*math.pi*1.24/9
            pts = [(i+4+r*math.cos(t), j+2.6+r*math.sin(t), z)
                   for r, t, z in ((3.5, a, 0), (3.5, b, 0), (3.5, b, 27), (3.5, a, 27))]
            lit = math.sin((a+b)/2)-.5*math.cos((a+b)/2) > 0
            foot = P(s, *pts[0])
            def bricks(x, y, foot=foot, lit=lit):
                return BRICK['line' if lit else 'deep'] if int(y-foot[1]) % 3 == 0 and int(x) % 3 else BRICK['lit' if lit else 'dark']
            poly(s, [P(s, *p) for p in pts], bricks)
            seg(s, P(s, *pts[2]), P(s, *pts[3]), STONE['lit'])
            for t in (a, (a+b)/2):
                aa, bb = i+4+3.5*math.cos(t), j+2.6+3.5*math.sin(t)
                block(s, aa-.12, bb-.12, .24, .24, 3, BRICK, z=27)
        # Central brick gate with its round-headed recessed opening, not a blank wall.
        def gate(u, v, lit):
            if lit:
                opening = arch_opening(u, v, 12, 5.4, 10, BRICK['deep'])
                if opening:
                    return opening
            return stone_courses(BRICK, 3, 8)(u, v, lit)
        block(s, i+2.5, j+4.5, 3, .8, 26, BRICK, gate)
        crenellate(s, i+2.5, j+4.5, 3, .8, 26, BRICK, set(), step=5, height=4)
        for a, b in ((i+1, j+1), (i+7, j+1), (i+1.8, j+4.9), (i+6.2, j+4.9)):
            cylinder(s, a, b, .7, .7, 0, 34, BRICK,
                     lambda u, v, lit: BRICK['deep'] if int(u) % 13 in (4, 5) and (8 < v < 13 or 22 < v < 28)
                     else stone_courses(BRICK, 3, 9)(u, v, lit))
            cylinder(s, a, b, .78, .78, 32, 3, STONE)
            spire(s, a, b, .87, 35, 18, CLAY, conical=True)
        # Short surviving city wall to one side, with a raised crenellated walk.
        block(s, i-.8, j+.2, 2.3, .5, 18, BRICK)
        crenellate(s, i-.8, j+.2, 2.3, .5, 18, BRICK, set(), step=5, height=3)
    scene.add(i+j+16, draw)


def old_town_square(scene, i, j):
    """Market façades, open cobbled square and the sword/shield Mermaid over her basin."""
    def ground(s):
        poly(s, list(corners(s, i, j, 10, 8, 0)),
             lambda x, y: STONE['dark'] if (int(x)+2*(int(y) % 2)) % 5 == 0 else STONE['mid'])
    scene.add(i+j, ground)
    # Two back sides, leaving the Mermaid's forecourt unobscured.
    for n in range(4):
        townhouse(scene, i+n*2.5, j, 2.35, 2.25, 2+(n % 2), 2+n, ornate=True)
    for n in range(2):
        townhouse(scene, i, j+2.5+n*2.5, 2.25, 2.35, 2+n, n, ornate=True)
    def draw(s):
        ci, cj = i+6.2, j+5.6
        cylinder(s, ci, cj, 1.35, 1.35, 0, 3, STONE)
        ellipse(s, ci, cj, 1.13, 1.13, 3.2,
                lambda x, y: WATER[2] if (int(x)+int(y)) % 9 == 0 else WATER[1])
        cylinder(s, ci, cj, .47, .47, 3, 5, GRANITE)
        # Curled fish tail, torso, hair, shield and raised bent sword arm, all solid volumes.
        tail = [(-.48, 0), (.38, 0), (.55, 2), (.3, 4), (.2, 6), (-.12, 6),
                (-.08, 4), (.12, 2), (-.15, 1.5), (-.48, 2)]
        extrude(s, [(ci+a, 8+z) for a, z in tail], cj+.15, .3, BRONZE)
        figure(s, ci, cj, 12, 7, BRONZE)
        cylinder(s, ci+.52, cj+.1, .35, .15, 13, 4, BRONZE)
        extrude(s, [(ci-.17, 17), (ci-.58, 19), (ci-.65, 22), (ci-.49, 22),
                    (ci-.4, 20), (ci, 18)], cj+.1, .17, BRONZE)
        seg(s, P(s, ci-.57, cj+.1, 21), P(s, ci-.9, cj+.1, 26), STONE['hi'], 2)
        seg(s, P(s, ci-.8, cj+.1, 21), P(s, ci-.35, cj+.1, 21), BRONZE['hi'])
        # Café tables and folded parasols remain on the open paving.
        for aa, bb in ((i+8.7, j+3.7), (i+4, j+6.8)):
            cylinder(s, aa, bb, .12, .12, 0, 4, WOOD_MATERIAL)
            cylinder(s, aa, bb, .42, .42, 4, 1, PALE)
    scene.add(i+j+19, draw)


WOOD_MATERIAL = palette_of(WOOD)


def st_john(scene, i, j):
    """Mazovian Gothic stepped brick west gable, white blind tracery, portals and buttresses."""
    def draw(s):
        wi, wj, H = 5.6, 7, 41
        block(s, i, j, wi, wj, H, BRICK, windows(BRICK, H, 11, 26, True))
        gable_roof(s, i, j, wi, wj, H, 28, CLAY, BRICK)
        for n in range(5):
            a = i+wi
            b = j+.5+n*1.45
            block(s, a, b, .65, .35, 29, BRICK)
            block(s, a, b, .45, .35, 8, BRICK, z=29)
            hip_roof(s, a-.02, b-.03, .5, .42, 37, 5, CLAY)
        def front(u, v, lit):
            if not lit:
                return stone_courses(BRICK, 3, 10)(u, v, lit)
            d = abs(u-22.4)
            if d < 5.5 and v < 17-d*.9:
                return PALE['lit'] if d > 4.2 or v > 14-d else BRICK['deep']
            for centre in (7.5, 22.4, 37.3):
                d = abs(u-centre)
                if d < 3.8 and 18 < v < 35-d*1.6:
                    return BRICK['hi'] if d > 2.8 or int(v) == 19 else PALE['mid'] if int(u) % 4 == 0 else GLASS['dark']
            if int(v) in (22, 24, 38, 40):
                return PALE['lit']
            return stone_courses(BRICK, 3, 10)(u, v, lit)
        block(s, i, j+wj-.2, wi, .3, H, BRICK, front)
        profile = [(0, 0), (0, 6), (.12, 6), (.12, 13), (.25, 13), (.25, 20),
                   (.38, 20), (.38, 27), (.47, 27), (.47, 32), (.53, 32), (.53, 27),
                   (.62, 27), (.62, 20), (.75, 20), (.75, 13), (.88, 13), (.88, 6), (1, 6), (1, 0)]
        face = extrude(s, [(i+u*wi, H+z) for u, z in profile], j+wj+.18, .32, BRICK)
        # Tall, pale, pointed blind panels on the gable, clipped to its staircase.
        foot = P(s, i, j+wj+.18, H)
        def tracery(x, y):
            u = x-foot[0]
            v = foot[1]+u*.5-y
            col = int(u) % 6
            head = 29-abs(u-wi*4)*1.1-abs(col-3)*1.7
            if 1 < col < 5 and 2 < v < head:
                return PALE['hi'] if col in (2, 4) or v > head-2 else BRICK['deep']
            return stone_courses(BRICK, 3, 10)(u, v, True) or BRICK['lit']
        poly(s, face, tracery)
        for a, b in zip(face, face[1:]+face[:1]):
            seg(s, a, b, PALE['lit'])
        # Tiny copper roof rider behind the tall front gable, not a pair of invented towers.
        spire(s, i+wi/2, j+1.6, .42, H+22, 18, COPPER)
    scene.add(i+j+14, draw)


def royal_castle(scene, i, j):
    """Salmon palace court, white window surrounds, Sigismund clock tower and royal column."""
    def draw(s):
        W, D, H = 10, 6.5, 29
        block(s, i, j, W, D, 3, STONE)
        wings = [(i, j, W, 1.5), (i, j+1.4, 1.8, D-1.4),
                 (i+W-1.8, j+1.4, 1.8, D-1.4), (i, j+D-1.5, W, 1.5)]
        for a, b, wi, wj in wings:
            block(s, a, b, wi, wj, H, SALMON, windows(SALMON, H, 10, 13))
            hip_roof(s, a-.1, b-.1, wi+.2, wj+.2, H, 12, CLAY)
        for aa in (i+.1, i+W-1.1):
            block(s, aa, j+D-1.1, 1, 1, 40, SALMON, windows(SALMON, 40, 8, 13))
            band(s, aa, j+D-1.1, 1, 1, 39)
            spire(s, aa+.5, j+D-.6, .65, 41, 14, COPPER, onion=True)
        # Large rusticated gate in the centre of the square-facing western wing.
        a, b = i+3.9, j+D-1.9
        def gate(u, v, lit):
            if lit and v < 18:
                opening = arch_opening(u, v, 8.8, 3.7, 9, WOOD)
                if opening:
                    return PALE['lit'] if abs(u-8.8) > 2.8 else opening
            return windows(SALMON, 65, 9, 15)(u, v, lit)
        block(s, a, b, 2.2, 2.2, 66, SALMON, gate)
        for z in (30, 49, 64):
            band(s, a, b, 2.2, 2.2, z)
        clock(s, a+1.1, b+2.23, 56, 5)
        clock(s, a+2.23, b+1.1, 56, 5, lit=False)
        spire(s, a+1.1, b+1.1, 1.45, 68, 27, COPPER, onion=True)
        seg(s, P(s, a+1.1, b+1.1, 95), P(s, a+1.1, b+1.1, 105), GOLD['dark'])
        for n, color in enumerate((PALE['hi'], FLAG_RED)):
            poly(s, [P(s, a+1.1, b+1.1, 104-n*2), P(s, a+1.9, b+1.1, 104-n*2),
                     P(s, a+1.9, b+1.1, 102-n*2), P(s, a+1.1, b+1.1, 102-n*2)], lambda x, y, c=color: c)
        # Sigismund III west/south of the palace: granite shaft, capital, solid crowned king.
        ci, cj = i-1.7, j+D+1.2
        for r, z in ((.9, 0), (.7, 2), (.5, 4)):
            block(s, ci-r/2, cj-r/2, r, r, 2, STONE, z=z)
        cylinder(s, ci, cj, .19, .19, 6, 26, GRANITE)
        block(s, ci-.4, cj-.4, .8, .8, 3, STONE, z=32)
        figure(s, ci, cj, 35, 10, BRONZE, sword=True)
        # Raised cross held beside the crowned king, with a substantial bronze body.
        seg(s, P(s, ci-.35, cj, 38), P(s, ci-.35, cj, 49), BRONZE['dark'], 2)
        seg(s, P(s, ci-.65, cj, 46), P(s, ci, cj, 46), BRONZE['lit'])
    scene.add(i+j+21, draw)


def culture_palace(scene, i, j):
    """Limestone wedding-cake skyscraper: wings, setbacks, crenellated attic, four clocks, spire."""
    def draw(s):
        W, D = 10, 8
        block(s, i-.5, j-.5, W+1, D+1, 4, STONE)
        for a, b, wi, wj in ((i, j, 10, 3), (i, j+3, 3, 5), (i+7, j+3, 3, 5)):
            block(s, a, b, wi, wj, 26, STONE, windows(STONE, 26, 9, 17, pilasters=True), z=4)
            band(s, a, b, wi, wj, 29)
        # Connected setbacks; vertical pilasters and dressed glass stay on both wall planes.
        for a, b, wi, wj, base, height in ((i+1.7, j+1.3, 6.6, 5.4, 29, 26),
                                         (i+2.5, j+1.9, 5, 4.2, 55, 42),
                                         (i+2.9, j+2.3, 4.2, 3.4, 97, 24)):
            def elevation(u, v, lit, H=height):
                c, level = int(u) % 7, int(v) % 10
                if c in (0, 1):
                    return PALE['hi' if lit else 'mid']
                if 3 <= c <= 5 and 2 < level < 8 and v < H-3:
                    return GLASS['mid' if lit else 'dark']
                if int(v) in (0, H-2, H-1):
                    return STONE['deep' if v < H-1 else 'hi']
                return stone_courses(STONE, 5, 15)(u, v, lit)
            block(s, a, b, wi, wj, height, STONE, elevation, z=base)
            band(s, a, b, wi, wj, base+height)
        # Polish Renaissance attic: open crown above the observation terrace.
        for n in range(6):
            for a, b in ((i+2.85+n*.84, j+5.8), (i+7.12, j+2.4+n*.65)):
                block(s, a, b, .3, .3, 7, STONE, z=123)
                spire(s, a+.15, b+.15, .22, 130, 3, STONE, conical=True)
        block(s, i+3.5, j+2.7, 3, 2.8, 22, STONE,
              windows(STONE, 22, 9, 15, pilasters=True), z=125)
        clock(s, i+5, j+5.53, 137, 6)
        clock(s, i+6.53, j+4.1, 137, 6, lit=False)
        band(s, i+3.5, j+2.7, 3, 2.8, 146)
        mansard(s, i+3.5, j+2.7, 3, 2.8, 149, 8, .7, COPPER)
        spire(s, i+5, j+4.1, .72, 157, 27, COPPER)
        seg(s, P(s, i+5, j+4.1, 184), P(s, i+5, j+4.1, 196), SLATE['deep'])
        # Entrance portico, relief panels, and sculpted people on the lower cornice.
        for n in range(5):
            a = i+3.3+n*.7
            block(s, a, j+6.3, .28, 1.1, 18, PALE, z=4)
            figure(s, a+.1, j+6.8, 24, 7, STONE)
        block(s, i+3, j+6.3, 4, 1.2, 3, STONE, z=22)
        for n in range(4):
            block(s, i+2.8-n*.2, j+7.6+n*.25, 4.4+n*.4, .3, 1, PALE, z=4-n)
    scene.add(i+j+19, draw)


def chopin_monument(scene, i, j):
    """Seated Chopin under Szymanowski's windswept bronze willow, by the circular pool."""
    def draw(s):
        ci, cj = i+3.5, j+3
        cylinder(s, ci, cj+1.2, 3.2, 2.5, 0, 3, GRANITE)
        ellipse(s, ci, cj+1.2, 2.95, 2.25, 3.2,
                lambda x, y: WATER[2] if (int(x)+int(y)) % 11 == 0 else WATER[0])
        block(s, ci-1.8, cj-1.4, 3.6, 2.5, 6, GRANITE)
        # Willow is a curved solid bronze mass with a split crown and hanging tendrils.
        profile = [(1.2, 6), (1.65, 12), (1.5, 20), (1.1, 28), (.7, 33),
                   (-.2, 38), (-1.4, 41), (-2.2, 40), (-2.65, 36), (-2.4, 33),
                   (-2.15, 37), (-1.4, 38), (-.65, 35), (-.2, 30), (.2, 25),
                   (.45, 18), (.6, 11), (.35, 6)]
        extrude(s, [(ci+a, z) for a, z in profile], cj+.15, .9, BRONZE)
        for k, off in enumerate((-.1, .15, .4)):
            seg(s, P(s, ci+1+off, cj+.17, 9), P(s, ci+.65+off, cj+.17, 27), BRONZE['hi' if k == 0 else 'deep'])
        for a, b in ((-1.8, -1.9), (-1.4, -1.2), (-.9, -.7)):
            seg(s, P(s, ci+a, cj+.16, 38), P(s, ci+b, cj+.16, 31), BRONZE['dark'], 2)
        # Seated body: folded coat, bent knees, shoes, shoulders, head and swept hair.
        body = [(-1.3, 7), (-.25, 7), (-.15, 10), (-.55, 14), (-.35, 20),
                (-.7, 24), (-1.12, 23), (-1.4, 19), (-1.7, 14), (-1.65, 11)]
        extrude(s, [(ci+a, z) for a, z in body], cj+.9, .6, BRONZE)
        cylinder(s, ci-.85, cj+.57, .28, .26, 23, 5, BRONZE)
        extrude(s, [(ci-1.12, 26), (ci-1.08, 29), (ci-.62, 29.5), (ci-.52, 27)], cj+.75, .35, BRONZE)
        for off in (0, .4):
            block(s, ci-1.65+off, cj+1.1, .3, .65, 2, BRONZE, z=6)
        extrude(s, [(ci-1.35, 20), (ci-1.65, 16), (ci-.75, 14), (ci-.55, 15),
                    (ci-1.13, 17), (ci-1.04, 21)], cj+1, .25, BRONZE)
        seg(s, P(s, ci-1.3, cj+1.02, 11), P(s, ci-.6, cj+1.02, 15), BRONZE['hi'])
    scene.add(i+j+13, draw)


def palace_isle(scene, i, j):
    """Neoclassical Palace on the Isle: four-column portico, roof statues and side colonnades."""
    def draw(s):
        W, D, H = 8, 4.8, 26
        block(s, i-.5, j-.5, W+1, D+1, 4, STONE)
        block(s, i, j, W, D, H, PALE, windows(PALE, H, 10, 12, pilasters=True), z=4)
        hip_roof(s, i, j, W, D, H+4, 6, SLATE)
        # Recessed central entrance behind four free-standing Corinthian columns.
        block(s, i+2, j+D, 4, .15, 21, PALE,
              lambda u, v, lit: WOOD if lit and int(u) % 10 in range(3, 8) and v < 15 else None, z=4)
        for n in range(4):
            a = i+2.3+n*1.13
            cylinder(s, a, j+D+1, .18, .18, 4, 20, PALE,
                     lambda u, v, lit: PALE['line'] if int(u) % 3 == 0 else None)
            for z in (4, 23):
                block(s, a-.28, j+D+.72, .56, .56, 2, PALE, z=z)
        block(s, i+1.9, j+D+.65, 4.2, .7, 4, PALE, z=25)
        band(s, i, j, W, D, 30)
        block(s, i+2.9, j+1.6, 2.2, 1.6, 10, PALE,
              windows(PALE, 10, 7, 10, pilasters=True), z=35)
        hip_roof(s, i+2.8, j+1.5, 2.4, 1.8, 45, 4, SLATE)
        for aa, bb in ((i+3, j+1.7), (i+5, j+3)):
            figure(s, aa, bb, 46, 7, PALE)
        # Balustrade and the four allegorical figures over the portico.
        for n in range(9):
            block(s, i+.2+n*.94, j+D-.05, .14, .14, 4, PALE, z=31)
        seg(s, P(s, i, j+D, 35), P(s, i+W, j+D, 35), PALE['hi'])
        for n in range(4):
            figure(s, i+2.2+n*1.2, j+D+.7, 30, 8, PALE)
        for side in (-1, 1):
            a = i-2.8 if side < 0 else i+W
            block(s, a, j+1.5, 2.8, 1.4, 3, STONE)
            for n in range(3):
                block(s, a+.3+n*.95, j+2.4, .24, .24, 12, PALE, z=3)
            block(s, a-.1, j+1.7, 3, 1.1, 2, PALE, z=15)
            hip_roof(s, a-.1, j+1.7, 3, 1.1, 17, 4, SLATE)
        for n in range(3):
            block(s, i+1.7-n*.15, j+D+1.3+n*.18, 4.6+n*.3, .23, 1, STONE, z=3-n)
    scene.add(i+j+19, draw)


def wilanow(scene, i, j):
    """Yellow Baroque palace: white giant pilasters, reliefs, twin copper towers and garden stair."""
    def draw(s):
        W, D, H = 11, 5, 27
        for a, b, wi, wj in ((i, j, W, 2), (i, j+1.8, 2, 3.2), (i+W-2, j+1.8, 2, 3.2)):
            block(s, a, b, wi, wj, H, YELLOW, windows(YELLOW, H, 11, 13, pilasters=True))
            hip_roof(s, a-.1, b-.1, wi+.2, wj+.2, H, 9, CLAY)
        # Central garden pavilion, with a broad carved attic over tall dressed windows.
        a, b = i+3.2, j+1.2
        block(s, a, b, 4.6, 2.5, 33, YELLOW, windows(YELLOW, 33, 10, 16, pilasters=True))
        hip_roof(s, a-.1, b-.1, 4.8, 2.7, 33, 7, COPPER)
        band(s, a, b, 4.6, 2.5, 29)
        block(s, a+1, b+.2, 2.6, 2.2, 18, YELLOW,
              windows(YELLOW, 18, 9, 18, pilasters=True), z=34)
        band(s, a+1, b+.2, 2.6, 2.2, 51)
        for n in range(4):
            figure(s, a+1.15+n*.75, b+2.4, 53, 7, PALE)
        # Projected relief pediment and oval royal cartouche (not a flat screen-facing badge).
        extrude(s, [(a+.2, 31), (a+4.4, 31), (a+2.3, 37)], b+2.6, .22, PALE)
        cylinder(s, a+2.3, b+2.65, .38, .1, 32, 4, GOLD)
        for aa in (i+1, i+9):
            block(s, aa, j+1.9, 1.5, 1.5, 38, YELLOW,
                  windows(YELLOW, 38, 8, 15, pilasters=True))
            for z in (27, 36):
                band(s, aa, j+1.9, 1.5, 1.5, z)
            clock(s, aa+.75, j+3.43, 31, 3)
            spire(s, aa+.75, j+2.65, 1, 40, 18, COPPER, onion=True)
        for n in range(5):
            block(s, i+3.1-n*.1, j+4+n*.24, 4.8+n*.2, .25, 1, PALE, z=5-n)
        # White stucco figures and relief tablets between the windows on the ochre wings.
        for aa in (i+.4, i+2.8, i+8.1, i+10.5):
            figure(s, aa, j+2.04, 14, 7, PALE)
    scene.add(i+j+18, draw)


if __name__ == '__main__':
    plots = [('barbican', barbican, (235, 200), (110, 65)),
             ('old-town-square', old_town_square, (280, 225), (125, 70)),
             ('st-john', st_john, (220, 220), (105, 100)),
             ('royal-castle', royal_castle, (280, 245), (130, 110)),
             ('culture-palace', culture_palace, (250, 320), (120, 215)),
             ('chopin', chopin_monument, (210, 180), (100, 65)),
             ('palace-isle', palace_isle, (280, 210), (130, 70)),
             ('wilanow', wilanow, (270, 215), (120, 85))]
    for name, builder, size, origin in plots:
        print(preview([lambda s, build=builder: build(s, 3, 3)], f'warsaw-{name}',
                      size=size, origin=origin, tiles=18))
    print(preview([lambda s: townhouse(s, 2, 2, 2.5, 3, 3, 0, True),
                   lambda s: townhouse(s, 7, 2, 2.7, 3, 4, 1),
                   lambda s: townhouse(s, 7, 7, 2.4, 3, 2, 2, True)], 'warsaw-houses',
                  size=(245, 220), origin=(110, 80), tiles=17))
    import sprites
    print(preview([lambda s: s.sprite(sprites.malbork(), *P(s, 7, 7, 0))], 'poland-malbork',
                  size=(160, 160), origin=(80, 20), tiles=15))
