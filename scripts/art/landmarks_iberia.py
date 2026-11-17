"""Detailed Lisbon and Madrid landmarks in true isometric 3D (ART_CONTRACT.md, capital scale).

Same construction as scripts/art/landmarks_paris.py, whose helpers this reuses: points are
(i, j, height); the +j face is lit, the +i face shaded; every landmark is checked alone on a test
plot before it goes into a scene.

Preview:  .venv/bin/python scripts/art/landmarks_iberia.py  ->  docs/art/capitals/lisbon-*.png, madrid-*.png
"""

import math

import iso
from iso import rgb, shade, h01
from landmarks_paris import P, seg, poly, corners, facade, mansard, egg_dome, preview, GLASS


def tones(hi, lit, mid, dark, deep, line, outline):
    return {"hi": rgb(hi), "lit": rgb(lit), "mid": rgb(mid), "dark": rgb(dark), "deep": rgb(deep),
            "line": rgb(line), "outline": rgb(outline)}


LIOZ = tones("#FFFDF6", "#F2EBDD", "#E2D8C4", "#CBBEA4", "#968A74", "#B3A68C", "#4E4232")  # Lisbon limestone
CASTLE = tones("#E6D9BE", "#D2C2A2", "#BCAA87", "#9F8D6D", "#6E604A", "#8A7A5E", "#3E3426")
GRANITE = tones("#F6F4EE", "#E8E4DA", "#D4CEC0", "#BAB3A4", "#86806F", "#A49D8C", "#3E3A32")
TERRACOTTA = {"hi": rgb("#F6A070"), "lit": rgb("#E4764C"), "mid": rgb("#CF623C"), "dark": rgb("#AC4C2E"),
              "outline": rgb("#5A2418")}
SLATE = {"hi": rgb("#97A3BC"), "lit": rgb("#74819C"), "mid": rgb("#626E88"), "dark": rgb("#4E5970"),
         "outline": rgb("#262C3A")}
BLACK_SLATE = {"hi": rgb("#626873"), "lit": rgb("#414650"), "mid": rgb("#2C303A"),
               "dark": rgb("#1C2029"), "outline": rgb("#12151D")}
BRONZE = {"hi": rgb("#969276"), "lit": rgb("#696D59"), "dark": rgb("#343E37")}
IRON = rgb("#2A2624")
GOLD, GOLD_DARK = rgb("#F2C14E"), rgb("#C9962E")
WOOD = rgb("#6B4228")


def palette_of(wall):
    """A wall colour expanded into lit/shaded tones for facade()."""
    return {"hi": shade(wall, 0.25), "lit": wall, "mid": shade(wall, -0.08), "dark": shade(wall, -0.2),
            "deep": shade(wall, -0.45), "line": shade(wall, -0.3), "outline": shade(wall, -0.7)}


# ------------------------------------------------------------- primitives --

