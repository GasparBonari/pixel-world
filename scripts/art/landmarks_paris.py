"""Detailed Paris landmarks for the capital scene, built in true isometric 3D (ART_CONTRACT.md).

Points are (i, j, z): tile coordinates on the ground plus height in art pixels, projected with the
scene's own isometric transform. Light comes from the upper left, so faces whose normal points
towards +j (screen lower-left) are lit and faces towards +i (screen lower-right) are shaded.

Preview every landmark on a test plot, enlarged:  .venv/bin/python scripts/art/landmarks_paris.py
"""

import math
from pathlib import Path

import iso
from iso import Box, rgb, shade, h01

# Wrought iron in "Eiffel Tower brown", lit and shaded faces, highlights and a dark outline.
IRON = {"hi": rgb("#C49A74"), "lit": rgb("#9E7556"), "mid": rgb("#82604A"), "dark": rgb("#5E4434"),
        "deep": rgb("#3E2C22"), "back": rgb("#6E5444")}
STONE = {"hi": rgb("#FBF6EA"), "lit": rgb("#EEE5D0"), "mid": rgb("#DDD2B8"), "dark": rgb("#C3B699"),
         "deep": rgb("#8E8270"), "line": rgb("#A99C82"), "outline": rgb("#4A3E30")}
ZINC = {"hi": rgb("#B4BEC8"), "lit": rgb("#8F9AA6"), "mid": rgb("#7A8591"), "dark": rgb("#606A76"),
        "outline": rgb("#343A42")}
GLASS = {"lit": rgb("#BFE6F2"), "mid": rgb("#93CDE2"), "dark": rgb("#6FA8C4"), "frame": rgb("#5A6A7A"),
         "glint": rgb("#FFFFFF")}


def P(scene, i, j, z=0.0):
    return scene.screen(i, j, z)


def seg(scene, a, b, color, width=1):
    """A 1-2 pixel line between two screen points."""
    steps = int(max(abs(b[0] - a[0]), abs(b[1] - a[1]))) or 1
    for k in range(steps + 1):
        x = a[0] + (b[0] - a[0]) * k / steps
        y = a[1] + (b[1] - a[1]) * k / steps
        scene.put(x, y, color)
        if width > 1:
            scene.put(x + 1, y, color)


def poly(scene, points, color_at):
    for x, y in iso.polygon_pixels(points):
        scene.put(x, y, color_at(x, y))


# ------------------------------------------------------------- Eiffel Tower --

