"""Kyiv's hilltop churches, Golden Gate and steel Motherland in true (i, j, z).

Two-source building coordinates, compass decisions and model limits: DEVELOPMENT_PLAN.md.
Run directly for isolated 4× studies, houses and the Khotyn country sprite.
"""
import math
from pathlib import Path

import iso
from iso import rgb
from landmarks_paris import P, seg, poly, facade, preview, GLASS
from landmarks_iberia import hip_roof, crenellate, stone_courses, arch_opening, palette_of, tones
from landmarks_slovakia import block, band, pediment
from landmarks_italy import cylinder, ellipse
from landmarks_slovenia import windows

WHITE = tones('#FFFCED', '#EEE9D7', '#DCD6BF', '#BAB49C', '#827D65', '#C9C2A9', '#504B38')
STONE = tones('#F4E5C5', '#D8C59F', '#BFA983', '#9A845F', '#6B593E', '#AE9874', '#493B28')
OCHRE = tones('#FFE6AA', '#EAC87D', '#D2AC60', '#B38B45', '#7D612C', '#C29A4E', '#514020')
BLUE = tones('#D5EEF0', '#A0CFDF', '#7EB8CF', '#578DA9', '#395D78', '#6FA1BA', '#2B4257')
TURQUOISE = tones('#D4EEE1', '#9FCBB9', '#7DB29D', '#548775', '#375E50', '#6D9D89', '#294536')
GREEN = tones('#AFD2A1', '#6E9E6E', '#528456', '#386440', '#26482D', '#47764C', '#1E3825')
GOLD = tones('#FFF5B6', '#EFD277', '#CDA746', '#A47D2C', '#75571D', '#BA9138', '#55401B')
BRICK = tones('#E5AA88', '#BE805C', '#A36847', '#7E4932', '#573023', '#935C3F', '#42271E')
WOOD = tones('#D6AD75', '#AE8050', '#92643D', '#6F472B', '#4B2F1C', '#835534', '#362419')
METAL = tones('#C1CCC1', '#8E9D92', '#75867C', '#53685E', '#384A42', '#66796E', '#293A32')
LEAD = tones('#C6CED1', '#919EA6', '#76858F', '#546874', '#3C4C56', '#667985', '#293A45')
CASTLE_ROOF = tones('#C4BCAF', '#91877B', '#776D64', '#574E48', '#3C3531', '#695F57', '#2D2723')
STEEL = tones('#F4F5E8', '#CFD9D7', '#ACBDBE', '#7E989D', '#516D77', '#94ADB2', '#344F5B')
ROCK = tones('#D6C8AA', '#AE9D7B', '#968560', '#756542', '#53482F', '#8B7953', '#3E3524')
WALLS = [rgb(c) for c in ('#E9D6AC', '#D7E0C8', '#E3BCAC', '#BBD0D1', '#EEDFC7', '#CBBBD1')]
IRON, DARK_GLASS = rgb('#35433E'), rgb('#30464D')
FRIEZE = rgb('#557A8A')
GROUND = {k: rgb(v) for k, v in {
    'pave': '#C7BCAA', 'square': '#E3D5B9', 'joint': '#B9A88C', 'rose': '#CFAD98',
    'cobble': '#B4AE9F', 'cobble_joint': '#948E80', 'garden': '#729452',
    'garden_hi': '#8EAA63', 'flower': '#E8D7AB', 'water': '#4E859B',
    'water_dark': '#396B87', 'water_hi': '#B9DBDB',
}.items()}


def cross(s, i, j, z, height=7):
    seg(s, P(s, i, j, z), P(s, i, j, z+height), GOLD['deep'])
    seg(s, P(s, i-.23, j, z+height*.66), P(s, i+.23, j, z+height*.66), GOLD['hi'])
    s.put(*P(s, i, j, z+height), GOLD['hi'])