def hip_roof(scene, i, j, wi, wj, base, rise, roof=TERRACOTTA, cover=None, eaves=True):
    """A hipped roof of clay tiles: four slopes up to a ridge along the longer side, tile courses
    following the slope, a lit front-left slope and a shaded front-right one."""
    cover = cover if cover is not None else set()
    T, R, B, L = corners(scene, i, j, wi, wj, base)
    if wi >= wj:
        a = P(scene, i + wj / 2, j + wj / 2, base + rise)
        b = P(scene, i + wi - wj / 2, j + wj / 2, base + rise)
        faces = [((T, R, b, a), roof["dark"]), ((T, a, L), roof["mid"]), ((L, B, b, a), roof["lit"]),
                 ((B, R, b), roof["dark"])]
    else:
        a = P(scene, i + wi / 2, j + wi / 2, base + rise)
        b = P(scene, i + wi / 2, j + wj - wi / 2, base + rise)
        faces = [((T, L, b, a), roof["mid"]), ((T, R, a), roof["dark"]), ((R, B, b, a), roof["dark"]),
                 ((L, B, b), roof["lit"])]
    for pts, tone in faces:
        for x, y in iso.polygon_pixels(list(pts)):
            course = int(y) % 3 == 0
            joint = (int(x) + (int(y) // 3) * 2) % 4 == 0
            scene.put(x, y, shade(tone, -0.16) if course else shade(tone, 0.08) if joint else tone)
            cover.add((int(x), int(y)))
    seg(scene, a, b, roof["hi"])  # ridge tiles
    if eaves:
        for p0, p1 in ((L, B), (B, R)):
            seg(scene, (p0[0], p0[1] + 1), (p1[0], p1[1] + 1), roof["outline"])
    return cover


def crenellate(scene, i, j, wi, wj, z, stone, cover, step=3, height=3, cross=None):
    """Merlons along the four top edges of a block, with a walkway behind them. cross: a colour for
    a small cross on each front merlon (Belém's cross of the Order of Christ)."""
    T, R, B, L = corners(scene, i, j, wi, wj, z)
    poly(scene, [T, R, B, L], lambda x, y: stone["mid"])
    for a, c, lit in ((T, R, False), (T, L, True), (L, B, True), (B, R, False)):
        steps = int(abs(c[0] - a[0])) or 1
        for k in range(0, steps + 1):
            if k % step >= step - 1:
                continue  # the gap (crenel) between merlons
            x = a[0] + (c[0] - a[0]) * k / steps
            y = a[1] + (c[1] - a[1]) * k / steps
            for dy in range(1, height + 1):
                tone = stone["hi"] if dy == height else stone["lit"] if lit else stone["dark"]
                scene.put(x, y - dy, tone)
                cover.add((int(x), int(y - dy)))
            if cross and (a, c) in ((L, B), (B, R)) and k % step == 0 and height >= 3:
                scene.put(x, y - 2, cross)


def stone_courses(stone, rows=4, every=6):
    """Ashlar: mortar courses every `rows` pixels, staggered vertical joints."""
    def pattern(u, v, lit):
        u, v = int(u), int(v)
        if v % rows == 0 or (u + (v // rows) * (every // 2)) % every == 0:
            return stone["line"] if lit else stone["deep"]
        return None
    return pattern


def arch_opening(u, v, centre, half, spring, colour):
    """True-colour for a round-headed opening centred at u=centre, `half` wide, springing at `spring`."""
    du = abs(u - centre)
    if du <= half and (v < spring or v < spring + math.sqrt(max(0, half * half - du * du))):
        return colour
    return None


# ----------------------------------------------------------------- Lisbon --

def castelo_sao_jorge(scene, i, j, elev):
    """São Jorge: crenellated curtain walls of old stone around the ward, square towers at the
    corners and midpoints, the gate, and the keep (Torre de Menagem) flying Portugal's flag."""
    W, D = 11, 9
    wall_h, tower_h = 16, 28
    courses = stone_courses(CASTLE)

    def gate_pattern(u, v, lit):
        if lit:
            g = arch_opening(u, v, W * 4, 3, 7, CASTLE["deep"] if v < 9 else rgb("#2E2620"))
            if g:
                return rgb("#2E2620")
        return courses(u, v, lit)

    def wall(a, b, wi, wj, pattern=courses):
        def draw(s):
            cover = facade(s, a, b, wi, wj, wall_h, pattern, palette=CASTLE, z0=elev)
            crenellate(s, a, b, wi, wj, elev + wall_h, CASTLE, cover)
            iso.outline(s, cover, CASTLE["outline"])
        scene.add(a + b + wi + wj, draw)

    def tower(a, b, size, height, flag=False):
        def draw(s):
            cover = facade(s, a, b, size, size, height,
                           lambda u, v, lit: (rgb("#2E2620") if int(u) % 6 in (2, 3) and height - 12 < v < height - 6
                                              else courses(u, v, lit)), palette=CASTLE, z0=elev)
            crenellate(s, a, b, size, size, elev + height, CASTLE, cover)
            if flag:
                x, y = P(s, a + size / 2, b + size / 2, elev + height + 3)
                for dy in range(0, 16):
                    s.put(x, y - dy, rgb("#3A3530"))
                for dy in range(10, 16):  # green at the hoist, red in the fly
                    for dx in range(1, 4):
                        s.put(x + dx, y - dy, rgb("#2E7D32"))
                    for dx in range(4, 9):
                        s.put(x + dx, y - dy, rgb("#D32F2F"))
                    s.put(x + 4, y - 13, GOLD)
            iso.outline(s, cover, CASTLE["outline"])
        scene.add(a + b + 2 * size + 0.2, draw)

    wall(i, j, W, 1)  # north
    wall(i, j + 1, 1, D - 1)  # west
    tower(i - 0.5, j - 0.5, 2, tower_h)
    tower(i + W / 2 - 1, j - 0.5, 2, tower_h - 2)
    tower(i + W - 1.5, j - 0.5, 2, tower_h)
    tower(i + 3, j + 2.5, 3.2, 40, flag=True)  # the keep
    tower(i - 0.5, j + D / 2 - 1, 2, tower_h - 2)
    wall(i + W - 1, j + 1, 1, D - 1)  # east
    wall(i + 1, j + D - 1, W - 2, 1, gate_pattern)  # south, with the gate
    tower(i - 0.5, j + D - 1.5, 2, tower_h)
    tower(i + W - 1.5, j + D - 1.5, 2, tower_h + 2)
    tower(i + W - 1.5, j + D / 2 - 1, 2, tower_h - 2)


def se_lisboa(scene, i, j):
    """Sé de Lisboa, the fortress-cathedral: two massive crenellated towers flank a deep Romanesque
    portal with receding archivolts and a rose window; behind, a crenellated nave under tiles and
    the lantern tower over the crossing. The west front faces the viewer (+j)."""
    W, L = 5.0, 9.0
    courses = stone_courses(LIOZ, rows=5, every=8)

    def front(u, v, lit, width):
        u, v = int(u), int(v)
        centre = width / 2
        if not lit:
            return rgb("#2E2620") if 30 <= v <= 36 and u % 5 in (2, 3) else courses(u, v, lit)
        for k, colour in enumerate((LIOZ["deep"], LIOZ["line"], LIOZ["mid"], rgb("#3A2E24"))):
            hole = arch_opening(u, v, centre, 6.5 - k * 1.4, 7, colour)
            if hole and (k == 3 or not arch_opening(u, v, centre, 6.5 - (k + 1) * 1.4, 7, colour)):
                return hole  # receding archivolts, darkest at the doors
        rose = math.hypot(u - centre, v - 22)
        if rose <= 5.0:
            return LIOZ["hi"] if rose > 4.0 else (GLASS["dark"] if (u + v) % 2 else rgb("#C9A0E0"))
        for tower_centre in (width * 0.17, width * 0.83):  # paired belfry openings
            if abs(u - tower_centre) <= 2.5 and 36 <= v <= 43 and u != int(tower_centre):
                return rgb("#2E2620")
        return courses(u, v, lit)

    def nave(s):
        cover = facade(s, i + 0.3, j, W - 0.6, L - 2, 26, lambda u, v, lit: (
            rgb("#2E2620") if int(u) % 7 == 3 and 14 <= v <= 20 else courses(u, v, lit)), palette=LIOZ)
        hip_roof(s, i + 0.3, j, W - 0.6, L - 2, 26, 9, cover=cover)
        lantern = facade(s, i + 1.2, j + 2, 1.8, 1.8, 40, courses, palette=LIOZ)
        crenellate(s, i + 1.2, j + 2, 1.8, 1.8, 40, LIOZ, lantern)
        iso.outline(s, cover | lantern, LIOZ["outline"])

    def west_front(s):
        fw = W * 8
        cover = set()
        # Towers stand forward; the lower centre with the portal and rose is set back between them.
        for x0, wi, height, depth, back in ((0.0, 1.7, 50, 1.4, 0.0), (1.7, 1.6, 34, 1.4, 0.0),
                                            (3.3, 1.7, 50, 1.4, 0.0)):
            offset = x0 * 8
            jj = j + L - 1.4 - back
            cover |= facade(s, i + x0, jj, wi, depth, height,
                            lambda u, v, lit, o=offset: front(u + o if lit else u, v, lit, fw), palette=LIOZ)
            crenellate(s, i + x0, jj, wi, depth, height, LIOZ, cover)
        iso.outline(s, cover, LIOZ["outline"])

    scene.add(i + j + W + L - 2, nave)
    scene.add(i + j + W + L + 0.5, west_front)


def torre_belem(scene, i, j):
    """Torre de Belém: a Manueline bastion in the Tagus with gun ports, domed corner watchtowers and
    shield-merlons; the tower above has a Venetian loggia, rope mouldings and a crenellated top."""
    def bartizan(s, x, y):
        for dy in range(0, 7):
            for dx in range(-2, 3):
                s.put(x + dx, y - dy, LIOZ["hi"] if dx < 0 else LIOZ["mid"] if dx == 0 else LIOZ["dark"])
        for dx, h in ((-2, 1), (-1, 3), (0, 4), (1, 3), (2, 1)):  # ribbed dome
            for dy in range(0, h):
                s.put(x + dx, y - 7 - dy, LIOZ["lit"] if dx <= 0 else LIOZ["dark"])
        s.put(x, y - 12, LIOZ["deep"])

    def draw(s):
        cover = facade(s, i, j, 5.5, 4.5, 15, lambda u, v, lit: (
            rgb("#2E2620") if int(u) % 7 in (3, 4) and 6 <= v <= 9 else
            LIOZ["line"] if v in (11, 12) and int(u) % 2 else None), palette=LIOZ)  # gun ports, rope moulding
        crenellate(s, i, j, 5.5, 4.5, 15, LIOZ, cover, step=3, height=4, cross=rgb("#C0392B"))
        for ci, cj in ((i, j + 4.5), (i + 5.5, j + 4.5), (i + 5.5, j)):
            bartizan(s, *P(s, ci, cj, 15))

        def tower_face(u, v, lit):
            u, v = int(u), int(v)
            if lit and 22 <= v <= 30 and 3 <= u <= 17:  # the Venetian loggia: a balcony of arches
                if v == 22:
                    return LIOZ["hi"]
                if u % 4 in (1, 2) and v < 29:
                    return rgb("#3A2E24")
                return LIOZ["mid"]
            if v in (12, 33) and u % 2:
                return LIOZ["line"]  # rope mouldings
            if 38 <= v <= 44 and u % 6 in (2, 3):
                return rgb("#3A2E24")
            return None
        tower = facade(s, i + 0.6, j + 0.4, 2.6, 2.6, 50, tower_face, palette=LIOZ, z0=15)
        crenellate(s, i + 0.6, j + 0.4, 2.6, 2.6, 65, LIOZ, tower, step=3, height=4, cross=rgb("#C0392B"))
        for ci, cj in ((i + 0.6, j + 3.0), (i + 3.2, j + 3.0), (i + 3.2, j + 0.4)):
            bartizan(s, *P(s, ci, cj, 65))
        top = facade(s, i + 1.4, j + 1.2, 1.2, 1.2, 8, None or (lambda u, v, lit: None), palette=LIOZ, z0=65)
        crenellate(s, i + 1.4, j + 1.2, 1.2, 1.2, 73, LIOZ, top, step=2, height=2)
        iso.outline(s, cover | tower | top, LIOZ["outline"])
    scene.add(i + j + 10, draw)


def arco_rua_augusta(scene, i, j):
    """Arco da Rua Augusta: a triumphal arch with paired columns, an entablature, a clock in the
    attic and the statue group of Glory crowning Genius and Valour."""
    W, D, H = 6.5, 1.8, 46

    def pattern(u, v, lit):
        u, v = int(u), int(v)
        width = W * 8 if lit else D * 8
        centre = width / 2
        if lit:
            vault = arch_opening(u, v, centre, 8, 20, rgb("#3A3026"))
            if vault:
                return vault
            for c in (centre - 12, centre - 15, centre + 12, centre + 15):  # paired columns
                if abs(u - c) <= 0.5 and 2 <= v <= 30:
                    return LIOZ["hi"]
                if abs(u - c) <= 1.5 and v in (30, 31):
                    return LIOZ["mid"]  # capitals
            if v in (32, 33):
                return LIOZ["line"]  # entablature
            if v >= 36 and math.hypot(u - centre, v - 40) < 3:  # the clock
                return rgb("#F6F4EE") if math.hypot(u - centre, v - 40) < 2.3 else rgb("#2E2A28")
        return None

    def draw(s):
        cover = facade(s, i, j, W, D, H, pattern, palette=LIOZ)
        T, R, B, L = corners(s, i, j, W, D, H)
        poly(s, [T, R, B, L], lambda x, y: LIOZ["mid"])
        x, y = P(s, i + W / 2, j + D / 2, H)
        for dy in range(0, 4):  # plinth of the statue group
            for dx in range(-7, 8):
                s.put(x + dx, y - dy, LIOZ["lit"] if dx < 2 else LIOZ["dark"])
        def figure(fx, base, height, seated, arms):
            """A stone statue: head, shoulders, robe; seated figures are wider and lower."""
            body_w = 2 if seated else 1
            for dy in range(0, height):
                w = body_w if dy < height - 3 else 1
                for dx in range(-w, w + 1):
                    s.put(x + fx + dx, y - base - dy, LIOZ["hi"] if dx < 0 else LIOZ["lit"] if dx == 0 else LIOZ["dark"])
            for dx in (-1, 0):  # head
                s.put(x + fx + dx, y - base - height, LIOZ["hi"])
                s.put(x + fx + dx, y - base - height - 1, LIOZ["lit"])
            if arms:  # Glory raises a wreath in each hand
                for k in range(1, 5):
                    s.put(x + fx - 1 - k, y - base - height + 2 - k, LIOZ["lit"])
                    s.put(x + fx + k, y - base - height + 2 - k, LIOZ["dark"])
                for wx in (-6, 5):
                    for ddx, ddy in ((0, 0), (1, 0), (0, 1), (1, 1), (-1, 0), (2, 1)):
                        s.put(x + fx + wx + ddx, y - base - height - 3 + ddy, rgb("#7A9A5A"))

        figure(-5, 4, 7, True, False)   # Valour, seated
        figure(5, 4, 7, True, False)    # Genius, seated
        figure(0, 4, 12, False, True)   # Glory, standing above them
        iso.outline(s, cover, LIOZ["outline"])
    scene.add(i + j + W + D, draw)


AZULEJO = (rgb("#2F5DA8"), rgb("#F2F4F6"), rgb("#7FA8D8"))


def lisbon_house(scene, i, j, wi, wj, floors, wall, seed, arcade=False, tiles=False, roof=TERRACOTTA):
    """A Lisbon house: pastel or azulejo-tiled walls, stone window frames, iron balconies on the
    first floor, a door, and a hipped terracotta roof with a chimney. arcade: Pombaline ground-floor
    arches (the arcades of Praça do Comércio)."""
    height = 9 * floors + 3
    pal = palette_of(wall)

    def pattern(u, v, lit):
        u, v = int(u), int(v)
        col = u % 7
        frame = rgb("#FFFFFF") if lit else rgb("#DCD6CC")
        if v <= 1:
            return pal["deep"]  # stone plinth
        if v < 10:  # ground floor
            if arcade:
                hole = arch_opening(u % 8, v, 4, 2.6, 5, rgb("#3A3026"))
                return hole or (frame if u % 8 in (0, 7) else None)
            if (u // 7 + seed) % 3 == 0 and 2 <= col <= 4 and v <= 8:
                return WOOD if v < 8 else frame
        level, inside = divmod(v - 10, 9)
        if 2 <= col <= 4 and 2 <= inside <= 7:
            if col == 3 or inside in (2, 7):
                return frame
            return rgb("#34405A") if (inside + seed) % 3 else rgb("#8FB4D8")
        if level == 0 and inside == 1 and 1 <= col <= 5:
            return IRON  # first-floor balconies
        if inside == 1 and 2 <= col <= 4:
            return frame  # sills
        if v >= height - 1:
            return frame  # cornice
        if tiles:  # azulejo façade: a small blue-and-white pattern
            return AZULEJO[0] if (u + v) % 3 == 0 else AZULEJO[2] if (u - v) % 3 == 0 else AZULEJO[1]
        return None

    def draw(s):
        cover = facade(s, i, j, wi, wj, height, pattern, palette=pal)
        hip_roof(s, i, j, wi, wj, height, 5 + min(wi, wj) * 2, roof=roof, cover=cover)
        x, y = P(s, i + wi * 0.75, j + wj * 0.3, height + 4)
        for dy in range(0, 5):  # chimney
            s.put(x, y - dy, pal["lit"])
            s.put(x + 1, y - dy, pal["dark"])
        iso.outline(s, cover, rgb("#3A2A22"))
    scene.add(i + j + wi + wj, draw)


def tram_28(scene, i, j, along_j=True):
    """Lisbon's yellow Remodelado tram: rounded ends, a white roof band, a window band, red trim,
    the destination sign, wheels and the trolley pole."""
    wi, wj = (1.25, 3.4) if along_j else (3.4, 1.25)

    def body(u, v, lit):
        u, v = int(u), int(v)
        yellow = rgb("#F2C14E") if lit else rgb("#D9A436")
        if v <= 1:
            return rgb("#2E2A28") if u % 5 in (1, 2) else rgb("#8A3A26")  # wheels and skirt
        if v == 2:
            return rgb("#8A3A26")
        if 6 <= v <= 9 and u % 4 != 0 and 1 < u < (wj if along_j else wi) * 8 - 1:
            return rgb("#8FB4D8") if v == 9 else rgb("#34405A")  # windows
        if v >= 11:
            return rgb("#F6F2EA") if lit else rgb("#DCD6CC")  # white roof band
        return yellow

    def draw(s):
        cover = facade(s, i, j, wi, wj, 12, body, palette=palette_of(rgb("#F2C14E")))
        T, R, B, L = corners(s, i, j, wi, wj, 12)
        poly(s, [T, R, B, L], lambda x, y: rgb("#E8E2D6"))
        x, y = P(s, i + wi / 2, j + wj / 2, 12)
        seg(s, (x, y), (x + 9, y - 12), rgb("#2E2A28"))  # trolley pole
        sx, sy = P(s, i, j + wj, 10)
        for dx in range(1, 5):  # destination sign "28"
            s.put(sx + dx, sy + dx * 0.5 - 1, rgb("#2E2A28"))
        iso.outline(s, cover, rgb("#3A2A22"))
    scene.add(i + j + wi + wj, draw)


# ----------------------------------------------------------------- Madrid --

BRICK = rgb("#B4553C")


def palacio_real(scene, i, j):
    """Palacio Real: a rusticated granite base, white limestone above with giant pilasters and
    columns, pedimented balcony windows, a cornice and a balustrade crowned with statues; a
    projecting central bay and corner pavilions."""
    W, D, H = 15, 8, 42

    def pattern(u, v, lit, bay=7):
        u, v = int(u), int(v)
        base, hi, line, deep = (GRANITE["lit"], GRANITE["hi"], GRANITE["line"], GRANITE["deep"]) if lit else \
            (GRANITE["dark"], GRANITE["mid"], GRANITE["deep"], rgb("#6E6858"))
        col = u % bay
        if lit and abs(u - W * 4) <= 14 and 14 <= v < H - 4 and col in (0, 1, 6):
            return hi if col != 1 else GRANITE["mid"]  # the central portico's paired columns
        if v < 13:  # rusticated granite base with arched windows
            hole = arch_opening(col, v, 3.5, 1.6, 7, rgb("#3E4A5E"))
            return hole or (line if v % 3 == 0 or (u + (v // 3) * 3) % 7 == 0 else base)
        if v == 13:
            return line
        if v >= H - 4:
            if v == H - 4:
                return line  # cornice
            return hi if u % 3 else shade(base, -0.1)  # balustrade
        if col == 0:
            return hi  # giant pilasters
        if col == 1:
            return shade(base, -0.06)
        for top in (28, 38):  # two floors of tall windows with pediments and balconies
            if 3 <= col <= 5 and top - 11 <= v <= top - 3:
                return rgb("#3E4A5E") if (col + v) % 4 else rgb("#8FB4D8")
            if 2 <= col <= 6 and v == top - 2:
                return hi  # pediment
            if 2 <= col <= 6 and v == top - 12:
                return IRON  # balcony
        return base

    def block(a, b, wi, wj, height, roof=True):
        def draw(s):
            cover = facade(s, a, b, wi, wj, height, lambda u, v, lit: pattern(u, v, lit) if v < height else None,
                           palette=GRANITE)
            T, R, B, L = corners(s, a, b, wi, wj, height)
            poly(s, [T, R, B, L], lambda x, y: SLATE["mid"])
            for p0, p1 in ((L, B), (B, R)):  # statues on the balustrade
                steps = int(abs(p1[0] - p0[0]))
                for k in range(3, steps - 2, 7):
                    x = p0[0] + (p1[0] - p0[0]) * k / steps
                    y = p0[1] + (p1[1] - p0[1]) * k / steps
                    for dy in range(1, 6):
                        s.put(x, y - dy, GRANITE["hi"] if dy < 5 else GRANITE["mid"])
            iso.outline(s, cover, GRANITE["outline"])
        return draw

    def main_block(s):
        block(i, j, W, D, H)(s)
        # The great courtyard: seen from above, its inner walls on the far sides and its floor.
        ci, cj, cw, cd = i + 3, j + 2.4, W - 6, D - 4.8
        ti, ri, bi, li = corners(s, ci, cj, cw, cd, H)
        t0, r0, b0, l0 = corners(s, ci, cj, cw, cd, 0)
        inner = iso.polygon_pixels([ti, ri, bi, li])
        inside = set(inner)
        for x, y in iso.polygon_pixels([t0, r0, b0, l0]):  # the floor, seen only through the opening
            if (int(x), int(y)) in inside:
                s.put(x, y, GRANITE["mid"] if (int(x) + int(y)) % 5 else GRANITE["line"])
        for a0, c0, a1, c1, lit in ((t0, r0, ti, ri, True), (t0, l0, ti, li, False)):
            for x, y in iso.polygon_pixels([a0, c0, c1, a1]):
                if (int(x), int(y)) in inside:
                    window = int(x) % 7 in (3, 4) and int(y) % 9 in (2, 3, 4, 5)
                    s.put(x, y, rgb("#3E4A5E") if window else GRANITE["lit"] if lit else GRANITE["dark"])
        for x, y in inner:  # shade where the far wings fall into the court
            if (int(x) + int(y)) % 9 == 0:
                s.put(x, y, GRANITE["deep"])
    scene.add(i + j + W + D, main_block)
    for a, b in ((i - 0.4, j + D - 2.6), (i + W - 2.6, j + D - 2.6)):  # corner pavilions
        scene.add(a + b + 6, block(a, b, 3, 3, H + 4))


def almudena(scene, i, j):
    """Almudena Cathedral: a neo-classical front between two bell towers with small domes, and
    behind it the great blue-grey dome on a windowed drum with its lantern and cross."""
    W, L = 5.6, 9.0

    def front(u, v, lit):
        u, v = int(u), int(v)
        if lit:
            hole = arch_opening(u, v, W * 4, 3.2, 10, rgb("#3A3026"))
            if hole:
                return hole
            if v in (16, 17, 30):
                return GRANITE["line"]
            if u % 6 == 0 and v < 30:
                return GRANITE["hi"]  # pilasters
            if u % 6 in (2, 3, 4) and 20 <= v <= 27:
                return rgb("#3E4A5E")
        return None

    def nave_wall(u, v, lit):
        u, v = int(u), int(v)
        if v in (12, 28):
            return GRANITE["line"]
        if u % 8 == 0:
            return GRANITE["hi"] if lit else GRANITE["mid"]  # pilasters
        hole = arch_opening(u % 8, v, 4, 1.6, 20, rgb("#3E4A5E"))
        if hole and v > 15:
            return hole  # clerestory windows
        return front(u, v, lit) if lit else None

    def tower_face(u, v, lit):
        u, v = int(u), int(v)
        if v in (14, 30, 46):
            return GRANITE["line"]
        if u in (0, 1) or u >= 11:
            return GRANITE["hi"] if lit else GRANITE["mid"]  # corner pilasters
        hole = arch_opening(u, v, 6.5, 2.4, 37, rgb("#3A3026"))
        if hole and v >= 33:
            return hole  # the arched belfry
        if 18 <= v <= 26 and 5 <= u <= 8:
            return rgb("#3E4A5E")
        return None

    def draw(s):
        cover = facade(s, i + 0.4, j, W - 0.8, L - 2, 30, nave_wall, palette=GRANITE)
        hip_roof(s, i + 0.4, j, W - 0.8, L - 2, 30, 8, roof=SLATE, cover=cover)
        for x0 in (0.0, W - 1.6):
            tw = facade(s, i + x0, j + L - 2.6, 1.6, 1.6, 48, tower_face, palette=GRANITE)
            x, y = P(s, i + x0 + 0.8, j + L - 1.8, 48)
            for dy in range(0, 4):  # drum under the tower dome
                for dx in range(-6, 7):
                    s.put(x + dx, y - dy, GRANITE["lit"] if dx < 2 else GRANITE["dark"])
            egg_dome(s, x, y - 4, 7, 10, (SLATE["hi"], SLATE["lit"], SLATE["dark"]))
            for dy in range(14, 18):
                s.put(x, y - dy, GRANITE["hi"] if dy < 17 else GOLD)
            cover |= tw
        front_block = facade(s, i + 1.6, j + L - 2.6, W - 3.2, 1.2, 34, front, palette=GRANITE)
        x, y = P(s, i + 1.6 + (W - 3.2) / 2, j + L - 1.4, 34)
        for dy in range(0, 6):  # pediment
            for dx in range(-9 + dy, 10 - dy):
                s.put(x + dx, y - dy, GRANITE["hi"] if dx < 0 else GRANITE["mid"])
        cx, cy = P(s, i + W / 2, j + (L - 2) / 2, 40)
        for dy in range(0, 12):  # the drum, with windows between pilasters
            for dx in range(-11, 12):
                window = dx % 4 == 2 and 3 <= dy <= 9
                s.put(cx + dx, cy - dy, rgb("#3E4A5E") if window else GRANITE["lit"] if dx < 3 else GRANITE["dark"])
        egg_dome(s, cx, cy - 12, 12, 16, (SLATE["hi"], SLATE["lit"], SLATE["dark"]))
        for dy in range(28, 36):  # lantern and cross
            s.put(cx, cy - dy, GRANITE["hi"] if dy < 33 else GOLD)
            if dy < 33:
                s.put(cx + 1, cy - dy, GRANITE["dark"])
        s.put(cx - 1, cy - 34, GOLD)
        s.put(cx + 1, cy - 34, GOLD)
        iso.outline(s, cover | front_block, GRANITE["outline"])
    scene.add(i + j + W + L, draw)


ALMAGRE = rgb("#A8473A")  # the Plaza Mayor's deep red


def madrid_house(scene, i, j, wi, wj, floors, wall, seed, roof=SLATE, mansard_roof=True, corner_dome=False):
    """A Madrid house: brick, ochre or cream walls, white stone window surrounds, an iron balcony on
    every floor, a slate mansard with dormers (or a tiled roof), and sometimes a domed corner."""
    height = 9 * floors + 3
    pal = palette_of(wall)

    def pattern(u, v, lit):
        u, v = int(u), int(v)
        col = u % 7
        frame = rgb("#F6F2EA") if lit else rgb("#D9D4CA")
        if v <= 1:
            return pal["deep"]
        if v < 10:
            if 2 <= col <= 4 and v <= 8:
                return WOOD if (u // 7 + seed) % 2 == 0 else rgb("#34405A")
            return pal["dark"] if v % 3 == 0 else None
        level, inside = divmod(v - 10, 9)
        if 2 <= col <= 4 and 2 <= inside <= 7:
            return frame if col in (2, 4) or inside == 7 else rgb("#34405A") if inside > 3 else rgb("#8FB4D8")
        if inside == 1 and 1 <= col <= 5:
            return IRON  # a balcony on every floor
        if v >= height - 1:
            return frame
        return None

    def draw(s):
        cover = facade(s, i, j, wi, wj, height, pattern, palette=pal)
        if mansard_roof:
            mansard(s, i, j, wi, wj, height, 9, 0.35, roof=SLATE, dormers=6, cover=cover)
        else:
            hip_roof(s, i, j, wi, wj, height, 5 + min(wi, wj) * 2, cover=cover)
        if corner_dome:
            x, y = P(s, i + wi, j + wj, height + 4)
            egg_dome(s, x, y, 5, 9, (SLATE["hi"], SLATE["lit"], SLATE["dark"]))
            s.put(x, y - 10, GOLD)
        iso.outline(s, cover, rgb("#3A2A22"))
    scene.add(i + j + wi + wj, draw)


def plaza_mayor(scene, i, j, size=11):
    """Plaza Mayor: an enclosed square of deep-red arcaded ranges under slate, the Casa de la
    Panadería with its two slate spires and painted façade, and Philip III on horseshoe."""
    def range_(a, b, wi, wj, panaderia=False):
        pal = palette_of(ALMAGRE)

        def pattern(u, v, lit):
            u, v = int(u), int(v)
            hole = arch_opening(u % 6, v, 3, 2.2, 5, rgb("#3A2A22")) if v < 9 else None
            if hole:
                return hole  # the porticoes
            if v < 9:
                return rgb("#D9CFC0") if u % 6 in (0, 5) else None  # granite piers
            if panaderia and lit and 10 <= v <= 34 and (u + v) % 5 == 0:
                return rgb("#E9B872") if (u // 3) % 2 else rgb("#6E9AC8")  # the painted façade
            inside = (v - 9) % 8
            if u % 6 in (2, 3) and 2 <= inside <= 6:
                return rgb("#34405A") if inside > 2 else rgb("#F6F2EA")
            if inside == 1 and u % 6 in (1, 2, 3, 4):
                return IRON
            return None

        def draw(s):
            cover = facade(s, a, b, wi, wj, 36, pattern, palette=pal)
            mansard(s, a, b, wi, wj, 36, 8, 0.3, roof=SLATE, dormers=6, cover=cover)
            if panaderia:
                for ta in (a + 0.3, a + wi - 1.5):  # the twin slate spires
                    x, y = P(s, ta + 0.6, b + wj / 2, 44)
                    for dy in range(0, 20):
                        w = max(0, 4 - dy // 4)
                        for dx in range(-w, w + 1):
                            s.put(x + dx, y - dy, SLATE["lit"] if dx < 0 else SLATE["dark"] if dx > 0 else SLATE["mid"])
                    s.put(x, y - 21, GOLD)
            iso.outline(s, cover, rgb("#3A2A22"))
        scene.add(a + b + wi + wj, draw)

    range_(i, j, size, 1.6, panaderia=True)  # north range: the Casa de la Panadería
    range_(i, j + 1.6, 1.6, size - 3.2)  # west
    range_(i + size - 1.6, j + 1.6, 1.6, size - 3.2)  # east
    range_(i, j + size - 1.6, size, 1.6)  # south

    def statue(s):
        x, y = P(s, i + size / 2, j + size / 2)
        for dy in range(0, 6):
            for dx in range(-3, 4):
                s.put(x + dx, y - dy, GRANITE["lit"] if dx < 1 else GRANITE["dark"])
        horse = [(-3, 6), (-2, 6), (-1, 6), (0, 6), (1, 6), (2, 6), (3, 7), (3, 8), (-3, 7), (-3, 8), (2, 7),
                 (-1, 7), (0, 7), (1, 7), (0, 8), (0, 9), (0, 10), (-1, 9), (1, 9), (3, 9), (4, 9)]
        for dx, dy in horse:
            s.put(x + dx, y - dy, rgb("#5E5038"))
        s.put(x, y - 11, rgb("#7A6A48"))
    scene.add(i + j + size, statue)


def casa_correos(scene, i, j):
    """Real Casa de Correos on Puerta del Sol: brick with white stone dressings, a projecting
    centre and the clock tower with its bell under a small slate dome."""
    W, D = 8, 3.5

    def draw(s):
        pal = palette_of(BRICK)
        cover = facade(s, i, j, W, D, 30, lambda u, v, lit: (
            rgb("#F6F2EA") if int(u) % 8 in (0, 7) or v in (10, 29) else
            rgb("#34405A") if int(u) % 8 in (3, 4) and (13 <= v <= 20 or 22 <= v <= 27) else
            rgb("#3A2A22") if int(u) % 8 in (3, 4) and v <= 7 else None), palette=pal)
        mansard(s, i, j, W, D, 30, 7, 0.3, roof=SLATE, dormers=7, cover=cover)
        tower = facade(s, i + W / 2 - 0.9, j + D / 2 - 0.9, 1.8, 1.8, 18, lambda u, v, lit: (
            rgb("#F6F4EE") if 6 <= v <= 11 and 3 <= int(u) <= 10 and lit else None),
            palette=palette_of(rgb("#EDE8DE")), z0=37)
        x, y = P(s, i + W / 2 - 0.9, j + D / 2 + 0.9, 37)
        cx, cy = x + 7, y - 9
        for dx in range(-3, 4):  # the clock face
            for dy in range(-3, 4):
                if dx * dx + dy * dy <= 10:
                    s.put(cx + dx, cy + dy, rgb("#2E2A28") if dx * dx + dy * dy > 6 or (dx, dy) in ((0, -1), (0, -2), (1, 0)) else rgb("#FFFFFF"))
        tx, ty = P(s, i + W / 2, j + D / 2, 55)
        egg_dome(s, tx, ty, 6, 7, (SLATE["hi"], SLATE["lit"], SLATE["dark"]))
        s.put(tx, ty - 8, GOLD)
        iso.outline(s, cover | tower, rgb("#3A2A22"))
    scene.add(i + j + W + D, draw)


def metropolis(scene, i, j):
    """Metrópolis: a curved stone rotunda, giant paired columns and balconies, an attic with
    relief panels, and a black-and-gold cupola with oculi and a bronze winged Victory.

    The rotunda's circular plan projects to a 2:1 ellipse. Cornices, windows and column feet
    follow its near arc, with the centre closest to the viewer, as on the isometric blocks.
    """
    def draw(s):
        x, y = P(s, i, j)
        r, height = 15, 55

        def wing_windows(u, v, lit):
            u, v = int(u), int(v)
            if v in (2, 13, 26, 40):
                return GRANITE["line"]
            if u % 8 in (2, 3, 4, 5) and (4 <= v <= 10 or 17 <= v <= 23 or 30 <= v <= 37):
                return GRANITE["hi" if lit else "mid"] if u % 8 in (2, 5) else BLACK_SLATE["mid"]
            if v in (15, 28) and u % 8 in (1, 3, 5):
                return IRON
            return None

        # The set-back street wing joins the rotunda instead of leaving a freestanding tower.
        cover = facade(s, i - 1.8, j - 2.6, 2.8, 2.5, 41, wing_windows, palette=GRANITE)
        mansard(s, i - 1.8, j - 2.6, 2.8, 2.5, 41, 5, 0.35,
                roof=SLATE, dormers=7, cover=cover)

        def put(dx, dy, tone):
            s.put(x + dx, y + dy, tone)
            cover.add((int(x + dx), int(y + dy)))

        def front(dx, radius=r):
            return math.sqrt(max(0, radius * radius - dx * dx)) / 2

        def stone(dx):
            return GRANITE["hi" if dx < -7 else "lit" if dx < 2 else "mid" if dx < 10 else "dark"]

        def band(z, radius, thickness=2):
            # Only the exposed ledge: the rotunda above hides the rear of the ellipse.
            for dy in range(-math.ceil(radius / 2), math.ceil(radius / 2) + 1):
                for dx in range(-radius, radius + 1):
                    if dx * dx + (dy * 2) ** 2 <= radius * radius and \
                            (abs(dx) > r or dy >= front(dx)):
                        put(dx, dy - z, GRANITE["lit"])
            for dx in range(-radius, radius + 1):
                for dz in range(thickness):
                    put(dx, front(dx, radius) - z + dz,
                        stone(dx) if dz == 0 else GRANITE["line"])

        for dx in range(-r, r + 1):
            for z in range(height + 1):
                tone = stone(dx)
                # Rusticated lower storey, with a restrained joint every fourth course.
                if z < 14 and (z % 4 == 0 or (dx + z // 4 * 3) % 8 == 0):
                    tone = GRANITE["line"]
                put(dx, front(dx) - z, tone)

        for cx in (-9, 0, 9):
            for z0, z1 in ((3, 12), (20, 28), (31, 40)):
                for dx in range(cx - 2, cx + 3):
                    for z in range(z0, z1 + 1):
                        # Stone archivolts around recessed, divided windows.
                        if z > z1 - 2 and abs(dx - cx) == 2:
                            continue
                        frame = abs(dx - cx) == 2 or z in (z0, z1)
                        tone = stone(dx) if frame else BLACK_SLATE["mid"]
                        if not frame and dx == cx:
                            tone = GRANITE["line"]
                        put(dx, front(dx) - z, tone)
                if z0 > 3:
                    # Projecting balcony sill, fine iron rail and separate balusters.
                    for dx in range(cx - 3, cx + 4):
                        put(dx, front(dx) - z0 + 1, stone(dx))
                        put(dx, front(dx) - z0 - 2, IRON)
                        if (dx - cx) % 2 == 0:
                            put(dx, front(dx) - z0 - 1, IRON)

        band(15, r + 1)
        # Giant paired columns span two floors; distinct bases and leafy capitals.
        for cx in (-13, -5, 5, 13):
            for dx in (cx - 1, cx + 1):
                for z in range(17, 42):
                    put(dx, front(dx) - z, stone(dx - 3))
                put(dx + 1, front(dx) - 40, GRANITE["line"])
            for dx in range(cx - 2, cx + 3):
                for z in (17, 41, 42):
                    put(dx, front(dx) - z, stone(dx))
        band(44, r + 2, 3)

        # Attic reliefs and round-headed openings beneath the overhanging cornice.
        for cx in (-9, 0, 9):
            for dx in range(cx - 2, cx + 3):
                for z in range(47, 52):
                    edge = abs(dx - cx) == 2 or z in (47, 51)
                    tone = GRANITE["line"] if edge else stone(dx)
                    if abs(dx - cx) <= 1 and z in (48, 49):
                        tone = GRANITE["deep"] if cx else GRANITE["mid"]
                    put(dx, front(dx) - z, tone)
        band(height, r + 2, 2)
        iso.outline(s, cover, GRANITE["outline"])

        # A full, shouldered cupola. Horizontal rings are projected from circular sections,
        # so the dome and its curved gold swags share the rotunda's volume.
        dome_base, dome_h = height + 1, 20
        roof_cover = set()

        def roof_put(dx, dy, tone):
            s.put(x + dx, y + dy, tone)
            roof_cover.add((int(x + dx), int(y + dy)))

        def radius(z):
            return 3 + 12 * math.sqrt(max(0, 1 - (z / dome_h) ** 2))

        for z in range(dome_h + 1):
            rr = radius(z)
            for dx in range(-int(rr), int(rr) + 1):
                arc = front(dx, rr)
                tone = BLACK_SLATE["lit" if dx < -rr * 0.35 else "mid" if dx < rr * 0.4 else "dark"]
                if dx < -rr * 0.55 and z > 8:
                    tone = BLACK_SLATE["hi"]
                roof_put(dx, arc - dome_base - z, tone)
        iso.outline(s, roof_cover, BLACK_SLATE["outline"])

        # Curved gilded ribs and festoons, with a dark gap between each gold detail.
        for z in range(dome_h + 1):
            rr = radius(z)
            for t in (-0.83, -0.28, 0.36, 0.86):
                dx = round(rr * t)
                if z > 13 or z < 4:
                    roof_put(dx, front(dx, rr) - dome_base - z, GOLD if t < 0 else GOLD_DARK)
        for z in (1, 16, 19):
            rr = radius(z)
            for dx in range(-int(rr), int(rr) + 1):
                roof_put(dx, front(dx, rr) - dome_base - z, GOLD if dx < 0 else GOLD_DARK)
        for centre in (-7, 4):
            for dx in range(centre - 4, centre + 5):
                z = 5 + abs(dx - centre) // 2
                roof_put(dx, front(dx, radius(z)) - dome_base - z, GOLD if dx < 0 else GOLD_DARK)

        # Two raised oval dormers, with stone rims and gold crowns, on the black slate.
        for cx in (-7, 6):
            cy = front(cx, radius(10)) - dome_base - 10
            for dx in range(-2, 3):
                for dy in range(-3, 4):
                    d = (dx / 2.2) ** 2 + (dy / 3.2) ** 2
                    if d <= 1:
                        roof_put(cx + dx, cy + dy,
                                 stone(cx) if d > 0.42 else BLACK_SLATE["outline"])
            roof_put(cx, cy - 4, GOLD)

        # Gilded crown and plinth, then the dark bronze Victory with distinct feathered wings.
        apex = dome_base + dome_h
        for dz, width in ((0, 3), (1, 2), (2, 2), (3, 1)):
            for dx in range(-width, width + 1):
                roof_put(dx, -apex - dz, GOLD if dx <= 0 else GOLD_DARK)
        victory = [(-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1), (0, 2), (0, 3),
                   (1, 3), (0, 4), (1, 4), (0, 5), (0, 6), (0, 7),
                   (-1, 5), (-2, 6), (-3, 7), (-4, 8), (-5, 10), (-4, 10), (-3, 9),
                   (-2, 8), (-1, 7), (1, 5), (2, 6), (3, 7), (4, 9), (5, 11),
                   (4, 11), (3, 10), (2, 8), (1, 7), (-1, 9), (0, 9)]
        for dx, dz in victory:
            roof_put(dx, -apex - 4 - dz, BRONZE["hi" if dx < 0 else "lit" if dx == 0 else "dark"])
    scene.add(i + j + 1, draw)


def puerta_alcala(scene, i, j):
    """Puerta de Alcalá: a granite gate with three round arches and two square openings, paired
    Ionic columns, and the central attic with its pediment and sculpture."""
    W, D, H = 8, 1.8, 34

    def pattern(u, v, lit):
        if not lit:
            return None
        u, v = int(u), int(v)
        for k in range(5):
            c = W * 8 * (k + 0.5) / 5
            if k in (1, 2, 3):
                hole = arch_opening(u, v, c, 3.2, 13, rgb("#3A3026"))
            else:
                hole = rgb("#3A3026") if abs(u - c) <= 2.4 and v <= 13 else None
            if hole:
                return hole
            if abs(u - (c + W * 8 / 10)) <= 0.5 and 2 <= v <= 26:
                return GRANITE["hi"]  # columns between the openings
        if v in (27, 28):
            return GRANITE["line"]
        return None

    def draw(s):
        cover = facade(s, i, j, W, D, H, pattern, palette=GRANITE)
        T, R, B, L = corners(s, i, j, W, D, H)
        poly(s, [T, R, B, L], lambda x, y: GRANITE["mid"])
        x, y = P(s, i + W / 2, j + D / 2, H)
        for dy in range(0, 8):  # attic with pediment
            for dx in range(-10 + max(0, dy - 3) * 2, 11 - max(0, dy - 3) * 2):
                s.put(x + dx, y - dy, GRANITE["hi"] if dx < 0 else GRANITE["mid"])
        for dx in (-9, -5, 5, 9):  # sculptures on the corners of the attic
            for dy in range(0, 5):
                s.put(x + dx, y - 3 - dy, GRANITE["lit"])
        iso.outline(s, cover, GRANITE["outline"])
    scene.add(i + j + W + D, draw)


def cibeles(scene, i, j):
    """Cibeles Fountain: a round basin with jets, the goddess enthroned on her chariot drawn by two
    lions, in white marble."""
    def draw(s):
        x, y = P(s, i, j)
        for dy in range(-7, 8):
            for dx in range(-15, 16):
                r = (dx / 15) ** 2 + (dy / 7.5) ** 2
                if r <= 1:
                    rim = r > 0.8
                    s.put(x + dx, y + dy, GRANITE["mid"] if rim else rgb("#4C8CC8") if (dx + dy) % 6 else rgb("#E4F4FA"))
        for dy in range(0, 5):  # the chariot
            for dx in range(-4, 5):
                s.put(x + dx, y - dy, GRANITE["hi"] if dx < 1 else GRANITE["dark"])
        for dy in range(5, 13):  # the goddess, with her sceptre
            for dx in (-1, 0, 1):
                if dy < 11 or dx == 0:
                    s.put(x + dx, y - dy, GRANITE["hi"] if dx <= 0 else GRANITE["mid"])
        for dy in range(9, 15):
            s.put(x + 3, y - dy, GRANITE["dark"])
        for lx in (-9, -6):  # two lions
            for dx, dy in ((0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (2, 1), (3, 1), (3, 2), (0, 2)):
                s.put(x + lx + dx, y - dy - 1, GRANITE["lit"] if dy < 2 else GRANITE["hi"])
        for jet in (-12, 12):  # water jets
            for dy in range(0, 6):
                s.put(x + jet + (dy // 3) * (1 if jet < 0 else -1), y - dy, rgb("#E4F4FA"))
    scene.add(i + j + 1, draw)


def palacio_cristal(scene, i, j):
    """Palacio de Cristal in the Retiro: white iron and glass over a ceramic-tiled brick base, a
    glazed barrel vault and dome, and a portico of columns."""
    W, D = 6, 3.5

    def glass(u, v, lit):
        u, v = int(u), int(v)
        if v < 4:
            return rgb("#B4553C") if (u + v) % 4 else rgb("#2F5DA8")  # tiled brick base
        if u % 3 == 0 or v % 4 == 0:
            return rgb("#F2F2EE") if lit else rgb("#D2D2CC")  # white iron frame
        return GLASS["lit"] if lit else GLASS["dark"]

    def draw(s):
        cover = facade(s, i, j, W, D, 18, glass, palette=GRANITE)
        T, R, B, L = corners(s, i, j, W, D, 18)
        poly(s, [T, R, B, L], lambda x, y: GLASS["mid"] if (int(x) + int(y)) % 3 else rgb("#F2F2EE"))
        x, y = P(s, i + W / 2, j + D / 2, 18)
        for dy in range(-13, 1):  # glass dome on a ribbed iron frame, lit on the left
            for dx in range(-11, 12):
                if dx * dx / 121 + (dy / 13) ** 2 <= 1:
                    frame = dx % 4 == 0 or dy % 4 == 0
                    pane = GLASS["glint"] if dx < -5 and dy < -6 else GLASS["lit"] if dx < 0 else GLASS["mid"] if dx < 6 else GLASS["dark"]
                    s.put(x + dx, y + dy, (rgb("#F2F2EE") if dx < 3 else rgb("#C9CCD0")) if frame else pane)
        for dy in range(14, 17):
            s.put(x, y - dy, rgb("#F2F2EE"))
        iso.outline(s, cover, rgb("#5A6A7A"))
    scene.add(i + j + W + D, draw)


def alfonso_xii(scene, i, j):
    """Monument to Alfonso XII by the Retiro lake: a curved colonnade of paired columns under an
    entablature, on a stepped base down to the water, and before it a tall column carrying the
    king on horseback in bronze."""
    def draw(s):
        x, y = P(s, i, j)
        for k in range(-7, 8):  # the curved colonnade: chunky paired columns behind the column
            cx = x + k * 4
            cy = y - 4 + (k / 7) ** 2 * 9
            for dy in range(2, 18):
                s.put(cx, cy - dy, GRANITE["hi"] if k < 0 else GRANITE["lit"])
                s.put(cx + 1, cy - dy, GRANITE["mid"] if k < 0 else GRANITE["dark"])
            for dx in range(0, 4):  # continuous entablature and base
                for dy in (18, 19, 20):
                    s.put(cx + dx, cy - dy + (dx / 4) * (2 * k / 49) * 9, GRANITE["line"] if dy == 18 else GRANITE["lit"])
                for dy in (0, 1):
                    s.put(cx + dx, cy - dy, GRANITE["mid"])
        for step in range(3):  # steps down to the water
            for dx in range(-14 + step * 2, 15 - step * 2):
                s.put(x + dx, y + 2 + step * 2, GRANITE["lit"] if step % 2 else GRANITE["mid"])
                s.put(x + dx, y + 3 + step * 2, GRANITE["dark"])
        for dy in range(0, 36):  # the column with its plinth
            w = 3 if dy < 5 else 2
            for dx in range(-w, w + 1):
                s.put(x + dx, y + 2 - dy, GRANITE["hi"] if dx < 0 else GRANITE["mid"] if dx == 0 else GRANITE["dark"])
        horse = [(-4, 0), (-3, 0), (-2, 0), (-1, 0), (0, 0), (1, 0), (2, 0), (3, 1), (3, 2), (4, 2), (4, 3),
                 (-3, 1), (-3, 2), (-4, 2), (2, 1), (-1, 1), (0, 1), (1, 1), (0, 2), (-1, 2), (0, 3), (0, 4),
                 (-1, 3), (0, 5)]
        for dx, dy in horse:
            s.put(x + dx, y - 34 - dy, rgb("#6E5A3A") if dx < 1 else rgb("#4E4028"))
    scene.add(i + j + 1, draw)


# ---------------------------------------------------------------- preview --

if __name__ == "__main__":
    pastel = [rgb(c) for c in ("#F4D35E", "#F2A6A0", "#9CC3E0", "#F6F0E4", "#A8D5BA")]
    print(preview([lambda s: castelo_sao_jorge(s, 2, 2, 0), lambda s: se_lisboa(s, 13, 9)],
                  "lisbon-castle-se", size=(260, 210), origin=(120, 80), tiles=20))
    print(preview([lambda s: torre_belem(s, 2, 3), lambda s: arco_rua_augusta(s, 10, 3),
                   lambda s: tram_28(s, 11, 9)] +
                  [lambda s, n=n: lisbon_house(s, 2 + n * 3, 12, 3, 2, 3, pastel[n], n, tiles=(n == 2),
                                               arcade=(n == 0)) for n in range(4)],
                  "lisbon-belem-arch-houses", size=(260, 200), origin=(120, 70), tiles=20))
    print(preview([lambda s: palacio_real(s, 1, 1), lambda s: almudena(s, 3, 11)],
                  "madrid-palace-almudena", size=(280, 230), origin=(120, 70), tiles=22))
    print(preview([lambda s: plaza_mayor(s, 1, 1), lambda s: casa_correos(s, 14, 2),
                   lambda s: metropolis(s, 16, 10)],
                  "madrid-plaza-sol-metropolis", size=(280, 210), origin=(130, 70), tiles=22))
    print(preview([lambda s: metropolis(s, 5, 5)], "madrid-metropolis",
                  size=(120, 140), origin=(60, 75), tiles=10))
    print(preview([lambda s: puerta_alcala(s, 1, 2), lambda s: cibeles(s, 13, 4), lambda s: palacio_cristal(s, 3, 9),
                   lambda s: alfonso_xii(s, 13, 12)] +
                  [lambda s, n=n: madrid_house(s, 2 + n * 3, 15, 3, 2, 4, [BRICK, rgb("#E3B66B"), rgb("#EEE1C6")][n], n,
                                               corner_dome=(n == 1), mansard_roof=(n != 2)) for n in range(3)],
                  "madrid-alcala-retiro-houses", size=(260, 220), origin=(120, 70), tiles=22))