def eiffel_tower(scene, ci, cj):
    """The Eiffel Tower at tile (ci, cj): four curved lattice legs joined by great arches, a first
    platform with its arcaded frieze, a second platform, a tapering spire, the top cabin and mast."""
    H = 156.0  # height in art pixels
    BASE = 1.9  # half-width of the square footprint, in tiles
    P1, P2, P3 = 0.25 * H, 0.50 * H, 0.89 * H

    def half(z):
        """Half-width of the tower's square section at height z (the famous concave profile)."""
        t = z / H
        return BASE * (1 - t) ** 2.15 + 0.11

    def corner(sx, sy, z, inset=0.0):
        h = half(z) - inset
        return P(scene, ci + sx * h, cj + sy * h, z)

    # Faces in back-to-front order: back (-i, -j) faces first, then the lit +j and shaded +i faces.
    faces = [((-1, -1), (1, -1), "back"), ((-1, -1), (-1, 1), "back"),
             ((-1, 1), (1, 1), "lit"), ((1, -1), (1, 1), "dark")]

    def lattice(face, z0, z1, step, tone, arch=None):
        (ax, ay), (bx, by), _ = face
        z = z0
        while z < z1 - 0.5:
            zt = min(z1, z + step)
            a0, b0 = corner(ax, ay, z), corner(bx, by, z)
            a1, b1 = corner(ax, ay, zt), corner(bx, by, zt)
            lerp = lambda a, b, u: (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)
            if arch is not None and arch(0.5, z):
                # Under the great arch the face is open: rungs only beside the legs.
                left = 0.5 - SPAN
                while left < 0.5 and arch(left, z) is False:
                    left += 0.02
                seg(scene, a0, lerp(a0, b0, left), tone)
                seg(scene, lerp(a0, b0, 1 - left), b0, tone)
            else:
                seg(scene, a0, b0, tone)
            for k in range(1, 4):  # X-bracing, three panels across the face
                u0, u1 = (k - 1) / 3, k / 3

                def at(u, low):
                    a, b = (a0, b0) if low else (a1, b1)
                    return a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u
                if arch is None or not arch(u0, z) and not arch(u1, zt):
                    seg(scene, at(u0, True), at(u1, False), tone)
                    seg(scene, at(u1, True), at(u0, False), tone)
            z = zt

    SPRING, CROWN, SPAN = 0.30 * P1, 0.90 * P1, 0.30

    def arch_z(u):
        """Height of the great arch's underside at u across a face (it springs from the legs)."""
        return SPRING + (CROWN - SPRING) * math.sqrt(max(0.0, 1 - ((u - 0.5) / SPAN) ** 2))

    def arch_open(u, z):
        """True below the great arch between two legs (u across the face, z height)."""
        return 0.5 - SPAN < u < 0.5 + SPAN and z < arch_z(u)

    def leg(sx, sy, tone_lit, tone_dark, edge):
        """A corner leg: an open lattice truss (edge girders with X-bracing between them) that
        follows the tower's curve to the first platform, then one heavy corner girder above."""
        def pts(z, w):
            outer = corner(sx, sy, z)
            inner_j = P(scene, ci + sx * (half(z) - w), cj + sy * half(z), z)
            inner_i = P(scene, ci + sx * half(z), cj + sy * (half(z) - w), z)
            return outer, inner_j, inner_i
        width = lambda z: 0.5 * (1 - z / P1) + 0.18
        z, step = 0.0, 4.0
        while z < P1 - 0.5:
            zt = min(P1, z + step)
            o0, j0, i0 = pts(z, width(z))
            o1, j1, i1 = pts(zt, width(zt))
            for (a0, a1), (b0, b1), tone in (((o0, o1), (j0, j1), tone_lit if sy > 0 else tone_dark),
                                             ((o0, o1), (i0, i1), tone_dark if sy > 0 else tone_lit)):
                seg(scene, a0, b1, tone)
                seg(scene, b0, a1, tone)
                seg(scene, b0, b1, tone)
            seg(scene, j0, i0, IRON["deep"])
            z = zt
        for z0 in range(0, int(P3), 2):  # the corner girder, the leg's strongest line
            seg(scene, corner(sx, sy, z0), corner(sx, sy, z0 + 2), edge, 2 if z0 < P2 else 1)

    def platform(z, depth, overhang, frieze):
        """A deck: an overhanging slab with a lit edge, a shaded edge, railing posts and arches."""
        h = half(z) + overhang
        T, R = P(scene, ci - h, cj - h, z), P(scene, ci + h, cj - h, z)
        B, L = P(scene, ci + h, cj + h, z), P(scene, ci - h, cj + h, z)
        poly(scene, [T, R, B, L], lambda x, y: IRON["lit"] if (int(x) + int(y)) % 4 else IRON["hi"])
        down = lambda p: (p[0], p[1] + depth)
        poly(scene, [L, B, down(B), down(L)], lambda x, y: IRON["mid"])
        poly(scene, [B, R, down(R), down(B)], lambda x, y: IRON["dark"])
        if frieze:  # the first floor's famous arcade frieze
            for edge, tone in (((L, B), IRON["deep"]), ((B, R), IRON["deep"])):
                (ax, ay), (bx, by) = edge
                steps = int(abs(bx - ax))
                for k in range(1, steps, 3):
                    x, y = ax + (bx - ax) * k / steps, ay + (by - ay) * k / steps
                    for dy in range(1, depth - 1):
                        scene.put(x, y + dy, tone)
        for p0, p1 in ((L, B), (B, R), (T, L), (T, R)):  # railing
            steps = int(abs(p1[0] - p0[0]))
            for k in range(0, steps + 1, 2):
                x, y = p0[0] + (p1[0] - p0[0]) * k / max(1, steps), p0[1] + (p1[1] - p0[1]) * k / max(1, steps)
                scene.put(x, y - 1, IRON["deep"])
            seg(scene, (p0[0], p0[1] - 2), (p1[0], p1[1] - 2), IRON["dark"])

    def draw(s):
        # Behind: the far faces' lattice, darker, seen through the tower.
        for face in faces[:2]:
            lattice(face, 0, P1, 6, IRON["back"], arch_open)
            lattice(face, P1, P2, 5, IRON["back"])
            lattice(face, P2, P3, 4, IRON["back"])
        leg(-1, -1, IRON["back"], IRON["deep"], IRON["back"])
        leg(-1, 1, IRON["lit"], IRON["mid"], IRON["hi"])
        leg(1, -1, IRON["mid"], IRON["dark"], IRON["mid"])
        platform(P1, 5, 0.22, True)
        platform(P2, 3, 0.14, False)
        # In front: the near faces' lattice, the arches, the near leg.
        for face, tone in ((faces[2], IRON["lit"]), (faces[3], IRON["dark"])):
            lattice(face, 0, P1, 6, tone, arch_open)
            lattice(face, P1, P2, 5, tone)
            lattice(face, P2, P3, 4, tone)
            (ax, ay), (bx, by), _ = face
            bright = IRON["hi"] if tone == IRON["lit"] else IRON["mid"]
            for lift, colour in ((0, bright), (4, tone)):  # the great arch: a double curved girder
                prev = None
                for k in range(0, 49):
                    u = 0.5 - SPAN + 2 * SPAN * k / 48
                    z = arch_z(u) + lift
                    a, b = corner(ax, ay, z), corner(bx, by, z)
                    p = (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)
                    if prev:
                        seg(s, prev, p, colour, 2 if lift == 0 else 1)
                        if k % 4 == 0:
                            seg(s, p, (p[0], p[1] - 4), tone)  # ties between the girders
                    prev = p
        leg(1, 1, IRON["lit"], IRON["dark"], IRON["hi"])
        # The spire above the second platform tapers to the top.
        for z in range(int(P2), int(P3)):
            for sx, sy, tone in ((-1, 1, IRON["lit"]), (1, -1, IRON["dark"]), (1, 1, IRON["mid"])):
                s.put(*corner(sx, sy, z), tone)
        platform(P3, 2, 0.12, False)
        cx, cy = P(s, ci, cj, P3)
        for dy in range(0, 7):  # the top cabin
            for dx in range(-3, 4):
                s.put(cx + dx, cy - dy, IRON["lit"] if dx < 0 else IRON["dark"])
        for dy in range(7, 20):  # the mast
            s.put(cx, cy - dy, IRON["deep"] if dy < 16 else IRON["mid"])
        s.put(cx, cy - 20, rgb("#E2434E"))
        # Pedestal plinths under each leg.
        for sx, sy in ((-1, 1), (1, -1), (1, 1)):
            x, y = corner(sx, sy, 0)
            for dx in range(-3, 4):
                for dy in range(0, 2):
                    s.put(x + dx, y - dy, STONE["mid"] if dx < 0 else STONE["dark"])

    scene.add(ci + cj + 2 * BASE, draw)



