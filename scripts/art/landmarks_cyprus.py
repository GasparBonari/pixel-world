"""Nicosia's limestone landmarks and shuttered townhouses, projected from (i, j, z)."""
import math

import iso
from iso import rgb, h01
from landmarks_iberia import arch_opening, hip_roof, palette_of, stone_courses, tones
from landmarks_italy import cylinder
from landmarks_paris import GLASS, P, corners, poly, preview, seg
from landmarks_slovakia import band, block, pediment
from landmarks_slovenia import DOME, revolve, slab

STONE = tones('#F3DEB7', '#DFC49B', '#C7AA7C', '#AA8D66', '#786046', '#B39873', '#51412F')
MARBLE = tones('#FFF8E9', '#F0E6D3', '#D7CCB6', '#B9AE9B', '#807462', '#C4B79F', '#544B40')
CLAY = tones('#EAA27A', '#BE7658', '#AB654C', '#8D503B', '#65382F', '#975743', '#512E26')
LEAD = tones('#AFB9B3', '#8A9996', '#788984', '#5B6C68', '#3C4B46', '#687973', '#35443F')
EARTH = tones('#ABBD7D', '#92A66A', '#879660', '#6E7B51', '#515C3B', '#778553', '#4E5836')
WHITE = tones('#FFFEF2', '#EEECE0', '#DEDED3', '#B1B9B3', '#78877E', '#C5CEC4', '#505E55')
PAVING = tones('#EBDFCB', '#DACBB3', '#D2C2AA', '#B0A089', '#877A68', '#BDAF98', '#554D42')
WOOD = rgb('#604837')
IRON = rgb('#344841')
SHUTTERS = [rgb(c) for c in ('#507164', '#54707A', '#867556', '#456354')]
WALLS = [rgb(c) for c in ('#E6D1A5', '#E5BD91', '#E5CCBC', '#EFE1C1', '#C8CDB1', '#D8B588')]


def dressed_arch(u, v, center, half, spring, material, lit, recess, pointed=False):
    """Stone voussoirs around a recessed doorway or lancet; v rises from its threshold."""
    du = abs(u-center)
    if v < 0 or du > half+1.6:
        return None
    cap = (half+1.6-du)*1.65 if pointed else math.sqrt(max(0, (half+1.6)**2-du**2))
    if v > spring+cap:
        return None
    inside = (du <= half and v < spring+(half-du)*1.65) if pointed else (
        arch_opening(u, v, center, half, spring, True))
    if inside:
        return recess
    if v >= spring and int(math.atan2(v-spring, u-center)*3.5) % 3 == 0:
        return material['line']
    return material['hi' if lit else 'mid']