def roof_mesh(s, ci, cj, radius, base, rise, material, pear=True, ribs=8, profile=None):
    """Revolved pear/spherical roof, shaded by surface normal, without horizontal striping."""
    profile = profile or ([(0, .75), (.12, .96), (.3, 1), (.5, .86), (.7, .55), (.86, .24), (1, .04)]
               if pear else [(0, 1), (.18, .99), (.4, .91), (.65, .7), (.85, .4), (1, .04)])
    faces = []
    for (t, r), (nt, nr) in zip(profile, profile[1:]):
        for n in range(32):
            a, b = n*math.tau/32, (n+1)*math.tau/32
            light = (math.sin((a+b)/2)-math.cos((a+b)/2)) / math.sqrt(2)
            key = 'hi' if light > .8 else 'lit' if light > .05 else 'mid' if light > -.6 else 'dark'
            pts = [P(s, ci+rr*radius*math.cos(ang), cj+rr*radius*math.sin(ang), base+tt*rise)
                   for tt, rr, ang in ((t, r, a), (t, r, b), (nt, nr, b), (nt, nr, a))]
            faces.append((math.cos(a)+math.sin(a)+math.cos(b)+math.sin(b), n, pts, key))
    for _, n, pts, key in sorted(faces):
        poly(s, pts, lambda x, y, key=key: material[key])
        if ribs and n % ribs == 0:
            seg(s, pts[0], pts[3], GOLD['lit'] if material == GREEN else material['hi'])


def dome(s, i, j, z, radius, drum, rise, wall=WHITE, roof=GOLD, pear=True):
    def lights(u, v, lit):
        c = int(u) % max(5, int(radius*9))
        if 2 <= c <= 4 and 2 < v < drum-2:
            return WHITE['hi' if lit else 'mid'] if c in (2, 4) else DARK_GLASS
        return wall['hi'] if lit and c == 0 else None
    cylinder(s, i, j, radius*.66, radius*.66, z, drum, wall, lights)
    cylinder(s, i, j, radius*.78, radius*.78, z+drum-1, 2, WHITE)
    roof_mesh(s, i, j, radius, z+drum+1, rise, roof, pear)
    top = z+drum+rise+1
    if roof == GREEN:
        # Kyiv's green crowns have a distinct gilded lantern and small terminal bulb.
        cylinder(s, i, j, radius*.19, radius*.19, top, 3, GOLD)
        roof_mesh(s, i, j, max(.12, radius*.23), top+3, 4, GOLD)
        top += 7
    cross(s, i, j, top, 5 if radius < .7 else 7)


def church_windows(material, height, bay=12):
    joints = stone_courses(material, 5, 11)
    def pattern(u, v, lit):
        c = u % bay
        trim = WHITE['hi' if lit else 'mid']
        if v < 2 or int(v) in (height-1, height-3) or int(c) in (0, 1):
            return trim
        # Tall recessed semicircular lights, with a frame and a central glazing bar.
        du = abs(c-bay/2)
        top = height-9+math.sqrt(max(0, 6.25-du*du))
        if du < 3.5 and 6 < v < top+1:
            if du > 2.5 or v < 8 or v > top-1: return trim
            return IRON if du < .6 or int(v) % 7 == 0 else DARK_GLASS
        return joints(u, v, lit) if material == STONE else None
    return pattern