# --------------------------------------------------- façades and mansards --

def corners(scene, i, j, wi, wj, z):
    """Top (T), right (R), bottom (B), left (L) screen corners of a footprint at height z."""
    return (P(scene, i, j, z), P(scene, i + wi, j, z), P(scene, i + wi, j + wj, z), P(scene, i, j + wj, z))


def facade(scene, i, j, wi, wj, height, pattern, palette=STONE, outline=True, z0=0):
    """Two visible walls of a block. pattern(u, v, lit) gives a colour (or None for plain stone),
    where u runs along the wall from its left end and v is the height above its foot (at z0)."""
    T, R, B, L = corners(scene, i, j, wi, wj, z0)
    cover = set()
    for start, end, lit, slope in ((L, B, True, 0.5), (B, R, False, -0.5)):
        top = [(end[0], end[1] - height), (start[0], start[1] - height)]
        for x, y in iso.polygon_pixels([start, end, *top]):
            u = x - start[0]
            v = start[1] + u * slope - y
            colour = pattern(u, v, lit) or (palette["lit"] if lit else palette["dark"])
            scene.put(x, y, colour)
            cover.add((int(x), int(y)))
    seg(scene, B, (B[0], B[1] - height), palette["deep"])  # the near corner
    return cover


def mansard(scene, i, j, wi, wj, base, rise, inset, roof=ZINC, dormers=0, cover=None, dome=False):
    """A mansard (or, with dome=True, a tall curved pavilion roof): steep slopes from the cornice
    up to an inset flat top, dormer windows along the front slopes, cresting along the top."""
    cover = cover if cover is not None else set()
    outer = corners(scene, i, j, wi, wj, base)
    d = min(inset, wi / 2 - 0.05, wj / 2 - 0.05)
    inner = corners(scene, i + d, j + d, wi - 2 * d, wj - 2 * d, base + rise)
    T, R, B, L = outer
    t, r, b, l = inner

    def tiles(c1, c2):
        def colour(x, y):
            return c2 if int(y) % 3 == 0 else c1
        return colour
    faces = [((T, R, r, t), roof["dark"]), ((T, L, l, t), roof["mid"]), ((L, B, b, l), roof["lit"]),
             ((B, R, r, b), roof["dark"])]
    for pts, tone in faces:
        for x, y in iso.polygon_pixels(pts):
            scene.put(x, y, tiles(tone, shade(tone, -0.12))(x, y))
            cover.add((int(x), int(y)))
    if dome:  # pavilion roofs swell slightly: lighter upper band on the lit slope
        for x, y in iso.polygon_pixels([l, b, (b[0], b[1] + rise * 0.35), (l[0], l[1] + rise * 0.35)]):
            scene.put(x, y, roof["hi"] if int(y) % 3 else roof["lit"])
    for x, y in iso.polygon_pixels([t, r, b, l]):
        scene.put(x, y, roof["mid"])
        cover.add((int(x), int(y)))
    for a, c in ((l, b), (b, r), (t, l), (t, r)):  # lead cresting
        steps = int(abs(c[0] - a[0]))
        for k in range(steps + 1):
            x, y = a[0] + (c[0] - a[0]) * k / max(1, steps), a[1] + (c[1] - a[1]) * k / max(1, steps)
            scene.put(x, y - (1 if k % 2 else 0), roof["outline"])
    if dormers:
        for (a, c, lit) in ((L, B, True), (B, R, False)):
            steps = int(abs(c[0] - a[0]))
            for k in range(dormers, steps - 3, dormers):
                x = a[0] + (c[0] - a[0]) * k / steps
                y = a[1] + (c[1] - a[1]) * k / steps - 3
                for dy in range(0, 6):
                    for dx in range(-1, 2):
                        top = dy == 5 and dx != 0
                        if top:
                            continue
                        glass = 0 < dy < 4 and dx == 0
                        scene.put(x + dx, y - dy, GLASS["dark"] if glass else STONE["hi" if lit else "mid"])
    for p0, p1 in ((L, B), (B, R)):  # cornice shadow under the eaves
        seg(scene, (p0[0], p0[1] + 1), (p1[0], p1[1] + 1), STONE["deep"])
    return cover