def townhouse(scene, i, j, floors=2, seed=0):
    """Shuttered old-town terraces with timber bays, stone surrounds and clay roofs."""
    w, d, height = 3.25, 3.45, 11*floors+2
    plaster = palette_of(WALLS[seed % len(WALLS)])
    shutter = SHUTTERS[(seed//7) % len(SHUTTERS)]

    def front(u, v, lit):
        x, y = int(u), int(v)
        c, level = x % 9, y % 11
        trim = STONE['hi' if lit else 'mid']
        if y < 2 or y >= height-2 or x in (0, 1, 24, 25):
            return trim if y % 4 else STONE['line']
        if v < 10:
            if c == 8:
                return trim
            if (lit or x < 10) and 1 <= c <= 6 and 2 <= y <= 8-abs(c-3)*.4:
                return trim if c == 1 or y == 8 else WOOD if x < 9 else GLASS['frame']
            return None
        if 1 <= c <= 7 and 2 <= level <= 8:
            if c in (1, 7) or level in (2, 8):
                return trim
            if c in (2, 6):
                return shutter if y % 2 else IRON
            if c == 4:
                return GLASS['frame']
            return GLASS['lit' if level > 6 and lit else 'dark']
        return None

    def draw(s):
        block(s, i, j, w, d, height, plaster, front)
        band(s, i, j, w, d, height-1, STONE)
        hip_roof(s, i-.09, j-.09, w+.18, d+.18, height, 7, CLAY)
        block(s, i+2.1, j+1.1, .43, .5, 5, STONE, z=height+4)
        band(s, i+2.1, j+1.1, .43, .5, height+9, CLAY, 1.5)
        if seed % 4 == 0:
            # Timber oriel supported by two brackets on the lit wall.
            a, b = i+.94, j+d-.05
            block(s, a, b, 1.28, .34, 9, palette_of(shutter), front, z=12)
            hip_roof(s, a-.08, b-.08, 1.44, .5, 21, 3, CLAY)
            for x in (a+.17, a+1.12):
                seg(s, P(s, x, b+.34, 12), P(s, x, b, 8), WOOD)
        elif seed % 3 == 0:
            a, b = i+1.05, j+d
            band(s, a, b, 1.1, .35, 11, STONE, 1.3)
            for step in range(5):
                x = a+.24*step
                seg(s, P(s, x, b+.33, 12), P(s, x, b+.33, 16), IRON)
            seg(s, P(s, a, b+.33, 16), P(s, a+1.1, b+.33, 16), IRON)

    scene.add(i+j+w+d, draw)


def paphos_gate(scene, i, j):
    """Low, un-towered western opening through a battered Venetian rampart."""
    w, d = 7.5, 5.8
    courses = stone_courses(STONE, 4, 11)

    def draw(s):
        bottom = [(i, j), (i+w, j), (i+w, j+4.75), (i+w-2.1, j+5.15),
                  (i+1.2, j+5.45), (i, j+4.5)]
        top = [(a+.25*(i+w/2-a)/w, b+.8*(j+d/2-b)/d) for a, b in bottom]
        # The escarp slopes inward to its grass-covered crown.
        for n in (1, 2, 3, 4):
            a, b = bottom[n], bottom[n+1]
            pts = [P(s, *a), P(s, *b), P(s, *top[n+1], 21), P(s, *top[n], 21)]
            def ashlar(x, y, a=pts[0], b=pts[1]):
                v = a[1]+(x-a[0])*(b[1]-a[1])/max(1, b[0]-a[0])-y if b[0] > a[0] else (
                    b[1]+(x-b[0])*(a[1]-b[1])/max(1, a[0]-b[0])-y)
                return courses(x, v, n != 1) or STONE['lit' if n != 1 else 'dark']
            poly(s, pts, ashlar)
            seg(s, pts[2], pts[3], STONE['mid' if n == 1 else 'hi'])
        poly(s, [P(s, *p, 21) for p in top],
             lambda x, y: EARTH['hi' if h01(x, y, 284) < .12 else 'mid'])
        def entrance(u, v, lit):
            if lit:
                return dressed_arch(u, v, 13.6, 7.1, 8, STONE, lit, STONE['outline']) or courses(u, v, lit)
            return courses(u, v, lit)
        block(s, i+1.9, j+4.2, 3.4, 1.35, 18, STONE, entrance)
        band(s, i+1.9, j+4.2, 3.4, 1.35, 18, STONE)

    scene.add(i+j+w+d, draw)


def famagusta_gate(scene, i, j):
    """The eastern gate's west-facing inner portal, recessed between its long earthen shoulders."""
    w, d = 10, 6.1
    courses = stone_courses(STONE, 5, 13)

    def draw(s):
        for a, width, tip in ((i, 3.2, .9), (i+6.8, 3.2, -1.05)):
            base = [(a, j), (a+width, j), (a+width, j+4.4), (a+width/2+tip, j+d), (a, j+4.4)]
            slab(s, base, 0, 25, STONE, courses)
            inner = [(x+(a+width/2-x)*.08, y+(j+2-y)*.08) for x, y in base]
            poly(s, [P(s, *p, 25) for p in inner],
                 lambda x, y: EARTH['hi' if h01(x, y, 380) < .12 else 'mid'])
            for k in range(2, 5):
                seg(s, P(s, *base[k-1], 25), P(s, *base[k], 25), STONE['hi'])
        def portal(u, v, lit):
            if not lit:
                return courses(u, v, lit)
            arch = dressed_arch(u, v, 15.2, 6.8, 11, STONE, lit, STONE['outline'])
            if arch:
                return arch
            if 17 < v < 23 and (3 < u < 7 or 23 < u < 27):
                return STONE['deep'] if (u+v) % 4 else STONE['hi']
            if 10 < v < 12:
                return STONE['hi']
            return courses(u, v, lit)
        block(s, i+3.1, j+2.2, 3.8, 2.75, 25, STONE, portal)
        band(s, i+3.1, j+2.2, 3.8, 2.75, 24, STONE, 2)
        pediment(s, i+3.06, j+4.23, 3.88, .79, 26, 6, STONE)

    scene.add(i+j+w+d, draw)


def cyprus_museum(scene, i, j):
    """The old archaeological museum: low ochre wings and a white four-column temple portico."""
    w, d = 10.7, 5.8

    def ashlar(u, v, lit):
        c = int(u) % 14
        if 4 <= c <= 10 and 7 < v < 20:
            if c in (4, 10) or int(v) in (8, 19):
                return MARBLE['lit' if lit else 'dark']
            return GLASS['frame'] if c == 7 or int(v) == 14 else GLASS['dark']
        return stone_courses(STONE, 5, 13)(u, v, lit)

    def draw(s):
        block(s, i, j, w, 4.3, 27, STONE, ashlar)
        band(s, i, j, w, 4.3, 2, STONE, 2)
        band(s, i, j, w, 4.3, 26, MARBLE, 2)
        hip_roof(s, i-.12, j-.1, w+.24, 4.5, 28, 8, CLAY)
        a, b, span = i+3.45, j+4.2, 3.8
        for step in range(3):
            block(s, a-step*.12, b, span+step*.24, 1+step*.35, 3-step, MARBLE, z=(2-step))
        block(s, a+.95, b-.08, 1.9, .23, 21, STONE,
              lambda u, v, lit: WOOD if lit and 3 < u < 12 and 4 < v < 16 else None)
        for k in range(4):
            x = a+.36+k*(span-.72)/3
            cylinder(s, x, b+1.14, .23, .23, 4, 1.4, MARBLE)
            cylinder(s, x, b+1.14, .16, .16, 5.4, 20.5, MARBLE,
                     lambda u, v, lit: MARBLE['hi' if lit else 'deep'] if int(u) % 3 == 0 else None)
            block(s, x-.25, b+.89, .5, .5, 1.4, MARBLE, z=25.9)
        block(s, a-.04, b, span+.08, 1.41, 3.6, MARBLE, z=27)
        pediment(s, a-.12, b, span+.24, 1.49, 31, 8, MARBLE)

    scene.add(i+j+w+d, draw)


def selimiye(scene, i, j):
    """Gothic St Sophia nave with three western portals and two minarets on the west turrets."""
    w, d = 7.6, 12
    h = 42
    courses = stone_courses(STONE, 5, 13)

    def nave(u, v, lit):
        c = u % 15
        arch = dressed_arch(c, v-10, 8, 3.1, 11, MARBLE, lit, GLASS['frame'], pointed=True)
        if arch:
            return MARBLE['mid'] if 7 < c < 8 and 13 < v < 24 else arch
        return courses(u, v, lit)

    def turret(s, x, y):
        block(s, x-.8, y-.8, 1.6, 1.6, 49, STONE, nave)
        band(s, x-.8, y-.8, 1.6, 1.6, 48, MARBLE, 2)
        cylinder(s, x, y, .58, .58, 50, 33, STONE, courses)
        for z, radius, height in ((81, .72, 2), (83, .88, 2), (85, .8, 2), (87, .43, 11), (98, .56, 2)):
            cylinder(s, x, y, radius, radius, z, height, MARBLE, courses)
        revolve(s, x, y, .52, 100, 12, [(0, 1), (.18, .87), (1, .025)], LEAD, segments=16)
        seg(s, P(s, x, y, 112), P(s, x, y, 115), STONE['mid'])

    def draw(s):
        # Eastern polygonal apse, then clerestory and side aisle.
        apse = [(i+1, j+2.2), (i+1.6, j+.68), (i+3.1, j), (i+4.8, j+.6),
                (i+5.7, j+2.2)]
        slab(s, apse, 0, 32, STONE, nave)
        block(s, i+.86, j+1.8, 4.92, d-3.1, h, STONE, nave)
        for a, b in ((i+.8, j+1.8), (i+5.77, j+1.8)):
            block(s, a, b, .21, d-3.1, 3, STONE, z=h)
        block(s, i+5.76, j+2, 1.45, d-3.5, 23, STONE, nave)
        for yy in (j+2.85, j+4.65, j+6.45, j+8.25):
            # An open flying buttress: outer pier and a short, rising stone strut.
            block(s, i+7.12, yy-.22, .47, .46, 24, STONE, courses)
            quad = [(i+5.67, yy-.2, 34), (i+7.46, yy-.2, 23),
                    (i+7.46, yy-.2, 27), (i+5.67, yy-.2, 38),
                    (i+5.67, yy+.2, 34), (i+7.46, yy+.2, 23),
                    (i+7.46, yy+.2, 27), (i+5.67, yy+.2, 38)]
            pts = [P(s, *p) for p in quad]
            for face, tone in (((3, 2, 6, 7), 'hi'), ((4, 5, 6, 7), 'mid')):
                poly(s, [pts[k] for k in face], lambda x, y, tone=tone: STONE[tone])
            seg(s, pts[4], pts[5], STONE['deep'])
        turret(s, i+1, j+d-1.13)
        def west(u, v, lit):
            if lit:
                for center in (7.7, 20, 32.3):
                    opening = dressed_arch(u, v, center, 4.2 if center == 20 else 3.3, 13,
                                           MARBLE, lit, WOOD, pointed=True)
                    if opening:
                        return opening
                if 26 < v < 38 and abs(u-20) < 7-(v-26)*.4:
                    return GLASS['frame'] if int(u) % 3 else MARBLE['hi']
            return courses(u, v, lit)
        block(s, i+1.55, j+d-2.05, 5, 1.78, 39, STONE, west)
        band(s, i+1.55, j+d-2.04, 5, 1.8, 38, MARBLE, 2)
        turret(s, i+6.58, j+d-1.13)

    scene.add(i+j+w+d, draw)


def buyuk_han(scene, i, j):
    """Four connected ranges around a court with two arcaded floors and an octagonal mescit."""
    w, d = 10.8, 10.2
    courses = stone_courses(STONE, 4, 12)

    def exterior(u, v, lit):
        c = u % 11
        if 16 < v < 21 and 4 < c < 7:
            return STONE['outline']
        return courses(u, v, lit)

    def gallery(s, axis, start, fixed, count, z):
        # Portico walls with the arch holes left open. The bay returns sit behind.
        for k in range(count):
            a = start+k*1.25
            at = (lambda u, h: P(s, a+u, fixed, z+h)) if axis == 'i' else (
                lambda u, h: P(s, fixed, a+u, z+h))
            stone = STONE['lit' if axis == 'i' else 'dark']
            for col in (0, 1.16):
                poly(s, [at(col, 0), at(col+.09, 0), at(col+.09, 10), at(col, 10)], lambda x, y: stone)
            for n in range(10):
                u0, u1 = n/8, (n+1)/8
                def arch(u):
                    return 6+4*(1-abs(u-.625)/.625)
                pts = [at(u0, arch(u0)), at(u1, arch(u1)), at(u1, 11.5), at(u0, 11.5)]
                poly(s, pts, lambda x, y, n=n: STONE['hi'] if n % 3 == 0 else stone)

    def range_roof(s, x, y, wi, wj):
        roof = corners(s, x, y, wi, wj, 24)
        poly(s, list(roof), lambda px, py: STONE['line'] if (px+(py//4)*2) % 13 == 0
             or py % 5 == 0 else STONE['mid'])
        for a, b in zip(roof, roof[1:]+roof[:1]):
            seg(s, a, b, STONE['hi'])
        for k in range(3):
            a = x+wi*(.22+.27*k) if wi > wj else x+wi*.5
            b = y+wj*.5 if wi > wj else y+wj*(.22+.27*k)
            cylinder(s, a, b, .18, .18, 24, 7, STONE)

    def draw(s):
        # Back ranges and their two truly open gallery screens.
        block(s, i, j, w, 1.13, 24, STONE, exterior)
        block(s, i, j+1.13, 1.12, d-1.13, 24, STONE, exterior)
        for z in (0, 12):
            gallery(s, 'i', i+1.2, j+2.18, 7, z)
            gallery(s, 'j', j+2.18, i+2.19, 6, z)
        range_roof(s, i, j, w, 2.2)
        range_roof(s, i, j+2.2, 2.2, d-2.2)
        x, y = i+w/2, j+d/2
        cylinder(s, x, y, 1.16, 1.16, 0, 2.8, STONE)
        cylinder(s, x, y, .38, .38, 2.8, 2, MARBLE)
        for k in range(8):
            t = math.tau*k/8
            cylinder(s, x+.88*math.cos(t), y+.88*math.sin(t), .11, .11, 2.8, 9.2, MARBLE)
        cylinder(s, x, y, 1.04, 1.04, 12, 13, STONE,
                 lambda u, v, lit: exterior(u, v+11, lit))
        revolve(s, x, y, 1.16, 25, 8, DOME, LEAD, segments=16)
        cylinder(s, x, y, .08, .08, 32, 3, LEAD)
        block(s, i+w-1.1, j+2.2, 1.1, d-2.2, 23, STONE, exterior)
        range_roof(s, i+w-1.9, j+2.2, 1.9, d-2.2)
        def gate(u, v, lit):
            return (dressed_arch(u, v, 44, 4.8, 11, STONE, lit, WOOD) if lit else None) or exterior(u, v, lit)
        block(s, i+2.2, j+d-1.1, w-3.3, 1.1, 23, STONE, gate)
        range_roof(s, i+2.2, j+d-1.9, w-4.1, 1.9)

    scene.add(i+j+w+d, draw)


def eleftheria_square(scene, i, j):
    """The dry-moat park and the white, branching pedestrian deck below D'Avila."""
    def draw(s):
        def paving(u, v, lit):
            return PAVING['line'] if (int(u)+int(v)) % 6 == 0 else None
        court = [(i, j+2), (i+1.8, j+.52), (i+8.9, j), (i+10, j+2.1),
                 (i+9.7, j+5.8), (i+2.8, j+6.4)]
        slab(s, court, 0, 2, PAVING, paving)
        poly(s, [P(s, *p, 2.2) for p in court],
             lambda x, y: PAVING['line'] if (x+2*(y//3)) % 8 == 0 or (y+x//11) % 5 == 0 else PAVING['mid'])
        for a, b in ((1.15, 3), (7.6, 1.05), (7.1, 4.55)):
            planter = [(i+a, j+b), (i+a+1.7, j+b-.35), (i+a+2.04, j+b+.66),
                       (i+a+.42, j+b+1.04)]
            slab(s, planter, 2, 4, WHITE)
            poly(s, [P(s, x+.04, y+.01, 4.1) for x, y in planter],
                 lambda x, y: EARTH['hi' if h01(x, y, 221) < .22 else 'mid'])
        for a, b in ((3, 3.2), (5.9, 2.2)):
            column = [(i+a-.38, j+b), (i+a+.56, j+b-.26), (i+a+.43, j+b+.66)]
            slab(s, column, 2, 14, WHITE)
        deck = [(i+.05, j+.93), (i+1.85, j+.55), (i+4.12, j+1.56),
                (i+5.73, j+1.55), (i+8.6, j+.32), (i+9.62, j+.62),
                (i+8.08, j+2.72), (i+7.32, j+3.22), (i+8.28, j+4.9),
                (i+7.52, j+5.82), (i+5.22, j+4.27), (i+3.38, j+3.54),
                (i+1.27, j+3.04), (i+.02, j+2.3)]
        slab(s, deck, 14, 18, WHITE)
        for path in (deck[:6], deck[6:]):
            for (a, b), (c, d) in zip(path, path[1:]):
                seg(s, P(s, a, b, 20), P(s, c, d, 20), WHITE['hi'])
                for k in range(4):
                    x, y = a+(c-a)*k/4, b+(d-b)*k/4
                    seg(s, P(s, x, y, 18), P(s, x, y, 20), LEAD['mid'])
    scene.add(i+j+16.4, draw)


def main():
    for _, builder, _, _, _ in SITES:
        slug = builder.__name__.replace('_', '-')
        print(preview([lambda scene: builder(scene, 4, 4)], f'nicosia-{slug}', origin=(130, 86)))
    print(preview([lambda scene, k=k, seed=seed: townhouse(scene, 5+k*3.55, 6, 1+k%2, seed)
                   for k, seed in enumerate((0, 9, 5, 3))], 'nicosia-houses',
                  size=(240, 170), origin=(79, 36)))




# Ground-plan centres are in native scene pixels, north at the top.
SITES = [
    ('Paphos Gate', paphos_gate, (7.5, 5.8), (33.35673, 35.17373), (140, 302)),
    ('Famagusta Gate', famagusta_gate, (10, 6.1), (33.37119, 35.17424), (618, 272)),
    ('Cyprus Museum', cyprus_museum, (10.7, 5.8), (33.35575, 35.17173), (111, 401)),
    ('Eleftheria Square', eleftheria_square, (10, 6.4), (33.36017, 35.16953), (290, 429)),
    ('Büyük Han', buyuk_han, (10.8, 10.2), (33.36257, 35.17626), (323, 186)),
    ('Selimiye Mosque', selimiye, (7.6, 12), (33.36455, 35.17652), (492, 154)),
]


if __name__ == "__main__":
    main()