def townhouse(scene, i, j, wi=2.7, wj=3, floors=2, seed=0, z=0):
    """Kyiv historic stucco: rusticated shops, window hoods, iron balconies, metal hips."""
    wall, height = palette_of(WALLS[seed % len(WALLS)]), floors*12+4
    base = windows(wall, height, bay=10, floor=12, hood=True, pilasters=True)
    def pattern(u, v, lit):
        c, level = int(u) % 10, int(v) % 12
        trim = WHITE['lit' if lit else 'dark']
        if v < 11:
            if c in (2, 8) or int(v) in (2, 9): return trim
            if 2 < c < 8 and 2 < v < 9:
                return WOOD['dark'] if (int(u)//10+seed) % 3 == 0 else GLASS['dark']
            if int(v) % 3 == 0: return wall['line']
        if seed % 3 != 1 and v > 12 and level in (1, 2, 3) and 1 <= c <= 8:
            if level in (1, 3) or c % 3 == 1: return IRON
        return base(u, v, lit)
    def draw(s):
        block(s, i, j, wi, wj, height, wall, pattern, z=z)
        band(s, i, j, wi, wj, z+1, STONE, 2)
        band(s, i, j, wi, wj, z+height-2, WHITE, 2)
        hip_roof(s, i-.1, j-.1, wi+.2, wj+.2, z+height+1, 9, METAL if seed % 4 else GREEN)
        if seed % 5 == 0:
            pediment(s, i+.5, j+wj-.12, wi-1, .3, z+height, 7, WHITE)
        # Projecting balcony slab below one dressed upper-floor opening.
        if seed % 4 == 1 and floors > 1:
            block(s, i+.6, j+wj, 1.2, .28, 1, STONE, z=z+15)
            for k in range(5):
                seg(s, P(s, i+.6+k*.3, j+wj+.28, z+16),
                    P(s, i+.6+k*.3, j+wj+.28, z+20), IRON)
            seg(s, P(s, i+.6, j+wj+.28, z+20), P(s, i+1.8, j+wj+.28, z+20), IRON)
        block(s, i+.35, j+.45, .35, .35, 8, BRICK, z=z+height+5)
        band(s, i+.35, j+.45, .35, .35, z+height+12, STONE)
    scene.add(i+j+wi+wj, draw)


def st_andrew(scene, i, j, z=0):
    """One central dome and four corner turrets on the high Andriivska stylobate."""
    def draw(s):
        block(s, i, j, 7, 7, 12, WHITE, church_windows(WHITE, 12), z=z)
        band(s, i, j, 7, 7, z+11, STONE, 2)
        # Cross plan: narrow nave and transept, paired columns at the four corners.
        block(s, i+1.7, j+.4, 3.6, 6.2, 35, TURQUOISE, church_windows(TURQUOISE, 35), z=z+12)
        block(s, i+.5, j+1.9, 6, 3.2, 35, TURQUOISE, church_windows(TURQUOISE, 35), z=z+12)
        band(s, i+.5, j+1.9, 6, 3.2, z+45, WHITE, 3)
        hip_roof(s, i+.4, j+1.8, 6.2, 3.4, z+48, 7, GREEN)
        # Turrets occupy all four diagonal buttress positions, not five subsidiary domes.
        towers = [(1.25, 1.25), (5.75, 1.25), (1.25, 5.75), (5.75, 5.75)]
        for a, b in sorted(towers, key=lambda p: sum(p)):
            block(s, i+a-.48, j+b-.48, .96, .96, 39, TURQUOISE,
                  church_windows(TURQUOISE, 39, 8), z=z+12)
            for di, dj in ((-.55, .5), (.55, .5), (.5, -.55)):
                cylinder(s, i+a+di, j+b+dj, .095, .095, z+18, 31, WHITE)
                cylinder(s, i+a+di, j+b+dj, .17, .17, z+46, 3, GOLD)
            band(s, i+a-.55, j+b-.55, 1.1, 1.1, z+50, WHITE, 2)
            dome(s, i+a, j+b, z+52, .66, 6, 15, TURQUOISE, GREEN)
        # Main spherical green dome, gilded radial ribs, eight arched drum lights.
        dome(s, i+3.5, j+3.5, z+49, 1.8, 18, 22, TURQUOISE, GREEN, pear=False)
        # West entrance explicitly snapped SW; the broad stair is part of the raised terrace.
        for a in (2, 2.5, 4.5, 5):
            cylinder(s, i+a, j+6.68, .12, .12, z+15, 28, WHITE)
            cylinder(s, i+a, j+6.68, .2, .2, z+41, 3, GOLD)
        pediment(s, i+1.7, j+6.5, 3.6, .3, z+44, 8, WHITE)
        facade(s, i+2.9, j+6.62, 1.2, .14, 17,
               lambda u, v, lit: WOOD['dark'] if 1 < u < 8 and v < 15 else WHITE['hi'],
               WHITE, z0=z+12)
        # Gilt-framed circular front light and its divided glazing, on the SW plane only.
        ring = [P(s, i+3.5+.48*math.cos(n*math.tau/32), j+6.8,
                  z+38+3.8*math.sin(n*math.tau/32)) for n in range(32)]
        poly(s, ring, lambda x, y: DARK_GLASS)
        for a, b in zip(ring, ring[1:]+ring[:1]):seg(s, a, b, GOLD['lit'])
        seg(s, P(s, i+3.5, j+6.81, z+34.5), P(s, i+3.5, j+6.81, z+41.5), WHITE['lit'])
        seg(s, P(s, i+3.1, j+6.81, z+38), P(s, i+3.9, j+6.81, z+38), WHITE['lit'])
        for k in range(6):
            block(s, i+1.7, j+7+k*.28, 3.6, .32, 12-k*2, STONE, z=z)
    scene.add(i+j+16, draw)


def st_sophia(scene, i, j, z=0):
    """Broad Baroque cathedral: stepped galleries, nineteen unequal roof cupolas, east apses."""
    def draw(s):
        # Eastern apses are on the hidden NE rear, not spurious southern entrance towers.
        for a in (3, 5.7, 8.4):
            cylinder(s, i+a, j+.65, .9, 1.2, z, 24, WHITE, church_windows(WHITE, 24))
            roof_mesh(s, i+a, j+.65, 1, z+24, 9, GREEN, pear=False)
        block(s, i+.6, j+.9, 10.8, 8.9, 26, WHITE, church_windows(WHITE, 26), z=z)
        hip_roof(s, i+.5, j+.8, 11, 9.1, z+27, 10, GREEN)
        block(s, i+2.5, j+2.3, 7, 6, 36, WHITE, church_windows(WHITE, 36), z=z)
        hip_roof(s, i+2.4, j+2.2, 7.2, 6.2, z+37, 10, GREEN)
        # A medieval 1+4+8 core, plus six lower Baroque gallery crowns.
        crowns = [(6, 5.1, 48, 1.35, 13, 20, GOLD)]
        crowns += [(a, b, 39, .96, 10, 16, GREEN)
                   for a, b in ((3.5, 5.1), (8.5, 5.1), (6, 2.6), (6, 7.6))]
        crowns += [(a, b, 33, .68, 8, 13, GREEN)
                   for a, b in ((3.5, 2.6), (8.5, 2.6), (3.5, 7.6), (8.5, 7.6),
                                (1.4, 4.3), (10.6, 4.3), (4.5, 9), (7.5, 9))]
        crowns += [(a, b, 27, .5, 7, 10, GREEN)
                   for a, b in ((1.5, 1.8), (10.5, 1.8), (1.4, 7), (10.6, 7), (2, 9.2), (10, 9.2))]
        assert len(crowns) == 19
        for a, b, base, r, drum, rise, roof in sorted(crowns, key=lambda p: p[0]+p[1]):
            dome(s, i+a, j+b, z+base, r, drum, rise, WHITE, roof)
        # The SW nave front: shaped gables, paired pilasters, arched portal and stone steps.
        for a, width, rise in ((.6, 3, 9), (4, 4, 13), (8.4, 3, 9)):
            pediment(s, i+a, j+9.65, width, .23, z+27, rise, WHITE)
            ci = i+a+width/2
            for da in (-.72, .72):
                cylinder(s, ci+da, j+9.88, .11, .11, z+3, 23, WHITE)
            poly(s, [P(s, ci+u, j+9.9, z+v) for u, v in
                     ((-.36, 1), (.36, 1), (.36, 15), (0, 19), (-.36, 15))],
                 lambda x, y: WOOD['deep'])
        band(s, i+.6, j+.9, 10.8, 8.9, z+2, STONE, 2)
        for k in range(3):block(s, i+3.5, j+10+k*.3, 5, .35, 3-k, STONE, z=z)
    scene.add(i+j+23, draw)


def st_michael(scene, i, j, z=0):
    """Blue/white reconstructed cathedral, seven gold pear domes and Baroque scroll front."""
    def draw(s):
        for a in (3.3, 5.4, 7.5):
            cylinder(s, i+a, j+.8, .8, 1.1, z, 25, BLUE, church_windows(BLUE, 25))
        block(s, i+1, j+1, 8.8, 7.3, 32, BLUE, church_windows(BLUE, 32), z=z)
        band(s, i+1, j+1, 8.8, 7.3, z+29, WHITE, 3)
        hip_roof(s, i+.9, j+.9, 9, 7.5, z+33, 11, LEAD)
        block(s, i+3.2, j+2.8, 4.4, 3.6, 44, BLUE, church_windows(BLUE, 44), z=z)
        hip_roof(s, i+3.1, j+2.7, 4.6, 3.8, z+45, 8, LEAD)
        crowns = [(5.4, 4.6, 53, 1.25, 13, 21), (2.4, 2.1, 38, .8, 9, 16),
                  (8.4, 2.1, 38, .8, 9, 16), (2.4, 6.9, 36, .8, 10, 17),
                  (8.4, 6.9, 36, .8, 10, 17), (5.4, 1.6, 40, .75, 9, 16),
                  (5.4, 7.7, 42, .8, 10, 17)]
        for a, b, base, r, drum, rise in sorted(crowns, key=lambda p: p[0]+p[1]):
            dome(s, i+a, j+b, z+base, r, drum, rise, BLUE)
        # Three shaped front bays; the high central gable receives a blue oval icon panel.
        for a, width, rise in ((1, 2.8, 8), (3.8, 3.2, 13), (7, 2.8, 8)):
            pediment(s, i+a, j+8.15, width, .3, z+32, rise, BLUE)
            for da in (.15, width-.15):
                cylinder(s, i+a+da, j+8.5, .12, .12, z+3, 30, WHITE)
            c = i+a+width/2
            poly(s, [P(s, c+u, j+8.52, z+v) for u, v in
                     ((-.4, 2), (.4, 2), (.4, 17), (0, 21), (-.4, 17))],
                 lambda x, y: GOLD['dark'] if (x+y) % 5 == 0 else WOOD['deep'])
            # Curled gable shoulders, each projected on its own facade.
            for sign in (-1, 1):
                last = None
                for n in range(17):
                    angle = n*math.tau/16
                    p = P(s, c+sign*(width*.39+.17*math.cos(angle)), j+8.5,
                          z+34+rise*.25+2*math.sin(angle))
                    if last:seg(s, last, p, WHITE['hi'])
                    last = p
        band(s, i+1, j+1, 8.8, 7.3, z+2, STONE, 2)
    scene.add(i+j+22, draw)


def golden_gate(scene, i, j, z=0):
    """Present reconstructed gate: masonry tunnel, timber galleries, roof church and gold dome."""
    def draw(s):
        joints = stone_courses(STONE, 4, 9)
        def gate(u, v, lit):
            if lit:
                hole = arch_opening(u, v, 24, 10, 18, WOOD['deep'])
                if hole and v < 32:return hole
                # Voussoirs follow the semicircular opening, rather than leaking across a side.
                if 30 < v < 35 and abs(u-24) < 13:return STONE['hi']
            if int(v) % 9 in (0, 1):return BRICK['lit' if lit else 'dark']
            return joints(u, v, lit)
        block(s, i, j, 6, 7, 37, STONE, gate, z=z)
        # Massive timber log gallery below a covered defensive walkway.
        def timber(u, v, lit):
            if int(v) % 3 == 0:return WOOD['deep']
            if 4 < v < 12 and int(u) % 8 in (3, 4):return WOOD['deep']
            return WOOD['lit' if lit else 'dark']
        block(s, i-.2, j-.2, 6.4, 7.4, 16, WOOD, timber, z=z+37)
        hip_roof(s, i-.4, j-.4, 6.8, 7.8, z+54, 10, WOOD)
        # The famous brick gate screen rises above the passage, masking the timber
        # gallery's end. The thick return remains a real 3D wall, not a flat decal.
        def brick_gate(u, v, lit):
            hole = arch_opening(u, v, 24, 10, 22, WOOD['deep']) if lit else None
            if hole and v < 35:return hole
            return stone_courses(BRICK, 3, 10)(u, v, lit)
        cover = block(s, i, j+6.8, 6, .35, 59, BRICK, brick_gate, z=z)
        crenellate(s, i, j+6.8, 6, .35, z+59, BRICK, cover, step=7, height=3)
        # White/brick Annunciation church above the tunnel, not a castle keep.
        block(s, i+1.7, j+1.6, 2.6, 3.6, 23, WHITE, church_windows(WHITE, 23, 9), z=z+59)
        for a in (1.7, 4.1):
            block(s, i+a, j+5.08, .2, .18, 23, BRICK, z=z+59)
        band(s, i+1.7, j+1.6, 2.6, 3.6, z+80, WHITE, 2)
        hip_roof(s, i+1.6, j+1.5, 2.8, 3.8, z+83, 6, GREEN)
        # Reconstructed chapel's three scalloped brick gables facing the gate approach.
        pts = [P(s, i+1.7, j+5.3, z+77), P(s, i+4.3, j+5.3, z+77)]
        pts += [P(s, i+4.3-2.6*k/48, j+5.3,
                  z+83+5*abs(math.sin(k/48*3*math.pi))) for k in range(49)]
        poly(s, pts, lambda x, y: BRICK['line'] if int(y) % 3 == 0 else BRICK['lit'])
        for a, b in zip(pts[2:], pts[3:]):seg(s, a, b, BRICK['hi'])
        dome(s, i+3, j+3.2, z+87, .82, 8, 17)
        # Framed heavy doors, iron studs and a dark recess remain within the passage.
        for a in (1.85, 4.15):
            seg(s, P(s, i+a, j+7.02, z+1), P(s, i+a, j+7.02, z+18), WOOD['lit'], 2)
        for k in range(4):
            seg(s, P(s, i+1.9, j+7.03, z+3+k*4), P(s, i+4.1, j+7.03, z+3+k*4), WOOD['dark'])
    scene.add(i+j+14, draw)


def lavra_belltower(scene, i, j, z=0):
    """Four shrinking octagonal tiers, colonnades, open bells, clocks and one gilded crown."""
    from landmarks_bosnia import cylinder as octagonal

    ci, cj = i+2.5, j+2.5
    def draw(s):
        octagonal(s, ci, cj, 2.4, 2.4, z, 4, STONE, segments=8)
        stages = [(2.18, 4, 27), (1.88, 31, 32), (1.5, 63, 30), (1.14, 93, 25)]
        for rank, (r, base, height) in enumerate(stages):
            def pattern(u, v, lit, rank=rank, height=height):
                c = u % 12
                if v < 2 or v > height-3:return WHITE['hi' if lit else 'mid']
                if 3 < c < 9 and 5 < v < height-5+math.sqrt(max(0, 9-(c-6)**2)):
                    return WHITE['lit' if lit else 'dark'] if c < 4.5 or c > 7.5 else DARK_GLASS
                return OCHRE['line'] if rank == 0 and int(v) % 5 == 0 else None
            octagonal(s, ci, cj, r, r, z+base, height, OCHRE, pattern, segments=8)
            # Actual octagonal structure; columns arranged radially in paired/single groups.
            for n in range(8):
                for shift in ((-.12, .12) if rank in (1, 2) else (0,)):
                    a = (n+.5)*math.tau/8+shift
                    x, y = ci+(r+.02)*math.cos(a), cj+(r+.02)*math.sin(a)
                    cylinder(s, x, y, .10, .10, z+base+3, height-6, WHITE)
                    cylinder(s, x, y, .17, .17, z+base+height-5, 2, GOLD if rank > 0 else WHITE)
            octagonal(s, ci, cj, r+.17, r+.17, z+base+height-2, 3, WHITE, segments=8)
            octagonal(s, ci, cj, r+.14, r+.14, z+base+height-1, 1, WHITE,
                      lambda u, v, lit: FRIEZE if int(u) % 3 else WHITE['hi'], segments=8)
        # Dark clock dial on each visible fourth-tier facet (one radial tower, no handed pair).
        for a in (math.pi/4, math.pi*3/4):
            x, y = ci+1.17*math.cos(a), cj+1.17*math.sin(a)
            px, py = P(s, x, y, z+106)
            for dx in range(-3, 4):
                for dy in range(-3, 4):
                    if dx*dx+dy*dy <= 9:s.put(px+dx, py+dy, GOLD['hi'] if dx*dx+dy*dy > 5 else IRON)
            seg(s, (px, py), (px, py-2), WHITE['hi'])
            seg(s, (px, py), (px+2, py+1), WHITE['hi'])
        roof_mesh(s, ci, cj, 1.4, z+121, 19, GOLD,
                  profile=[(0, 1), (.1, 1.04), (.32, .92), (.6, .59), (.8, .32), (1, .18)])
        octagonal(s, ci, cj, .3, .3, z+140, 5, OCHRE,
                  lambda u, v, lit: DARK_GLASS if int(u) % 3 == 1 else GOLD['lit'], segments=8)
        roof_mesh(s, ci, cj, .35, z+146, 4, GOLD)
        cross(s, ci, cj, z+150, 8)
    scene.add(i+j+11, draw)


def sculpture_prism(s, i, j, z, profile, depth, material=STEEL):
    """Extrude an articulated profile in the i/z plane through j: solid steel, not a cut-out."""
    back = [P(s, i+a, j, z+h) for a, h in profile]
    front = [P(s, i+a, j+depth, z+h) for a, h in profile]
    poly(s, back, lambda x, y: material['dark'])
    for n in range(len(profile)):
        k = (n+1) % len(profile)
        poly(s, [back[n], back[k], front[k], front[n]],
             lambda x, y: material['mid'] if (x+y) % 9 else material['deep'])
    poly(s, front, lambda x, y: material['lit'])
    for a, b in zip(front, front[1:]+front[:1]):seg(s, a, b, material['hi'])


def motherland(scene, i, j, z=0):
    """Draped steel figure: right-hand sword, left-hand shield with the post-2023 tryzub.

    The real east-facing figure is explicitly turned locally to SW; the city stays north-up.
    """
    ci, cj = i+3, j+3
    def draw(s):
        cylinder(s, ci, cj, 3.1, 2.8, z, 9, STONE, stone_courses(STONE, 3, 9))
        cylinder(s, ci, cj, 2.5, 2.3, z+9, 20, STEEL,
                 lambda u, v, lit: STEEL['line'] if int(u) % 7 == 0 else None)
        cylinder(s, ci, cj, 1.6, 1.5, z+29, 25, STEEL,
                 lambda u, v, lit: STEEL['line'] if int(u) % 8 == 0 else None)
        # Keep the high museum/pedestal substantial relative to the 62 m sculpture.
        figure_z = z+20
        # Drapery is a faceted, tapered mesh with a solid cross-section at each height.
        sections = [(34, 1.05, .74), (44, .93, .66), (61, .68, .49),
                    (73, .56, .43), (80, .83, .42), (85, .75, .35)]
        faces = []
        for (base, ri, rj), (top, ti, tj) in zip(sections, sections[1:]):
            for n in range(16):
                a, b = n*math.tau/16, (n+1)*math.tau/16
                pts = [P(s, ci+ir*math.cos(t), cj+jr*math.sin(t), figure_z+h)
                       for ir, jr, h, t in ((ri, rj, base, a), (ri, rj, base, b),
                                             (ti, tj, top, b), (ti, tj, top, a))]
                key = 'lit' if math.sin((a+b)/2)-math.cos((a+b)/2) > 0 else 'dark'
                faces.append((math.cos(a)+math.sin(a), n, pts, key))
        for _, n, pts, key in sorted(faces):
            poly(s, pts, lambda x, y, key=key: STEEL[key])
            if n % 2 == 0:seg(s, pts[0], pts[3], STEEL['hi' if key == 'lit' else 'line'])
        # Left/right arms have elbow bends and substantial sleeve widths, not thin lines.
        sculpture_prism(s, ci, cj+.02, figure_z,
                        [(-.58, 78), (-1, 81), (-1.8, 94), (-2.25, 108),
                         (-1.85, 110), (-1.35, 96), (-.35, 84)], .5)
        sculpture_prism(s, ci, cj+.02, figure_z,
                        [(.35, 79), (1, 80), (1.7, 94), (2.05, 108),
                         (1.64, 109), (1.2, 96), (.25, 85)], .5)
        cylinder(s, ci, cj+.05, .22, .23, figure_z+85, 5, STEEL)
        cylinder(s, ci, cj+.05, .38, .33, figure_z+90, 10, STEEL)
        ellipse(s, ci, cj+.05, .38, .33, figure_z+100, STEEL['dark'])
        # Hair, brow, nose, chin and neck; visible side planes share the body lighting.
        sculpture_prism(s, ci-.25, cj+.32, figure_z+93,
                        [(0, 0), (.5, 0), (.5, 5), (.35, 7), (.12, 7), (0, 5)], .12)
        seg(s, P(s, ci-.15, cj+.5, figure_z+96), P(s, ci+.2, cj+.5, figure_z+96), STEEL['deep'])
        block(s, ci-.06, cj+.49, .13, .12, 2, STEEL, z=figure_z+94)
        # Right hand (NW/viewer-left after turn) grips a broad double-faced blade.
        block(s, ci-2.18, cj+.15, .35, .4, 5, STEEL, z=figure_z+107)
        sculpture_prism(s, ci-2, cj+.32, figure_z,
                        [(-.15, 111), (.15, 111), (.15, 139), (0, 144), (-.15, 139)], .14)
        block(s, ci-2.5, cj+.15, 1, .3, 2, STEEL, z=figure_z+113)
        # Left hand supports a thick rectangular shield; trident is drawn on that shield alone.
        sculpture_prism(s, ci+1.7, cj+.4, figure_z,
                        [(-.68, 104), (.68, 104), (.68, 126), (-.68, 126)], .22)
        def mark(u, h):return P(s, ci+1.7+u, cj+.64, figure_z+h)
        for a, b in (((0, 108), (0, 122)), ((-.43, 119), (-.43, 111)),
                     ((.43, 119), (.43, 111)), ((-.43, 111), (0, 108)),
                     ((.43, 111), (0, 108)), ((-.43, 111), (.43, 111)),
                     ((-.43, 119), (-.18, 115)), ((.43, 119), (.18, 115))):
            seg(s, mark(*a), mark(*b), STEEL['deep'])
    scene.add(i+j+15, draw)


def main():
    for name, builder, _, _, _, z in SITES:
        print(preview([lambda s, b=builder, z=z: b(s, 4, 4, z=z)], 'kyiv-'+name,
                      size=(290, 300), origin=(145, 145), tiles=24))
    print(preview([lambda s: townhouse(s, 4, 4, seed=0),
                   lambda s: townhouse(s, 9, 4, floors=3, seed=1),
                   lambda s: townhouse(s, 8, 10, floors=1, seed=5)], 'kyiv-houses',
                  size=(240, 195), origin=(110, 50), tiles=20))
    import sprites
    if 'khotyn' in sprites.ICONS:
        im = sprites.khotyn()
        path = Path(__file__).resolve().parents[2] / 'docs/art/capitals/ukraine-khotyn.png'
        im.resize((im.width*4, im.height*4), 0).save(path)
        print(path)


# (name, builder, footprint, real (longitude, latitude), scene anchor, elevation)
SITES = [
    ('st-andrew', st_andrew, (7, 8.7), (30.51806, 50.45889), (300, 165), 26),
    ('st-sophia', st_sophia, (12, 11), (30.5144, 50.4528), (225, 300), 18),
    ('st-michael', st_michael, (10.8, 9), (30.5228167, 50.4557845), (420, 225), 18),
    ('golden-gate', golden_gate, (6.8, 7.8), (30.51333, 50.44889), (85, 350), 12),
    ('lavra-belltower', lavra_belltower, (5, 5), (30.556455, 50.434691), (510, 390), 24),
    ('motherland', motherland, (6, 6), (30.563187, 50.426521), (590, 480), 24),
]


if __name__ == '__main__':
    main()