def louvre_pattern(u, v, lit, bay=8, floors=(10, 22, 29)):
    """The Louvre's elevation: rusticated arcade, tall arched windows between pilasters, an attic."""
    ground, noble, attic = floors
    col = int(u) % bay
    v = int(v)
    base, hi, line = (STONE["lit"], STONE["hi"], STONE["line"]) if lit else (STONE["dark"], STONE["mid"], STONE["deep"])
    if v >= attic:
        return line if v == attic else hi  # cornice and balustrade
    if v < ground:
        if 2 <= col <= 5 and v < 8 - (col in (2, 5)):
            return STONE["deep"] if lit else rgb("#6E6454")  # arcade openings
        return line if v % 3 == 0 else base  # rustication
    if v == ground:
        return line
    if v < noble:
        if col == 0:
            return hi  # pilasters
        if 3 <= col <= 5 and ground + 2 <= v <= noble - 2 - (col != 4):
            return GLASS["dark"] if (col + v) % 4 else GLASS["lit"]
        if 3 <= col <= 5 and v == noble - 1:
            return hi  # window pediments
        return base
    if v == noble:
        return line
    if 3 <= col <= 5 and noble + 2 <= v <= attic - 2:
        return GLASS["dark"]
    return base


def louvre(scene, i, j):
    """The Louvre around the Cour Napoléon: a long north wing and an east wing with domed corner and
    clock pavilions under zinc mansards with dormers, and I. M. Pei's glass pyramid in the court."""
    H = 30

    def wing(a, b, wi, wj, height=H, rise=10, dormers=8):
        def draw(s):
            cover = facade(s, a, b, wi, wj, height, louvre_pattern)
            mansard(s, a, b, wi, wj, height, rise, 0.45, dormers=dormers, cover=cover)
            iso.outline(s, cover, STONE["outline"])
        scene.add(a + b + wi + wj, draw)

    def pavilion(a, b, size, height, rise):
        def draw(s):
            cover = facade(s, a, b, size, size, height,
                           lambda u, v, lit: louvre_pattern(u, v, lit, bay=7, floors=(10, 24, height - 1)))
            mansard(s, a, b, size, size, height, rise, size * 0.32, dormers=7, cover=cover, dome=True)
            x, y = P(s, a + size / 2, b + size / 2, height + rise)
            for dy in range(1, 6):  # finial
                s.put(x, y - dy, ZINC["outline"] if dy < 5 else rgb("#E8B84A"))
            iso.outline(s, cover, STONE["outline"])
        scene.add(i + j + 30 + a + b, draw)  # after the wings: pavilions rise through the roofline

    # The U opens towards the viewer: a long north wing at the back and a long west wing on the
    # left, both presenting their courtyard façades, with the pyramid in the open court.
    wing(i, j, 14, 2.5)  # north wing (Richelieu)
    wing(i, j + 2.5, 2.5, 11)  # west wing
    pavilion(i - 0.25, j - 0.25, 3.0, 34, 15)  # corner pavilion
    pavilion(i + 6.0, j - 0.25, 3.0, 33, 13)  # mid pavilion of the north wing
    pavilion(i - 0.25, j + 6.5, 3.0, 35, 16)  # mid pavilion of the west wing
    pyramid(scene, i + 6.2, j + 6.2, 4.4, 30)
    for a, b, size in ((i + 11.6, j + 7.0, 1.3), (i + 7.0, j + 11.6, 1.3), (i + 4.2, j + 4.2, 1.3)):
        pyramid(scene, a, b, size, 9)
    for a, b in ((i + 10.4, j + 4.6), (i + 4.4, j + 10.6), (i + 11.0, j + 10.4)):  # the basins
        def basin(s, a=a, b=b):
            rim = [P(s, a, b), P(s, a + 2.6, b), P(s, a + 1.3, b + 1.8)]
            water = [P(s, a + 0.3, b + 0.2), P(s, a + 2.2, b + 0.2), P(s, a + 1.25, b + 1.4)]
            poly(s, rim, lambda x, y: STONE["mid"])
            poly(s, water, lambda x, y: GLASS["glint"] if h01(int(x) // 2, int(y), 3) < 0.08 else rgb("#4C8CC8"))
        scene.add(a + b, basin)


def pyramid(scene, i, j, size, height):
    """A glass pyramid: four triangular faces glazed in a regular grid (mullions rising to the apex,
    courses parallel to the base) inside a slim dark frame."""
    def draw(s):
        T, R, B, L = corners(s, i, j, size, size, 0)
        apex = P(s, i + size / 2, j + size / 2, height)
        mullions = max(3, int(size * 2.2))
        courses = max(2, int(height / 4))
        for (a, c), tone in (((T, L), GLASS["mid"]), ((L, B), GLASS["lit"]), ((B, R), GLASS["dark"])):
            poly(s, [a, c, apex], lambda x, y, t=tone: t)
            frame = shade(tone, -0.32)
            for k in range(1, mullions):
                u = k / mullions
                seg(s, (a[0] + (c[0] - a[0]) * u, a[1] + (c[1] - a[1]) * u), apex, frame)
            for k in range(1, courses):
                f = k / courses
                p0 = (a[0] + (apex[0] - a[0]) * f, a[1] + (apex[1] - a[1]) * f)
                p1 = (c[0] + (apex[0] - c[0]) * f, c[1] + (apex[1] - c[1]) * f)
                seg(s, p0, p1, frame)
        for a in (L, B, R):
            seg(s, a, apex, GLASS["frame"])
        seg(s, L, B, GLASS["frame"])
        seg(s, B, R, GLASS["frame"])
        for k in range(2, 6):  # a glint of sky on the lit face
            s.put(apex[0] - k, apex[1] + k * 2, GLASS["glint"])
    scene.add(i + j + 2 * size, draw)


# ------------------------------------------------------------- Notre-Dame --

def gothic_front(u, v, lit, width, towers):
    """Notre-Dame's west front, seen on its lit face: three deep portals, the Gallery of Kings,
    the rose window between the towers, tall paired belfry lancets and the open gallery above."""
    u, v = int(u), int(v)
    base, hi, line, deep = (STONE["lit"], STONE["hi"], STONE["line"], STONE["deep"]) if lit else \
        (STONE["dark"], STONE["mid"], STONE["deep"], rgb("#6E6454"))
    centre = width / 2
    for c in (width * 0.17, centre, width * 0.83):  # three portals, pointed arches
        span = 3.2 if c == centre else 2.6
        if abs(u - c) <= span and v < 13 - abs(u - c) * 0.8:
            return deep if v < 11 - abs(u - c) else line
    if 15 <= v <= 17:
        return line if v != 16 else (deep if u % 2 else hi)  # Gallery of Kings
    rose = math.hypot(u - centre, (v - 25) * 1.0)
    if rose <= 4.5:
        if rose > 3.6:
            return hi
        return GLASS["dark"] if (int(math.atan2(v - 25, u - centre) * 4) + int(rose)) % 2 else rgb("#C9A0E0")
    for c in towers:
        if abs(u - c) <= 2.2 and 30 <= v <= 40 and int(u - c + 3) % 3 != 0:
            return deep  # paired lancets in the belfries
    if v in (30, 41):
        return hi  # string courses and the open gallery
    return base


def tower_side(u, v, height):
    """The towers' shaded side walls: string courses and tall belfry lancets only."""
    u, v = int(u), int(v)
    if v in (16, 30) or v == height - 5:
        return STONE["deep"]
    if height > 40 and 31 <= v <= 40 and u % 5 in (2, 3):
        return rgb("#6E6454")
    return None


def notre_dame(scene, i, j):
    """Notre-Dame de Paris. The nave runs back along -j; its west front faces the viewer (+j)."""
    W, L = 3.6, 9.0  # width (i) and length (j) of the nave in tiles

    def draw(s):
        cover = set()
        # Nave with flying buttresses along its visible south (+i) side and a steep lead roof.
        nave = corners(s, i, j, W, L, 0)
        cover |= facade(s, i + 0.2, j, W - 0.4, L - 1.6, 24,
                        lambda u, v, lit: (GLASS["dark"] if int(u) % 6 in (2, 3) and 8 <= v <= 18 else None))
        mansard(s, i + 0.2, j, W - 0.4, L - 1.6, 24, 16, 1.6, cover=cover)
        for k in range(1, 7):  # flying buttresses: a pier, then an arched strut to the clerestory
            jj = j + k * (L - 2) / 7
            pier_base = P(s, i + W + 0.9, jj, 0)
            wall_top = P(s, i + W - 0.2, jj, 22)
            for z in range(0, 20):
                s.put(pier_base[0] - 1, pier_base[1] - z, STONE["mid"])
                s.put(pier_base[0], pier_base[1] - z, STONE["dark"])
                s.put(pier_base[0] + 1, pier_base[1] - z, STONE["deep"])
            for z in range(20, 24):  # pinnacle
                s.put(pier_base[0], pier_base[1] - z, STONE["hi"] if z < 23 else STONE["mid"])
            prev = (pier_base[0], pier_base[1] - 18)
            for t in range(1, 9):
                f = t / 8
                x = prev[0] + (wall_top[0] - pier_base[0]) / 8
                y = pier_base[1] - 18 + (wall_top[1] - pier_base[1] + 18) * f - math.sin(f * math.pi) * 3
                seg(s, prev, (x, y), STONE["mid"])
                prev = (x, y)
        # The spire (flèche) over the crossing, with its gilded rooster.
        x, y = P(s, i + W / 2, j + L * 0.45, 40)
        for dy in range(0, 34):
            w = max(0, int(2.6 - dy / 10))
            for dx in range(-w, w + 1):
                s.put(x + dx, y - dy, ZINC["lit"] if dx < 0 else ZINC["dark"] if dx > 0 else ZINC["mid"])
        s.put(x, y - 35, rgb("#E8B84A"))
        # West front: two square towers rising above a lower centre with the rose window.
        fw = W * 8
        front = set()
        towers = (fw * 0.19, fw * 0.81)
        for x0, wi, height in ((0.0, 1.35, 46), (1.35, 0.9, 34), (2.25, 1.35, 46)):
            offset = x0 * 8
            front |= facade(s, i + x0, j + L - 1.6, wi, 1.6, height,
                            lambda u, v, lit, o=offset, h=height: gothic_front(u + o, v, lit, fw, towers)
                            if lit else tower_side(u, v, h))
            T, R, B, Lc = corners(s, i + x0, j + L - 1.6, wi, 1.6, height)
            poly(s, [T, R, B, Lc], lambda x, y: STONE["mid"])
            for a2, c2 in ((Lc, B), (B, R)):  # balustrades
                steps = int(abs(c2[0] - a2[0]))
                for k in range(0, steps, 2):
                    px = a2[0] + (c2[0] - a2[0]) * k / max(1, steps)
                    py = a2[1] + (c2[1] - a2[1]) * k / max(1, steps)
                    s.put(px, py - 1, STONE["hi"])
                    s.put(px, py - 2, STONE["line"])
                    front.update({(int(px), int(py - 1)), (int(px), int(py - 2))})
        cover |= front
        iso.outline(s, cover, STONE["outline"])

    scene.add(i + j + W + L, draw)


# ------------------------------------------------------- Arc de Triomphe --

def arc_pattern(u, v, lit, width):
    u, v = int(u), int(v)
    base, hi, line, deep = (STONE["lit"], STONE["hi"], STONE["line"], STONE["deep"]) if lit else \
        (STONE["dark"], STONE["mid"], STONE["deep"], rgb("#6E6454"))
    centre = width / 2
    span = width * 0.2
    if abs(u - centre) <= span:  # the great vault
        crown = 30 + math.sqrt(max(0, span * span - (u - centre) ** 2)) * 1.1
        if v < crown:
            return rgb("#3A3026") if v < crown - 1 else line
    if v >= 54:
        return hi if v % 3 else line  # attic with its row of shields
    if v in (49, 50):
        return line  # frieze
    pier = u < centre - span - 1 or u > centre + span + 1
    if pier and 14 <= v <= 40:  # sculpture groups on the piers
        cx = width * 0.13 if u < centre else width * 0.87
        if math.hypot(u - cx, (v - 26) * 0.55) < 4.8:
            return hi if (u + v) % 3 else STONE["mid"]
    return base


def arc_de_triomphe(scene, i, j):
    W, D, H = 6.0, 3.6, 64  # monumental: it rises well above the Haussmann rooftops

    def draw(s):
        cover = facade(s, i, j, W, D, H, lambda u, v, lit: arc_pattern(u, v, lit, (W if lit else D) * 8))
        T, R, B, L = corners(s, i, j, W, D, H)
        poly(s, [T, R, B, L], lambda x, y: STONE["mid"])
        for a, c in ((L, B), (B, R)):
            seg(s, (a[0], a[1] - 1), (c[0], c[1] - 1), STONE["hi"])
        iso.outline(s, cover, STONE["outline"])
    scene.add(i + j + W + D, draw)


# ------------------------------------------------------------ Sacré-Cœur --

def egg_dome(s, x, y, rx, ry, tones):
    for dy in range(-ry, 1):
        for dx in range(-rx, rx + 1):
            t = dy / ry
            width = rx * math.sqrt(max(0, 1 - t * t)) * (1 - 0.25 * (-t) ** 3)
            if abs(dx) <= width:
                tone = tones[0] if dx < -width * 0.35 else tones[2] if dx > width * 0.4 else tones[1]
                if dx % 4 == 0 and dy < -2:
                    tone = shade(tone, -0.08)  # ribs
                s.put(x + dx, y + dy, tone)


def sacre_coeur(scene, i, j, elev):
    """Sacré-Cœur: white travertine, a tall ovoid dome on a colonnaded drum, four small domes,
    a three-arched portico and the campanile behind."""
    WHITE = (rgb("#FFFFFF"), rgb("#F1EFE8"), rgb("#D9D5CA"))

    def draw(s):
        # Campanile behind.
        cover = facade(s, i + 3.2, j - 1.0, 1.4, 1.4, 42, lambda u, v, lit: None,
                       palette={**STONE, "lit": WHITE[1], "dark": WHITE[2]}, z0=elev)
        tx, ty = P(s, i + 3.9, j - 0.3, elev + 42)
        egg_dome(s, tx, ty, 5, 8, WHITE)
        body = facade(s, i, j, 4, 4, 22, lambda u, v, lit: (
            rgb("#3A3026") if int(u) % 8 in (3, 4, 5) and v < 10 - abs(int(u) % 8 - 4) and lit else
            GLASS["dark"] if int(u) % 6 == 3 and 13 <= v <= 18 else None),
            palette={**STONE, "lit": WHITE[1], "dark": WHITE[2]}, z0=elev)
        T, R, B, L = corners(s, i, j, 4, 4, elev + 22)
        poly(s, [T, R, B, L], lambda x, y: WHITE[1])
        cx, cy = P(s, i + 2, j + 2, elev + 22)
        for dy in range(0, 13):  # colonnaded drum
            for dx in range(-10, 11):
                s.put(cx + dx, cy - dy, WHITE[2] if dx % 3 == 0 else WHITE[1] if dx < 3 else WHITE[2])
        egg_dome(s, cx, cy - 13, 11, 24, WHITE)
        for dy in range(37, 44):  # lantern
            s.put(cx, cy - dy, WHITE[2])
            s.put(cx - 1, cy - dy, WHITE[0])
        for a, b in ((i, j + 4), (i + 4, j + 4), (i, j)):
            x, y = P(s, a, b, elev + 22)
            egg_dome(s, x, y, 4, 7, WHITE)
        for a in (1.2, 2.8):  # equestrian statues on the portico
            x, y = P(s, i + a, j + 4, elev + 12)
            for dx, dy in ((0, 0), (1, 0), (-1, 1), (0, 1), (1, 1), (0, 2), (0, 3)):
                s.put(x + dx, y - dy, rgb("#4E6A4E"))
        iso.outline(s, cover | body, rgb("#8E8A80"))
    scene.add(i + j + 8, draw)


# ---------------------------------------------------- Haussmann buildings --

AWNINGS = [rgb(c) for c in ("#B83A3A", "#2E6B4A", "#2E4E7A", "#C9962E", "#6B2E4A")]


def haussmann_pattern(seed):
    """Six storeys: shopfronts with awnings, tall French windows with white surrounds, continuous
    wrought-iron balconies on the 2nd and 5th floors, cornices between."""
    awning = AWNINGS[int(h01(seed, 1) * len(AWNINGS))]

    def pattern(u, v, lit):
        u, v = int(u), int(v)
        base, hi, line = (STONE["lit"], STONE["hi"], STONE["line"]) if lit else (STONE["dark"], STONE["mid"], STONE["deep"])
        col = u % 6
        if v < 10:  # ground floor: shop windows under awnings
            if v in (7, 8):
                return awning if lit else shade(awning, -0.25)
            if 1 <= col <= 4 and v < 7:
                return GLASS["dark"] if v < 6 else line
            return line if v % 3 == 0 else base
        floor, inside = divmod(v - 10, 8)
        if inside == 0 and floor in (1, 4):
            return rgb("#2A2624")  # continuous iron balcony
        if inside == 0:
            return line  # cornice
        if 2 <= col <= 3 and 2 <= inside <= 6:
            return GLASS["dark"] if inside != 2 else GLASS["mid"]
        if col in (1, 4) and 2 <= inside <= 6:
            return hi  # window surrounds
        return base
    return pattern


def haussmann(scene, i, j, wi, wj, seed, floors=5):
    height = 10 + floors * 8

    def draw(s):
        cover = facade(s, i, j, wi, wj, height, haussmann_pattern(seed))
        mansard(s, i, j, wi, wj, height, 10, 0.35, dormers=6, cover=cover)
        T, R, B, L = corners(s, i + 0.3, j + 0.3, wi - 0.6, wj - 0.6, height + 10)
        for x, y in (T, (T[0] + 6, T[1] + 3)):  # chimney stacks with terracotta pots
            for dy in range(0, 5):
                s.put(x, y - dy, STONE["dark"])
                s.put(x + 1, y - dy, STONE["deep"])
            s.put(x, y - 5, rgb("#C9654A"))
            s.put(x + 1, y - 5, rgb("#A84E36"))
        iso.outline(s, cover, STONE["outline"])
    scene.add(i + j + wi + wj, draw)


def obelisk(scene, i, j):
    """The Luxor Obelisk on Place de la Concorde, gilded pyramidion on top."""
    def draw(s):
        x, y = P(s, i, j)
        for dy in range(0, 4):
            for dx in range(-3, 4):
                s.put(x + dx, y - dy, STONE["mid"] if dx < 0 else STONE["dark"])
        for dy in range(4, 30):
            w = 2 if dy < 22 else 1
            for dx in range(-w, w + 1):
                s.put(x + dx, y - dy, rgb("#D9C7A0") if dx < 0 else rgb("#B9A47C"))
        s.put(x, y - 30, rgb("#E8B84A"))
        s.put(x, y - 31, rgb("#E8B84A"))
    scene.add(i + j + 0.5, draw)


# ----------------------------------------------------------------- bridges --

def stone_bridge(scene, i, j, length, width=1.6, deck=7, gilded=False, along_i=False):
    """A masonry bridge along +j (or +i with along_i=True): arches on its long visible face, a
    parapet; with gilded=True, Pont Alexandre III's gilded statues on tall pillars at both ends."""
    wi, wj = (length, width) if along_i else (width, length)

    def draw(s):
        arches = max(2, int(length / 2.4))
        span = length * 8 / arches  # screen length of one arch along the face

        def face(u, v, lit):
            u, v = int(u), int(v)
            k = (u % span) - span / 2
            r = span / 2 - 1.5
            if v < deck - 2 and abs(k) < r and v < (deck - 3) * math.sqrt(max(0, 1 - (k / r) ** 2)):
                return rgb("#2E4E6E")  # arch over the water
            if v >= deck - 1:
                return STONE["hi"] if lit else STONE["mid"]  # parapet
            return None
        cover = facade(s, i, j, wi, wj, deck, face)
        T, R, B, L = corners(s, i, j, wi, wj, deck)
        poly(s, [T, R, B, L], lambda x, y: ground_cobble(x, y))
        if gilded:
            for a in (0.4, length - 0.4):
                for c in (0.1, width - 0.1):
                    x, y = P(s, i + c, j + a) if not along_i else P(s, i + a, j + c)
                    y -= deck
                    for dy in range(0, 16):
                        s.put(x, y - dy, STONE["lit"] if dy < 13 else rgb("#E8B84A"))
                        s.put(x + 1, y - dy, STONE["dark"] if dy < 13 else rgb("#C9962E"))
        iso.outline(s, cover, STONE["outline"])
    scene.add(i + j + wi + wj + 0.5, draw)


def ground_cobble(x, y):
    return rgb("#9C9486") if (int(x) + 2 * (int(y) % 2)) % 4 == 0 else rgb("#B9B1A3")


# ---------------------------------------------------------------- preview --

def preview(builders, name, size=(260, 230), origin=(130, 10), tiles=18, scale=4):
    """Render landmarks alone on a grass test plot, enlarged, into docs/art/capitals/."""
    scene = iso.Scene(*size, origin)
    for i in range(-2, tiles):
        for j in range(-2, tiles):
            iso.ground_tile(scene, i, j, lambda x, y: rgb("#8AC240") if (x * 3 + y) % 11 else rgb("#74AC3D"))
    for build in builders:
        build(scene)
    scene.paint_objects()
    out = Path(__file__).resolve().parents[2] / "docs" / "art" / "capitals"
    out.mkdir(parents=True, exist_ok=True)
    img = scene.img.convert("RGB")
    img.resize((img.width * scale, img.height * scale), 0).save(out / f"{name}.png")
    return out / f"{name}.png"


if __name__ == "__main__":
    print(preview([lambda s: eiffel_tower(s, 9, 9)], "paris-eiffel", size=(170, 240), origin=(85, 130), tiles=14))
    print(preview([lambda s: louvre(s, 2, 2)], "paris-louvre", size=(260, 200), origin=(110, 40), tiles=18))
    print(preview([lambda s: notre_dame(s, 3, 2), lambda s: arc_de_triomphe(s, 11, 10)],
                  "paris-notre-dame-arc", size=(240, 180), origin=(120, 60), tiles=16))
    print(preview([lambda s: sacre_coeur(s, 4, 4, 0), lambda s: haussmann(s, 10, 2, 3, 3, 1),
                   lambda s: haussmann(s, 10, 6, 3, 2, 2), lambda s: stone_bridge(s, 2, 11, 6, gilded=True)],
                  "paris-sacre-coeur-houses", size=(240, 190), origin=(110, 70), tiles=16))
