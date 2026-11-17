"""Capital-city scenes: one illustrated isometric diorama per country (ART_CONTRACT.md, capital scale).

Each scene arranges the capital's real landmarks in their real relative positions, compressed to
fit one scene; it is an illustration, not a street-accurate map. Lisbon: the Tagus along the south,
Praça do Comércio with the Rua Augusta arch and its yellow arcades on the waterfront, the Baixa
grid behind it, a cobbled tram street climbing past the Sé cathedral to Alfama and São Jorge castle
on its hill, and Belém Tower in the river.

Writes assets/world/capitals/<id>.png and src/data/capitals.json.

    .venv/bin/python scripts/art/build_capitals.py
"""

import json
import math
from pathlib import Path

import iso
from iso import Box, rgb, shade, h01
import sprites

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "assets" / "world" / "capitals"
DATA = ROOT / "src" / "data" / "capitals.json"
IMAGES = ROOT / "src" / "data" / "capital-images.ts"
WIDTH, HEIGHT = 720, 520
CENTER_TILE = 40

C = {k: rgb(v) for k, v in {
    "grass": "#8AC240", "grass_dark": "#74AC3D", "grass_light": "#A3CF4E",
    "cobble": "#B9B1A3", "cobble_dark": "#9C9486", "cobble_light": "#D2CBBE",
    "pave": "#D6CDBB", "pave_dark": "#BDB3A0",
    "calcada": "#EFE9DB", "calcada_wave": "#5E5E62",
    "quay": "#DCD2BC", "quay_joint": "#B8AD94",
    "water": "#2E6DAF", "water_light": "#4C8CC8", "water_deep": "#25579A", "foam": "#E4F4FA",
    "sand": "#E8D3A0", "stone": "#DCD1B8", "limestone": "#EDE6D3", "roof": "#D9643A",
    "rail": "#4E4A46", "yellow": "#F2C14E",
}.items()}
FACADES = [rgb(c) for c in ("#F4D35E", "#F2A6A0", "#F6F0E4", "#9CC3E0", "#E9B872", "#F2C9A0",
                            "#A8D5BA", "#F6F0E4", "#E07A5F", "#F4D35E")]
ROOFS = [rgb(c) for c in ("#D9643A", "#CF5A34", "#E07040", "#D86A44")]


def tile_of(sx, sy):
    """Tile for screen-space diagonal coordinates (sx = i - j, sy = i + j)."""
    return (sy + sx) / 2, (sy - sx) / 2


def to_s(i, j):
    return i - j, i + j


# ------------------------------------------------------------------ sprites --

def round_tree(seed, palette="#5FA83C", outline="#22472A", size=1.0):
    s = sprites.Sprite(int(15 * size) + 2, int(17 * size) + 2)
    w, h = s.w, s.h
    sprites.ground_shadow(s, w / 2, h - 1.6, w / 2 - 2)
    for y in range(int(h * 0.62), h - 1):
        s.put(w // 2 - 1, y, sprites.C["bark_lt"], sprites.C["bark_ol"])
        s.put(w // 2, y, sprites.C["bark"], sprites.C["bark_ol"])
    tones = sprites.ramp(palette, outline)
    j = h01(seed) - 0.5
    for cx, cy, r in ((w / 2 + j, h * 0.32, w * 0.33), (w * 0.3, h * 0.45, w * 0.26),
                      (w * 0.7 + j, h * 0.46, w * 0.25), (w / 2, h * 0.52, w * 0.26)):
        sprites.blob(s, cx, cy, r, r * 0.95, tones,
                     lambda x, y, nx, ny, t: tones[0][min(3, t + 1)] if h01(seed, x, y) < 0.09 else None)
    return s.image()


def umbrella_pine(seed):
    """Stone pine: a tall bare trunk under a flat, wide dark-green crown."""
    s = sprites.Sprite(23, 22)
    sprites.ground_shadow(s, 11.5, 20.4, 6)
    for y in range(8, 21):
        s.put(11 + (1 if y < 13 else 0), y, sprites.C["bark_lt"], sprites.C["bark_ol"])
        s.put(12 + (1 if y < 13 else 0), y, sprites.C["bark"], sprites.C["bark_ol"])
    tones = sprites.ramp("#4E8A3E", "#1E3A22")
    sprites.blob(s, 11.5, 5.0, 10.5, 3.6, tones)
    sprites.blob(s, 8.0, 3.2, 5.0, 2.4, tones)
    return s.image()


# ------------------------------------------------------------------ ground --

def ground_color(kind, x, y, seed=0):
    if kind == "grass":
        r = h01(x, y, 3)
        return C["grass_dark"] if r < 0.1 else C["grass_light"] if r < 0.16 else C["grass"]
    if kind == "cobble":
        if (x + 2 * (y % 2)) % 4 == 0:
            return C["cobble_dark"]
        return C["cobble_light"] if (x + y) % 7 == 0 else C["cobble"]
    if kind == "pave":
        return C["pave_dark"] if (x + 3 * (y % 2)) % 6 == 0 or y % 3 == 0 and x % 2 == 0 else C["pave"]
    if kind == "calcada":
        return C["calcada_wave"] if (y + round(2 * math.sin(x / 4.0))) % 7 == 0 else C["calcada"]
    if kind == "quay":
        return C["quay_joint"] if y % 4 == 0 or (x + (y // 4) * 4) % 8 == 0 else C["quay"]
    if kind == "sand":
        return shade(C["sand"], -0.08) if h01(x, y, 5) < 0.1 else C["sand"]
    if kind in ("water", "shallow"):
        base = C["water_light"] if kind == "shallow" else C["water"]
        if h01(x // 3, y, 9) < 0.02:
            return C["foam"]
        return C["water_deep"] if kind == "water" and h01(x // 6, y // 3, 4) < 0.25 else base
    return C["grass"]


# ---------------------------------------------------------- Lisbon, Madrid --
# Landmarks are built in true isometric 3D in scripts/art/landmarks_iberia.py.

import landmarks_iberia as lb
import landmarks_paris as lp

TAGUS = (rgb("#3E86C0"), rgb("#2E6DAF"), rgb("#5A9AD0"))
LISBON_WALLS = [rgb(c) for c in ("#F4D35E", "#F2A6A0", "#F6F0E4", "#9CC3E0", "#E9B872", "#F2C9A0",
                                 "#A8D5BA", "#F6F0E4", "#E8A27A", "#F4D35E")]
MADRID_WALLS = [rgb(c) for c in ("#B4553C", "#E3B66B", "#EEE1C6", "#E59A7A", "#F2EEE4", "#C96A4A",
                                 "#D9A66E", "#B4553C", "#EEE1C6")]


def rowboat(seed):
    s = sprites.Sprite(11, 6)
    for x in range(1, 10):
        s.put(x, 3, sprites.C["hull_lt"], sprites.C["hull_ol"])
        if 2 <= x <= 8:
            s.put(x, 4, sprites.C["hull"], sprites.C["hull_ol"])
    s.put(5, 2, rgb("#E2434E"), sprites.C["hull_ol"])
    s.put(5, 1, rgb("#F2C9A0"), sprites.C["hull_ol"])
    s.put(2, 2, sprites.C["bark"], sprites.C["bark"])
    s.put(8, 2, sprites.C["bark"], sprites.C["bark"])
    return s.image()


def new_scene():
    ox = WIDTH / 2
    oy = HEIGHT / 2 - CENTER_TILE * 2 * 4
    return iso.Scene(WIDTH, HEIGHT, (ox, oy))


def visible_tiles(scene, margin=50):
    for i in range(-20, 120):
        for j in range(-20, 120):
            x, y = scene.screen(i, j)
            if -16 < x < WIDTH + 16 and -margin < y < HEIGHT + 8:
                yield i, j


def paint_ground(scene, kinds, elev, water, wall_stone):
    wall = iso.stone_wall(wall_stone)
    for (i, j) in sorted(kinds, key=lambda t: (t[0] + t[1], t[0])):
        kind, e = kinds[(i, j)], elev.get((i, j), 0)

        def color(x, y, k=kind):
            if k == "water":
                if h01(x // 3, y, 9) < 0.02:
                    return rgb("#E4F4FA")
                return water[1] if h01(x // 6, y // 2, 4) < 0.3 else water[0]
            if k == "quay":
                return rgb("#D8CDB2") if (x + y) % 6 else rgb("#B3A68C")
            if k == "gravel":
                return shade(rgb("#E6DAB8"), -0.08) if h01(x, y, 6) < 0.15 else rgb("#E6DAB8")
            return ground_color("pave" if k in ("lot", "court") else k, x, y)
        iso.ground_tile(scene, i, j, color, e, wall if e else None)


def lisbon():
    scene = new_scene()
    # The Tagus lies beyond a shoreline along the i axis (lower left); Alfama climbs to the castle
    # (upper right); the Baixa grid runs north from Praça do Comércio on the waterfront.
    shore = lambda i: 62 + 2 * math.sin(i / 9)
    hill = (52, 18)
    tram_path = [(46, 36), (50, 37), (53, 34), (54, 30), (54, 27), (53, 25)]

    def near_tram(i, j):
        return any(math.hypot(i - (a[0] + (b[0] - a[0]) * t), j - (a[1] + (b[1] - a[1]) * t)) < 1.0
                   for a, b in zip(tram_path, tram_path[1:]) for t in (k / 8 for k in range(9)))

    kinds, elev = {}, {}
    for i, j in visible_tiles(scene):
        hill_r = math.hypot(i - hill[0], (j - hill[1]) * 1.1)
        if j > shore(i) + 0.5:
            kind = "water"
        elif j > shore(i) - 1.5:
            kind = "quay"
        elif 33 <= i <= 45 and 49 <= j:
            kind = "calcada"  # Praça do Comércio, open to the river
        elif hill_r < 9.5:
            kind = "grass"
        elif 35 <= i <= 43 and 19 <= j <= 23:
            kind = "calcada"  # Rossio, at the top of the Baixa
        elif near_tram(i, j) or (38 <= i <= 39 and 24 <= j < 47) or (j in (27, 32, 37, 42) and 26 <= i <= 48) \
                or (i in (32, 45) and 24 <= j <= 46):
            kind = "cobble"  # Tram 28's street, Rua Augusta and the Baixa's grid of streets
        elif i > 48 and (abs((i - 48) - (j - 34) * 0.9) < 0.7 or abs((i - 60) + (j - 40)) < 0.7):
            kind = "cobble"  # Alfama's winding lanes
        else:
            kind = "lot"
        kinds[(i, j)] = kind
        elev[(i, j)] = 14 if hill_r < 9.5 else 0

    reserved = set()

    def reserve(i, j, wi, wj, ground="pave"):
        for a in range(int(i), int(math.ceil(i + wi))):
            for b in range(int(j), int(math.ceil(j + wj))):
                reserved.add((a, b))
                if kinds.get((a, b)) == "lot":
                    kinds[(a, b)] = ground

    lb.castelo_sao_jorge(scene, hill[0] - 5, hill[1] - 4, 14)
    lb.se_lisboa(scene, 50, 40)
    reserve(49, 39, 7, 11)
    lb.arco_rua_augusta(scene, 35.5, 46.5)
    reserve(35, 46, 8, 3)
    for k in range(3):  # yellow Pombaline arcades: west side facing the square, north beside the arch
        lb.lisbon_house(scene, 30.5, 49 + k * 3.5, 2.5, 3.5, 3, rgb("#F2C14E"), k, arcade=True)
    for a0 in (30.5, 43.0):
        lb.lisbon_house(scene, a0, 46, 4.5 if a0 > 40 else 5, 2.5, 3, rgb("#F2C14E"), 7, arcade=True)
    reserve(30, 45, 19, 15)
    lb.torre_belem(scene, 27, shore(27) + 3)
    for (a, b, along) in ((47, 35.5, False), (57.2, 30, True)):
        lb.tram_28(scene, a, b, along_j=along)

    paint_ground(scene, kinds, elev, TAGUS, lb.CASTLE["dark"])

    # Houses: uniform Pombaline blocks in the Baixa, irregular pastel and azulejo houses in Alfama.
    for li in range(-12, 110, 3):
        for lj in range(-12, 110, 3):
            baixa = 26 <= li <= 48 and 22 <= lj <= 46
            for wi, wj in (((3, 3), (3, 2)) if baixa else ((3, 2), (2, 3), (2, 2))):
                cells = [(a, b) for a in range(li, li + wi) for b in range(lj, lj + wj)]
                if all(kinds.get(c) == "lot" and c not in reserved for c in cells):
                    reserved.update(cells)
                    seed = int(h01(li, lj, 7) * 1000)
                    floors = 4 if baixa else 2 + int(h01(seed, 9) * 2)
                    wall = LISBON_WALLS[int(h01(seed, 5) * len(LISBON_WALLS))]
                    lb.lisbon_house(scene, li, lj, wi, wj, floors, wall, seed,
                                    tiles=not baixa and h01(seed, 11) < 0.18)
                    break
                if kinds.get((li, lj)) == "lot" and (li, lj) not in reserved and h01(li, lj, 13) < 0.6:
                    for a in range(li, li + 2):
                        for b in range(lj, lj + 2):
                            if kinds.get((a, b)) == "lot" and (a, b) not in reserved:
                                kinds[(a, b)] = "garden"

    jacaranda = [round_tree(n, "#A98BD8", "#3E2A5E") for n in range(3)]
    green = [round_tree(n) for n in range(3)]
    pines = [umbrella_pine(n) for n in range(2)]
    for (i, j), kind in kinds.items():
        x, y = scene.screen(i + 0.5, j + 0.5, elev[(i, j)])
        pick = None
        if kind == "grass" and elev[(i, j)] and h01(i, j, 21) < 0.16:
            pick = pines[(i + j) % 2]
        elif kind == "quay" and i % 4 == 0:
            pick = green[i % 3]
        elif kind == "calcada" and (i in (33, 45)) and j % 3 == 0:
            pick = jacaranda[j % 3]
        elif kind in ("lot", "garden") and (i, j) not in reserved and h01(i, j, 22) < 0.4:
            pick = (jacaranda if h01(i, j, 23) < 0.45 else green)[(i * 7 + j) % 3]
        if pick is not None:
            scene.add(i + j + 1.5, lambda s, img=pick, x=x, y=y: s.sprite(img, x, y + 6))
    boat = sprites.sailboat(0)
    for i0, dj in ((14, 6), (44, 8), (58, 5), (70, 9), (30, 12)):
        x, y = scene.screen(i0, shore(i0) + dj)
        scene.add(i0 + shore(i0) + dj, lambda s, x=x, y=y: s.sprite(boat, x, y))

    scene.paint_objects()
    return scene.img.convert("RGB")


def madrid():
    scene = new_scene()
    # The city runs west to east across the scene (2.8 km against 0.7 km north-south, so east-west is
    # compressed most): the Palacio Real above the Manzanares, the Almudena facing it across the Plaza
    # de la Armería; Plaza Mayor; Puerta del Sol with the Casa de Correos; Calle de Alcalá climbing
    # north-east past the Metrópolis (where the Gran Vía forks off north-west) to Cibeles on the
    # Prado-Recoletos boulevard and the Puerta de Alcalá; then the Retiro, wholly east of the
    # boulevard, with the Estanque, Alfonso XII on its east bank and the Palacio de Cristal south-east.
    bank = lambda i: 76 + 2 * math.sin(i / 7)
    river = lambda i, j: bank(i) < j < bank(i) + 6  # the Manzanares, along the south-west
    alcala, gran_via, mayor = 46.5, 34.5, 49  # Calle de Alcalá (constant i), Gran Vía and Calle Mayor (constant j)
    pond = lambda i, j: 56 <= i <= 61 and 26 <= j <= 30  # the Estanque
    retiro = lambda i, j: i >= 48 and i - j >= 25
    # The Campo del Moro and the Vistillas gardens fall from the palace and the Almudena to the river.
    # The Plaza de Oriente's gardens lie east of the palace.
    campo = lambda i, j: j >= bank(i) + 7.5 or (j >= 53 and i < 22) or (j >= 60 and i - j < -32) or \
        28 <= i < 31 and 43 <= j < 52
    rects = [(22, 40, 53, 63), (27, 31, 42, 53),  # Plaza de la Armería; Plaza de Oriente's paving
             (41, 53, 44, 48),  # Puerta del Sol's south side, before the Casa de Correos
             (40, 53, 50, 67),  # Plaza Mayor and the streets around it
             (31, 42, 72, 76), (42, 46, 29, 33)]  # the Almudena's forecourt; the Metrópolis corner
    circles = [((48, 39), 4.5), ((46.5, 28), 3.5), ((46.5, 19.5), 7)]  # Sol, Cibeles, Independencia

    kinds = {}
    for i, j in visible_tiles(scene):
        ci, cj = i + 0.5, j + 0.5
        if river(i, j):
            kind = "water"
        elif river(i, j - 1.5) or river(i, j + 1.5):
            kind = "quay"
        elif pond(i, j):
            kind = "water"
        elif campo(i, j):
            kind = "grass"
        elif any(a <= i < b and c <= j < d for a, b, c, d in rects) or \
                any(math.hypot(ci - a, cj - b) < r for (a, b), r in circles):
            kind = "pave"
        elif retiro(i, j):
            ring = 55 <= i <= 62 and 25 <= j <= 31
            kind = "gravel" if ring or (i - 52) % 8 == 0 or j % 9 == 0 else "grass"
        elif abs(ci - alcala) < 1.6 and cj < 42 or abs(cj - gran_via) < 1.1 and ci < alcala or \
                abs(cj - mayor) < 1.1 and 31 <= i < 53:
            kind = "cobble"  # Calle de Alcalá from Sol, the Gran Vía, Calle Mayor
        elif 17 <= i - j <= 20:
            kind = "gravel"  # the Paseo del Prado and Recoletos, north-south through Cibeles
        else:
            kind = "lot"
        kinds[(i, j)] = kind

    reserved, silhouette = set(), {}  # landmark pixel -> the earliest draw depth of the landmarks there

    def reserve(i, j, wi, wj, ground="court"):
        for a in range(math.floor(i), math.ceil(i + wi)):
            for b in range(math.floor(j), math.ceil(j + wj)):
                reserved.add((a, b))
                if kinds.get((a, b)) == "lot":
                    kinds[(a, b)] = ground

    def landmark(build):
        """Draw a landmark and record its painted pixels, so that nothing drawn after it covers them."""
        build(scene)
        study = iso.Scene(WIDTH + 200, HEIGHT + 200, (scene.ox + 100, scene.oy + 100))
        build(study)
        depth = min(o[0] for o in study.objects)
        study.paint_objects()
        img = study.img.convert("RGB")
        left, top, right, bottom = img.getbbox()
        pixels = img.load()
        for sy in range(top, bottom):
            for sx in range(left, right):
                if pixels[sx, sy] != (0, 0, 0):
                    for dx in range(-3, 4):
                        for dy in range(-3, 4):
                            p = (sx - 100 + dx, sy - 100 + dy)
                            silhouette[p] = min(silhouette.get(p, depth), depth)

    def covers(pixels, depth):
        """Would something drawn at this depth over these pixels paint on a landmark?"""
        return any(silhouette.get(p, math.inf) <= depth for p in pixels)

    landmark(lambda s: lb.palacio_real(s, 11.5, 44.5))
    reserve(11.5, 44.5, 15, 8)
    landmark(lambda s: lb.almudena(s, 33, 63))  # due south of the palace, across the Armería
    reserve(33, 63, 5.6, 9)
    landmark(lambda s: lb.plaza_mayor(s, 40.5, 52))
    landmark(lambda s: lb.casa_correos(s, 44, 41.5))
    reserve(44, 41.5, 8, 3.5)
    landmark(lambda s: lb.metropolis(s, 44.5, 32.5))
    landmark(lambda s: lb.cibeles(s, 46.5, 28))
    landmark(lambda s: lb.puerta_alcala(s, 42.5, 18.5))  # astride Calle de Alcalá
    landmark(lambda s: lb.alfonso_xii(s, 62, 26))
    landmark(lambda s: lb.palacio_cristal(s, 76, 39))
    reserve(75, 38, 8, 6, ground="gravel")
    i0 = 44  # the Puente de Segovia
    landmark(lambda s: lp.stone_bridge(s, i0, 76 + 2 * math.sin(i0 / 7) - 1.5, 9))

    paint_ground(scene, kinds, {}, TAGUS, lb.GRANITE["dark"])

    for li in range(-12, 110, 3):
        for lj in range(-12, 110, 3):
            for wi, wj in ((3, 3), (3, 2), (2, 3)):
                cells = [(a, b) for a in range(li, li + wi) for b in range(lj, lj + wj)]
                if not all(kinds.get(c) == "lot" and c not in reserved for c in cells):
                    continue
                seed = int(h01(li, lj, 27) * 1000)
                wall = MADRID_WALLS[int(h01(seed, 25) * len(MADRID_WALLS))]
                # Lower houses on the near side of the Gran Vía and Calle de Alcalá let the avenues show.
                low = lj == 36 and li < 45 or li == 48 and lj < 42
                floors = 2 if low else 4 + int(h01(seed, 29) * 2)
                house = lambda s, wi=wi, wj=wj: lb.madrid_house(
                    s, li, lj, wi, wj, floors, wall, seed,
                    mansard_roof=h01(seed, 26) < 0.75, corner_dome=h01(seed, 28) < 0.07)
                ax, ay = scene.screen(li, lj)
                x0, y0 = math.floor(ax - 60), math.floor(ay - 110)
                study = iso.Scene(120, 180, (scene.ox - x0, scene.oy - y0))
                house(study)
                depth = max(o[0] for o in study.objects)
                study.paint_objects()
                img = study.img.convert("RGB")
                l, t, r, b = img.getbbox()
                pixels = img.load()
                if covers(((sx + x0, sy + y0) for sy in range(t, b) for sx in range(l, r)
                           if pixels[sx, sy] != (0, 0, 0)), depth):
                    continue  # it would stand over a landmark: leave the ground open
                house(scene)
                reserved.update(cells)
                break

    green = [round_tree(n) for n in range(3)]
    dark = [round_tree(n, "#4E9A3E", "#1E3A22") for n in range(2)]
    for (i, j), kind in kinds.items():
        x, y = scene.screen(i + 0.5, j + 0.5)
        # A tree may stand beside a landmark, never over any of its painted pixels.
        if covers(((x + dx, y + dy) for dx in range(-9, 10, 3) for dy in range(-16, 8, 3)), i + j + 1.5):
            continue
        pick = None
        if kind == "grass" and h01(i, j, 31) < 0.42 and (i, j) not in reserved:
            pick = (dark if h01(i, j, 32) < 0.45 else green)[int(h01(i, j, 33) * 2)]
        elif kind == "quay" and i % 3 == 0:
            pick = green[i % 3]
        elif kind == "gravel" and (i - j) in (17, 20) and (i + j) % 4 == 0:
            pick = green[(i + j) % 3]  # the double rows of planes on the Prado and Recoletos
        elif kind == "cobble" and (i + j) % 5 == 0 and h01(i, j, 34) < 0.5:
            pick = green[(i + j) % 3]  # plane trees along the avenues
        if pick is not None:
            scene.add(i + j + 1.5, lambda s, img=pick, x=x, y=y: s.sprite(img, x, y + 6))
    boat = rowboat(0)
    for a, b in ((57.5, 30), (59, 28.4), (60.4, 30.2)):
        x, y = scene.screen(a, b)
        if not covers(((x + dx, y + dy) for dx in range(-6, 7) for dy in range(-6, 3)), a + b):
            scene.add(a + b, lambda s, x=x, y=y: s.sprite(boat, x, y))

    scene.paint_objects()
    return scene.img.convert("RGB")


# ------------------------------------------------------------------- Paris --
# Landmarks are built in true isometric 3D in scripts/art/landmarks_paris.py.

import landmarks_paris as lp

SEINE_WATER = (rgb("#3E7FB8"), rgb("#2E6DAF"), rgb("#5A9AD0"))


def bateau(seed):
    """Bateau-mouche: a long, low river boat with a glazed cabin and a white hull stripe."""
    s = sprites.Sprite(23, 9)
    sprites.ground_shadow(s, 11.5, 7.6, 10, 0.8)
    for x in range(1, 22):
        s.put(x, 5, rgb("#F6F4EE"), rgb("#3A3632"))
        s.put(x, 6, rgb("#2E3A4E") if 2 < x < 21 else rgb("#F6F4EE"), rgb("#3A3632"))
        if 4 <= x <= 18:
            for y in (3, 4):
                glass = x % 3 != 0
                s.put(x, y, (rgb("#BFE6F2") if y == 3 else rgb("#93CDE2")) if glass else rgb("#F6F4EE"), rgb("#3A3632"))
    for x in range(5, 18, 4):
        s.put(x, 2, rgb("#E2434E"), rgb("#3A3632"))
    return s.image()


def paris():
    scene = new_scene()

    # North up, west left, distances compressed. The Seine comes in from the east (lower right) past
    # the Île de la Cité and Notre-Dame and flows west-north-west along -i (at j = RA), with the Louvre,
    # the Tuileries and Concorde on its Right Bank (smaller j). West of Concorde it bends south-west
    # along +j (at i = RB) past the Eiffel Tower on its Left Bank (larger i), the Champ de Mars behind
    # it. The Champs-Élysées climbs along -i from Concorde to the Arc on its star; Montmartre and
    # Sacré-Cœur rise in the north. Both reaches run on isometric axes, so bridges cross squarely.
    RA, RB, HW = 46, 18, 2.8
    ISLAND = (66, 83)  # the Île de la Cité, along i
    montmartre = (30.5, 10.5)
    concorde = (24.5, 38)
    etoile = (10, 37.8)  # the centre of the Arc's footprint
    louvre_at = (39, 26.5)
    pond = (31, 36.5)  # the Tuileries' round basin
    eiffel_at = (25, 62)
    champs_j = 38

    def half_width(i):
        return 7.2 if ISLAND[0] - 2 <= i <= ISLAND[1] + 2 else HW  # wider around the island

    def river(i, j):
        """Square (Chebyshev) distances from a tile's centre to the two reaches, so the bend has
        square corners and every bank runs on an isometric axis."""
        x, y = i + 0.5, j + 0.5
        return max(abs(y - RA), RB - x), max(abs(x - RB), RA - y)

    kinds, elev = {}, {}
    for i, j in visible_tiles(scene):
        x, y = i + 0.5, j + 0.5
        da, db = river(i, j)
        hw = half_width(i)
        hill = math.hypot(x - montmartre[0], y - montmartre[1]) * 0.8
        di, dj = x - etoile[0], y - etoile[1]
        star = math.hypot(di, dj)
        if ISLAND[0] <= i <= ISLAND[1] and abs(y - (RA + 0.3)) <= 5.0:
            kind = "island"
        elif da <= hw or db <= HW:
            kind = "water"
        elif da <= hw + 1.2 or db <= HW + 1.2:
            kind = "quay"
        elif da <= hw + 2.4 or db <= HW + 2.4 or (x > RB and y > RA and (da <= hw + 8.5 or db <= HW + 8.5)):
            kind = "promenade"  # the Left Bank kept open so its tall blocks never hide the river
        elif hill < 7:
            kind = "grass"
        elif star < 6.5:
            kind = "pave"  # Place de l'Étoile
        elif star < 16 and min(abs(di), abs(dj), abs(di - dj) * 0.8, abs(di + dj) * 0.8) < 0.8:
            kind = "cobble"  # the avenues radiating from the star
        elif etoile[0] < x < concorde[0] and abs(y - champs_j) < 1.2:
            kind = "cobble"  # the Champs-Élysées
        elif etoile[0] < x < concorde[0] and abs(y - champs_j) < 2.2:
            kind = "allee"  # its tree-lined side walks
        elif 28 <= i <= 37 and 30 <= j <= 41:
            kind = "gravel"  # the Tuileries
        elif 28 <= i <= 42 and 58 <= j <= 66:
            kind = "grass"  # the Champ de Mars
        elif (j == 27 and 12 <= i <= 62) or (j == 19 and i >= 40) or (j == 68 and i >= 44) \
                or (i == 58 and j < 38) or (i == 25 and j < 35) or (i == 52 and j > 60):
            kind = "cobble"  # rue de Rivoli, the Grands Boulevards, Saint-Germain, Sébastopol, Royale
        else:
            kind = "lot"
        kinds[(i, j)] = kind
        elev[(i, j)] = 14 if hill < 7 and kind == "grass" else 0

    reserved, protected = set(), []

    def reserve(i, j, wi, wj, ground="pave"):
        for a in range(int(i), int(math.ceil(i + wi))):
            for b in range(int(j), int(math.ceil(j + wj))):
                reserved.add((a, b))
                if kinds.get((a, b)) == "lot":
                    kinds[(a, b)] = ground

    def place(build):
        """Build a landmark and record its painted pixels and earliest draw depth, so nothing drawn
        after it (houses, trees, boats) may cover it."""
        build(scene)
        study = iso.Scene(WIDTH + 200, HEIGHT + 200, (scene.ox + 100, scene.oy + 100))
        build(study)
        first = min(d for d, _, _ in study.objects)
        study.paint_objects()
        img = study.img.convert("RGB")
        px = img.load()
        l, t, r, b = img.getbbox()
        sil = {(x - 100, y - 100) for x in range(l, r) for y in range(t, b) if px[x, y] != (0, 0, 0)}
        protected.append((first, (l - 101, t - 101, r - 99, b - 99), sil))

    def clear(depth, x0, y0, x1, y1):
        """True when an object drawn at this depth over this screen box hides no landmark pixel."""
        for first, (l, t, r, b), sil in protected:
            if depth >= first and x1 > l and x0 < r and y1 > t and y0 < b:
                if any((x, y) in sil for x in range(int(x0), int(x1) + 1) for y in range(int(y0), int(y1) + 1)):
                    return False
        return True

    # Landmarks.
    place(lambda s: lp.sacre_coeur(s, montmartre[0] - 2, montmartre[1] - 2, 14))
    place(lambda s: lp.louvre(s, *louvre_at))
    reserve(louvre_at[0] - 1, louvre_at[1] - 1, 17, 16)
    place(lambda s: lp.obelisk(s, *concorde))
    reserve(concorde[0] - 3.5, concorde[1] - 3, 7, 6)  # Place de la Concorde
    place(lambda s: lp.arc_de_triomphe(s, etoile[0] - 3, etoile[1] - 1.8))
    place(lambda s: lp.eiffel_tower(s, *eiffel_at))
    reserve(eiffel_at[0] - 3, eiffel_at[1] - 4, 6, 8)
    place(lambda s: lp.notre_dame(s, 72.5, 39.8))
    # Pont Alexandre III (gilded), Pont de la Concorde, Pont Royal, Pont des Arts, Pont Neuf.
    for i0, gilded in ((22, True), (26, False), (36.5, False), (49, False), (67, False)):
        hw = half_width(i0)
        start = RA - hw - 1.4
        lp.stone_bridge(scene, i0, start, 2 * hw + 2.8, gilded=gilded)
        reserve(i0, start, 2, 2 * hw + 2.8, ground="cobble")
    start = RB - HW - 1.4  # Pont d'Iéna, straight to the tower
    lp.stone_bridge(scene, start, eiffel_at[1] - 0.8, 2 * HW + 2.8, along_i=True)
    reserve(start, eiffel_at[1] - 0.8, 2 * HW + 2.8, 2, ground="cobble")

    # Ground, back to front.
    wall = iso.stone_wall(lp.STONE["dark"])
    for (i, j) in sorted(kinds, key=lambda t: (t[0] + t[1], t[0])):
        kind, e = kinds[(i, j)], elev[(i, j)]

        def color(x, y, k=kind):
            if k == "water":
                if h01(x // 3, y, 9) < 0.02:
                    return rgb("#E4F4FA")
                return SEINE_WATER[1] if h01(x // 6, y // 2, 4) < 0.3 else SEINE_WATER[0]
            if k == "quay":
                return lp.STONE["mid"] if (x + y) % 6 else lp.STONE["line"]
            if k in ("gravel", "allee"):
                return shade(rgb("#E6DAB8"), -0.08) if h01(x, y, 6) < 0.15 else rgb("#E6DAB8")
            if k in ("promenade", "island"):
                return ground_color("pave", x, y)
            return ground_color("pave" if k == "lot" else k, x, y)
        iso.ground_tile(scene, i, j, color, e, wall if e else None)
    # The Tuileries' round pond.
    cx, cy = scene.screen(*pond)
    for dy in range(-6, 7):
        for dx in range(-12, 13):
            r = (dx / 12) ** 2 + (dy / 6) ** 2
            if r <= 1:
                scene.put(cx + dx, cy + dy, lp.STONE["mid"] if r > 0.78 else SEINE_WATER[2] if (dx + dy) % 5 else rgb("#E4F4FA"))

    # Haussmann blocks fill the remaining lots as continuous street walls, never in front of a landmark.
    for li in range(-12, 110, 4):
        for lj in range(-12, 110, 4):
            for wi, wj in ((3, 3), (3, 2), (2, 3), (2, 2)):
                cells = [(a, b) for a in range(li, li + wi) for b in range(lj, lj + wj)]
                if all(kinds.get(c) == "lot" and c not in reserved for c in cells):
                    seed = int(h01(li, lj, 47) * 1000)
                    floors = 4 + int(h01(seed, 3) * 2)
                    left, right = scene.screen(li, lj + wj)[0], scene.screen(li + wi, lj)[0]
                    top, bottom = scene.screen(li, lj)[1] - (10 + floors * 8) - 16, scene.screen(li + wi, lj + wj)[1]
                    if not clear(li + lj + wi + wj, left, top, right, bottom):
                        continue
                    reserved.update(cells)
                    lp.haussmann(scene, li, lj, wi, wj, seed, floors=floors)
                    break

    # Trees: rows along the quays and the Champs-Élysées, in the gardens and on Montmartre.
    green = [round_tree(n) for n in range(3)]
    chestnut = [round_tree(n, "#4E9A3E", "#1E3A22") for n in range(2)]
    for (i, j), kind in kinds.items():
        if (i, j) in reserved:
            continue
        da, db = river(i, j)
        edge = da <= half_width(i) + 2.6 or db <= HW + 2.6
        pick = None
        if kind == "promenade" and ((edge and (i + j) % 3 == 0) or (not edge and i % 3 == 0 and j % 3 == 0)):
            pick = green[i % 3]
        elif kind == "island" and i <= ISLAND[0] + 2 and (i + j) % 2 == 0:
            pick = green[j % 3]  # the Square du Vert-Galant at the island's western tip
        elif kind == "allee" and i % 2 == 0:
            pick = chestnut[(i + j) % 2]
        elif kind == "gravel" and (i % 3 == 0) and (j % 3 == 0) and math.hypot(i + 0.5 - pond[0], j + 0.5 - pond[1]) > 2.5:
            pick = chestnut[(i + j) % 2]
        elif kind == "grass" and elev[(i, j)] and h01(i, j, 61) < 0.25:
            pick = green[(i + j) % 3]
        elif kind == "grass" and not elev[(i, j)] and (i in (28, 42) or j in (58, 66)) and (i + j) % 2 == 0:
            pick = chestnut[(i + j) % 2]  # the Champ de Mars' tree-lined edges
        if pick is not None:
            x, y = scene.screen(i + 0.5, j + 0.5, elev[(i, j)])
            if clear(i + j + 1.5, x - 9, y - 14, x + 9, y + 6):
                scene.add(i + j + 1.5, lambda s, img=pick, x=x, y=y: s.sprite(img, x, y + 6))

    boat = bateau(0)
    for a, b in [(i0, RA) for i0 in (31, 41, 54, 61, 88)] + [(RB, j0) for j0 in (56, 70)]:
        x, y = scene.screen(a, b)
        if kinds.get((int(a), int(b))) == "water" and clear(a + b, x - 12, y - 8, x + 12, y + 1):
            scene.add(a + b, lambda s, x=x, y=y: s.sprite(boat, x, y))

    scene.paint_objects()
    return scene.img.convert("RGB")


# ------------------------------------------------------------------ Berlin --

import landmarks_berlin as be


def berlin():
    scene = new_scene()
    # A north-up illustration, with distances compressed. The Spree enters from the south-east
    # (Mühlendamm) south-west of the Rotes Rathaus, splits around Museum Island (main arm on the
    # east side, Kupfergraben on the west), then runs west and bends around the Reichstag's north
    # and east sides. Rathaus and TV Tower share the east (Alexanderplatz) bank. Tiergarten stays
    # west of the Gate. Every reach follows an isometric axis so bridges cross squarely.
    def at(x, y):
        return tile_of((x - WIDTH / 2) / 8, (y - scene.oy) / 4)

    def river(i, j):
        return (i > 50.4 and abs(j - 38) < 2) \
            or (37 <= i <= 52 and abs(j - 38) < 1.4) \
            or (35.4 <= i <= 53.6 and abs(j - 25) < 2) \
            or (abs(i - 52) < 1.6 and 23 <= j <= 40) \
            or (abs(i - 37) < 1.6 and 23 <= j <= 43.5) \
            or (i < 38.6 and abs(j - 41.5) < 2)

    kinds = {}
    for i, j in visible_tiles(scene):
        x, y = scene.screen(i + .5, j + .5)
        island = 38.6 < i < 50.4 and 27 < j < 36.6
        if river(i + .5, j + .5):
            kind = "water"
        elif any(river(i + .5 + di, j + .5 + dj) for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            kind = "quay"
        elif any(river(i + .5 + di, j + .5 + dj) for di, dj in ((2, 0), (-2, 0), (0, 2), (0, -2))):
            kind = "promenade"
        elif x < 228 and y > 310:
            kind = "gravel" if abs(y - 352) < 5 or abs((x - 113) + (y - 410) * .7) < 4 else "grass"
        elif island:
            kind = "grass" if j > 33 else "pave"  # Lustgarten, beside the cathedral
        elif (235 < x < 480 and abs(y - (355 - (x - 260) * .38)) < 6) \
                or (abs(x - 349) < 5 and 310 < y < 510) \
                or i % 12 in (0, 1) or j % 12 == 0:
            kind = "cobble"  # Unter den Linden, Friedrichstraße and the surrounding streets
        else:
            kind = "lot"
        kinds[(i, j)] = kind

    reserved = set()
    protected = []

    def reserve(i, j, wi, wj, ground="pave"):
        for a in range(math.floor(i), math.ceil(i + wi)):
            for b in range(math.floor(j), math.ceil(j + wj)):
                reserved.add((a, b))
                if kinds.get((a, b)) == "lot":
                    kinds[(a, b)] = ground

    def landmark(builder, x, y, wi, wj, height, forecourt=4):
        ci, cj = at(x, y)
        i, j = ci - wi / 2, cj - wj / 2
        builder(scene, i, j)
        reserve(i - 1, j - 1, wi + 2, wj + 1 + forecourt)
        # Also protect its projected silhouette from the roofs of houses just south of it.
        half = (wi + wj) * 4 + 9
        protected.append((x - half, y - height, x + half, y + (wi + wj) * 2 + 12))

    landmark(be.reichstag, 224, 254, 10, 6, 75)
    landmark(be.brandenburg_gate, 267, 357, 8.2, 2, 70, forecourt=6)
    landmark(be.berlin_cathedral, 469, 237, 7.4, 6.2, 85)
    landmark(be.rotes_rathaus, 572, 293, 7, 5, 95)
    landmark(be.konzerthaus, 389, 440, 8.5, 5.2, 70, forecourt=6)
    for builder, x, y, height in ((be.victory_column, 113, 410, 93), (be.tv_tower, 600, 191, 165)):
        i, j = at(x, y)
        builder(scene, i, j)
        reserve(i - 2, j - 2, 5, 7)
        protected.append((x - 23, y - height, x + 23, y + 22))

    # Open cobbled forecourts keep the Gate, Gendarmenmarkt and Alexanderplatz readable.
    for x, y, wi, wj in ((284, 381, 5, 6), (406, 473, 8, 6), (610, 219, 4, 6)):
        i, j = at(x, y)
        reserve(i - wi / 2, j - wj / 2, wi, wj)
    # Moltkebrücke west of the Reichstag, Liebknecht- and Schlossbrücke to the island, Mühlendamm.
    for i, j, length in ((20, 38.5, 6), (46, 22, 6), (43, 36, 4), (62, 35, 6)):
        lp.stone_bridge(scene, i, j, length, width=1.4)
        reserve(i - 1, j - 1, 3, length + 3, "cobble")

    water = (rgb("#3E7D9C"), rgb("#336B8B"), rgb("#71AEC1"))
    paint_ground(scene, kinds, {}, water, be.SAND["dark"])

    for li in range(-12, 110, 4):
        for lj in range(-12, 110, 4):
            for wi, wj in ((3, 3), (3, 2), (2, 3)):
                cells = [(a, b) for a in range(li, li + wi) for b in range(lj, lj + wj)]
                if not all(kinds.get(c) == "lot" and c not in reserved for c in cells):
                    continue
                seed = int(h01(li, lj, 79) * 1000)
                floors = 3 + seed % 2
                x, y = scene.screen(li + wi / 2, lj + wj / 2)
                half, top, bottom = (wi + wj) * 4 + 2, y - floors * 9 - 19, y + (wi + wj) * 2
                if any(x + half > l and x - half < r and bottom > t and top < b for l, t, r, b in protected):
                    reserve(li, lj, wi, wj)
                    continue
                be.berlin_house(scene, li, lj, wi, wj, floors, seed)
                reserved.update(cells)
                break

    green = [round_tree(n, "#659D4F", "#27432C") for n in range(3)]
    lindens = [round_tree(n, "#83AF59", "#31482D") for n in range(3)]
    for (i, j), kind in kinds.items():
        x, y = scene.screen(i + .5, j + .5)
        if any(l - 5 < x < r + 5 and t < y < b + 10 for l, t, r, b in protected):
            continue
        pick = None
        if kind == "grass" and h01(i, j, 81) < .35 and (i, j) not in reserved:
            pick = green[(i + j) % 3]
        elif kind == "promenade" and (i + j) % 3 == 0 and (i, j) not in reserved:
            pick = lindens[(i + j) % 3]
        elif kind == "cobble" and 300 < x < 430 and abs(y - (355 - (x - 260) * .38)) < 4 and i % 3 == 0:
            pick = lindens[i % 3]
        if pick is not None:
            scene.add(i + j + 1.5, lambda s, img=pick, x=x, y=y: s.sprite(img, x, y + 5))
    for i, j in ((8, 41.5), (30, 41.5), (42, 25), (68, 38), (76, 38)):
        x, y = scene.screen(i, j)
        scene.add(i + j, lambda s, x=x, y=y: s.sprite(bateau(0), x, y))

    scene.paint_objects()
    return scene.img.convert("RGB")


# --------------------------------------------------------------- Amsterdam --

import landmarks_amsterdam as am


def amsterdam():
    scene = new_scene()
    def at(x, y):
        return tile_of((x - WIDTH / 2) / 8, (y - scene.oy) / 4)

    # North-up illustration. IJ/Oosterdok at the north; three compressed canal-belt rings
    # (Herengracht, Keizersgracht, Prinsengracht) wrap Dam on the west, south-west and south, open
    # to the IJ. Each ring has a north-west reach (i = west), a south-west reach (j = bank) and a
    # southern reach (i = corner); Brouwersgracht joins their northern ends to the IJ.
    # Prinsengracht steps west to east in front of the Westerkerk, so the Anne Frank House (north)
    # and the church stand on its inner (east) quay with the water beside and in front of them.
    # Each waterway segment follows i or j, including the Amstel at Magere Brug.
    rings = ((37, 31, 56, 58), (33, 31, 68, 70), (27, 54, 80, 82))  # (west, top, bank, corner)

    def water(i, j):
        return i + j < 34 or (i > 48 and j < 30) \
            or (i < rings[0][0] + 1.1 and abs(j - 31) < 1.1) \
            or (abs(i - 19) < 1.1 and 31 <= j <= 55.1) or (17.9 <= i <= 28.1 and abs(j - 54) < 1.1) \
            or any((abs(i - west) < 1.1 and top <= j <= bank + 1.1)
                   or (west - 1.1 <= i <= corner and abs(j - bank) < 1.1)
                   or (j <= bank and abs(i - corner) < 1.1)
                   for west, top, bank, corner in rings) \
            or (i > 60 and abs(j - 48.5) < 3.2)

    kinds = {}
    for i, j in visible_tiles(scene):
        x, y = scene.screen(i + .5, j + .5)
        if water(i + .5, j + .5):
            kind = "water"
        elif any(water(i + .5 + di, j + .5 + dj) for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            kind = "quay"
        elif any(water(i + .5 + di, j + .5 + dj) for di, dj in ((2, 0), (-2, 0), (0, 2), (0, -2))):
            kind = "promenade"
        elif x < 200 and y > 410:
            kind = "gravel" if i % 6 == 0 or j % 6 == 0 else "grass"  # Vondelpark, southwest
        elif 260 < x < 390 and y > 466:
            kind = "grass" if i % 4 and j % 4 else "gravel"  # Museumplein and museum garden
        elif i % 10 == 0 or j % 10 == 0:
            kind = "cobble"
        else:
            kind = "lot"
        kinds[(i, j)] = kind

    reserved, protected = set(), []
    def reserve(i, j, wi, wj, ground="pave"):
        for a in range(math.floor(i), math.ceil(i + wi)):
            for b in range(math.floor(j), math.ceil(j + wj)):
                reserved.add((a, b))
                if kinds.get((a, b)) == "lot":
                    kinds[(a, b)] = ground

    def landmark(builder, x, y, wi, wj, height, front=2):
        ci, cj = at(x, y)
        i, j = ci - wi / 2, cj - wj / 2
        builder(scene, i, j)
        reserve(i - .5, j - .5, wi + 1, wj + front + 1)
        half = (wi + wj) * 4 + 3
        protected.append((x - half, y - height, x + half, y + (wi + wj) * 2 + 4))
        # Curated sites sit on land. Water is shaped around their reserved footprints, not through them.
        for a in range(math.floor(i - .5), math.ceil(i + wi + .5)):
            for b in range(math.floor(j - .5), math.ceil(j + wj + .5)):
                if (a, b) in kinds:
                    kinds[(a, b)] = "pave"

    landmark(am.centraal_station, 496, 124, 13.5, 3.6, 69)
    landmark(am.anne_frank_house, 230, 184, 2.8, 4.3, 48)
    landmark(am.westerkerk, 166, 231, 6.5, 5, 103)
    landmark(am.oude_kerk, 468, 245, 5.8, 7.2, 93)
    landmark(am.royal_palace, 350, 300, 9.5, 5, 77, front=4)
    landmark(am.nemo, 612, 266, 8, 4.2, 45)
    landmark(am.rijksmuseum, 318, 457, 12, 5.8, 73)

    # Dam Square lies east of the palace. Westermarkt stays open beside the Westertoren.
    for x, y, wi, wj in ((407, 320, 6, 6), (180, 272, 4, 4)):
        i, j = at(x, y)
        reserve(i - wi / 2, j - wj / 2, wi, wj)
    # The Anne Frank House's rear Annex stands behind its footprint; keep roofs off it.
    i, j = at(230, 184)
    reserve(i - 1.4, j - 4.5, 2.8, 2.5)
    protected.append((236, 128, 278, 182))

    # Stone canal bridges along +j and the white double drawbridge across the wider Amstel.
    for i, j, length in ((45, 53, 6), (43, 65, 6), (53, 77, 6), (27, 29, 4)):
        lp.stone_bridge(scene, i, j, length, width=1.2, deck=5)
        reserve(i - 1, j - 1, 3, length + 2, "cobble")
    am.magere_brug(scene, 71, 43.5, length=10)
    reserve(70, 42, 4, 14)
    bx, by = scene.screen(71.85, 48.5)
    protected.append((bx - 53, by - 47, bx + 53, by + 32))

    # NEMO's pedestrian connection to the mainland, supported above the dock water.
    def nemo_walkway(s):
        for a in (47.5, 51.5):
            am.block(s, a, 24.1, .35, .7, 5, am.STONE)
        am.block(s, 47.5, 24, 5.5, 1, 2, am.STONE, z=5)
        for jj in (24, 25):
            for a in range(48, 54):
                seg0, seg1 = lp.P(s, a, jj, 7), lp.P(s, a, jj, 10)
                lp.seg(s, seg0, seg1, am.COPPER["deep"])
            lp.seg(s, lp.P(s, 47.5, jj, 10), lp.P(s, 53, jj, 10), am.COPPER["deep"])
    scene.add(53 + 25, nemo_walkway)
    reserve(47, 23, 7, 3)

    # All canal-front lots have a broad open quay: buildings cannot cover the foreground water.
    paint_ground(scene, kinds, {}, am.WATER, am.STONE["dark"])
    for li in range(-12, 110, 2):
        for lj in range(-12, 110, 3):
            wi, wj = 2, 2
            cells = [(a, b) for a in range(li, li + wi) for b in range(lj, lj + wj)]
            if not all(kinds.get(c) == "lot" and c not in reserved for c in cells):
                continue
            seed = int(h01(li, lj, 89) * 10000)
            floors = 2 + (seed % 4 == 0)
            x, y = scene.screen(li + wi / 2, lj + wj / 2)
            half, top, bottom = (wi + wj) * 4 + 2, y - floors * 9 - 26, y + (wi + wj) * 2
            if any(x + half > l and x - half < r and bottom > t and top < b for l, t, r, b in protected):
                reserve(li, lj, wi, wj)
                continue
            am.canal_house(scene, li, lj, wi, wj, floors, seed)
            reserved.update(cells)

    elms = [round_tree(n, "#719C56", "#2C4935") for n in range(3)]
    for (i, j), kind in kinds.items():
        x, y = scene.screen(i + .5, j + .5)
        if (i, j) in reserved or any(l - 4 < x < r + 4 and t < y < b + 12 for l, t, r, b in protected):
            continue
        if (kind == "promenade" and (i + j) % 5 == 0) or (kind == "grass" and h01(i, j, 91) < .23):
            scene.add(i + j + 1.5, lambda s, x=x, y=y, tree=elms[(i + j) % 3]: s.sprite(tree, x, y + 5))
    for i, j in ((27, 64), (33, 46), (50, 56), (40, 68), (50, 80), (64, 48), (87, 48), (36, 12),
                 (60, 14), (10, 31)):
        if kinds.get((i, j)) == "water":
            x, y = scene.screen(i, j)
            scene.add(i + j, lambda s, x=x, y=y: s.sprite(bateau(0), x, y))
    scene.paint_objects()
    return scene.img.convert("RGB")


# ---------------------------------------------------------------- Brussels --

import landmarks_belgium as bel


def brussels():
    scene = new_scene()
    def at(x, y):
        return tile_of((x - WIDTH / 2) / 8, (y - scene.oy) / 4)

    # North-up, compressed geography: the Brussels canal runs southwest/northeast west of
    # the centre. The Senne is buried here; there is deliberately no invented downtown river.
    # The canal follows +j, with broad open banks on the foreground (+i) side.
    kinds = {}
    for i, j in visible_tiles(scene):
        x, y = scene.screen(i + .5, j + .5)
        if abs(i + .5 - 27) < 1.6:
            kind = "water"
        elif abs(i + .5 - 27) < 2.7:
            kind = "quay"
        elif 29 < i < 36 or 22 < i < 25:
            kind = "promenade"
        elif (40 < x < 190 and 185 < y < 300) or (420 < x < 550 and 215 < y < 285) \
                or (550 < x < 710 and 355 < y < 480):
            # Elisabeth Park, Brussels Park north of the palace, Cinquantenaire gardens.
            kind = "gravel" if i % 6 == 0 or j % 6 == 0 else "grass"
        elif i % 9 == 0 or j % 11 == 0:
            kind = "cobble"
        else:
            kind = "lot"
        kinds[(i, j)] = kind

    reserved, protected = set(), []
    def reserve(i, j, wi, wj, ground="pave"):
        for a in range(math.floor(i), math.ceil(i + wi)):
            for b in range(math.floor(j), math.ceil(j + wj)):
                reserved.add((a, b))
                if (a, b) in kinds:
                    kinds[(a, b)] = ground

    def landmark(builder, x, y, wi, wj, height, front=2, extra=4):
        ci, cj = at(x, y)
        i, j = ci - wi / 2, cj - wj / 2
        builder(scene, i, j)
        reserve(i - .6, j - .6, wi + 1.2, wj + front + 1.2)
        half = (wi + wj) * 4 + extra
        protected.append((x - half, y - height, x + half, y + (wi + wj) * 2 + 12))

    landmark(bel.atomium, 250, 155, 9, 9, 143, extra=1)
    landmark(bel.basilica, 110, 180, 8.5, 10, 106)
    landmark(bel.cathedral, 475, 190, 7.6, 9, 80, front=4)
    landmark(bel.kings_house, 350, 220, 7.5, 4.3, 96)
    landmark(bel.town_hall, 290, 310, 11, 4, 133)
    landmark(bel.royal_palace, 485, 340, 14, 4.5, 64, front=5)
    landmark(bel.cinquantenaire, 605, 440, 10.5, 3, 79, front=4, extra=50)
    landmark(bel.palace_of_justice, 290, 471, 12, 9, 122, front=2)

    # Grand-Place is between the King’s House (northeast) and Town Hall (southwest).
    # Distinct cobbling and a stone border, with ornate guild houses on its east edge.
    for i, j in list(kinds):
        x, y = scene.screen(i + .5, j + .5)
        if 320 < x < 425 and 255 < y < 312:
            reserve(i, j, 1, 1, "cobble")
    for n, (x, y) in enumerate(((418, 286), (444, 301), (470, 316))):
        ci, cj = at(x, y)
        wi, wj = 2.3, 2.4
        bel.brussels_house(scene, ci - wi / 2, cj - wj / 2, wi, wj, 3, n * 2, guild=True)
        reserve(ci - wi / 2 - .3, cj - wj / 2 - .3, wi + .6, wj + .6)
        protected.append((x - 22, y - 60, x + 22, y + 14))

    # Low stone bridges cross the canal squarely along i, not diagonally across the water.
    for jj in (20, 41, 59):
        def bridge(s, jj=jj):
            def masonry(u, v, lit):
                if lit and lb.arch_opening(u % 16, v, 8, 5, 2, True):
                    return rgb("#345B64")
                return bel.PALE["lit" if lit else "dark"] if v > 4 else lb.stone_courses(bel.BLUE_STONE, 3, 8)(u, v, lit)
            bel.block(s, 23, jj, 8, 1.4, 6, bel.BLUE_STONE, masonry)
            for b in (jj, jj + 1.4):
                lp.seg(s, lp.P(s, 23, b, 8), lp.P(s, 31, b, 8), bel.PALE["lit"])
                for a in range(24, 31, 2):
                    bel.block(s, a, b, .18, .18, 3, bel.PALE, z=6)
        scene.add(31 + jj + 2, bridge)
        for a in range(22, 33):
            for b in range(jj - 1, jj + 3):
                reserved.add((a, b))

    paint_ground(scene, kinds, {}, (rgb("#497F89"), rgb("#386673"), rgb("#8FB9BC")), bel.BLUE_STONE["dark"])
    for li in range(-12, 112, 3):
        for lj in range(-12, 112, 4):
            wi, wj = 2.5, 3
            cells = [(a, b) for a in range(li, li + 3) for b in range(lj, lj + 3)]
            if not all(kinds.get(c) == "lot" and c not in reserved for c in cells):
                continue
            seed = int(h01(li, lj, 111) * 10000)
            floors = 2 + seed % 2
            x, y = scene.screen(li + wi / 2, lj + wj / 2)
            half = (wi + wj) * 4 + 4
            top, bottom = y - floors * 10 - 28, y + (wi + wj) * 2
            if any(x + half > l and x - half < r and bottom > t and top < b for l, t, r, b in protected):
                continue
            # Keep the foreground bank open far enough that roofs cannot hide the canal.
            if 30 < li < 40:
                continue
            bel.brussels_house(scene, li, lj, wi, wj, floors, seed)
            reserved.update(cells)

    lindens = [round_tree(n, "#7CA257", "#304B32") for n in range(3)]
    for (i, j), kind in kinds.items():
        x, y = scene.screen(i + .5, j + .5)
        if (i, j) in reserved or any(l - 5 < x < r + 5 and t < y < b + 10 for l, t, r, b in protected):
            continue
        if kind == "grass" and h01(i, j, 113) < .17 \
                or kind == "promenade" and (i + j) % 6 == 0:
            scene.add(i + j + 1.5, lambda s, x=x, y=y, tree=lindens[(i + j) % 3]: s.sprite(tree, x, y + 4))
    for jj in (12, 32, 50, 69):
        x, y = scene.screen(27, jj)
        scene.add(27 + jj, lambda s, x=x, y=y: s.sprite(bateau(0), x, y))
    scene.paint_objects()
    return scene.img.convert("RGB")


# ------------------------------------------------------------------ London --

import landmarks_london as lon

THAMES = (rgb("#527F89"), rgb("#3D6575"), rgb("#9BBAB9"))
LONDON_PLANE = ("#779B51", "#2D4932")


def london():
    scene = new_scene()
    def at(x, y):
        return tile_of((x - WIDTH / 2) / 8, (y - scene.oy) / 4)

    # A compressed north-up Thames S-bend. Every reach follows i or j, allowing
    # square crossings; the west/north bank holds Westminster and the City.
    river = [at(x, y) for x, y in ((610, 550), (410, 450), (490, 410),
                                  (330, 330), (492.5, 248.75), (790, 397.5))]
    def river_distance(i, j):
        best = float("inf")
        for (a, b), (c, d) in zip(river, river[1:]):
            t = max(0, min(1, ((i - a) * (c - a) + (j - b) * (d - b)) / ((c - a) ** 2 + (d - b) ** 2)))
            best = min(best, math.hypot(i - a - t * (c - a), j - b - t * (d - b)))
        return best

    kinds = {}
    for i, j in visible_tiles(scene):
        x, y = scene.screen(i + .5, j + .5)
        distance = river_distance(i + .5, j + .5)
        if distance < 1.65:
            kind = "water"
        elif distance < 2.6:
            kind = "quay"
        elif distance < 5:
            kind = "promenade"
        elif (40 < x < 190 and 175 < y < 290) or (130 < x < 210 and 285 < y < 365):
            # Green Park and St James's Park, north/east of Buckingham Palace.
            kind = "gravel" if i % 6 == 0 or j % 6 == 0 else "grass"
        elif i % 10 == 0 or j % 10 == 0:
            kind = "cobble"
        else:
            kind = "lot"
        kinds[(i, j)] = kind

    reserved, protected = set(), []
    def reserve(i, j, wi, wj, ground="pave"):
        for a in range(math.floor(i), math.ceil(i + wi)):
            for b in range(math.floor(j), math.ceil(j + wj)):
                reserved.add((a, b))
                if (a, b) in kinds and kinds[(a, b)] not in ("water", "quay"):
                    kinds[(a, b)] = ground

    def landmark(builder, x, y, wi, wj, front=2, ground="pave"):
        ci, cj = at(x, y)
        i, j = ci - wi / 2, cj - wj / 2
        builder(scene, i, j)
        reserve(i - .7, j - .7, wi + 1.4, wj + front + 1.4, ground)
        # Measure the actual projected silhouette, including flags, spires and flying
        # buttresses; foreground terraces and trees must never cover any part of it.
        study = iso.Scene(WIDTH + 200, HEIGHT + 200, (scene.ox + 100, scene.oy + 100))
        builder(study, i, j)
        study.paint_objects()
        bounds = study.img.convert("RGB").getbbox()
        left, top, right, bottom = (n - 100 for n in bounds)
        assert 0 < left < right < WIDTH and 0 < top < bottom < HEIGHT, (builder.__name__, bounds)
        protected.append((left - 5, top - 4, right + 5, bottom + 6))

    landmark(lon.st_pauls, 480, 145, 10, 5.5, front=3)
    landmark(lon.trafalgar, 145, 230, 8, 8, front=1, ground="quay")
    landmark(lon.tower_of_london, 600, 210, 8.5, 7, front=3)
    landmark(lon.buckingham_palace, 105, 340, 13, 6.5, front=3)
    landmark(lon.london_eye, 445, 330, 8, 8, front=1)
    landmark(lon.parliament, 415, 465, 5, 15, front=3)
    landmark(lon.westminster_abbey, 250, 400, 9, 5.5, front=2)
    # Tower Bridge crosses the east reach squarely along j, on its real SE side of the Tower.
    landmark(lon.tower_bridge, 635, 320, 2.8, 15, front=1)

    # Westminster Bridge: a stone span across the western i-axis reach, north of Parliament.
    bi, bj = at(430, 380)
    lp.stone_bridge(scene, bi - .8, bj - 4.3, 8.6, width=1.6, deck=7)
    reserve(bi - 1, bj - 5, 2, 10)
    paint_ground(scene, kinds, {}, THAMES, lon.STONE["dark"])

    for li in range(-12, 112, 3):
        for lj in range(-12, 112, 3):
            wi, wj = 2.5, 3
            cells = [(a, b) for a in range(li, li + 3) for b in range(lj, lj + 3)]
            if not all(kinds.get(c) == "lot" and c not in reserved for c in cells):
                continue
            seed = int(h01(li, lj, 121) * 10000)
            floors = 2 + seed % 2
            x, y = scene.screen(li + wi / 2, lj + wj / 2)
            half = (wi + wj) * 4 + 4
            top, bottom = y - floors * 11 - 21, y + (wi + wj) * 2
            if any(x + half > l and x - half < r and bottom > t and top < b for l, t, r, b in protected):
                continue
            if river_distance(li + wi / 2, lj + wj / 2) < 7:
                continue  # deep open embankments keep the water visible below the roofs
            lon.terrace(scene, li, lj, wi, wj, floors, seed)
            reserved.update(cells)

    planes = [round_tree(n, *LONDON_PLANE) for n in range(3)]
    for (i, j), kind in kinds.items():
        x, y = scene.screen(i + .5, j + .5)
        if (i, j) in reserved or any(l - 8 < x < r + 8 and t - 2 < y < b + 22 for l, t, r, b in protected):
            continue
        if kind == "grass" and h01(i, j, 123) < .18 or kind == "promenade" and (i + j) % 7 == 0:
            scene.add(i + j + 1.5, lambda s, x=x, y=y, tree=planes[(i + j) % 3]: s.sprite(tree, x, y + 4))
    for x, y in ((450, 430), (374, 352), (472, 259), (550, 277.5), (710, 357.5)):
        i, j = at(x, y)
        scene.add(i + j, lambda s, x=x, y=y: s.sprite(bateau(0), x, y))
    scene.paint_objects()
    return scene.img.convert("RGB")


def dublin():
    import landmarks_ireland as irl

    scene = new_scene()
    def at(x, y):
        return tile_of((x - WIDTH / 2) / 8, (y - scene.oy) / 4)

    # Compressed north-up Liffey: i/j reaches, with Four Courts and Custom House
    # on the north bank and Ha'penny Bridge squarely across the central i reach.
    river = [at(x, y) for x, y in ((-80, 175), (180, 305), (350, 220),
                                  (470, 280), (620, 205), (800, 295))]
    def river_distance(i, j):
        best = float('inf')
        for (a, b), (c, d) in zip(river, river[1:]):
            t = max(0, min(1, ((i - a) * (c - a) + (j - b) * (d - b)) / ((c - a) ** 2 + (d - b) ** 2)))
            best = min(best, math.hypot(i - a - t * (c - a), j - b - t * (d - b)))
        return best

    kinds = {}
    for i, j in visible_tiles(scene):
        x, y = scene.screen(i + .5, j + .5)
        distance = river_distance(i + .5, j + .5)
        if distance < 1.7:
            kind = 'water'
        elif distance < 2.7:
            kind = 'quay'
        elif distance < 4.4:
            kind = 'promenade'
        elif (450 < x < 650 and 405 < y < 510) or (50 < x < 160 and 415 < y < 510):
            # St Stephen's Green southeast of the Castle, and St Patrick's Park.
            kind = 'gravel' if i % 7 == 0 or j % 7 == 0 else 'grass'
        elif i % 10 == 0 or j % 10 == 0:
            kind = 'cobble'
        else:
            kind = 'lot'
        kinds[(i, j)] = kind

    reserved, protected = set(), []
    def reserve(i, j, wi, wj, ground='pave'):
        for a in range(math.floor(i), math.ceil(i + wi)):
            for b in range(math.floor(j), math.ceil(j + wj)):
                reserved.add((a, b))
                if (a, b) in kinds and kinds[(a, b)] not in ('water', 'quay'):
                    kinds[(a, b)] = ground

    def landmark(builder, x, y, wi, wj, front=2, ground='pave'):
        ci, cj = at(x, y)
        i, j = ci - wi / 2, cj - wj / 2
        builder(scene, i, j)
        reserve(i - .8, j - .8, wi + 1.6, wj + front + 1.6, ground)
        study = iso.Scene(WIDTH + 200, HEIGHT + 200, (scene.ox + 100, scene.oy + 100))
        builder(study, i, j)
        study.paint_objects()
        bounds = study.img.convert('RGB').getbbox()
        left, top, right, bottom = (n - 100 for n in bounds)
        assert 0 < left < right < WIDTH and 0 < top < bottom < HEIGHT, (builder.__name__, bounds)
        protected.append((left - 5, top - 4, right + 5, bottom + 6))

    # Anchor centres retain the real sites' east/west and north/south ordering.
    landmark(irl.gpo, 400, 95, 12, 5, front=3)
    landmark(irl.custom_house, 600, 150, 14, 5, front=3)
    landmark(irl.four_courts, 112, 229, 12, 5, front=3)
    landmark(irl.hapenny_bridge, 365, 227.5, 2.2, 8.5, front=1)
    # Christ Church lies just east of the Four Courts' longitude; St Patrick's is directly south of it.
    landmark(irl.christ_church, 158, 349, 11, 5, front=2)
    landmark(irl.dublin_castle, 326, 395, 13.8, 8, front=2)
    landmark(irl.trinity, 535, 330, 11, 8.8, front=2)
    landmark(irl.st_patricks, 160, 482, 14.2, 6, front=2, ground='gravel')
    paint_ground(scene, kinds, {}, (rgb('#447F87'), rgb('#346573')), irl.STONE['dark'])

    for li in range(-12, 112, 3):
        for lj in range(-12, 112, 3):
            wi, wj = 2.5, 3
            cells = [(a, b) for a in range(li, li + 3) for b in range(lj, lj + 3)]
            if not all(kinds.get(c) == 'lot' and c not in reserved for c in cells):
                continue
            seed = int(h01(li, lj, 137) * 10000)
            floors = 2 + seed % 2
            x, y = scene.screen(li + wi / 2, lj + wj / 2)
            half = (wi + wj) * 4 + 5
            top, bottom = y - floors * 12 - 22, y + (wi + wj) * 2 + 8
            if any(x + half > l and x - half < r and bottom > t and top < b for l, t, r, b in protected):
                continue
            if river_distance(li + wi / 2, lj + wj / 2) < 7:
                continue
            irl.georgian_house(scene, li, lj, wi, wj, floors, seed)
            reserved.update(cells)

    trees = [round_tree(n, '#63954C', '#284B32') for n in range(3)]
    for (i, j), kind in kinds.items():
        x, y = scene.screen(i + .5, j + .5)
        if (i, j) in reserved or any(l - 8 < x < r + 8 and t - 2 < y < b + 22 for l, t, r, b in protected):
            continue
        if kind == 'grass' and h01(i, j, 139) < .17 or kind == 'promenade' and (i + j) % 7 == 0:
            scene.add(i + j + 1.5, lambda s, x=x, y=y, tree=trees[(i + j) % 3]: s.sprite(tree, x, y + 4))
    for x, y in ((50, 240), (250, 270), (440, 265), (565, 232.5), (690, 240)):
        i, j = at(x, y)
        scene.add(i + j, lambda s, x=x, y=y: s.sprite(rowboat(0), x, y))
    scene.paint_objects()
    return scene.img.convert('RGB')


def rome():
    import landmarks_italy as it

    scene = new_scene()
    def at(x, y):
        return tile_of((x - WIDTH / 2) / 8, (y - scene.oy) / 4)

    # Compressed Tiber bends follow i/j axes. Vatican and Castel are on its west bank;
    # the ancient and baroque centre lies to the east. St Peter's is in Vatican City.
    river = [at(x, y) for x, y in ((130, -80), (390, 50), (190, 150),
                                  (290, 200), (30, 330), (370, 500), (210, 580))]
    def river_distance(i, j):
        best = float('inf')
        for (a, b), (c, d) in zip(river, river[1:]):
            t = max(0, min(1, ((i - a) * (c - a) + (j - b) * (d - b)) / ((c - a) ** 2 + (d - b) ** 2)))
            best = min(best, math.hypot(i - a - t * (c - a), j - b - t * (d - b)))
        return best

    kinds = {}
    for i, j in visible_tiles(scene):
        x, y = scene.screen(i + .5, j + .5)
        distance = river_distance(i + .5, j + .5)
        if distance < 1.45:
            kind = 'water'
        elif distance < 2.35:
            kind = 'quay'
        elif distance < 4:
            kind = 'promenade'
        elif (510 < x < 700 and y < 80) or (70 < x < 175 and 350 < y < 500):
            # Villa Borghese to the northeast; Janiculum gardens southwest of the Vatican.
            kind = 'gravel' if i % 8 == 0 or j % 8 == 0 else 'grass'
        elif 590 < x < 710 and y > 420:
            kind = 'gravel'  # Colosseum archaeological grounds
        elif i % 9 == 0 or j % 11 == 0:
            kind = 'cobble'
        else:
            kind = 'lot'
        kinds[(i, j)] = kind

    reserved, protected = set(), []
    def reserve(i, j, wi, wj):
        for a in range(math.floor(i), math.ceil(i + wi)):
            for b in range(math.floor(j), math.ceil(j + wj)):
                reserved.add((a, b))
                if (a, b) in kinds and kinds[(a, b)] not in ('water', 'quay'):
                    kinds[(a, b)] = 'pave'

    def landmark(builder, x, y, wi, wj):
        ci, cj = at(x, y)
        i, j = ci - wi / 2, cj - wj / 2
        builder(scene, i, j)
        reserve(i - .5, j - .5, wi + 1, wj + 2)
        study = iso.Scene(WIDTH + 200, HEIGHT + 200, (scene.ox + 100, scene.oy + 100))
        builder(study, i, j)
        study.paint_objects()
        bounds = tuple(v - 100 for v in study.img.convert('RGB').getbbox())
        left, top, right, bottom = bounds
        assert 0 < left < right < WIDTH and 0 < top < bottom < HEIGHT, (builder.__name__, bounds)
        protected.append((left - 3, top - 3, right + 3, bottom + 4))

    # Ground anchors preserve every site's real longitude/latitude ordering.
    # St Peter's faces east: dome at the west end, square opening south-east (+i) to the river.
    landmark(it.st_peters, 122, 195, 16.5, 12)
    landmark(it.castel_santangelo, 260, 125, 8, 7)
    landmark(it.spanish_steps, 460, 120, 9, 9)
    landmark(it.trevi, 600, 245, 10, 8)
    landmark(it.navona, 280, 290, 10, 11)
    landmark(it.pantheon, 365, 410, 9, 9)
    landmark(it.vittoriano, 510, 440, 13, 7)
    landmark(it.colosseum, 650, 480, 10.4, 7.4)
    paint_ground(scene, {cell: 'pave' if kind == 'promenade' else kind for cell, kind in kinds.items()},
                 {}, (rgb('#568C7D'), rgb('#3D7369')), it.STONE['dark'])

    # Stone crossings perpendicular to the i-axis reaches; no river hidden by houses.
    for x, y in ((282, 173), (190, 382)):
        i, j = at(x, y)
        lp.stone_bridge(scene, i, j, 7, width=1.5)

    for li in range(-12, 112, 3):
        for lj in range(-12, 112, 3):
            wi, wj = 2.5, 3
            cells = [(a, b) for a in range(li, li + 3) for b in range(lj, lj + 3)]
            if not all(kinds.get(c) == 'lot' and c not in reserved for c in cells):
                continue
            seed = int(h01(li, lj, 149) * 10000)
            floors = 2 + seed % 3
            x, y = scene.screen(li + wi / 2, lj + wj / 2)
            half = (wi + wj) * 4 + 5
            top, bottom = y - floors * 11 - 20, y + (wi + wj) * 2 + 8
            if any(x + half > l and x - half < r and bottom > t and top < b for l, t, r, b in protected):
                continue
            if river_distance(li + wi / 2, lj + wj / 2) < 6:
                continue
            it.palazzo(scene, li, lj, wi, wj, floors, seed)
            reserved.update(cells)

    pines = [umbrella_pine(n) for n in range(3)]
    for (i, j), kind in kinds.items():
        x, y = scene.screen(i + .5, j + .5)
        if (i, j) in reserved or any(l - 14 < x < r + 14 and t - 2 < y < b + 26 for l, t, r, b in protected):
            continue
        if kind == 'grass' and h01(i, j, 151) < .13 or kind == 'promenade' and (i + j) % 8 == 0:
            scene.add(i + j + 1.5, lambda s, x=x, y=y, tree=pines[(i + j) % 3]: s.sprite(tree, x, y + 4))
    for x, y in ((340, 25), (231, 129), (89, 300), (278, 454)):
        i, j = at(x, y)
        scene.add(i + j, lambda s, x=x, y=y: s.sprite(rowboat(0), x, y))
    scene.paint_objects()
    return scene.img.convert('RGB')


def copenhagen():
    import landmarks_denmark as dk

    scene = new_scene()
    def at(x, y):
        return tile_of((x - WIDTH / 2) / 8, (y - scene.oy) / 4)

    # North-up, compressed harbour bends along i/j axes. Nyhavn opens east into it;
    # Slotsholmen stays on the city side, Christianshavn and Our Saviour on the east bank.
    # Slotsholmen is an island: the harbour on its south-east (+i) side, Slotsholmskanalen along
    # its north-east (-j) and north-west (-i) sides, Frederiksholms Kanal along its south-west
    # (+j) side; both canals join the harbour.
    ni, nj = at(450, 300)
    ni, nj = ni - 11.4 / 2, nj - 6.5 / 2
    def water(i, j):
        return (i > 28 and j < 5) or (52 < i < 58 and j < 35) or (52 < i < 67 and 29 < j < 35) \
            or (61 < i < 67 and j >= 29) \
            or (ni < i < 65 and nj + 2.9 < j < nj + 6.2) \
            or (44.5 < i < 62 and 47 < j < 49.5) \
            or (44.5 < i < 47 and 47 < j < 68) \
            or (44.5 < i < 62 and 65.5 < j < 68)

    kinds = {}
    for i, j in visible_tiles(scene):
        x, y = scene.screen(i + .5, j + .5)
        if water(i + .5, j + .5):
            kind = 'water'
        elif any(water(i + .5 + di, j + .5 + dj) for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            kind = 'quay'
        elif any(water(i + .5 + di, j + .5 + dj) for di, dj in ((2, 0), (-2, 0), (0, 2), (0, -2))):
            kind = 'promenade'
        elif 215 < x < 390 and 70 < y < 205:
            kind = 'gravel' if i % 7 == 0 or j % 7 == 0 else 'grass'  # King's Garden
        elif x < 150 and y > 445:
            kind = 'gravel' if i % 5 == 0 or j % 5 == 0 else 'grass'  # Tivoli's garden edge
        elif i % 10 == 0 or j % 10 == 0:
            kind = 'cobble'
        else:
            kind = 'lot'
        kinds[(i, j)] = kind

    reserved, protected = set(), []
    def reserve(i, j, wi, wj):
        for a in range(math.floor(i), math.ceil(i + wi)):
            for b in range(math.floor(j), math.ceil(j + wj)):
                reserved.add((a, b))
                if kinds.get((a, b)) == 'lot':
                    kinds[(a, b)] = 'pave'

    def landmark(builder, x, y, wi, wj):
        ci, cj = at(x, y)
        i, j = ci - wi / 2, cj - wj / 2
        builder(scene, i, j)
        reserve(i - .5, j - .5, wi + 1, wj + 2)
        study = iso.Scene(WIDTH + 200, HEIGHT + 200, (scene.ox + 100, scene.oy + 100))
        builder(study, i, j)
        study.paint_objects()
        bounds = tuple(v - 100 for v in study.img.convert('RGB').getbbox())
        left, top, right, bottom = bounds
        assert 0 < left < right < WIDTH and 0 < top < bottom < HEIGHT, (builder.__name__, bounds)
        protected.append((left - 4, top - 3, right + 4, bottom + 5))

    # Ground anchors preserve every site's real longitude and latitude ordering.
    landmark(dk.little_mermaid, 580, 85, 3.6, 3.2)
    landmark(dk.rosenborg, 300, 135, 8, 4.5)
    landmark(dk.marble_church, 440, 160, 8, 7.2)
    landmark(dk.amalienborg, 560, 220, 9.4, 9.4)
    landmark(dk.round_tower, 245, 255, 5.2, 7)
    landmark(dk.nyhavn, 450, 300, 11.4, 6.5)
    landmark(dk.christiansborg, 330, 389.4, 8.6, 7.1)
    landmark(dk.city_hall, 140, 435, 8, 4.8)
    landmark(dk.our_saviour, 570, 477, 5.6, 7.6)
    # Rådhuspladsen and Kongens Nytorv remain paved/open in front of their buildings.
    for x, y, wi, wj in ((115, 470, 7, 5), (400, 270, 5, 4)):
        i, j = at(x, y)
        reserve(i - wi / 2, j - wj / 2, wi, wj)
    paint_ground(scene, {cell: 'pave' if kind == 'promenade' else kind for cell, kind in kinds.items()},
                 {}, dk.WATER, dk.STONE['dark'])

    # Square crossings on the isometric harbour reaches; low decks keep water visible.
    # Slotsholmen's bridges: Højbro and Holmens Bro over Slotsholmskanalen, Marmorbroen over
    # Frederiksholms Kanal from the riding ground, and Knippelsbro from the island's east tip.
    for i, j, length, along_i in ((43.6, 52, 4.8, True), (56.5, 45.8, 4.4, False), (53.5, 63.8, 5.4, False)):
        lp.stone_bridge(scene, i, j, length, width=1.4, deck=5, along_i=along_i)
        reserve(i - .5, j - .5, (length if along_i else 1.4) + 1, (1.4 if along_i else length) + 1)
    def harbour_bridge(s):
        dk.block(s, 59.5, 50.5, 9, 1.4, 5, dk.STONE,
                 lambda u, v, lit: dk.WATER[1] if lit and 2 < int(u) % 18 < 14 and v < 3 else None)
        for jj in (50.5, 51.9):
            dk.block(s, 59.5, jj, 9, .12, 2, dk.STONE, z=5)
    scene.add(59.5 + 50.5 + 9 + 1.4, harbour_bridge)
    reserve(59, 49.5, 11, 4)

    for li in range(-12, 112, 3):
        for lj in range(-12, 112, 3):
            wi, wj = 2.4, 2.7
            cells = [(a, b) for a in range(li, li + 3) for b in range(lj, lj + 3)]
            if not all(kinds.get(c) == 'lot' and c not in reserved for c in cells):
                continue
            seed = int(h01(li, lj, 163) * 10000)
            floors = 2 + (seed % 3 != 0)
            x, y = scene.screen(li + wi / 2, lj + wj / 2)
            half = (wi + wj) * 4 + 5
            top, bottom = y - floors * 10 - 26, y + (wi + wj) * 2 + 7
            if any(x + half > l and x - half < r and bottom > t and top < b for l, t, r, b in protected):
                continue
            # Broad promenades on BOTH banks, so foreground houses cannot mask the harbour.
            if any(water(li + wi / 2 + di, lj + wj / 2 + dj)
                   for di, dj in ((3, 0), (-3, 0), (0, 3), (0, -3))):
                continue
            dk.townhouse(scene, li, lj, wi, wj, floors, seed)
            reserved.update(cells)

    lindens = [round_tree(n, '#719A58', '#2A4935') for n in range(3)]
    for (i, j), kind in kinds.items():
        x, y = scene.screen(i + .5, j + .5)
        if (i, j) in reserved or any(l - 10 < x < r + 10 and t - 2 < y < b + 24 for l, t, r, b in protected):
            continue
        if kind == 'grass' and h01(i, j, 167) < .14 or kind == 'promenade' and (i + j) % 9 == 0:
            scene.add(i + j + 1.5, lambda s, x=x, y=y, tree=lindens[(i + j) % 3]: s.sprite(tree, x, y + 4))
    for i, j in ((54, 12), (55, 24), (64, 46), (64, 60), (64, 72), (51, 62)):
        if water(i, j):
            x, y = scene.screen(i, j)
            scene.add(i + j, lambda s, x=x, y=y: s.sprite(bateau(0), x, y))
    scene.paint_objects()
    return scene.img.convert('RGB')


def stockholm():
    import landmarks_sweden as se

    scene = new_scene()
    def at(x, y):
        return tile_of((x - WIDTH / 2) / 8, (y - scene.oy) / 4)

    # Compressed north-up island groups. Every bank follows i/j axes: Riddarfjärden west,
    # Norrström north of Gamla Stan, Riddarholmen west and Djurgården to the east.
    # Kungsholmen's south shore runs along i = 36 and Klara sjö splits it from Norrmalm,
    # so City Hall stands on the island's eastern tip with Riddarfjärden at its feet.
    def water(i, j):
        kungsholmen = i < 35 and j > 54.5
        mainland = (i < 36 and j < 52) or kungsholmen or (i < 40 and 19 < j < 30)
        gamla_stan = 41 < i < 79 and 38 < j < (71 if i > 58 else 68)
        riddarholmen = 44 < i < 56 and 69 < j < 79
        djurgarden = (i > 38 and j < 16) or (i > 43 and j < 28)
        sodermalm = (i > 83 and j > 43) or j > 86
        return not (mainland or gamla_stan or riddarholmen or djurgarden or sodermalm)

    kinds = {}
    for i, j in visible_tiles(scene):
        x, y = scene.screen(i + .5, j + .5)
        if water(i + .5, j + .5):
            kind = 'water'
        elif any(water(i + .5 + di, j + .5 + dj) for di, dj in ((1,0),(-1,0),(0,1),(0,-1))):
            kind = 'quay'
        elif any(water(i + .5 + di, j + .5 + dj) for di, dj in ((3,0),(-3,0),(0,3),(0,-3))):
            kind = 'promenade'
        elif x > 600 or (80 < x < 260 and 130 < y < 230):
            kind = 'gravel' if i % 7 == 0 or j % 7 == 0 else 'grass'
        elif i % 9 == 0 or j % 9 == 0:
            kind = 'cobble'
        else:
            kind = 'lot'
        kinds[(i, j)] = kind

    reserved, protected = set(), []
    def reserve(i, j, wi, wj):
        for a in range(math.floor(i), math.ceil(i + wi)):
            for b in range(math.floor(j), math.ceil(j + wj)):
                reserved.add((a, b))
                if kinds.get((a, b)) == 'lot':
                    kinds[(a, b)] = 'pave'

    def landmark(builder, x, y, wi, wj):
        ci, cj = at(x, y)
        i, j = ci - wi / 2, cj - wj / 2
        builder(scene, i, j)
        reserve(i - .5, j - .5, wi + 1, wj + 2)
        study = iso.Scene(WIDTH + 200, HEIGHT + 200, (scene.ox + 100, scene.oy + 100))
        builder(study, i, j)
        study.paint_objects()
        bounds = tuple(v - 100 for v in study.img.convert('RGB').getbbox())
        left, top, right, bottom = bounds
        assert 0 < left < right < WIDTH and 0 < top < bottom < HEIGHT, (builder.__name__, bounds)
        protected.append((left - 4, top - 3, right + 4, bottom + 5))

    # Ground anchors preserve the real longitude and latitude ordering, including the
    # palace/German Church's shared longitude and the closely spaced Djurgården museums.
    landmark(se.nordiska, 633, 146, 12, 5.6)
    landmark(se.nationalmuseum, 450, 175, 7.8, 5)
    landmark(se.vasa_museum, 555, 225, 7.5, 6)
    # City Hall on Kungsholmen's tip: its tower corner stands on the Riddarfjärden quay
    # and the colonnade opens onto a garden that runs down to the water.
    landmark(se.city_hall, *scene.screen(29.7, 60.6), 8.4, 5.4)
    for a in range(26, 36):
        for b in range(64, 68):
            if kinds.get((a, b)) in ('lot', 'pave', 'cobble', 'promenade'):
                kinds[(a, b)] = 'gravel' if b == 65 or a == 34 else 'grass'
    landmark(se.royal_palace, 385, 300, 9, 7)
    landmark(se.storkyrkan, 285, 390, 4.3, 6.3)
    landmark(se.riddarholmen, 196, 428, 4.8, 6.5)
    landmark(se.german_church, 385, 480, 4, 5.8)
    # Stortorget's open cobbled square south of the cathedral, and palace forecourt.
    for x,y,wi,wj in ((305,427,6,4),(350,340,5,3)):
        i,j=at(x,y)
        reserve(i-wi/2,j-wj/2,wi,wj)

    paint_ground(scene, {cell:'pave' if kind == 'promenade' else kind for cell,kind in kinds.items()},
                 {}, se.WATER, se.STONE['dark'])
    # Low bridges cross the island channels squarely, with open stone quays on both banks.
    lp.stone_bridge(scene, 46, 65.5, 6, width=1.3, deck=5)
    reserve(45,65,4,8)
    lp.stone_bridge(scene, 54, 26, 13, width=1.4, deck=5)
    reserve(53,25,4,15)
    def north_bridge(s):
        se.block(s,34,48,9,1.4,5,se.STONE,
                 lambda u,v,lit:se.WATER[1] if lit and 3<int(u)%17<13 and v<3 else None)
        for jj in (48,49.4):
            se.block(s,34,jj,9,.12,2,se.STONE,z=5)
    scene.add(34+48+10.4,north_bridge)
    reserve(33,47,11,4)
    # Stadshusbron over Klara sjö, just north of City Hall.
    lp.stone_bridge(scene, 30, 51.3, 3.9, width=1.3, deck=5)
    reserve(29,50,3,6)

    for li in range(-12,112,3):
        for lj in range(-12,112,3):
            wi,wj=2.3,2.8
            cells=[(a,b) for a in range(li,li+3) for b in range(lj,lj+3)]
            if not all(kinds.get(c)=='lot' and c not in reserved for c in cells):
                continue
            seed=int(h01(li,lj,181)*10000)
            floors=2+(seed%3!=0)
            x,y=scene.screen(li+wi/2,lj+wj/2)
            half=(wi+wj)*4+5
            top,bottom=y-floors*10-29,y+(wi+wj)*2+8
            if any(x+half>l and x-half<r and bottom>t and top<b for l,t,r,b in protected):
                continue
            if any(water(li+wi/2+di,lj+wj/2+dj) for di,dj in ((4,0),(-4,0),(0,4),(0,-4))):
                continue
            se.townhouse(scene,li,lj,wi,wj,floors,seed)
            reserved.update(cells)

    lindens=[round_tree(n,'#739B59','#2A4935') for n in range(3)]
    for (i,j),kind in kinds.items():
        x,y=scene.screen(i+.5,j+.5)
        if (i,j) in reserved or any(l-10<x<r+10 and t-2<y<b+24 for l,t,r,b in protected):
            continue
        if kind=='grass' and h01(i,j,183)<.13 or kind=='promenade' and (i+j)%10==0:
            scene.add(i+j+1.5,lambda s,x=x,y=y,tree=lindens[(i+j)%3]:s.sprite(tree,x,y+4))
    for i,j in ((30,70),(39,58),(58,33),(74,35),(65,77),(45,18)):
        if water(i,j):
            x,y=scene.screen(i,j)
            scene.add(i+j,lambda s,x=x,y=y:s.sprite(bateau(0),x,y))
    scene.paint_objects()
    return scene.img.convert('RGB')


def oslo():
    import landmarks_norway as no

    scene = new_scene()
    def at(x, y):
        return tile_of((x - WIDTH / 2) / 8, (y - scene.oy) / 4)

    # North-up compressed harbour: Pipervika west of Akershus's peninsula,
    # Bjørvika east of it; the opera and MUNCH occupy the opposite eastern shore.
    # All quay segments follow i/j axes, including the small Akerselva mouth.
    def water(i, j):
        mainland = i < 49 or (i < 63 and j < 74) or j < 44
        akershus = i < 78 and 58 < j < 74
        east_shore = j < (52 if i < 80 else 56)
        akerselva = 79 < i < 82 and 31 < j < 56
        return akerselva or not (mainland or akershus or east_shore)

    kinds = {}
    for i, j in visible_tiles(scene):
        x, y = scene.screen(i + .5, j + .5)
        if water(i+.5, j+.5):
            kind = 'water'
        elif any(water(i+.5+di, j+.5+dj) for di,dj in ((1,0),(-1,0),(0,1),(0,-1))):
            kind = 'quay'
        elif any(water(i+.5+di, j+.5+dj) for di,dj in ((3,0),(-3,0),(0,3),(0,-3))):
            kind = 'promenade'
        elif (x < 220 and y < 190) or (200 < x < 350 and 150 < y < 240) or (300 < x < 420 and 320 < y < 420):
            kind = 'gravel' if i % 7 == 0 or j % 7 == 0 else 'grass'
        elif 30 < j < 35 and 5 < i < 59 or i % 10 == 0 or j % 10 == 0:
            kind = 'cobble'  # Karl Johans gate and Kvadraturen streets
        else:
            kind = 'lot'
        kinds[(i,j)] = kind

    reserved, protected = set(), []
    def reserve(i,j,wi,wj):
        for a in range(math.floor(i), math.ceil(i+wi)):
            for b in range(math.floor(j), math.ceil(j+wj)):
                reserved.add((a,b))
                if kinds.get((a,b)) == 'lot':
                    kinds[(a,b)] = 'pave'

    def landmark(builder,x,y,wi,wj):
        ci,cj=at(x,y)
        i,j=ci-wi/2,cj-wj/2
        builder(scene,i,j)
        reserve(i-.7,j-.7,wi+1.4,wj+2.5)
        study=iso.Scene(WIDTH+200,HEIGHT+200,(scene.ox+100,scene.oy+100))
        builder(study,i,j)
        study.paint_objects()
        left,top,right,bottom=(v-100 for v in study.img.convert('RGB').getbbox())
        assert 0 < left < right < WIDTH and 0 < top < bottom < HEIGHT, (builder.__name__,(left,top,right,bottom))
        protected.append((left-4,top-3,right+4,bottom+5))

    # The castle is south of the opera (the castle proper, not the fortress's northern gate).
    # Ground anchors retain every real longitude/latitude ordering; distances are compressed.
    landmark(no.royal_palace,125,130,10,5)
    landmark(no.national_theatre,280,185,6.7,5.5)
    landmark(no.storting,420,235,7.7,5)
    # The cathedral stands west of the Opera (about 370 m), east of the Storting.
    landmark(no.cathedral,522,300,5,6.8)
    landmark(no.city_hall,195,340,8.4,5.3)
    landmark(no.akershus,340,465,9.2,6.4)
    landmark(no.opera_house,553,414,9.5,6.3)
    landmark(no.munch,662,484,3.2,2.9)
    # Open Rådhusplassen, Løvebakken and Stortorvet; never put tall houses before them.
    for x,y,wi,wj in ((195,380,8,3),(430,280,6,3),(460,314,5,3)):
        i,j=at(x,y)
        reserve(i-wi/2,j-wj/2,wi,wj)

    paint_ground(scene,{cell:'pave' if kind=='promenade' else kind for cell,kind in kinds.items()},
                 {},no.WATER,no.GRANITE['dark'])
    # A low footbridge over the Akerselva mouth, east of the opera, crosses squarely.
    def footbridge(s):
        no.block(s,78.5,37,4,1,4,no.GRANITE)
        for jj in (37,38):
            no.block(s,78.5,jj,4,.08,2,no.METAL,z=4)
    scene.add(78.5+37+5,footbridge)
    reserve(78,36,5,3)
    for i,j,wi,wj in ((50,75,1,4),(56,75,1,4)):
        scene.add(i+j+wi+wj,lambda s,i=i,j=j,wi=wi,wj=wj:
                  no.block(s,i,j,wi,wj,3,no.TIMBER))

    for li in range(-12,112,3):
        for lj in range(-12,112,3):
            wi,wj=2.6,2.8
            cells=[(a,b) for a in range(li,li+3) for b in range(lj,lj+3)]
            if not all(kinds.get(c)=='lot' and c not in reserved for c in cells):
                continue
            seed=int(h01(li,lj,191)*10000)
            floors=2+(seed%3!=0)
            x,y=scene.screen(li+wi/2,lj+wj/2)
            half=(wi+wj)*4+7
            top,bottom=y-floors*10-30,y+(wi+wj)*2+9
            if any(x+half>l and x-half<r and bottom>t and top<b for l,t,r,b in protected):
                continue
            if any(water(li+wi/2+di,lj+wj/2+dj) for di,dj in ((4,0),(-4,0),(0,4),(0,-4))):
                continue
            no.townhouse(scene,li,lj,wi,wj,floors,seed)
            reserved.update(cells)

    trees=[round_tree(n,'#6A9B64','#2A4935') for n in range(3)]
    for (i,j),kind in kinds.items():
        x,y=scene.screen(i+.5,j+.5)
        if (i,j) in reserved or any(l-10<x<r+10 and t-2<y<b+24 for l,t,r,b in protected):
            continue
        if kind=='grass' and h01(i,j,193)<.12 or kind=='promenade' and (i+j)%11==0:
            scene.add(i+j+1.5,lambda s,x=x,y=y,tree=trees[(i+j)%3]:s.sprite(tree,x,y+4))
    for i,j in ((54,83),(61,81),(69,56),(83,58),(85,68)):
        if water(i,j):
            x,y=scene.screen(i,j)
            image=bateau(0) if i%2 else sprites.sailboat(0)
            scene.add(i+j,lambda s,x=x,y=y,image=image:s.sprite(image,x,y))
    scene.paint_objects()
    return scene.img.convert('RGB')


def helsinki():
    import landmarks_finland as fi

    scene = new_scene()
    def at(x,y):
        return tile_of((x-WIDTH/2)/8,(y-scene.oy)/4)

    # The South Harbour opens southeast of the mainland. Katajanokka lies on
    # its eastern side, and Kustaanmiekka is a separate offshore island.
    # Shores follow tile axes; Töölönlahti lies east of Finlandia Hall.
    def water(i,j):
        toolo = 19 < i < 38 and 15 < j < 26
        mainland = i < 64 or (i < 78 and j < 61) or (i < 81 and j < 42)
        fortress_island = 79.5 < i < 92 and 43.5 < j < 54
        return toolo or not (mainland or fortress_island)

    kinds = {}
    for i,j in visible_tiles(scene):
        x,y = scene.screen(i+.5,j+.5)
        if water(i+.5,j+.5):
            kind = 'water'
        elif any(water(i+.5+di,j+.5+dj) for di,dj in ((1,0),(-1,0),(0,1),(0,-1))):
            kind = 'quay'
        elif any(water(i+.5+di,j+.5+dj) for di,dj in ((3,0),(-3,0),(0,3),(0,-3))):
            kind = 'promenade'
        elif (150 < x < 350 and y < 185) or (230 < x < 455 and 360 < y < 420) or i>79:
            kind = 'gravel' if i%7==0 or j%7==0 else 'grass'
        elif i%11==0 or j%11==0 or (31<j<34 and i<65):
            kind = 'cobble'
        else:
            kind = 'lot'
        kinds[(i,j)] = kind

    reserved,protected = set(),[]
    def reserve(i,j,wi,wj):
        for a in range(math.floor(i),math.ceil(i+wi)):
            for b in range(math.floor(j),math.ceil(j+wj)):
                reserved.add((a,b))
                if kinds.get((a,b))=='lot':kinds[(a,b)]='pave'

    def landmark(builder,x,y,wi,wj):
        ci,cj=at(x,y)
        i,j=ci-wi/2,cj-wj/2
        builder(scene,i,j)
        reserve(i-.7,j-.7,wi+1.4,wj+2.5)
        study=iso.Scene(WIDTH+200,HEIGHT+200,(scene.ox+100,scene.oy+100))
        builder(study,i,j)
        study.paint_objects()
        left,top,right,bottom=(v-100 for v in study.img.convert('RGB').getbbox())
        assert 0<left<right<WIDTH and 0<top<bottom<HEIGHT,(builder.__name__,(left,top,right,bottom))
        protected.append((left-4,top-3,right+4,bottom+5))

    # Real longitude/latitude ordering, with distances compressed independently
    # to keep the monuments and harbour readable within the 720×520 illustration.
    landmark(fi.finlandia,235,120,9.5,5)
    landmark(fi.national_museum,95,185,7.8,4.6)
    landmark(fi.parliament,250,280,11,6)
    landmark(fi.railway_station,380,310,9,4.5)
    landmark(fi.cathedral,515,350,8,6.5)
    landmark(fi.uspenski,650,380,6,6.5)
    landmark(fi.market_hall,530,450,4,8.2)
    landmark(fi.suomenlinna,657,475,10,6)
    # Senate Square, Railway Square and Market Square have open paved forecourts.
    for x,y,wi,wj in ((500,389,7,2),(385,343,7,2),(565,414,4,3)):
        i,j=at(x,y)
        reserve(i-wi/2,j-wj/2,wi,wj)
    paint_ground(scene,{c:'pave' if k=='promenade' else k for c,k in kinds.items()},
                 {},fi.WATER,fi.GRANITE['dark'])

    # Low harbour landings beside the market. No bridge is invented across the
    # sea: Suomenlinna is reached by boat, as it is in the actual city.
    for i,j,wi,wj in ((78,53,2.5,.8),(78,57,2.5,.8)):
        scene.add(i+j+wi+wj,lambda s,i=i,j=j,wi=wi,wj=wj:fi.block(s,i,j,wi,wj,3,fi.WOOD))
        reserve(i,j,wi,wj)
    for li in range(-12,112,3):
        for lj in range(-12,112,3):
            wi,wj=2.7,3
            cells=[(a,b) for a in range(li,li+3) for b in range(lj,lj+3)]
            if not all(kinds.get(c)=='lot' and c not in reserved for c in cells):continue
            seed=int(h01(li,lj,211)*10000)
            floors=2+(seed%3!=0)
            x,y=scene.screen(li+wi/2,lj+wj/2)
            half=(wi+wj)*4+9
            top,bottom=y-floors*10-45,y+(wi+wj)*2+12
            if any(x+half>l and x-half<r and bottom>t and top<b for l,t,r,b in protected):continue
            if any(water(li+wi/2+di,lj+wj/2+dj) for di,dj in ((4,0),(-4,0),(0,4),(0,-4))):continue
            fi.townhouse(scene,li,lj,wi,wj,floors,seed)
            reserved.update(cells)

    trees=[round_tree(n,'#739D69','#2C4A37') for n in range(3)]
    for (i,j),kind in kinds.items():
        x,y=scene.screen(i+.5,j+.5)
        if (i,j) in reserved or any(l-11<x<r+11 and t-2<y<b+25 for l,t,r,b in protected):continue
        if kind=='grass' and h01(i,j,213)<.12 or kind=='promenade' and (i+j)%11==0:
            scene.add(i+j+1.5,lambda s,x=x,y=y,tree=trees[(i+j)%3]:s.sprite(tree,x,y+4))
    for i,j in ((83,57),(89,61),(76,66),(69,72),(30,20)):
        if water(i,j):
            x,y=scene.screen(i,j)
            image=bateau(0) if i%2 else sprites.sailboat(0)
            scene.add(i+j,lambda s,x=x,y=y,image=image:s.sprite(image,x,y))
    scene.paint_objects()
    return scene.img.convert('RGB')


def reykjavik():
    import landmarks_iceland as ice

    scene = new_scene()

    def at(x, y):
        return tile_of((x-WIDTH/2)/8, (y-scene.oy)/4)

    # North-up: the old harbour and Faxaflói are north of the centre. Tjörnin
    # runs south from City Hall; Öskjuhlíð is southeast of Hallgrímskirkja.
    # Both pond and harbour shore segments follow the isometric tile axes.
    def water(i, j):
        harbour = i+j < 40 or (j > 29 and i < 18) or (i > 28 and j < 20)
        tjornin = 39 < i < 53 and 65 < j < 78
        return harbour or tjornin

    kinds = {}
    for i, j in visible_tiles(scene):
        x, y = scene.screen(i+.5, j+.5)
        if water(i+.5, j+.5):
            kind = 'water'
        elif any(water(i+.5+di, j+.5+dj) for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            kind = 'quay'
        elif any(water(i+.5+di, j+.5+dj) for di, dj in ((3, 0), (-3, 0), (0, 3), (0, -3))):
            kind = 'promenade'
        elif ((x > 525 and y > 390) or (x < 245 and y > 375)
              or (40 < x < 150 and 170 < y < 265) or (205 < x < 275 and 190 < y < 225)
              or (590 < x < 700 and 250 < y < 355)):
            kind = 'gravel' if i % 9 == 0 or j % 9 == 0 else 'grass'
        elif i % 14 == 0 or j % 14 == 0 or 31 < j < 34:
            kind = 'cobble'
        else:
            kind = 'lot'
        kinds[(i, j)] = kind

    reserved, protected = set(), []

    def reserve(i, j, wi, wj):
        for a in range(math.floor(i), math.ceil(i+wi)):
            for b in range(math.floor(j), math.ceil(j+wj)):
                reserved.add((a, b))
                if kinds.get((a, b)) == 'lot':
                    kinds[(a, b)] = 'pave'

    def landmark(builder, x, y, wi, wj):
        ci, cj = at(x, y)
        i, j = ci-wi/2, cj-wj/2
        builder(scene, i, j)
        reserve(i-.7, j-.7, wi+1.4, wj+3)
        # Measure the actual projected silhouette, including roof, flag and statue.
        study = iso.Scene(WIDTH+200, HEIGHT+200, (scene.ox+100, scene.oy+100))
        builder(study, i, j)
        study.paint_objects()
        left, top, right, bottom = (v-100 for v in study.img.convert('RGB').getbbox())
        assert 0 < left < right < WIDTH and 0 < top < bottom < HEIGHT, (builder.__name__, (left, top, right, bottom))
        protected.append((left-4, top-3, right+4, bottom+5))

    # Curated real anchors, compressed independently to keep the city legible.
    # Longitude ordering: Landakot, City Hall, Alþingi, Harpa, Hallgrímskirkja,
    # Sun Voyager, Perlan, Höfði. Latitude ordering is preserved as well.
    landmark(ice.harpa, 340, 140, 9.5, 5.4)
    landmark(ice.sun_voyager, 510, 215, 8, 4.5)
    landmark(ice.landakotskirkja, 95, 235, 6, 9)
    landmark(ice.parliament, 250, 285, 8, 4.4)
    landmark(ice.hofdi, 635, 305, 5.5, 6)
    landmark(ice.city_hall, 180, 360, 8.5, 5)
    landmark(ice.hallgrimskirkja, 435, 385, 8, 10)
    landmark(ice.perlan, 600, 465, 8, 8)
    # Austurvöllur and Hallgrímstorg stay open; the pond's banks are low promenades.
    for x, y, wi, wj in ((250, 320, 6, 3), (425, 433, 7, 3), (635, 320, 4, 3)):
        i, j = at(x, y)
        reserve(i-wi/2, j-wj/2, wi, wj)
    # Low iron-clad cottages fit the narrow streets between the civic squares
    # and Hallgrímskirkja without entering any monument's projected silhouette.
    for x, y, seed in ((333, 218, 0), (380, 218, 3), (332, 285, 2)):
        ci, cj = at(x, y)
        ice.house(scene, ci-1, cj-1.25, 2, 2.5, floors=1, seed=seed)
        reserve(ci-1.2, cj-1.4, 2.4, 3)
    paint_ground(scene, {c: 'pave' if k == 'promenade' else k for c, k in kinds.items()},
                 {}, ice.WATER, ice.BASALT['dark'])

    # Old-harbour timber landings, with boats in the sheltered northern water.
    for i, j, wi, wj in ((16, 27, 1, 5), (21, 18, 5, 1)):
        scene.add(i+j+wi+wj, lambda s, i=i, j=j, wi=wi, wj=wj:
                  ice.block(s, i, j, wi, wj, 3, ice.WOOD))
        reserve(i, j, wi, wj)
    for li in range(-12, 112, 3):
        for lj in range(-12, 112, 3):
            wi, wj = 2.5, 3
            cells = [(a, b) for a in range(li, li+3) for b in range(lj, lj+3)]
            if not all(kinds.get(c) == 'lot' and c not in reserved for c in cells):
                continue
            seed = int(h01(li, lj, 281)*10000)
            floors = 1 if seed % 4 == 0 else 2
            x, y = scene.screen(li+wi/2, lj+wj/2)
            half = (wi+wj)*4+4
            top, bottom = y-floors*11-23, y+(wi+wj)*2+5
            if any(x+half > l and x-half < r and bottom > t and top < b for l, t, r, b in protected):
                continue
            if any(water(li+wi/2+di, lj+wj/2+dj) for di, dj in ((4, 0), (-4, 0), (0, 4), (0, -4))):
                continue
            ice.house(scene, li, lj, wi, wj, floors, seed)
            reserved.update(cells)

    trees = [round_tree(n, '#789D71', '#2E4D3C', .85) for n in range(3)]
    for (i, j), kind in kinds.items():
        x, y = scene.screen(i+.5, j+.5)
        if (i, j) in reserved or any(l-10 < x < r+10 and t-2 < y < b+23 for l, t, r, b in protected):
            continue
        if kind == 'grass' and h01(i, j, 283) < .1 or kind == 'promenade' and (i+j) % 13 == 0:
            scene.add(i+j+1.5, lambda s, x=x, y=y, tree=trees[(i+j) % 3]: s.sprite(tree, x, y+4))
    for i, j in ((8, 25), (12, 19), (19, 13), (25, 8)):
        x, y = scene.screen(i, j)
        if water(i, j):
            image = bateau(0) if i % 2 else sprites.sailboat(0)
            scene.add(i+j, lambda s, x=x, y=y, image=image: s.sprite(image, x, y))
    scene.paint_objects()
    return scene.img.convert('RGB')


def bern():
    import landmarks_switzerland as ch

    scene = new_scene()

    def at(x, y):
        return tile_of((x-WIDTH/2)/8, (y-scene.oy)/4)

    # The Aare embraces the peninsula on its north/east/south sides. Compress
    # its loop to two joined tile-axis reaches; keep both foreground banks low.
    def water(i, j):
        return (12 < j < 17 and i < 62) or (57 < i < 62 and j > 12)

    kinds = {}
    for i, j in visible_tiles(scene):
        x, y = scene.screen(i+.5, j+.5)
        if water(i+.5, j+.5):
            kind = 'water'
        elif any(water(i+.5+di, j+.5+dj) for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            kind = 'quay'
        elif any(water(i+.5+di, j+.5+dj) for di, dj in ((3, 0), (-3, 0), (0, 3), (0, -3))):
            kind = 'promenade'
        elif ((x > 570 and y < 180) or (x > 610 and 265 < y < 390)
              or (y > 440 and 245 < x < 460) or (x < 225 and 365 < y < 445)):
            # Schosshalden, Rosengarten, museum gardens and Bundeshausterrasse.
            kind = 'gravel' if i % 8 == 0 or j % 8 == 0 else 'grass'
        elif i % 12 == 0 or j % 12 == 0 or 215 < y < 231 or 275 < y < 286:
            kind = 'cobble'
        else:
            kind = 'lot'
        kinds[(i, j)] = kind

    reserved, protected = set(), []

    def reserve(i, j, wi, wj):
        for a in range(math.floor(i), math.ceil(i+wi)):
            for b in range(math.floor(j), math.ceil(j+wj)):
                reserved.add((a, b))
                if kinds.get((a, b)) == 'lot':
                    kinds[(a, b)] = 'pave'

    def landmark(builder, x, y, wi, wj):
        ci, cj = at(x, y)
        i, j = ci-wi/2, cj-wj/2
        builder(scene, i, j)
        reserve(i-.8, j-.8, wi+1.6, wj+3)
        study = iso.Scene(WIDTH+200, HEIGHT+200, (scene.ox+100, scene.oy+100))
        builder(study, i, j)
        study.paint_objects()
        left, top, right, bottom = (v-100 for v in study.img.convert('RGB').getbbox())
        assert 0 < left < right < WIDTH and 0 < top < bottom < HEIGHT, (builder.__name__, (left, top, right, bottom))
        protected.append((left-4, top-3, right+4, bottom+5))

    # North-up ground anchors, ordered from real longitude/latitude records.
    landmark(ch.paul_klee, 635, 100, 11.4, 5)
    landmark(ch.kafigturm, 80, 270, 5, 3.2)
    landmark(ch.rathaus, 475, 225, 7, 5)
    landmark(ch.nydeggkirche, 590, 212, 4.3, 7.2)
    landmark(ch.zytglogge, 265, 295, 4.4, 3.3)
    landmark(ch.minster, 425, 335, 5.7, 9)
    landmark(ch.federal_palace, 170, 365, 12, 5.3)
    landmark(ch.historical_museum, 395, 468, 10, 5.5)
    # Bundesplatz, Münsterplatz and the Münsterplattform stay open.
    for x, y, wi, wj in ((170, 305, 7, 5), (425, 370, 8, 3), (265, 315, 5, 3)):
        ci, cj = at(x, y)
        reserve(ci-wi/2, cj-wj/2, wi, wj)

    # Nydegg's stone bridge crosses the northern reach squarely along +j.
    lp.stone_bridge(scene, 49, 10, 10, width=1.8, deck=10)
    reserve(48.5, 9.5, 2.8, 11)
    # Kirchenfeld's iron bridge crosses the southern reach along +i.
    ch.kirchenfeld_bridge(scene, 54, 62)
    reserve(53.5, 61.5, 11, 2.8)
    paint_ground(scene, {c: 'pave' if k == 'promenade' else k for c, k in kinds.items()},
                 {}, ch.WATER, ch.SAND['dark'])

    for li in range(-12, 112, 3):
        for lj in range(-12, 112, 3):
            wi, wj = 2.5, 3
            cells = [(a, b) for a in range(li, li+3) for b in range(lj, lj+3)]
            if not all(kinds.get(c) == 'lot' and c not in reserved for c in cells):
                continue
            seed = int(h01(li, lj, 311)*10000)
            floors = 2 if seed % 3 == 0 else 3
            x, y = scene.screen(li+wi/2, lj+wj/2)
            half = (wi+wj)*4+5
            top, bottom = y-floors*11-31, y+(wi+wj)*2+5
            if any(x+half > l and x-half < r and bottom > t and top < b for l, t, r, b in protected):
                continue
            if any(water(li+wi/2+di, lj+wj/2+dj) for di, dj in ((4, 0), (-4, 0), (0, 4), (0, -4))):
                continue
            ch.townhouse(scene, li, lj, wi, wj, floors, seed)
            reserved.update(cells)

    trees = [round_tree(n, '#648A57', '#2E4D36') for n in range(3)]
    for (i, j), kind in kinds.items():
        x, y = scene.screen(i+.5, j+.5)
        if (i, j) in reserved or any(l-11 < x < r+11 and t-2 < y < b+24 for l, t, r, b in protected):
            continue
        if kind == 'grass' and h01(i, j, 313) < .11 or kind == 'promenade' and (i+j) % 11 == 0:
            scene.add(i+j+1.5, lambda s, x=x, y=y, tree=trees[(i+j) % 3]: s.sprite(tree, x, y+4))
        # Rose beds on the real northeastern Rosengarten hillside.
        if kind == 'grass' and x > 560 and y < 80 and (i+j) % 4 == 0:
            for dx, dy in ((-2, 0), (2, 0), (0, -2)):
                scene.put(x+dx, y+dy, ch.RED if i % 2 else ch.PALE['hi'])
    # Small rowing craft, rather than seagoing ships, on the Aare.
    for i, j in ((58.7, 42), (59.2, 73), (20, 14), (43, 14)):
        x, y = scene.screen(i, j)
        image = rowboat(int(i))
        scene.add(i+j, lambda s, x=x, y=y, image=image: s.sprite(image, x, y))
    scene.paint_objects()
    return scene.img.convert('RGB')


def vienna():
    import landmarks_austria as at

    scene = new_scene()

    def tile(x, y):
        return tile_of((x-WIDTH/2)/8, (y-scene.oy)/4)

    # The Donaukanal runs northwest/southeast, northeast of the historic core.
    # The Prater and its wheel sit beyond it; the main Danube is farther away.
    def water(i, j):
        return 12 < j < 16

    kinds = {}
    for i, j in visible_tiles(scene):
        x, y = scene.screen(i+.5, j+.5)
        ring = math.hypot((x-365)/235, (y-245)/145)
        if water(i+.5, j+.5):
            kind = 'water'
        elif any(water(i+.5+di, j+.5+dj) for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            kind = 'quay'
        elif any(water(i+.5+di, j+.5+dj) for di, dj in ((3, 0), (-3, 0), (0, 3), (0, -3))):
            kind = 'promenade'
        elif ((x > 575 and y < 160) or (80 < x < 215 and 200 < y < 280)
              or (x < 215 and y > 375) or (x > 560 and 340 < y < 430)
              or (425 < x < 550 and y > 450)):
            # Prater, Rathauspark, Schönbrunn/Belvedere parterres and Resselpark.
            kind = 'gravel' if i % 7 == 0 or j % 7 == 0 else 'grass'
        elif .94 < ring < 1.06 or i % 12 == 0 or j % 12 == 0:
            kind = 'cobble'
        else:
            kind = 'lot'
        kinds[(i, j)] = kind

    reserved, protected = set(), []

    def reserve(i, j, wi, wj):
        for a in range(math.floor(i), math.ceil(i+wi)):
            for b in range(math.floor(j), math.ceil(j+wj)):
                reserved.add((a, b))
                if kinds.get((a, b)) == 'lot':
                    kinds[(a, b)] = 'pave'

    def landmark(builder, x, y, wi, wj):
        ci, cj = tile(x, y)
        i, j = ci-wi/2, cj-wj/2
        builder(scene, i, j)
        reserve(i-.8, j-.8, wi+1.6, wj+3.5)
        study = iso.Scene(WIDTH+200, HEIGHT+200, (scene.ox+100, scene.oy+100))
        builder(study, i, j)
        study.paint_objects()
        left, top, right, bottom = (v-100 for v in study.img.convert('RGB').getbbox())
        assert 0 < left < right < WIDTH and 0 < top < bottom < HEIGHT, (builder.__name__, (left, top, right, bottom))
        protected.append((left-4, top-3, right+4, bottom+5))

    # Ground anchors retain every real east/west and north/south relationship.
    landmark(at.riesenrad, 650, 130, 9.6, 4)
    landmark(at.rathaus, 180, 185, 12, 4.6)
    landmark(at.stephansdom, 515, 245, 5, 9)
    landmark(at.hofburg, 300, 285, 12, 4.5)
    landmark(at.opera, 370, 385, 8, 6)
    landmark(at.karlskirche, 490, 430, 8.2, 5.2)
    landmark(at.belvedere, 618, 465, 15, 4.2)
    landmark(at.schonbrunn, 115, 470, 14, 4)
    # Stephansplatz, Heldenplatz and Karlsplatz are low paved forecourts.
    for x, y, wi, wj in ((505, 280, 6, 3), (275, 310, 8, 4), (470, 455, 6, 3)):
        ci, cj = tile(x, y)
        reserve(ci-wi/2, cj-wj/2, wi, wj)
    for i in (35, 53):
        lp.stone_bridge(scene, i, 10, 9, width=1.8, deck=7)
        reserve(i-.4, 9.6, 2.6, 9.8)
    paint_ground(scene, {c: 'pave' if k == 'promenade' else k for c, k in kinds.items()},
                 {}, at.WATER, at.STONE['dark'])

    for li in range(-12, 112, 3):
        for lj in range(-12, 112, 3):
            wi, wj = 2.5, 3
            cells = [(a, b) for a in range(li, li+3) for b in range(lj, lj+3)]
            if not all(kinds.get(c) == 'lot' and c not in reserved for c in cells):
                continue
            seed = int(h01(li, lj, 337)*10000)
            floors = 2 if seed % 3 == 0 else 3
            x, y = scene.screen(li+wi/2, lj+wj/2)
            half = (wi+wj)*4+6
            top, bottom = y-floors*12-28, y+(wi+wj)*2+6
            if any(x+half > l and x-half < r and bottom > t and top < b for l, t, r, b in protected):
                continue
            if any(water(li+wi/2+di, lj+wj/2+dj) for di, dj in ((4, 0), (-4, 0), (0, 4), (0, -4))):
                continue
            at.townhouse(scene, li, lj, wi, wj, floors, seed)
            reserved.update(cells)

    trees = [round_tree(n, '#71955A', '#304D33') for n in range(3)]
    for (i, j), kind in kinds.items():
        x, y = scene.screen(i+.5, j+.5)
        if (i, j) in reserved or any(l-11 < x < r+11 and t-2 < y < b+25 for l, t, r, b in protected):
            continue
        if kind == 'grass' and h01(i, j, 339) < .12 or kind == 'promenade' and (i+j) % 11 == 0:
            scene.add(i+j+1.5, lambda s, x=x, y=y, tree=trees[(i+j) % 3]: s.sprite(tree, x, y+4))
        # Formal beds, separated by gravel walks, around the two palace gardens.
        if kind == 'grass' and (x < 215 and y > 390 or x > 560 and 350 < y < 425) and (i+j) % 4 == 0:
            for dx in (-2, 0, 2):
                scene.put(x+dx, y, at.RED['lit'] if i % 2 else at.PALE['hi'])
    for i, j in ((14, 14), (26, 14), (45, 14), (59, 14)):
        x, y = scene.screen(i, j)
        image = bateau(0) if i % 2 else rowboat(i)
        scene.add(i+j, lambda s, x=x, y=y, image=image: s.sprite(image, x, y))
    scene.paint_objects()
    return scene.img.convert('RGB')


def valletta():
    import landmarks_malta as mt

    scene = new_scene()

    def tile(x, y):
        return tile_of((x-WIDTH/2)/8, (y-scene.oy)/4)

    # Mount Sciberras points northeast: Marsamxett on the northwest, the Grand
    # Harbour on the southeast. Distances are compressed, with north still up.
    peninsula = set(iso.polygon_pixels([
        (-30, 550), (-30, 375), (115, 235), (325, 100), (520, 65),
        (635, 55), (705, 120), (605, 240), (535, 335), (485, 410), (475, 550),
    ]))

    def water(i, j):
        x, y = scene.screen(i, j)
        return (int(x), int(y)) not in peninsula

    kinds = {}
    for i, j in visible_tiles(scene):
        x, y = scene.screen(i+.5, j+.5)
        if water(i+.5, j+.5):
            kind = 'water'
        elif any(water(i+.5+di, j+.5+dj) for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            kind = 'quay'
        elif any(water(i+.5+di, j+.5+dj) for di, dj in ((3, 0), (-3, 0), (0, 3), (0, -3))):
            kind = 'promenade'
        elif 65 < x < 180 and 260 < y < 335:
            kind = 'gravel' if i % 5 == 0 or j % 5 == 0 else 'grass'  # Hastings Gardens
        elif i % 12 == 0 or j % 12 == 0 or abs(x+1.55*y-790) < 7:
            kind = 'cobble'
        else:
            kind = 'lot'
        kinds[(i, j)] = kind

    reserved, protected, silhouette = set(), [], set()

    def reserve(i, j, wi, wj):
        for a in range(math.floor(i), math.ceil(i+wi)):
            for b in range(math.floor(j), math.ceil(j+wj)):
                reserved.add((a, b))
                if kinds.get((a, b)) == 'lot':
                    kinds[(a, b)] = 'pave'

    def landmark(builder, x, y, wi, wj):
        ci, cj = tile(x, y)
        i, j = ci-wi/2, cj-wj/2
        builder(scene, i, j)
        reserve(i-.45, j-.45, wi+.9, wj+1.6)
        study = iso.Scene(WIDTH+200, HEIGHT+200, (scene.ox+100, scene.oy+100))
        builder(study, i, j)
        study.paint_objects()
        left, top, right, bottom = (v-100 for v in study.img.convert('RGB').getbbox())
        assert 0 < left < right < WIDTH and 0 < top < bottom < HEIGHT, (builder.__name__, (left, top, right, bottom))
        protected.append((left-4, top-3, right+4, bottom+5))
        pixels = study.img.convert('RGB').load()
        for sy in range(top+100,bottom+100):
            for sx in range(left+100,right+100):
                if pixels[sx,sy] != (0,0,0):
                    silhouette.update((sx-100+dx,sy-100+dy) for dx in range(-3,4) for dy in range(-3,4))

    # Coordinates and ordering are recorded in the Phase 4 landmark table.
    landmark(mt.fort_st_elmo, 620, 110, 10, 8)
    landmark(mt.st_paul, 270, 180, 6, 7.5)
    landmark(mt.carmelite, 390, 195, 6, 6.5)
    landmark(mt.grandmaster, 550, 285, 9, 7.2)
    landmark(mt.st_john, 430, 340, 6, 7.5)
    landmark(mt.parliament, 100, 395, 9.4, 6.5)
    landmark(mt.castille, 230, 435, 9.2, 6.8)
    landmark(mt.upper_barrakka, 370, 465, 8.8, 8)

    paint_ground(scene, {c: 'pave' if k == 'promenade' else k for c, k in kinds.items()},
                 {}, mt.WATER, mt.STONE['dark'])

    # Paint a continuous eight-pixel retaining cliff below the land surface.
    # Sharing the target image but lowering this painter's origin keeps every
    # ground anchor fixed; neighbouring land tiles cover all internal faces.
    land_scene = iso.Scene(WIDTH, HEIGHT, (scene.ox, scene.oy+8))
    land_scene.img, land_scene.px = scene.img, scene.px
    land_kinds = {c: 'pave' if k == 'promenade' else k for c,k in kinds.items() if k != 'water'}
    paint_ground(land_scene,land_kinds,{c:8 for c in land_kinds},mt.WATER,mt.STONE['dark'])

    for li in range(-12, 112):
        for lj in range(-12, 112):
            wi, wj = 2.5, 3
            cells = [(a, b) for a in range(li, li+3) for b in range(lj, lj+3)]
            if not all(kinds.get(c) == 'lot' and c not in reserved for c in cells):
                continue
            seed = int(h01(li, lj, 467)*10000)
            floors = 2 if seed % 3 == 0 else 3
            x, y = scene.screen(li+wi/2, lj+wj/2)
            half = (wi+wj)*4+6
            top, bottom = y-floors*11-20, y+(wi+wj)*2+6
            if any(x+half > l and x-half < r and bottom > t and top < b for l, t, r, b in protected):
                # Test the actual projected shape near a monument. A narrow spire's
                # large bounding box should not empty the streets beside its shaft.
                ax,ay=scene.screen(li,lj)
                x0,y0=math.floor(ax-50),math.floor(ay-70)
                study=iso.Scene(100,120,(scene.ox-x0,scene.oy-y0))
                mt.townhouse(study,li,lj,wi,wj,floors,seed)
                study.paint_objects()
                left,upper,right,lower=study.img.convert('RGB').getbbox()
                pixels=study.img.convert('RGB').load()
                if any((sx+x0,sy+y0) in silhouette and pixels[sx,sy] != (0,0,0)
                       for sy in range(upper,lower) for sx in range(left,right)):
                    continue
            if any(water(li+wi/2+di, lj+wj/2+dj) for di,dj in ((2,0),(-2,0),(0,2),(0,-2))):
                continue
            mt.townhouse(scene,li,lj,wi,wj,floors,seed)
            reserved.update(cells)

    trees = [round_tree(n, '#718B50', '#30462D') for n in range(3)]
    for (i, j), kind in kinds.items():
        x, y = scene.screen(i+.5, j+.5)
        if (i,j) in reserved or any(l-11 < x < r+11 and t-2 < y < b+25 for l,t,r,b in protected):
            continue
        if kind == 'grass' and h01(i,j,469) < .15 or kind == 'promenade' and (i+j) % 12 == 0:
            scene.add(i+j+1.5,lambda s,x=x,y=y,tree=trees[(i+j)%3]:s.sprite(tree,x,y+4))

    # Dgħajsa harbour craft and sailing boats stay on water, outside all silhouettes.
    for x,y in ((115,115),(205,75),(540,395),(600,325),(660,225),(585,465)):
        i,j=tile(x,y)
        assert water(i,j)
        image = rowboat(int(x)) if x < 600 else bateau(0)
        scene.add(i+j,lambda s,x=x,y=y,image=image:s.sprite(image,x,y))
    scene.paint_objects()
    return scene.img.convert('RGB')


def prague():
    import landmarks_czechia as cz

    scene = new_scene()

    def tile(x, y):
        return tile_of((x-WIDTH/2)/8, (y-scene.oy)/4)

    # Compressed Vltava bends follow alternating isometric axes. The northern reach
    # passes east of Hradčany/Malá Strana; the southern reach passes west of New Town.
    def water(i, j):
        return (i <= 36 and 29 < j < 35 or 33 < i < 39 and 29 < j < 56
                or 36 <= i <= 58 and 50 < j < 56 or j >= 50 and 55 < i < 61)

    kinds = {}
    for i, j in visible_tiles(scene):
        x, y = scene.screen(i+.5, j+.5)
        if water(i+.5, j+.5):
            kind = 'water'
        elif any(water(i+.5+di, j+.5+dj) for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            kind = 'quay'
        elif any(water(i+.5+di, j+.5+dj) for di, dj in ((3, 0), (-3, 0), (0, 3), (0, -3))):
            kind = 'promenade'
        elif (x < 190 and y < 270) or (x < 220 and y > 350) or (x > 585 and y > 410):
            kind = 'gravel' if i % 9 == 0 or j % 9 == 0 else 'grass'
        elif i % 12 == 0 or j % 12 == 0 or (455 < x < 655 and 210 < y < 320):
            kind = 'cobble'
        else:
            kind = 'lot'
        kinds[(i, j)] = kind

    reserved, protected = set(), []

    def reserve(i, j, wi, wj):
        for a in range(math.floor(i), math.ceil(i+wi)):
            for b in range(math.floor(j), math.ceil(j+wj)):
                reserved.add((a, b))
                if kinds.get((a, b)) == 'lot':
                    kinds[(a, b)] = 'pave'

    def landmark(builder, x, y, wi, wj):
        ci, cj = tile(x, y)
        i, j = ci-wi/2, cj-wj/2
        builder(scene, i, j)
        reserve(i-.8, j-.8, wi+1.6, wj+3)
        study = iso.Scene(WIDTH+200, HEIGHT+200, (scene.ox+100, scene.oy+100))
        builder(study, i, j)
        study.paint_objects()
        left, top, right, bottom = (v-100 for v in study.img.convert('RGB').getbbox())
        assert 0 < left < right < WIDTH and 0 < top < bottom < HEIGHT, (builder.__name__, (left, top, right, bottom))
        protected.append((left-4, top-3, right+4, bottom+5))

    # North-up geographic order, with distances compressed independently on each axis.
    landmark(cz.prague_castle, 115, 135, 13, 8)
    landmark(cz.st_nicholas, 225, 220, 7.5, 5.2)
    landmark(cz.charles_bridge, 360, 365, 2.3, 14)
    landmark(cz.old_town_hall, 555, 345, 6.5, 3.6)
    landmark(cz.tyn_church, 595, 245, 6.8, 4.6)
    landmark(cz.powder_gate, 675, 290, 3.8, 3.2)
    landmark(cz.national_theatre, 415, 445, 8, 5.8)
    landmark(cz.dancing_house, 530, 490, 7, 5)
    # Old Town Square and the theatre forecourt stay paved and low.
    for x, y, wi, wj in ((535, 365, 9, 6), (435, 460, 6, 3)):
        ci, cj = tile(x, y)
        reserve(ci-wi/2, cj-wj/2, wi, wj)
    paint_ground(scene, {c: 'pave' if k == 'promenade' else k for c, k in kinds.items()},
                 {}, cz.WATER, cz.STONE['dark'])

    for li in range(-12, 112, 3):
        for lj in range(-12, 112, 3):
            wi, wj = 2.5, 3
            cells = [(a, b) for a in range(li, li+3) for b in range(lj, lj+3)]
            if not all(kinds.get(c) == 'lot' and c not in reserved for c in cells):
                continue
            seed = int(h01(li, lj, 367)*10000)
            floors = 2 if seed % 3 == 0 else 3
            x, y = scene.screen(li+wi/2, lj+wj/2)
            half = (wi+wj)*4+6
            top, bottom = y-floors*11-30, y+(wi+wj)*2+6
            if any(x+half > l and x-half < r and bottom > t and top < b for l, t, r, b in protected):
                continue
            if any(water(li+wi/2+di, lj+wj/2+dj) for di, dj in ((4, 0), (-4, 0), (0, 4), (0, -4))):
                continue
            cz.townhouse(scene, li, lj, wi, wj, floors, seed)
            reserved.update(cells)

    trees = [round_tree(n, '#739858', '#304C30') for n in range(3)]
    for (i, j), kind in kinds.items():
        x, y = scene.screen(i+.5, j+.5)
        if (i, j) in reserved or any(l-12 < x < r+12 and t-3 < y < b+25 for l, t, r, b in protected):
            continue
        if kind == 'grass' and h01(i, j, 369) < .11 or kind == 'promenade' and (i+j) % 11 == 0:
            scene.add(i+j+1.5, lambda s, x=x, y=y, tree=trees[(i+j) % 3]: s.sprite(tree, x, y+4))
    for i, j in ((16, 32), (36, 43), (58, 67), (58, 81)):
        x, y = scene.screen(i, j)
        image = bateau(0) if j % 2 else rowboat(i)
        scene.add(i+j, lambda s, x=x, y=y, image=image: s.sprite(image, x, y))
    scene.paint_objects()
    return scene.img.convert('RGB')


def warsaw():
    import landmarks_poland as pl

    scene = new_scene()

    def tile(x, y):
        return tile_of((x-WIDTH/2)/8, (y-scene.oy)/4)

    # The Vistula passes east of the Old Town and leaves the compressed scene to
    # the east. Its visible northern reach follows +i; Łazienki's lake is separate.
    lake_i, lake_j = tile(505, 435)
    lake_i, lake_j = lake_i-4, lake_j-2.4

    def water(i, j):
        river = 1 < j < 8
        lake = (lake_i-3 < i < lake_i+11 and lake_j-2 < j < lake_j+8
                and not (lake_i-.7 < i < lake_i+8.7 and lake_j-.7 < j < lake_j+5.5))
        return river or lake

    kinds = {}
    for i, j in visible_tiles(scene):
        x, y = scene.screen(i+.5, j+.5)
        if water(i+.5, j+.5):
            kind = 'water'
        elif any(water(i+.5+di, j+.5+dj) for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            kind = 'quay'
        elif any(water(i+.5+di, j+.5+dj) for di, dj in ((3, 0), (-3, 0), (0, 3), (0, -3))):
            kind = 'promenade'
        elif (x > 270 and y > 380) or (x > 555 and y > 350) or (x < 170 and y < 150):
            kind = 'gravel' if i % 9 == 0 or j % 9 == 0 else 'grass'
        elif i % 12 == 0 or j % 12 == 0 or abs(x+1.6*y-1050) < 8:
            kind = 'cobble'
        else:
            kind = 'lot'
        kinds[(i, j)] = kind

    reserved, protected, silhouette = set(), [], set()

    def reserve(i, j, wi, wj):
        for a in range(math.floor(i), math.ceil(i+wi)):
            for b in range(math.floor(j), math.ceil(j+wj)):
                reserved.add((a, b))
                if kinds.get((a, b)) == 'lot':
                    kinds[(a, b)] = 'pave'

    def landmark(builder, x, y, wi, wj):
        ci, cj = tile(x, y)
        i, j = ci-wi/2, cj-wj/2
        builder(scene, i, j)
        reserve(i-.7, j-.7, wi+1.4, wj+2)
        study = iso.Scene(WIDTH+200, HEIGHT+200, (scene.ox+100, scene.oy+100))
        builder(study, i, j)
        study.paint_objects()
        left, top, right, bottom = (v-100 for v in study.img.convert('RGB').getbbox())
        assert 0 < left < right < WIDTH and 0 < top < bottom < HEIGHT, (builder.__name__, (left, top, right, bottom))
        protected.append((left-4, top-3, right+4, bottom+5))
        pixels = study.img.convert('RGB').load()
        for sy in range(top+100, bottom+100):
            for sx in range(left+100, right+100):
                if pixels[sx, sy] != (0, 0, 0):
                    silhouette.update((sx-100+dx, sy-100+dy) for dx in range(-3, 4) for dy in range(-3, 4))

    # Real longitude and latitude orders, compressed independently. Palace on the
    # Isle lies slightly north and east of Chopin; Wilanów is farther southeast.
    landmark(pl.barbican, 100, 95, 8, 6)
    landmark(pl.old_town_square, 225, 165, 10, 8)
    landmark(pl.st_john, 355, 205, 6.3, 7)
    landmark(pl.royal_castle, 400, 335, 10, 8)
    landmark(pl.culture_palace, 95, 385, 10, 8)
    landmark(pl.palace_isle, 505, 435, 8, 4.8)
    landmark(pl.chopin_monument, 415, 470, 7, 6)
    landmark(pl.wilanow, 635, 475, 11, 5)

    # Defilad Square, Castle Square and the Royal Route remain distinct paving.
    for (i, j), kind in list(kinds.items()):
        x, y = scene.screen(i+.5, j+.5)
        if kind == 'lot' and (10 < x < 190 and 265 < y < 420 or 310 < x < 450 and 335 < y < 380):
            kinds[(i, j)] = 'cobble'
            reserved.add((i, j))
    paint_ground(scene, {c: 'pave' if k == 'promenade' else k for c, k in kinds.items()},
                 {}, pl.WATER, pl.STONE['dark'])

    for li in range(-12, 112, 3):
        for lj in range(-12, 112, 3):
            wi, wj = 2.5, 3
            cells = [(a, b) for a in range(li, li+3) for b in range(lj, lj+3)]
            if not all(kinds.get(c) == 'lot' and c not in reserved for c in cells):
                continue
            seed = int(h01(li, lj, 557)*10000)
            floors = 2 if seed % 3 == 0 else 3
            x, y = scene.screen(li+wi/2, lj+wj/2)
            if any(water(li+wi/2+di, lj+wj/2+dj) for di, dj in ((4, 0), (-4, 0), (0, 4), (0, -4))):
                continue
            half, top, bottom = (wi+wj)*4+6, y-floors*11-28, y+(wi+wj)*2+6
            if any(x+half > l and x-half < r and bottom > t and top < b for l, t, r, b in protected):
                ax, ay = scene.screen(li, lj)
                x0, y0 = math.floor(ax-50), math.floor(ay-80)
                study = iso.Scene(100, 140, (scene.ox-x0, scene.oy-y0))
                pl.townhouse(study, li, lj, wi, wj, floors, seed, ornate=seed % 3 == 0)
                study.paint_objects()
                l, t, r, b = study.img.convert('RGB').getbbox()
                pixels = study.img.convert('RGB').load()
                if any((sx+x0, sy+y0) in silhouette and pixels[sx, sy] != (0, 0, 0)
                       for sy in range(t, b) for sx in range(l, r)):
                    continue
            pl.townhouse(scene, li, lj, wi, wj, floors, seed, ornate=seed % 3 == 0)
            reserved.update(cells)

    trees = [round_tree(n, '#7D965F', '#344D34') for n in range(3)]
    for (i, j), kind in kinds.items():
        x, y = scene.screen(i+.5, j+.5)
        if (i, j) in reserved or any(l-12 < x < r+12 and t-3 < y < b+25 for l, t, r, b in protected):
            continue
        if kind == 'grass' and h01(i, j, 559) < .12 or kind == 'promenade' and (i+j) % 11 == 0:
            scene.add(i+j+1.5, lambda s, x=x, y=y, tree=trees[(i+j) % 3]: s.sprite(tree, x, y+4))
        # Formal rose beds in the two southern palace gardens.
        if kind == 'grass' and y > 400 and h01(i, j, 561) < .05:
            for dx in (-2, 0, 2):
                scene.put(x+dx, y, pl.SALMON['lit'] if i % 2 else pl.PALE['hi'])
    for i, j in ((29, 4), (42, 5)):
        x, y = scene.screen(i, j)
        image = bateau(0) if i % 2 else rowboat(i)
        scene.add(i+j, lambda s, x=x, y=y, image=image: s.sprite(image, x, y))
    scene.paint_objects()
    return scene.img.convert('RGB')


def luxembourg():
    import landmarks_luxembourg as lu

    scene = new_scene()

    def tile(x, y):
        return tile_of((x-WIDTH/2)/8, (y-scene.oy)/4)

    # The Ville Haute and the Kirchberg are raised plateaus cut by wooded gorges, all on
    # isometric axes. The Pétrusse runs up the i = 49 line under the Adolphe Bridge to its
    # confluence in the Grund; the Alzette arrives from the south along j = 47, turns past
    # Neumünster towards Clausen below the Bock, then runs north through Pfaffenthal (j = 20)
    # between the old town and the Kirchberg. Neumünster's Grund and the Bock's ravine are
    # valley floor; the Bock rock rises from it beside the Castle Bridge.
    UP = 30
    PETRUSSE = [(49, 130), (49, 47)]
    ALZETTE = [(120, 47), (49, 47), (49, 20), (-40, 20)]
    GRUND = (49.5, 63, 35.5, 47)
    BOCK = (36.3, 49, 21, 29.5)

    def path_nearest(i, j, path):
        best = (1e9, i, j)
        for (a, b), (c, d) in zip(path, path[1:]):
            ni, nj = min(max(i, min(a, c)), max(a, c)), min(max(j, min(b, d)), max(b, d))
            best = min(best, (math.hypot(i-ni, j-nj), ni, nj))
        return best

    def rect_nearest(i, j, rect):
        i0, i1, j0, j1 = rect
        ni, nj = min(max(i, i0), i1), min(max(j, j0), j1)
        return math.hypot(i-ni, j-nj), ni, nj

    def terrain(i, j):
        a, p = path_nearest(i, j, ALZETTE), path_nearest(i, j, PETRUSSE)
        e = UP
        for (d, ni, nj), floor in ((a, 2), (p, 1.4), (rect_nearest(i, j, GRUND), 0), (rect_nearest(i, j, BOCK), 0)):
            low = d-floor
            # Sandstone cliffs face the viewer across each gorge; the near side, which would
            # otherwise hide the river, descends in gentle wooded terraces.
            width = 5 if ni+nj < i+j-.3 else 1.5
            e = min(e, 0 if low <= 0 else min(UP, 6*math.ceil(UP*low/width/6)))
        return a[0], p[0], e

    # Raised tiles are drawn up to UP pixels higher, so cover the bottom edge with extra rows.
    tiles = [(i, j) for i in range(-20, 120) for j in range(-20, 120)
             if -16 < scene.screen(i, j)[0] < WIDTH+16 and -50 < scene.screen(i, j)[1] < HEIGHT+8+UP]
    kinds, elev = {}, {}
    for i, j in tiles:
        x, y = scene.screen(i+.5, j+.5)
        a, p, e = terrain(i+.5, j+.5)
        # Plateau edges standing in front of (below) a gorge stay open so the valley shows.
        front = e == UP and any(terrain(i+.5-k, j+.5-k)[2] < UP for k in (1, 2, 3, 4, 5))
        if a < 1.1 or p < .7:
            kind = 'water'
        elif e == 0:
            kind = 'quay' if a < 1.9 or p < 1.3 else 'grass'
        elif e < UP:
            kind = 'wood'
        elif front:
            kind = 'rim' if terrain(i+.5-1, j+.5-1)[2] < UP else 'grass'
        elif j+.5 < 20 and i+.5 < 49 or x < 150 and y < 200:
            # Kirchberg's parkland round Fort Thüngen; the municipal park north-west.
            kind = 'gravel' if i % 11 == 0 or j % 11 == 0 else 'grass'
        elif i % 12 == 0 or j % 12 == 0:
            kind = 'cobble'
        else:
            kind = 'lot'
        kinds[(i, j)] = kind
        if e:
            elev[(i, j)] = e

    reserved,protected,silhouette=set(),[],set()

    def reserve(i,j,wi,wj):
        for a in range(math.floor(i),math.ceil(i+wi)):
            for b in range(math.floor(j),math.ceil(j+wj)):
                reserved.add((a,b))
                if kinds.get((a,b))=='lot':kinds[(a,b)]='pave'

    def landmark(builder, ci, cj, wi, wj, z=0):
        i, j = ci-wi/2, cj-wj/2
        build = (lambda s: builder(s, i, j, z=z)) if z else (lambda s: builder(s, i, j))
        build(scene)
        reserve(i-.8, j-.8, wi+1.6, wj+2)
        study = iso.Scene(WIDTH+200, HEIGHT+200, (scene.ox+100, scene.oy+100))
        build(study)
        study.paint_objects()
        left, top, right, bottom = (v-100 for v in study.img.convert('RGB').getbbox())
        assert 0 < left < right < WIDTH and 0 < top < bottom < HEIGHT, (builder.__name__, (left, top, right, bottom))
        protected.append((left-4, top-4, right+4, bottom+5))
        pixels = study.img.convert('RGB').load()
        for sy in range(top+100, bottom+100):
            for sx in range(left+100, right+100):
                if pixels[sx, sy] != (0, 0, 0):
                    silhouette.update((sx-100+dx, sy-100+dy) for dx in range(-3, 4) for dy in range(-3, 4))

    # Relative coordinate order is preserved in both axes, with distance compressed. The Bock
    # rock, Neumünster and the Adolphe Bridge stand on the valley floor; the rest on the plateaus.
    landmark(lu.philharmonie, *tile(655, 100), 9, 6, UP)
    landmark(lu.mudam, 35.5, 12.9, 9, 6, UP)
    landmark(lu.bock, 42, 24.6, 10, 4.5)
    landmark(lu.palace, 38.5, 48.5, 9, 3.5, UP)
    landmark(lu.abbey, 55.5, 39.4, 10, 7)
    landmark(lu.cathedral, 43.2, 64, 6, 8, UP)
    landmark(lu.gelle_fra, 44.5, 75, 3.8, 3.8, UP)
    landmark(lu.adolphe_bridge, 49.5, 82.5, 12, 2.6)

    # Place de la Constitution round the Gëlle Fra and the palace's street front stay open.
    for (i, j), kind in list(kinds.items()):
        if kind in ('lot', 'pave', 'cobble') and (41 <= i <= 46 and 70 <= j <= 77 or 34 <= i <= 43 and 50 <= j <= 52):
            kinds[(i, j)] = 'square'
            reserved.add((i, j))

    rim, slope = iso.stone_wall(lu.ROCK['mid']), iso.stone_wall(rgb('#7F8A55'))
    for (i, j) in sorted(kinds, key=lambda t: (t[0]+t[1], t[0])):
        kind, e = kinds[(i, j)], elev.get((i, j), 0)
        def color(x, y, k=kind):
            if k == 'water':
                if h01(x//3, y, 9) < .02:
                    return lu.WATER[2]
                return lu.WATER[1] if h01(x//6, y//2, 4) < .3 else lu.WATER[0]
            if k == 'quay':
                return rgb('#D8CDB2') if (x+y) % 6 else rgb('#B3A68C')
            if k == 'rim':
                return rgb('#CFC2A2') if (x+3*(y % 2)) % 8 else rgb('#B5A786')
            if k == 'wood':
                r = h01(x, y, 6)
                return rgb('#5F8A3E') if r < .2 else rgb('#7FA94A') if r < .3 else rgb('#6E9A45')
            if k == 'gravel':
                return shade(rgb('#E6DAB8'), -.08) if h01(x, y, 6) < .15 else rgb('#E6DAB8')
            if k == 'square':
                return rgb('#C9C3B6') if (x+2*(y % 2)) % 6 else rgb('#B1AA9C') if y % 3 else rgb('#DAD4C8')
            return ground_color('pave' if k == 'lot' else k, x, y)
        iso.ground_tile(scene, i, j, color, e, (rim if e == UP else slope) if e else None)

    for li in range(-12, 112, 3):
        for lj in range(-12, 112, 3):
            wi, wj = 2.5, 3
            cells = [(a, b) for a in range(li, li+3) for b in range(lj, lj+3)]
            if not all(kinds.get(c) == 'lot' and c not in reserved for c in cells):
                continue
            up = {elev.get(c, 0) for c in cells}
            if len(up) != 1:
                continue
            z = up.pop()
            seed = int(h01(li, lj, 613)*10000)
            floors = 2 if seed % 3 == 0 else 3
            x, y = scene.screen(li+wi/2, lj+wj/2)
            y -= z
            half = (wi+wj)*4+7
            if any(x+half > l and x-half < r and y+17 > t and y-floors*11-30 < b for l, t, r, b in protected):
                ax, ay = scene.screen(li, lj)
                x0, y0 = math.floor(ax-50), math.floor(ay-80-z)
                study = iso.Scene(100, 140, (scene.ox-x0, scene.oy-y0))
                lu.townhouse(study, li, lj, wi, wj, floors, seed, z)
                study.paint_objects()
                l, t, r, b = study.img.convert('RGB').getbbox()
                pixels = study.img.convert('RGB').load()
                if any((sx+x0, sy+y0) in silhouette and pixels[sx, sy] != (0, 0, 0)
                       for sy in range(t, b) for sx in range(l, r)):
                    continue
            lu.townhouse(scene, li, lj, wi, wj, floors, seed, z)
            reserved.update(cells)

    # A low bridge into the Grund beside Neumünster, below the high Adolphe Bridge's level.
    lp.stone_bridge(scene, 57.5, 45.7, 2.6, width=1.2, deck=5)
    reserved.update((a, b) for a in range(56, 60) for b in range(44, 50))

    trees = [round_tree(n, '#78975F', '#304C36') for n in range(3)]
    woods = [round_tree(n, '#5C8F45', '#21391F') for n in range(3)]
    for (i, j), kind in kinds.items():
        x, y = scene.screen(i+.5, j+.5)
        y -= elev.get((i, j), 0)
        # A tree may stand beside a landmark, never over any of its painted pixels.
        if (i, j) in reserved or any((x+dx, y+dy) in silhouette for dx in range(-9, 10, 3) for dy in range(-18, 6, 3)):
            continue
        if kind == 'wood' and h01(i, j, 619) < .3:
            scene.add(i+j+1.5, lambda s, x=x, y=y, tree=woods[(i+j) % 3]: s.sprite(tree, x, y+4))
        elif kind == 'grass' and h01(i, j, 617) < .16 or kind == 'rim' and h01(i, j, 618) < .07:
            scene.add(i+j+1.5, lambda s, x=x, y=y, tree=trees[(i+j) % 3]: s.sprite(tree, x, y+4))
    # Rowing boats on the Alzette: in Pfaffenthal and upstream of the Grund.
    for bi, bj in ((30.5, 20.3), (68.5, 47.3)):
        x, y = scene.screen(bi, bj)
        scene.add(bi+bj, lambda s, x=x, y=y: s.sprite(rowboat(0), x, y))
    scene.paint_objects()
    return scene.img.convert('RGB')


def bratislava():
    import landmarks_slovakia as sk

    scene=new_scene()

    def tile(x,y):
        return tile_of((x-WIDTH/2)/8,(y-scene.oy)/4)

    # Danube along the i axis, with the bridge crossing squarely along j.
    bridge_i,bridge_j=tile(135,465)
    bridge_i-=1.4
    bridge_j-=11
    river_j=bridge_j+10
    kinds={}
    for i,j in visible_tiles(scene):
        x,y=scene.screen(i+.5,j+.5)
        distance=abs(j+.5-river_j)
        if distance<4:kind='water'
        elif distance<5.2:kind='quay'
        elif distance<6.5:kind='promenade'
        elif j>river_j or x<225 and y<310 or 345<x<510 and y<120:
            kind='gravel' if i%9==0 or j%9==0 else 'grass'
        elif i%11==0 or j%11==0:kind='cobble'
        else:kind='lot'
        kinds[(i,j)]=kind

    reserved,protected,silhouette=set(),[],set()

    def reserve(i,j,wi,wj):
        for a in range(math.floor(i),math.ceil(i+wi)):
            for b in range(math.floor(j),math.ceil(j+wj)):
                reserved.add((a,b))
                if kinds.get((a,b))=='lot':kinds[(a,b)]='pave'

    def landmark(builder,x,y,wi,wj):
        ci,cj=tile(x,y)
        i,j=ci-wi/2,cj-wj/2
        builder(scene,i,j)
        reserve(i-1,j-1,wi+2,wj+2.5)
        study=iso.Scene(WIDTH+200,HEIGHT+200,(scene.ox+100,scene.oy+100))
        builder(study,i,j);study.paint_objects()
        left,top,right,bottom=(v-100 for v in study.img.convert('RGB').getbbox())
        assert 0<left<right<WIDTH and 0<top<bottom<HEIGHT,(builder.__name__,(left,top,right,bottom))
        protected.append((left-4,top-4,right+4,bottom+5))
        pixels=study.img.convert('RGB').load()
        for sy in range(top+100,bottom+100):
            for sx in range(left+100,right+100):
                if pixels[sx,sy]!=(0,0,0):
                    silhouette.update((sx-100+dx,sy-100+dy) for dx in range(-3,4) for dy in range(-3,4))

    # Eight real anchors, compressed while retaining every lon/lat pair ordering.
    landmark(sk.grassalkovich,430,90,11,3.5)
    landmark(sk.michael_gate,325,170,3.8,3.5)
    landmark(sk.primatial_palace,565,190,8.5,3.5)
    landmark(sk.castle,130,320,10,8)
    landmark(sk.town_hall,455,245,8,6)
    landmark(sk.blue_church,650,300,5,6)
    landmark(sk.cathedral,300,420,5,8)
    landmark(sk.snp_bridge,135,465,2.8,22)

    # Main Square, Primatial Square and Hodžovo Square have open paved forecourts.
    for (i,j),kind in list(kinds.items()):
        x,y=scene.screen(i+.5,j+.5)
        if kind=='lot' and (390<x<520 and 245<y<290 or 505<x<620 and 190<y<225 or 365<x<495 and 90<y<130):
            kinds[(i,j)]='cobble';reserved.add((i,j))
    paint_ground(scene,{c:'pave' if k=='promenade' else k for c,k in kinds.items()},
                 {},sk.WATER,sk.ROCK['dark'])

    for li in range(-12,112,3):
        for lj in range(-12,112,3):
            wi,wj=2.5,3
            cells=[(a,b) for a in range(li,li+3) for b in range(lj,lj+3)]
            if not all(kinds.get(c)=='lot' and c not in reserved for c in cells):continue
            seed=int(h01(li,lj,1701)*10000)
            floors=2 if seed%3==0 else 3
            x,y=scene.screen(li+wi/2,lj+wj/2)
            half=(wi+wj)*4+7
            if any(x+half>l and x-half<r and y+17>t and y-floors*10-30<b for l,t,r,b in protected):
                ax,ay=scene.screen(li,lj)
                x0,y0=math.floor(ax-50),math.floor(ay-80)
                study=iso.Scene(100,140,(scene.ox-x0,scene.oy-y0))
                sk.townhouse(study,li,lj,wi,wj,floors,seed);study.paint_objects()
                l,t,r,b=study.img.convert('RGB').getbbox()
                pixels=study.img.convert('RGB').load()
                if any((sx+x0,sy+y0) in silhouette and pixels[sx,sy]!=(0,0,0)
                       for sy in range(t,b) for sx in range(l,r)):continue
            sk.townhouse(scene,li,lj,wi,wj,floors,seed)
            reserved.update(cells)

    trees=[round_tree(n,'#6D9959','#2D4B31') for n in range(3)]
    for (i,j),kind in kinds.items():
        x,y=scene.screen(i+.5,j+.5)
        if (i,j) in reserved or any(l-12<x<r+12 and t-3<y<b+25 for l,t,r,b in protected):continue
        if kind=='grass' and h01(i,j,1748)<.1 or kind=='promenade' and (i+j)%11==0:
            scene.add(i+j+1.5,lambda s,x=x,y=y,tree=trees[(i+j)%3]:s.sprite(tree,x,y+4))
    # River excursion boats retain the open water and stay clear of the bridge.
    for offset in (-12,8):
        bi,bj=bridge_i+offset,river_j+1
        x,y=scene.screen(bi,bj)
        scene.add(bi+bj,lambda s,x=x,y=y:s.sprite(bateau(1),x,y))
    scene.paint_objects()
    return scene.img.convert('RGB')


def budapest():
    import landmarks_hungary as hu

    scene=new_scene()

    def tile(x,y):
        return tile_of((x-WIDTH/2)/8,(y-scene.oy)/4)

    # Compressed Danube bends use only tile axes. The local reach through the
    # Chain Bridge follows j, so the deck crosses the water squarely along i.
    river_path=[tile(x,y) for x,y in [(325,-40),(165,40),(365,140),(225,210),
                                      (365,280),(285,320),(445,400),(345,450),(485,520)]]

    def river_distance(i,j):
        best=1e9
        for (ai,aj),(bi,bj) in zip(river_path,river_path[1:]):
            di,dj=bi-ai,bj-aj
            t=max(0,min(1,((i-ai)*di+(j-aj)*dj)/(di*di+dj*dj)))
            best=min(best,math.hypot(i-ai-t*di,j-aj-t*dj))
        return best
    kinds={}
    for i,j in visible_tiles(scene):
        x,y=scene.screen(i+.5,j+.5)
        distance=river_distance(i+.5,j+.5)
        if distance<3.2:kind='water'
        elif distance<4.2:kind='quay'
        elif distance<5.5:kind='promenade'
        elif x<210 and y>220 or x>480 and y<210:
            kind='gravel' if i%9==0 or j%9==0 else 'grass'
        elif i%11==0 or j%11==0:kind='cobble'
        else:kind='lot'
        kinds[(i,j)]=kind

    reserved,protected,silhouette=set(),[],set()

    def reserve(i,j,wi,wj):
        for a in range(math.floor(i),math.ceil(i+wi)):
            for b in range(math.floor(j),math.ceil(j+wj)):
                reserved.add((a,b))
                if kinds.get((a,b))=='lot':kinds[(a,b)]='pave'

    def landmark(builder,x,y,wi,wj):
        ci,cj=tile(x,y)
        i,j=ci-wi/2,cj-wj/2
        builder(scene,i,j)
        reserve(i-1,j-1,wi+2,wj+2.5)
        study=iso.Scene(WIDTH+200,HEIGHT+200,(scene.ox+100,scene.oy+100))
        builder(study,i,j);study.paint_objects()
        left,top,right,bottom=(v-100 for v in study.img.convert('RGB').getbbox())
        assert 0<left<right<WIDTH and 0<top<bottom<HEIGHT,(builder.__name__,(left,top,right,bottom))
        protected.append((left-4,top-4,right+4,bottom+5))
        pixels=study.img.convert('RGB').load()
        for sy in range(top+100,bottom+100):
            for sx in range(left+100,right+100):
                if pixels[sx,sy]!=(0,0,0):
                    silhouette.update((sx-100+dx,sy-100+dy) for dx in range(-3,4) for dy in range(-3,4))

    # Real north/east order, compressed; footprints/silhouettes reserve their squares.
    landmark(hu.szechenyi_baths,625,112,11,8)
    landmark(hu.heroes_square,590,215,11,7)
    landmark(hu.parliament,450,290,12,5)
    landmark(hu.fishermans_bastion,180,315,11,4.5)
    landmark(hu.matthias_church,70,365,5,7)
    landmark(hu.st_stephen,570,395,7,6)
    landmark(hu.chain_bridge,375,435,18,2.5)
    landmark(hu.buda_castle,210,480,12,4.5)

    # Kossuth Square and St Stephen's Square stay open in front of their monuments.
    for (i,j),kind in list(kinds.items()):
        x,y=scene.screen(i+.5,j+.5)
        if kind=='lot' and (325<x<450 and 290<y<325 or 560<x<655 and 390<y<430):
            kinds[(i,j)]='cobble';reserved.add((i,j))
    paint_ground(scene,{c:'pave' if k=='promenade' else k for c,k in kinds.items()},
                 {},hu.WATER,hu.STONE['dark'])

    for li in range(-12,112,3):
        for lj in range(-12,112,3):
            wi,wj=2.5,3
            cells=[(a,b) for a in range(li,li+3) for b in range(lj,lj+3)]
            if not all(kinds.get(c)=='lot' and c not in reserved for c in cells):continue
            seed=int(h01(li,lj,1801)*10000)
            floors=2 if seed%3==0 else 3
            x,y=scene.screen(li+wi/2,lj+wj/2)
            half=(wi+wj)*4+7
            if any(x+half>l and x-half<r and y+17>t and y-floors*10-30<b for l,t,r,b in protected):
                ax,ay=scene.screen(li,lj)
                x0,y0=math.floor(ax-50),math.floor(ay-80)
                study=iso.Scene(100,140,(scene.ox-x0,scene.oy-y0))
                hu.townhouse(study,li,lj,wi,wj,floors,seed);study.paint_objects()
                l,t,r,b=study.img.convert('RGB').getbbox()
                pixels=study.img.convert('RGB').load()
                if any((sx+x0,sy+y0) in silhouette and pixels[sx,sy]!=(0,0,0)
                       for sy in range(t,b) for sx in range(l,r)):continue
            hu.townhouse(scene,li,lj,wi,wj,floors,seed)
            reserved.update(cells)

    trees=[round_tree(n,'#6D9959','#2D4B31') for n in range(3)]
    for (i,j),kind in kinds.items():
        x,y=scene.screen(i+.5,j+.5)
        if (i,j) in reserved or any(l-12<x<r+12 and t-3<y<b+25 for l,t,r,b in protected):continue
        if kind=='grass' and h01(i,j,1848)<.1 or kind=='promenade' and (i+j)%11==0:
            scene.add(i+j+1.5,lambda s,x=x,y=y,tree=trees[(i+j)%3]:s.sprite(tree,x,y+4))
    # Excursion boats along open Danube reaches, away from bridge piers.
    for px,py in ((310,285),(415,485)):
        bi,bj=tile(px,py)
        x,y=scene.screen(bi,bj)
        if any(l-15<x<r+15 and t-5<y<b+10 for l,t,r,b in protected):continue
        scene.add(bi+bj,lambda s,x=x,y=y:s.sprite(bateau(1),x,y))
    scene.paint_objects()
    return scene.img.convert('RGB')


def tallinn():
    import landmarks_estonia as ee

    scene=new_scene()

    def tile(x,y):
        return tile_of((x-WIDTH/2)/8,(y-scene.oy)/4)

    # Tallinn Bay and the harbour are north of Old Town. Every shore segment
    # follows a tile axis; the lower town has no invented river.
    coast=[(-40,-25),(140,65),(280,-5),(420,65),(520,15),(720,115),(800,75)]

    def shore(x):
        for (ax,ay),(bx,by) in zip(coast,coast[1:]):
            if ax<=x<=bx:return ay+(by-ay)*(x-ax)/(bx-ax)
        return -25

    # Toompea, the limestone upper town, stands about 25 m above the Lower Town in the south-west.
    # Its plateau follows the tile axes, so the eastern escarpment shows as a limestone cliff above
    # Lühike jalg; a street runs along the foot of its northern rims, and a green strip along the cliff.
    UP=next(site[5] for site in ee.SITES if site[0]=='toompea')
    def hill(i,j):return 40<=i<=60 and j>=69

    kinds,elev={},{}
    # Plateau tiles just below the frame are kept, so its cut edge shows no wall.
    below=[(i,j) for i in range(-20,120) for j in range(-20,120)
           if hill(i,j) and HEIGHT+8<=scene.screen(i,j)[1]<HEIGHT+UP+16 and -16<scene.screen(i,j)[0]<WIDTH+16]
    for i,j in list(visible_tiles(scene))+below:
        x,y=scene.screen(i+.5,j+.5)
        distance=y-shore(x)
        if distance<0:kind='water'
        elif distance<9:kind='quay'
        elif distance<22:kind='promenade'
        elif hill(i,j):
            elev[(i,j)]=UP
            # Rampart walks along the northern rims; grass above the eastern cliff.
            if not hill(i-1,j) or not hill(i,j-1):kind='rampart'
            elif not hill(i+1,j):kind='grass'
            else:kind='cobble' if i%7==0 or j%7==0 else 'lot'
        elif any(hill(i+a,j+b) for a in range(5) for b in range(5)):kind='cobble'
        elif any(hill(i-a,j) for a in (1,2,3)):kind='grass'
        elif x<265 and y>330 or x>530 and 180<y<330:
            kind='gravel' if i%10==0 or j%10==0 else 'grass'
        elif i%11==0 or j%11==0:kind='cobble'
        else:kind='lot'
        kinds[(i,j)]=kind

    reserved,protected,silhouette=set(),[],set()

    def reserve(i,j,wi,wj):
        for a in range(math.floor(i),math.ceil(i+wi)):
            for b in range(math.floor(j),math.ceil(j+wj)):
                reserved.add((a,b))
                if kinds.get((a,b))=='lot':kinds[(a,b)]='pave'

    lower=set()   # pixels of the Lower Town landmarks, which stand behind Toompea's rims
    for _,builder,(wi,wj),_,(x,y),z in ee.SITES:
        ci,cj=tile(x,y)
        i,j=ci-wi/2,cj-wj/2
        build=(lambda s,b=builder,i=i,j=j,z=z:b(s,i,j,z=z)) if z else (lambda s,b=builder,i=i,j=j:b(s,i,j))
        build(scene)
        reserve(i-1,j-1,wi+2,wj+2.5)
        study=iso.Scene(WIDTH+200,HEIGHT+200,(scene.ox+100,scene.oy+100))
        build(study);study.paint_objects()
        left,top,right,bottom=(v-100 for v in study.img.convert('RGB').getbbox())
        assert 0<left<right<WIDTH and 0<top<bottom<HEIGHT,(builder.__name__,(left,top,right,bottom))
        protected.append((left-4,top-4,right+4,bottom+5))
        pixels=study.img.convert('RGB').load()
        for sy in range(top+100,bottom+100):
            for sx in range(left+100,right+100):
                if pixels[sx,sy]!=(0,0,0):
                    silhouette.update((sx-100+dx,sy-100+dy) for dx in range(-3,4) for dy in range(-3,4))
                    if not z:lower.add((sx-100,sy-100))

    # Raekoja plats opens north of the hall; Viru street and Lossi plats are paved.
    for (i,j),kind in list(kinds.items()):
        x,y=scene.screen(i+.5,j+.5)
        if kind=='lot' and (370<x<500 and 270<y<355 or 475<x<635 and 355<y<415):
            kinds[(i,j)]='cobble';reserved.add((i,j))
    paint_ground(scene,{c:'pave' if k=='promenade' else k for c,k in kinds.items() if c not in elev},
                 {},ee.WATER,ee.STONE['dark'])
    # Toompea's older, warmer limestone paving, painted after the Lower Town so it covers the ground
    # behind the plateau; each tile's cliff face is limestone.
    cliff=iso.stone_wall(ee.STONE['dark'])
    for (i,j) in sorted(elev,key=lambda t:(t[0]+t[1],t[0])):
        def color(x,y,k=kinds[(i,j)]):
            if k=='rampart':return rgb('#DCD6C2') if (x+2*(y%2))%8 else rgb('#B8B19C')
            if k=='cobble':return rgb('#978566') if (x+2*(y%2))%4==0 else rgb('#B5A27E')
            if k in ('lot','pave'):return rgb('#CBB994') if (x+2*(y%2))%5 else rgb('#AD9B77')
            return ground_color(k,x,y)
        iso.ground_tile(scene,i,j,color,UP,cliff)
    # The medieval curtain wall crowns the northern rims, with merlons on alternate tiles.
    for (i,j),kind in kinds.items():
        if kind!='rampart':continue
        reserved.add((i,j))
        # Leave a gap where the wall would cross in front of a landmark (St Nicholas below the rim).
        x,y=scene.screen(i+.5,j+.5,UP)
        if any((x+dx,y+dy) in lower for dx in range(-9,10) for dy in range(-14,6)):continue
        for wall,along in (((i,j,1,.3),not hill(i,j-1)),((i,j,.3,1),not hill(i-1,j))):
            if not along:continue
            def parapet(s,a=wall,n=i+j):
                ee.block(s,*a,6,ee.STONE,z=UP)
                if n%2:ee.block(s,a[0]+(.3 if a[2]==1 else 0),a[1]+(.3 if a[3]==1 else 0),
                                .4 if a[2]==1 else .3,.4 if a[3]==1 else .3,3,ee.STONE,z=UP+6)
            scene.add(i+j+1,parapet)
        reserved.add((i,j))

    for li in range(-12,112,3):
        for lj in range(-12,112,3):
            wi,wj=2.5,3
            cells=[(a,b) for a in range(li,li+3) for b in range(lj,lj+3)]
            if not all(kinds.get(c)=='lot' and c not in reserved for c in cells):continue
            up={elev.get(c,0) for c in cells}
            if len(up)!=1:continue
            z=up.pop()
            seed=int(h01(li,lj,1901)*10000)
            floors=2 if seed%3 or z else 3
            x,y=scene.screen(li+wi/2,lj+wj/2)
            y-=z
            half=(wi+wj)*4+7
            if any(x+half>l and x-half<r and y+17>t and y-floors*10-33<b for l,t,r,b in protected):
                ax,ay=scene.screen(li,lj)
                x0,y0=math.floor(ax-50),math.floor(ay-100)
                study=iso.Scene(100,160,(scene.ox-x0,scene.oy-y0))
                ee.townhouse(study,li,lj,wi,wj,floors,seed,z);study.paint_objects()
                l,t,r,b=study.img.convert('RGB').getbbox()
                pixels=study.img.convert('RGB').load()
                if any((sx+x0,sy+y0) in silhouette and pixels[sx,sy]!=(0,0,0)
                       for sy in range(t,b) for sx in range(l,r)):continue
            ee.townhouse(scene,li,lj,wi,wj,floors,seed,z)
            reserved.update(cells)

    trees=[round_tree(n,'#789664','#304E3B') for n in range(3)]
    for (i,j),kind in kinds.items():
        x,y=scene.screen(i+.5,j+.5)
        y-=elev.get((i,j),0)
        if (i,j) in reserved or any(l-12<x<r+12 and t-3<y<b+25 for l,t,r,b in protected):continue
        if kind=='grass' and h01(i,j,1948)<(.3 if (i,j) in elev else .12) or kind=='promenade' and (i+j)%11==0:
            scene.add(i+j+1.5,lambda s,x=x,y=y,tree=trees[(i+j)%3]:s.sprite(tree,x,y+4))
    # Kadriorg's formal flower beds, each low enough to leave the palace visible.
    for x,y in ((565,285),(585,300),(605,315),(670,310)):
        i,j=tile(x,y)
        if any(l-5<x<r+5 and t-5<y<b+10 for l,t,r,b in protected):continue
        iso.fill(scene,list(lp.corners(scene,i,j,1.8,1.8,1)),
                 lambda px,py:ee.RED['lit'] if h01(px,py,1950)<.22 else ee.DARK['lit'])
    for px,py in ((190,30),(680,75)):
        bi,bj=tile(px,py)
        x,y=scene.screen(bi,bj)
        if y<shore(x):scene.add(bi+bj,lambda s,x=x,y=y:s.sprite(bateau(1),x,y))
    scene.paint_objects()
    return scene.img.convert('RGB')


def riga():
    import landmarks_latvia as lv

    scene=new_scene()

    def tile(x,y):
        return tile_of((x-WIDTH/2)/8,(y-scene.oy)/4)

    # The Daugava runs NW/SE southwest of Old Town; the narrower city canal
    # follows the same isometric i axis through the northeastern park belt.
    def river_bank(x):return .5*x+300
    def canal_bank(x):return .5*x-85

    kinds={}
    for i,j in visible_tiles(scene):
        x,y=scene.screen(i+.5,j+.5)
        river=y-river_bank(x)
        canal=abs(y-canal_bank(x))
        if river>0 or canal<5:kind='water'
        elif river>-9 or canal<9:kind='quay'
        elif river>-24:kind='promenade'
        elif canal<38 or x>430 and y<290 or 605<x<715 and 325<y<385:
            kind='gravel' if i%10==0 or j%10==0 else 'grass'
        elif i%11==0 or j%11==0:kind='cobble'
        else:kind='lot'
        kinds[(i,j)]=kind

    reserved,protected,silhouette=set(),[],set()

    def reserve(i,j,wi,wj):
        for a in range(math.floor(i),math.ceil(i+wi)):
            for b in range(math.floor(j),math.ceil(j+wj)):
                reserved.add((a,b))
                if kinds.get((a,b))=='lot':kinds[(a,b)]='pave'

    for _,builder,(wi,wj),_,(x,y) in lv.SITES:
        ci,cj=tile(x,y)
        i,j=ci-wi/2,cj-wj/2
        builder(scene,i,j)
        reserve(i-1,j-1,wi+2,wj+2.5)
        study=iso.Scene(WIDTH+200,HEIGHT+200,(scene.ox+100,scene.oy+100))
        builder(study,i,j);study.paint_objects()
        left,top,right,bottom=(v-100 for v in study.img.convert('RGB').getbbox())
        assert 0<left<right<WIDTH and 0<top<bottom<HEIGHT,(builder.__name__,(left,top,right,bottom))
        protected.append((left-4,top-4,right+4,bottom+5))
        pixels=study.img.convert('RGB').load()
        for sy in range(top+100,bottom+100):
            for sx in range(left+100,right+100):
                if pixels[sx,sy]!=(0,0,0):
                    silhouette.update((sx-100+dx,sy-100+dy) for dx in range(-3,4) for dy in range(-3,4))

    # Cathedral Square and Town Hall Square stay open on the lower side.
    # The park bridge crosses the canal squarely along j, away from the monument.
    bi,bj=tile(425,127.5)
    lp.stone_bridge(scene,bi-.8,bj-2.2,4.4,width=1.6,deck=5)
    for (i,j),kind in list(kinds.items()):
        x,y=scene.screen(i+.5,j+.5)
        if kind=='lot' and (220<x<400 and 345<y<405 or 325<x<470 and 450<y<505):
            kinds[(i,j)]='cobble';reserved.add((i,j))
    paint_ground(scene,{c:'pave' if k=='promenade' else k for c,k in kinds.items()},
                 {},lv.WATER,lv.STONE['dark'])

    for li in range(-12,112,3):
        for lj in range(-12,112,3):
            wi,wj=2.5,3
            cells=[(a,b) for a in range(li,li+3) for b in range(lj,lj+3)]
            if not all(kinds.get(c)=='lot' and c not in reserved for c in cells):continue
            seed=int(h01(li,lj,2001)*10000)
            floors=2 if seed%3 else 3
            x,y=scene.screen(li+wi/2,lj+wj/2)
            half=(wi+wj)*4+7
            if any(x+half>l and x-half<r and y+17>t and y-floors*10-33<b for l,t,r,b in protected):
                ax,ay=scene.screen(li,lj)
                x0,y0=math.floor(ax-50),math.floor(ay-90)
                study=iso.Scene(100,150,(scene.ox-x0,scene.oy-y0))
                lv.townhouse(study,li,lj,wi,wj,floors,seed);study.paint_objects()
                l,t,r,b=study.img.convert('RGB').getbbox()
                pixels=study.img.convert('RGB').load()
                if any((sx+x0,sy+y0) in silhouette and pixels[sx,sy]!=(0,0,0)
                       for sy in range(t,b) for sx in range(l,r)):continue
            lv.townhouse(scene,li,lj,wi,wj,floors,seed)
            reserved.update(cells)

    trees=[round_tree(n,'#789664','#304E3B') for n in range(3)]
    for (i,j),kind in kinds.items():
        x,y=scene.screen(i+.5,j+.5)
        if (i,j) in reserved or any(l-12<x<r+12 and t-3<y<b+25 for l,t,r,b in protected):continue
        if kind=='grass' and h01(i,j,2048)<.12 or kind=='promenade' and (i+j)%11==0:
            scene.add(i+j+1.5,lambda s,x=x,y=y,tree=trees[(i+j)%3]:s.sprite(tree,x,y+4))
    # Formal flower beds and fountain in the Opera garden, clear of its facade.
    for x,y in ((615,340),(645,350),(685,330)):
        i,j=tile(x,y)
        if any(l-5<x<r+5 and t-5<y<b+10 for l,t,r,b in protected):continue
        iso.fill(scene,list(lp.corners(scene,i,j,1.5,1.5,1)),
                 lambda px,py:lv.BRICK['lit'] if h01(px,py,2050)<.2 else lv.COPPER['dark'])
    fi,fj=tile(670,360)
    def fountain(s):
        lv.cylinder(s,fi,fj,1.2,1.2,0,2,lv.STONE)
        lv.ellipse(s,fi,fj,1,1,2.2,lv.WATER[0])
        lv.cylinder(s,fi,fj,.16,.16,2,6,lv.PALE)
        lv.ellipse(s,fi,fj,.5,.5,7,lv.PALE['hi'])
    scene.add(fi+fj+2,fountain)
    for px,py in ((65,410),(270,495)):
        bi,bj=tile(px,py)
        x,y=scene.screen(bi,bj)
        if y>river_bank(x):scene.add(bi+bj,lambda s,x=x,y=y:s.sprite(bateau(1),x,y))
    scene.paint_objects()
    return scene.img.convert('RGB')


def vilnius():
    import landmarks_lithuania as lt

    scene = new_scene()

    def tile(x, y):
        return tile_of((x-WIDTH/2)/8, (y-scene.oy)/4)

    # The Neris passes north of the castle hill and Old Town along an isometric
    # axis. Its southern bank stays open. Castle Hill (Gediminas' Tower) and the higher Hill of
    # Three Crosses east of it rise as wooded mounds with flat summits, a valley between them.
    def river_bank(x):
        return .5*x-170

    tops = {name: z for name, _, _, _, _, z in lt.SITES if z}
    hills = [(480, 150, 96, 58, tops['gediminas']), (662, 222, 80, 60, tops['three-crosses'])]

    def hill_height(x, y):
        e = 0
        for cx, cy, rx, ry, top in hills:
            d = math.hypot((x-cx)/rx, (y-cy)/ry)
            if d < 1:
                # Flat summit, then a steep bank that eases out at the foot.
                e = max(e, top if d < .45 else 3*round(top*((1-d)/.55)**.6/3))
        return e

    kinds, elev = {}, {}
    for i, j in visible_tiles(scene):
        x, y = scene.screen(i+.5, j+.5)
        bank = y-river_bank(x)
        if -38 < bank < 0:
            kind = 'water'
        elif -48 < bank <= -38 or 0 <= bank < 10:
            kind = 'quay'
        elif -65 < bank <= -48 or 10 <= bank < 25:
            kind = 'promenade'
        elif hill_height(x, y) or x > 615 and 210 < y < 410 or 555 < x < 620 and 150 < y < 250:
            # The Bernardine Garden and the Vilnia valley between the two hills are parkland.
            kind = 'grass'
            if hill_height(x, y):
                elev[(i, j)] = hill_height(x, y)
        elif i % 11 == 0 or j % 11 == 0:
            kind = 'cobble'
        else:
            kind = 'lot'
        kinds[(i, j)] = kind

    def occluded(i, j):
        """True where a hill in front (screen-below) rises over this low cell's ground."""
        base = elev.get((i, j), 0)
        return any(elev.get((i+a, j+b), 0)-base > 4*(a+b)-2
                   for a in range(12) for b in range(12) if a+b and abs(a-b) <= 2)

    reserved, protected, silhouette = set(), [], set()

    def reserve(i, j, wi, wj):
        for a in range(math.floor(i), math.ceil(i+wi)):
            for b in range(math.floor(j), math.ceil(j+wj)):
                reserved.add((a, b))
                if kinds.get((a, b)) == 'lot':
                    kinds[(a, b)] = 'pave'

    for _, builder, (wi, wj), _, (x, y), z in lt.SITES:
        ci, cj = tile(x, y)
        i, j = ci-wi/2, cj-wj/2
        build = (lambda s, b=builder, i=i, j=j, z=z: b(s, i, j, z=z)) if z else (lambda s, b=builder, i=i, j=j: b(s, i, j))
        build(scene)
        reserve(i-1, j-1, wi+2, wj+2.5)
        # Measure the actual projected sculpture/roof silhouette, including tall spires.
        study = iso.Scene(WIDTH+200, HEIGHT+200, (scene.ox+100, scene.oy+100))
        build(study)
        study.paint_objects()
        left, top, right, bottom = (v-100 for v in study.img.convert('RGB').getbbox())
        assert 0 < left < right < WIDTH and 0 < top < bottom < HEIGHT, (builder.__name__, (left,top,right,bottom))
        protected.append((left-4, top-4, right+4, bottom+5))
        pixels = study.img.convert('RGB').load()
        for sy in range(top+100, bottom+100):
            for sx in range(left+100, right+100):
                if pixels[sx,sy] != (0,0,0):
                    silhouette.update((sx-100+dx, sy-100+dy) for dx in range(-3,4) for dy in range(-3,4))

    # Cathedral Square, university forecourt, Town Hall Square, Pilies/Didžioji
    # and the gate's approach are distinct paving, kept open in front of monuments.
    for (i,j), kind in list(kinds.items()):
        x,y = scene.screen(i+.5,j+.5)
        square = (90<x<295 and 305<y<380 or 45<x<205 and 455<y<520
                  or 275<x<415 and 420<y<487 or 405<x<525 and 475<y<520)
        pilies = 195<y<470 and abs(x-(290+.25*(y-280)))<11
        if kind == 'lot' and (square or pilies):
            kinds[(i,j)] = 'cobble'
            reserved.add((i,j))
    paint_ground(scene, {c:'pave' if k=='promenade' else k for c,k in kinds.items() if c not in elev},
                 {}, lt.WATER, lt.STONE['dark'])
    # The hills are painted over the low ground behind them, in depth order; their earthen,
    # grassy slopes step up to the summits.
    def slope(x, y, lit):
        if h01(x//2, y, 2204) < .25:
            return rgb('#7C6B4C') if lit else rgb('#54492F')
        return rgb('#5C8A3E') if lit else rgb('#3E5F31')
    for (i, j) in sorted(elev, key=lambda t: (t[0]+t[1], t[0])):
        # Lower slopes are darker under the woods; the open summits are lit.
        rise = elev[(i, j)]/max(tops.values())
        iso.ground_tile(scene, i, j, lambda x, y, k=rise: shade(ground_color('grass', x, y), -.28+.3*k),
                        elev[(i, j)], slope)
    # No bridge here: the real crossings (Mindaugas Bridge) lie north-west of the castle, off the scene.

    for li in range(-12,112,3):
        for lj in range(-12,112,3):
            wi,wj = 2.5,3
            cells = [(a,b) for a in range(li,li+3) for b in range(lj,lj+3)]
            if not all(kinds.get(c)=='lot' and c not in reserved for c in cells):
                continue
            if any(occluded(*c) for c in cells):
                continue
            seed = int(h01(li,lj,2201)*10000)
            floors = 2 if seed%3 else 3
            x,y = scene.screen(li+wi/2,lj+wj/2)
            half = (wi+wj)*4+7
            if any(x+half>l and x-half<r and y+17>t and y-floors*10-33<b for l,t,r,b in protected):
                ax,ay = scene.screen(li,lj)
                x0,y0 = math.floor(ax-50),math.floor(ay-90)
                study = iso.Scene(100,150,(scene.ox-x0,scene.oy-y0))
                lt.townhouse(study,li,lj,wi,wj,floors,seed)
                study.paint_objects()
                l,t,r,b = study.img.convert('RGB').getbbox()
                pixels = study.img.convert('RGB').load()
                if any((sx+x0,sy+y0) in silhouette and pixels[sx,sy]!=(0,0,0)
                       for sy in range(t,b) for sx in range(l,r)):
                    continue
            lt.townhouse(scene,li,lj,wi,wj,floors,seed)
            reserved.update(cells)

    trees = [round_tree(n,'#789361','#304C36') for n in range(3)]
    woods = [round_tree(n,'#5F8A4A','#243D27',1.1) for n in range(3)]
    for (i,j),kind in kinds.items():
        x,y = scene.screen(i+.5,j+.5)
        if occluded(i, j):
            continue
        if (i,j) in elev:
            # Wooded slopes; a tree may stand beside a monument, never over any of its pixels.
            y -= elev[(i,j)]
            if (i,j) in reserved or any((x+dx,y+dy) in silhouette for dx in range(-9,10,3) for dy in range(-18,6,3)):
                continue
            summit = elev[(i,j)] in tops.values()
            if h01(i,j,2205) < (.2 if summit else .55):
                scene.add(i+j+1.5,lambda s,x=x,y=y,tree=woods[(i+j)%3]:s.sprite(tree,x,y+4))
            continue
        if (i,j) in reserved or any(l-12<x<r+12 and t-3<y<b+25 for l,t,r,b in protected):
            continue
        if kind=='grass' and h01(i,j,2202)<.15 or kind=='promenade' and (i+j)%9==0:
            scene.add(i+j+1.5,lambda s,x=x,y=y,tree=trees[(i+j)%3]:s.sprite(tree,x,y+4))
    # Bernardine Garden east of St Anne's: gravel paths and small flower beds.
    for x,y in ((665,290),(678,335),(660,405)):
        gi,gj = tile(x,y)
        if any(l-8<x<r+8 and t-5<y<b+15 for l,t,r,b in protected):
            continue
        iso.fill(scene,list(lp.corners(scene,gi,gj,1.7,1.7,1)),
                 lambda px,py:lt.BRICK['lit'] if h01(px,py,2203)<.22 else lt.COPPER['dark'])
    for px,py in ((395,4),(650,120)):
        bi,bj = tile(px,py)
        if py<river_bank(px):
            scene.add(bi+bj,lambda s,x=px,y=py:s.sprite(rowboat(2),x,y))
    scene.paint_objects()
    return scene.img.convert('RGB')


def ljubljana():
    import landmarks_slovenia as sl

    scene = new_scene()

    def tile(x, y):
        return tile_of((x-WIDTH/2)/8, (y-scene.oy)/4)

    # The Ljubljanica crosses the scene along the j axis (south-west to north-east), so the Triple
    # and Dragon bridges cross it squarely along i. Castle Hill rises in the south-east.
    river_i = tile(240, 300)[0]
    plaza = tile(282, 247)  # Prešeren Square's radial paving centres on the monument.

    kinds = {}
    for i, j in visible_tiles(scene):
        x, y = scene.screen(i+.5, j+.5)
        d = i+.5-river_i
        hill = ((x-560)/190)**2+((y-480)/105)**2 < 1
        if abs(d) < 2.2:
            kind = 'water'
        elif abs(d) < 3:
            kind = 'quay'
        elif abs(d) < 4.8:
            kind = 'promenade'
        elif hill:
            kind = 'grass'
        elif i % 11 == 0 or j % 11 == 0:
            kind = 'cobble'
        else:
            kind = 'lot'
        kinds[(i, j)] = kind

    reserved, protected, silhouette = set(), [], set()

    def reserve(i, j, wi, wj):
        for a in range(math.floor(i), math.ceil(i+wi)):
            for b in range(math.floor(j), math.ceil(j+wj)):
                reserved.add((a, b))
                if kinds.get((a, b)) == 'lot':
                    kinds[(a, b)] = 'pave'

    # Castle Hill: a raised grass plateau with rock walls, below the castle's 20 px platform.
    castle = next(site for site in sl.SITES if site[0] == 'castle')
    hi, hj = tile(*castle[4])
    hw, hd = castle[2]
    elev = {}
    for (i, j), kind in kinds.items():
        di = max(hi-hw/2-i-.5, i+.5-hi-hw/2, 0)
        dj = max(hj-hd/2-j-.5, j+.5-hj-hd/2, 0)
        if kind in ('grass', 'lot', 'cobble') and max(di, dj) < 4.5:
            kinds[(i, j)] = 'grass'
            elev[(i, j)] = 10
            reserved.add((i, j))
    # The funicular climbs the north-west slope from Krekov trg to the castle.
    sl.funicular(scene, hi-hw/2-7, hj+.5, 7, 20)
    reserve(hi-hw/2-7, hj+.5, 7, 1)

    for _, builder, (wi, wj), _, (x, y) in sl.SITES:
        ci, cj = tile(x, y)
        i, j = ci-wi/2, cj-wj/2
        builder(scene, i, j)
        reserve(i-1, j-1, wi+2, wj+2.5)
        # Measure the projected silhouette, including spires, flags and dragon wings.
        study = iso.Scene(WIDTH+200, HEIGHT+200, (scene.ox+100, scene.oy+100))
        builder(study, i, j)
        study.paint_objects()
        left, top, right, bottom = (v-100 for v in study.img.convert('RGB').getbbox())
        assert 0 < left < right < WIDTH and 0 < top < bottom < HEIGHT, (builder.__name__, (left, top, right, bottom))
        protected.append((left-4, top-4, right+4, bottom+5))
        pixels = study.img.convert('RGB').load()
        for sy in range(top+100, bottom+100):
            for sx in range(left+100, right+100):
                if pixels[sx, sy] != (0, 0, 0):
                    silhouette.update((sx-100+dx, sy-100+dy) for dx in range(-3, 4) for dy in range(-3, 4))

    # Prešeren Square (radial granite), Town Square before the Town Hall, Cyril-Methodius Square
    # at the cathedral and Vodnik Square's open market behind the colonnade.
    squares = {}
    for (i, j), kind in list(kinds.items()):
        x, y = scene.screen(i+.5, j+.5)
        if kind not in ('lot', 'cobble'):
            continue
        if (i+.5-plaza[0])**2+(j+.5-plaza[1])**2 < 30 and i+.5 < river_i-4:
            squares[(i, j)] = 'radial'
        elif 210 < x < 330 and 395 < y < 470 or 330 < x < 470 and 345 < y < 380 or 440 < x < 545 and 245 < y < 320:
            squares[(i, j)] = 'cobble'
        else:
            continue
        kinds[(i, j)] = squares[(i, j)]
        reserved.add((i, j))

    for (i, j) in sorted(kinds, key=lambda t: (t[0]+t[1], t[0])):
        kind = kinds[(i, j)]
        if kind == 'radial':
            cx, cy = scene.screen(plaza[0], plaza[1])
            def color(x, y, cx=cx, cy=cy):
                dx, dy = x-cx, (y-cy)*2
                r, a = math.hypot(dx, dy), math.atan2(dy, dx)
                if abs(r-26) < 1.2 or abs(r-44) < 1.2 or r > 8 and abs((a*16/math.tau) % 1-.5) > .45:
                    return rgb('#EEE9DD')
                return C['cobble_dark'] if (x+2*(y % 2)) % 4 == 0 else rgb('#C9C1B2')
            iso.ground_tile(scene, i, j, color)
            continue
        k = 'pave' if kind == 'promenade' else kind
        e = elev.get((i, j), 0)
        def color(x, y, k=k):
            if k == 'water':
                if h01(x//3, y, 9) < .02:
                    return sl.WATER[2]
                return sl.WATER[1] if h01(x//6, y//2, 4) < .3 else sl.WATER[0]
            if k == 'quay':
                return rgb('#D9D2C0') if (x+y) % 6 else rgb('#B5AC98')
            return ground_color('pave' if k == 'lot' else k, x, y)
        iso.ground_tile(scene, i, j, color, e, iso.stone_wall(sl.ROCK['mid']) if e else None)

    for li in range(-12, 112, 3):
        for lj in range(-12, 112, 3):
            wi, wj = 2.5, 3
            cells = [(a, b) for a in range(li, li+3) for b in range(lj, lj+3)]
            if not all(kinds.get(c) == 'lot' and c not in reserved for c in cells):
                continue
            seed = int(h01(li, lj, 2301)*10000)
            floors = 2 if seed % 3 == 0 else 3
            x, y = scene.screen(li+wi/2, lj+wj/2)
            half = (wi+wj)*4+7
            if any(x+half > l and x-half < r and y+17 > t and y-floors*10-33 < b for l, t, r, b in protected):
                ax, ay = scene.screen(li, lj)
                x0, y0 = math.floor(ax-50), math.floor(ay-90)
                study = iso.Scene(100, 150, (scene.ox-x0, scene.oy-y0))
                sl.townhouse(study, li, lj, wi, wj, floors, seed)
                study.paint_objects()
                l, t, r, b = study.img.convert('RGB').getbbox()
                pixels = study.img.convert('RGB').load()
                if any((sx+x0, sy+y0) in silhouette and pixels[sx, sy] != (0, 0, 0)
                       for sy in range(t, b) for sx in range(l, r)):
                    continue
            sl.townhouse(scene, li, lj, wi, wj, floors, seed)
            reserved.update(cells)

    # Vodnik Square's open-air stalls between the cathedral and the colonnade.
    n = 0
    for x, y in ((470, 262), (500, 276), (478, 292), (510, 302), (455, 285)):
        si, sj = tile(x, y)
        if not any(l-2 < x < r+2 and t < y < b+6 for l, t, r, b in protected):
            sl.stall(scene, si, sj, n)
            n += 1

    trees = [round_tree(k, '#6F9B57', '#2C4A30') for k in range(3)]
    forest = [round_tree(k, '#557F45', '#21391F', 1.1) for k in range(3)]
    for (i, j), kind in kinds.items():
        x, y = scene.screen(i+.5, j+.5)
        if (i, j) in reserved or any(l-12 < x < r+12 and t-3 < y < b+25 for l, t, r, b in protected):
            continue
        if kind == 'grass' and h01(i, j, 2302) < .32:
            y -= elev.get((i, j), 0)
            scene.add(i+j+1.5, lambda s, x=x, y=y, tree=forest[(i+j) % 3]: s.sprite(tree, x, y+4))
        elif kind == 'promenade' and (i+j) % 3 == 0 and abs(i+.5-river_i) > 3.6:
            scene.add(i+j+1.5, lambda s, x=x, y=y, tree=trees[(i+j) % 3]: s.sprite(tree, x, y+4))
    # Tour boats on the river, clear of both bridges.
    for bj in (tile(140, 350)[1], tile(430, 205)[1]):
        x, y = scene.screen(river_i, bj)
        scene.add(river_i+bj, lambda s, x=x, y=y: s.sprite(rowboat(2), x, y))
    scene.paint_objects()
    return scene.img.convert('RGB')


def zagreb():
    import landmarks_croatia as hr

    scene = new_scene()

    def tile(x, y):
        return tile_of((x-WIDTH/2)/8, (y-scene.oy)/4)

    # Gradec (the Upper Town) is a raised plateau in the north-west; Ilica runs along its southern
    # foot on the i axis into Ban Jelačić Square; the Lower Town grid, Zrinjevac and the theatre
    # square lie south; Kaptol's cathedral stands east of Dolac.
    UP = 18
    square = tile(400, 352)
    ilica = square[1]+4
    zrinjevac = tile(440, 408)
    theatre_sq = tile(150, 440)

    def plateau(x, y):
        return ((x-205)/190)**2+((y-150)/92)**2 < 1

    kinds, elev = {}, {}
    for i, j in visible_tiles(scene):
        x, y = scene.screen(i+.5, j+.5)
        di, dj = i+.5-square[0], j+.5-square[1]
        if plateau(x, y):
            # Wooded southern slopes (Strossmayer promenade, Grič); a paved rim elsewhere.
            rim = not plateau(x, y+12) or not plateau(x-16, y) or not plateau(x+16, y)
            kind = ('grass' if y > 150 else 'cobble') if rim else 'cobble' if i % 7 == 0 or j % 7 == 0 else 'lot'
            elev[(i, j)] = UP
        elif abs(j+.5-ilica) < 1.2:
            kind = 'ilica'
        elif -6 < di < 7 and -5 < dj < 5.5:
            kind = 'square'
        elif abs(i+.5-zrinjevac[0]) < 4.5 and abs(j+.5-zrinjevac[1]) < 3.5:
            kind = 'park'
        elif abs(i+.5-theatre_sq[0]) < 7 and abs(j+.5-theatre_sq[1]) < 7.5:
            kind = 'park'
        elif (i-int(square[0])) % 11 == 0 or (j-int(square[1])) % 11 == 0:
            kind = 'cobble'
        else:
            kind = 'lot'
        kinds[(i, j)] = kind

    reserved, protected, silhouette = set(), [], set()

    def reserve(i, j, wi, wj):
        for a in range(math.floor(i), math.ceil(i+wi)):
            for b in range(math.floor(j), math.ceil(j+wj)):
                reserved.add((a, b))
                if kinds.get((a, b)) == 'lot':
                    kinds[(a, b)] = 'pave'

    def measure(build):
        study = iso.Scene(WIDTH+200, HEIGHT+200, (scene.ox+100, scene.oy+100))
        build(study)
        study.paint_objects()
        left, top, right, bottom = (v-100 for v in study.img.convert('RGB').getbbox())
        assert 0 < left < right < WIDTH and 0 < top < bottom < HEIGHT, (left, top, right, bottom)
        protected.append((left-4, top-4, right+4, bottom+5))
        pixels = study.img.convert('RGB').load()
        for sy in range(top+100, bottom+100):
            for sx in range(left+100, right+100):
                if pixels[sx, sy] != (0, 0, 0):
                    silhouette.update((sx-100+dx, sy-100+dy) for dx in range(-3, 4) for dy in range(-3, 4))

    for name, builder, (wi, wj), _, (x, y), z in hr.SITES:
        ci, cj = tile(x, y)
        i, j = ci-wi/2, cj-wj/2
        build = (lambda s, b=builder, i=i, j=j, z=z: b(s, i, j, z=z)) if z else (lambda s, b=builder, i=i, j=j: b(s, i, j))
        build(scene)
        reserve(i-1, j-1, wi+2, wj+2.5)
        measure(build)
        if name == 'lotrscak':
            # The funicular runs down the slope beside the tower from the promenade to Ilica.
            fi = math.floor(ci+3)
            top = max(b for (a, b) in elev if a == fi and b < ilica)
            length = ilica-1.6-(top+.5)
            hr.funicular(scene, fi, top+.5, length, UP)
            reserve(fi, top-2, 1, length+4)
            measure(lambda s: hr.funicular(s, fi, top+.5, length, UP))

    # Squares: the stone square with its tram stop, Kaptol before the cathedral, the Dolac stair foot.
    for (i, j), kind in list(kinds.items()):
        if kind == 'pave' and (i, j) not in elev:
            kinds[(i, j)] = 'square'

    for (i, j) in sorted(kinds, key=lambda t: (t[0]+t[1], t[0])):
        kind, e = kinds[(i, j)], elev.get((i, j), 0)
        def color(x, y, k=kind, i=i, j=j):
            if k == 'square':
                return rgb('#C9C3B6') if (x+2*(y % 2)) % 6 else rgb('#B1AA9C') if y % 3 else rgb('#DAD4C8')
            if k == 'ilica':
                d = j+.5-ilica
                if abs(abs(d)-.55) < .12 or abs(abs(d)-.15) < .1:
                    return rgb('#5B5650')   # tram rails
                return rgb('#8E8A84') if (x+y) % 5 else rgb('#7D7973')
            if k == 'park':
                pc = theatre_sq
                if abs(i+.5-pc[0]) < 7 and (abs(i+.5-pc[0]) < .7 or abs(j+.5-pc[1]) < .7 or abs(i-j-pc[0]+pc[1]) < .8):
                    return rgb('#E2D6B5') if h01(x, y, 7001) > .12 else rgb('#CBBE9B')  # gravel paths
                return ground_color('grass', x, y)
            if e and k in ('lot', 'pave', 'cobble', 'square'):
                # Gradec's older, warmer cobbles set it apart from the Lower Town's flagstones.
                if k == 'cobble':
                    return rgb('#9D9078') if (x+2*(y % 2)) % 4 == 0 else rgb('#BBAE93')
                return rgb('#D3C5A6') if (x+3*(y % 2)) % 6 else rgb('#BCAE90')
            return ground_color('pave' if k == 'lot' else k, x, y)
        iso.ground_tile(scene, i, j, color, e, iso.stone_wall(hr.ROCK['mid']) if e else None)

    # Ilica and the square stay open for the trams; the parks keep their trees and pavilion.
    for (i, j), kind in kinds.items():
        if kind in ('ilica', 'square', 'park'):
            reserved.add((i, j))
    reserved_paths = {(i, j) for (i, j), k in kinds.items() if k == 'park' and any(
        abs(a-pc[0]) < 1.2 or abs(b-pc[1]) < 1.2 or abs(i-j-pc[0]+pc[1]) < 1.3
        for pc in (theatre_sq,) for a, b in ((i+.5, j+.5),))}
    gi, gj = zrinjevac
    hr.gazebo(scene, gi, gj)
    measure(lambda s: hr.gazebo(s, gi, gj))

    for li in range(-12, 112, 3):
        for lj in range(-12, 112, 3):
            wi, wj = 2.5, 3
            cells = [(a, b) for a in range(li, li+3) for b in range(lj, lj+3)]
            if not all(kinds.get(c) == 'lot' and c not in reserved for c in cells):
                continue
            up = {elev.get(c, 0) for c in cells}
            if len(up) != 1:
                continue
            z = up.pop()
            seed = int(h01(li, lj, 7002)*10000)
            floors = 2 if z else 3 if seed % 3 else 4
            x, y = scene.screen(li+wi/2, lj+wj/2)
            y -= z
            half = (wi+wj)*4+7
            if any(x+half > l and x-half < r and y+17 > t and y-floors*10-33 < b for l, t, r, b in protected):
                ax, ay = scene.screen(li, lj)
                x0, y0 = math.floor(ax-50), math.floor(ay-100)
                study = iso.Scene(100, 160, (scene.ox-x0, scene.oy-y0))
                hr.townhouse(study, li, lj, wi, wj, floors, seed, z)
                study.paint_objects()
                l, t, r, b = study.img.convert('RGB').getbbox()
                pixels = study.img.convert('RGB').load()
                if any((sx+x0, sy+y0) in silhouette and pixels[sx, sy] != (0, 0, 0)
                       for sy in range(t, b) for sx in range(l, r)):
                    continue
            hr.townhouse(scene, li, lj, wi, wj, floors, seed, z)
            reserved.update(cells)

    # Blue trams on the Ilica line through the square, clear of the statue and fountain.
    for ti in (square[0]-6.4, square[0]+5):
        hr.tram(scene, ti, ilica-.55)

    planes = [round_tree(k, '#6FA04F', '#28472C', 1.1) for k in range(3)]
    woods = [round_tree(k, '#5C8F45', '#21391F') for k in range(3)]
    for (i, j), kind in kinds.items():
        x, y = scene.screen(i+.5, j+.5)
        y0 = y-elev.get((i, j), 0)
        # A tree may stand beside a landmark, never over any of its painted pixels.
        if any((x+dx, y0+dy) in silhouette for dx in range(-9, 10, 3) for dy in range(-18, 6, 3)):
            continue
        if kind == 'grass' and (i, j) not in reserved and h01(i, j, 7003) < .45:
            y -= elev.get((i, j), 0)
            scene.add(i+j+1.5, lambda s, x=x, y=y, tree=woods[(i+j) % 3]: s.sprite(tree, x, y+4))
        elif kind == 'park' and (i, j) not in reserved_paths and h01(i, j, 7004) < .45:
            scene.add(i+j+1.5, lambda s, x=x, y=y, tree=planes[(i+j) % 3]: s.sprite(tree, x, y+4))
    scene.paint_objects()
    return scene.img.convert('RGB')


def sarajevo():
    import landmarks_bosnia as ba

    scene = new_scene()

    def tile(x, y):
        return tile_of((x-WIDTH/2)/8, (y-scene.oy)/4)

    # Miljacka enters the valley from the east, below Vijećnica, and flows west below
    # Baščaršija. Its central reach follows j; Latin Bridge crosses it squarely along i.
    bridge = next(site for site in ba.SITES if site[0] == 'latin-bridge')
    bi, bj = tile(*bridge[4])
    river_i = bi
    kinds, elev = {}, {}
    for i, j in visible_tiles(scene):
        x, y = scene.screen(i+.5, j+.5)
        d = abs(i+.5-river_i)
        # The northern mahalas and the southern foothills rise outside the valley centre.
        hill = 14 if y < 95 and x > 185 else 10 if x > 570 and y > 440 else 0
        if d < 2.2:
            kind = 'water'
        elif d < 3.5 or river_i+2.2 < i+.5 < river_i+8:
            kind = 'quay'
            elev[(i, j)] = 2
        elif hill:
            kind = 'grass' if (i+j) % 7 else 'cobble'
            elev[(i, j)] = hill
        elif i % 10 == 0 or j % 9 == 0:
            kind = 'cobble'
        else:
            kind = 'lot'
        kinds[(i, j)] = kind

    reserved, protected, silhouette = set(), [], set()

    def reserve(i, j, wi, wj):
        for a in range(math.floor(i), math.ceil(i+wi)):
            for b in range(math.floor(j), math.ceil(j+wj)):
                reserved.add((a, b))
                if kinds.get((a, b)) == 'lot':
                    kinds[(a, b)] = 'square'

    for name, builder, (wi, wj), _, (x, y) in ba.SITES:
        ci, cj = tile(x, y)
        i, j = ci-wi/2, cj-wj/2
        builder(scene, i, j)
        reserve(i-1, j-1, wi+2, wj+2)
        study = iso.Scene(WIDTH+200, HEIGHT+200, (scene.ox+100, scene.oy+100))
        builder(study, i, j)
        study.paint_objects()
        l, t, r, b = (v-100 for v in study.img.convert('RGB').getbbox())
        assert 0 < l < r < WIDTH and 0 < t < b < HEIGHT, (name, l, t, r, b)
        protected.append((l-4, t-4, r+4, b+5))
        pixels = study.img.convert('RGB').load()
        silhouette.update((sx-100, sy-100) for sy in range(t+100, b+100) for sx in range(l+100, r+100)
                          if pixels[sx, sy] != (0, 0, 0))
        # Botanical garden within the museum's four pavilions; do not add trees over its roofs.
        if name == 'museum':
            reserve(i+2, j+3, wi-4, wj-5)

    for (i, j) in sorted(kinds, key=lambda t: (t[0]+t[1], t[0])):
        kind, z = kinds[(i, j)], elev.get((i, j), 0)
        def color(x, y, kind=kind):
            if kind == 'water':
                return ba.WATER[2] if h01(x//3, y, 8101) < .018 else ba.WATER[int(h01(x//5, y//2, 8102) < .3)]
            if kind == 'square':
                return ba.GROUND['square'] if (x+2*(y % 3)) % 8 else ba.GROUND['square_joint']
            if kind == 'cobble':
                return ba.GROUND['cobble'] if (x+2*(y % 2)) % 4 else ba.GROUND['cobble_joint']
            return ground_color('pave' if kind == 'lot' else kind, x, y)
        iso.ground_tile(scene, i, j, color, z, iso.stone_wall(ba.ROCK['mid']) if z else None)

    # Streets, squares and quays remain open. Low shops in the east, taller stucco westwards.
    for li in range(-12, 112, 3):
        for lj in range(-12, 112, 3):
            cells = [(a,b) for a in range(li, li+3) for b in range(lj, lj+3)]
            if not all(kinds.get(c) == 'lot' and c not in reserved for c in cells):
                continue
            x, y = scene.screen(li+1.3, lj+1.5)
            seed = int(h01(li, lj, 8103)*10000)
            floors = 2 if x > 350 else 2+seed % 2
            half = 31
            if any(x+half > l and x-half < r and y+16 > t and y-floors*10-27 < b for l,t,r,b in protected):
                continue
            ba.townhouse(scene, li, lj, floors=floors, seed=seed)
            reserved.update(cells)

    trees = [round_tree(k, '#678C4F', '#29452D') for k in range(3)]
    for (i,j),kind in kinds.items():
        if kind not in ('grass','quay') or (i,j) in reserved or h01(i,j,8104) > (.35 if kind == 'grass' else .09):
            continue
        x,y = scene.screen(i+.5,j+.5,elev.get((i,j),0))
        if any((sx,sy) in silhouette for sx in range(int(x)-9,int(x)+10)
               for sy in range(int(y)-18,int(y)+5)):
            continue
        scene.add(i+j+1.5,lambda s,x=x,y=y,im=trees[(i+j)%3]:s.sprite(im,x,y+3))
    # The shallow urban Miljacka is not navigable: no invented sightseeing boats.
    scene.paint_objects()
    return scene.img.convert('RGB')


def belgrade():
    import landmarks_serbia as rs

    scene = new_scene()

    def tile(x, y):
        return tile_of((x-WIDTH/2)/8, (y-scene.oy)/4)

    # The Sava enters from the SW, bends north around the old city's western ridge, and
    # joins the Danube NW of Kalemegdan. The Danube enters from NW and leaves NE.
    # Each segment follows an isometric axis; both rivers are genuinely navigable here.
    rivers = [[(-220,320),(140,140),(50,95)], [(-140,0),(50,95),(240,0)]]
    segments = [(tile(*a),tile(*b)) for path in rivers for a,b in zip(path,path[1:])]

    def water_distance(i, j):
        result = float('inf')
        for (a,b),(c,d) in segments:
            di,dj = c-a,d-b
            t = max(0,min(1,((i-a)*di+(j-b)*dj)/(di*di+dj*dj)))
            result = min(result, math.hypot(i-a-t*di,j-b-t*dj))
        return result

    kinds, elev = {}, {}
    for i,j in visible_tiles(scene):
        x,y = scene.screen(i+.5,j+.5)
        distance = water_distance(i+.5,j+.5)
        # Fortress promontory above the Lower Town and a separate Vračar plateau.
        fortress = 68 < x < 210 and 100 < y < 205
        vracar = x > 562 and y > 408
        if distance < 2.15:
            kind = 'water'
        elif fortress:
            kind = 'grass'
            elev[(i,j)] = 22
        elif vracar:
            kind = 'square' if x < 700 and y < 505 else 'grass'
            elev[(i,j)] = 12
        elif distance < 3.65:
            kind = 'quay'
        elif x < 220 and y < 240 or 415 < x < 520 and 445 < y < 503:
            kind = 'grass'  # Kalemegdan and Pionirski Park, on the old-city bank.
        elif i % 10 == 0 or j % 9 == 0:
            kind = 'cobble'
        else:
            kind = 'lot'
        kinds[(i,j)] = kind

    reserved, protected, silhouette = set(), [], set()

    def reserve(i,j,wi,wj):
        for a in range(math.floor(i),math.ceil(i+wi)):
            for b in range(math.floor(j),math.ceil(j+wj)):
                reserved.add((a,b))
                if kinds.get((a,b)) == 'lot':kinds[(a,b)] = 'square'

    for name,builder,(wi,wj),_,(x,y),z in rs.SITES:
        ci,cj = tile(x,y)
        i,j = ci-wi/2,cj-wj/2
        builder(scene,i,j,z=z)
        reserve(i-1,j-1,wi+2,wj+2)
        # Raise the entire footprint before drawing: no floating podium or flat Vračar.
        if z:
            for a in range(math.floor(i-1),math.ceil(i+wi+1)):
                for b in range(math.floor(j-1),math.ceil(j+wj+1)):
                    elev[(a,b)] = z
                    kinds[(a,b)] = 'grass' if name == 'victor' else 'square'
        study = iso.Scene(WIDTH+200,HEIGHT+200,(scene.ox+100,scene.oy+100))
        builder(study,i,j,z=z)
        study.paint_objects()
        l,t,r,b = (v-100 for v in study.img.convert('RGB').getbbox())
        assert 0 < l < r < WIDTH and 0 < t < b < HEIGHT,(name,l,t,r,b)
        protected.append((l-5,t-5,r+5,b+7))
        pixels = study.img.convert('RGB').load()
        silhouette.update((sx-100,sy-100) for sy in range(t+100,b+100) for sx in range(l+100,r+100)
                          if pixels[sx,sy] != (0,0,0))

    for (i,j) in sorted(kinds,key=lambda p:(p[0]+p[1],p[0])):
        kind,z = kinds[(i,j)],elev.get((i,j),0)
        def color(x,y,kind=kind):
            if kind == 'water':
                return rs.WATER[2] if h01(x//3,y,8301) < .025 else rs.WATER[int(h01(x//5,y//2,8302) < .28)]
            if kind == 'square':return rs.GROUND['square'] if (x+2*(y%3))%8 else rs.GROUND['joint']
            if kind == 'cobble':return rs.GROUND['cobble'] if (x+2*(y%2))%4 else rs.GROUND['cobble_joint']
            if kind == 'grass':return rs.GROUND['garden_light'] if h01(x,y,8303)<.14 else rs.GROUND['garden']
            return ground_color('pave' if kind == 'lot' else kind,x,y)
        iso.ground_tile(scene,i,j,color,z,iso.stone_wall(rs.ROCK['mid']) if z else None)

    # Academic stucco streets remain subordinate to the monuments. Open squares and
    # measured image bounds protect the complete silhouette, not only each ground footprint.
    for li in range(-12,112,3):
        for lj in range(-12,112,3):
            cells = [(a,b) for a in range(li,li+3) for b in range(lj,lj+3)]
            if not all(kinds.get(c) == 'lot' and c not in reserved and not elev.get(c) for c in cells):continue
            x,y = scene.screen(li+1.25,lj+1.5)
            seed = int(h01(li,lj,8304)*10000)
            floors = 2+seed%2
            if any(x+32>l and x-32<r and y+18>t and y-floors*10-29<b for l,t,r,b in protected):continue
            rs.townhouse(scene,li,lj,floors=floors,seed=seed)
            reserved.update(cells)

    trees = [round_tree(k,'#64864C','#2D452D') for k in range(3)]
    for (i,j),kind in kinds.items():
        if kind not in ('grass','quay') or (i,j) in reserved or h01(i,j,8305) > (.2 if kind == 'grass' else .08):continue
        z = elev.get((i,j),0)
        x,y = scene.screen(i+.5,j+.5,z)
        if any((sx,sy) in silhouette for sx in range(int(x)-10,int(x)+11) for sy in range(int(y)-20,int(y)+6)):continue
        scene.add(i+j+1.5,lambda s,x=x,y=y,im=trees[(i+j)%3]:s.sprite(im,x,y+3))
    for x,y,seed in ((37,176,0),(112,50,1)):
        i,j = tile(x,y)
        scene.add(i+j,lambda s,x=x,y=y,im= rowboat(seed):s.sprite(im,x,y))
    scene.paint_objects()
    return scene.img.convert('RGB')


def podgorica():
    import landmarks_montenegro as rs

    scene = new_scene()

    def tile(x, y):
        return tile_of((x-WIDTH/2)/8, (y-scene.oy)/4)

    # Morača flows south through its rocky channel. Ribnica joins from the east below
    # Stara Varoš; the two actual bridges span their respective rivers squarely.
    moraca = [(350,-40),(470,20),(290,110),(470,200),(230,320),(330,370),(210,430),(30,520)]
    ribnica = [(800,355),(630,440),(510,380),(430,420),(270,340)]
    segments = [(tile(*a),tile(*b),width) for path,width in ((moraca,2.1),(ribnica,1.05))
                for a,b in zip(path,path[1:])]

    def water_distance(i, j):
        result = float('inf')
        for (a,b),(c,d),width in segments:
            di,dj = c-a,d-b
            t = max(0,min(1,((i-a)*di+(j-b)*dj)/(di*di+dj*dj)))
            result = min(result, math.hypot(i-a-t*di,j-b-t*dj)-width)
        return result

    kinds, elev = {}, {}
    for i,j in visible_tiles(scene):
        x,y = scene.screen(i+.5,j+.5)
        distance = water_distance(i+.5,j+.5)
        # Both riverbanks rise above the bed. Gorica rises north of its church, while
        # Kruševac is a park terrace west of Morača, not a building in the water.
        z = 12
        if x > 540 and y < 190:
            z = 20 if y > 135 else 28 if y > 80 else 38
        if distance < 0:
            kind,z = 'water',0
        elif distance < .8:
            kind,z = 'quay',5
        elif distance < 1.7:
            kind = 'grass'
        elif x > 535 and y < 230 or x < 255 and 320 < y < 475:
            kind = 'grass'
        elif i % 10 == 0 or j % 9 == 0:
            kind = 'cobble'
        else:
            kind = 'lot'
        elev[(i,j)] = z
        kinds[(i,j)] = kind

    reserved, protected, silhouette = set(), [], set()

    def reserve(i,j,wi,wj):
        for a in range(math.floor(i),math.ceil(i+wi)):
            for b in range(math.floor(j),math.ceil(j+wj)):
                reserved.add((a,b))
                if kinds.get((a,b)) == 'lot':kinds[(a,b)] = 'square'

    for name,builder,(wi,wj),_,(x,y),z in rs.SITES:
        ci,cj = tile(x,y)
        i,j = ci-wi/2,cj-wj/2
        builder(scene,i,j,z=z)
        reserve(i-1,j-1,wi+2,wj+2)
        # Raise the entire footprint before drawing: each landmark rests on its bank or Gorica terrace.
        if z:
            for a in range(math.floor(i-1),math.ceil(i+wi+1)):
                for b in range(math.floor(j-1),math.ceil(j+wj+1)):
                    elev[(a,b)] = z
                    kinds[(a,b)] = 'grass' if name == 'st-george' else 'square'
        study = iso.Scene(WIDTH+200,HEIGHT+200,(scene.ox+100,scene.oy+100))
        builder(study,i,j,z=z)
        study.paint_objects()
        l,t,r,b = (v-100 for v in study.img.convert('RGB').getbbox())
        assert 0 < l < r < WIDTH and 0 < t < b < HEIGHT,(name,l,t,r,b)
        protected.append((l-5,t-5,r+5,b+7))
        pixels = study.img.convert('RGB').load()
        silhouette.update((sx-100,sy-100) for sy in range(t+100,b+100) for sx in range(l+100,r+100)
                          if pixels[sx,sy] != (0,0,0))

    for (i,j) in sorted(kinds,key=lambda p:(p[0]+p[1],p[0])):
        kind,z = kinds[(i,j)],elev.get((i,j),0)
        def color(x,y,kind=kind):
            if kind == 'water':
                return rs.WATER[2] if h01(x//3,y,8301) < .025 else rs.WATER[int(h01(x//5,y//2,8302) < .28)]
            if kind == 'square':return rs.GROUND['square'] if (x+2*(y%3))%8 else rs.GROUND['joint']
            if kind == 'cobble':return rs.GROUND['cobble'] if (x+2*(y%2))%4 else rs.GROUND['cobble_joint']
            if kind == 'grass':return rs.GROUND['garden_light'] if h01(x,y,8303)<.14 else rs.GROUND['garden']
            return ground_color('pave' if kind == 'lot' else kind,x,y)
        iso.ground_tile(scene,i,j,color,z,iso.stone_wall(rs.ROCK['mid']) if z else None)

    # Low limestone and shuttered stucco houses remain subordinate to the monuments. Open squares and
    # measured image bounds protect the complete silhouette, not only each ground footprint.
    for li in range(-12,112,3):
        for lj in range(-12,112,3):
            cells = [(a,b) for a in range(li,li+3) for b in range(lj,lj+3)]
            if not all(kinds.get(c) == 'lot' and c not in reserved and elev.get(c) == 12 for c in cells):continue
            x,y = scene.screen(li+1.25,lj+1.5,12)
            seed = int(h01(li,lj,8304)*10000)
            floors = 1+seed%2
            if any(x+32>l and x-32<r and y+18>t and y-floors*10-29<b for l,t,r,b in protected):continue
            rs.townhouse(scene,li,lj,floors=floors,seed=seed,z=12)
            reserved.update(cells)

    trees = [round_tree(k,'#64864C','#2D452D') for k in range(3)]
    for (i,j),kind in kinds.items():
        if kind not in ('grass','quay') or (i,j) in reserved or h01(i,j,8305) > (.2 if kind == 'grass' else .08):continue
        z = elev.get((i,j),0)
        x,y = scene.screen(i+.5,j+.5,z)
        if any((sx,sy) in silhouette for sx in range(int(x)-10,int(x)+11) for sy in range(int(y)-20,int(y)+6)):continue
        scene.add(i+j+1.5,lambda s,x=x,y=y,im=trees[(i+j)%3]:s.sprite(im,x,y+3))
    for x,y,seed in ((350,80,0),(160,455,1)):
        i,j = tile(x,y)
        scene.add(i+j,lambda s,x=x,y=y,im= rowboat(seed):s.sprite(im,x,y))
    scene.paint_objects()
    return scene.img.convert('RGB')


def tirane():
    import landmarks_albania as rs

    scene = new_scene()

    def tile(x,y):
        return tile_of((x-WIDTH/2)/8,(y-scene.oy)/4)

    # Lana enters NE and flows W/SW. Isometric-axis bends compress its real course.
    # Historic Tanners' Bridge is NW of the current river, over its DRY former channel.
    lana = [(800,340),(620,430),(580,410),(480,460),(400,420),(300,470),(220,430),(-40,560)]
    segments = [(tile(*a),tile(*b)) for a,b in zip(lana,lana[1:])]

    def water_distance(i,j):
        best = float('inf')
        for (a,b),(c,d) in segments:
            di,dj = c-a,d-b
            t = max(0,min(1,((i-a)*di+(j-b)*dj)/(di*di+dj*dj)))
            best = min(best,math.hypot(i-a-t*di,j-b-t*dj))
        return best

    kinds = {}
    for i,j in visible_tiles(scene):
        x,y = scene.screen(i+.5,j+.5)
        distance = water_distance(i+.5,j+.5)
        if distance < .65:kind = 'water'
        elif distance < 1.35:kind = 'quay'
        elif distance < 2.3:kind = 'grass'
        elif 200 < x < 555 and 125 < y < 320:kind = 'square'
        elif 225 < x < 405 and 370 < y < 430:kind = 'grass'  # Rinia south of cathedral
        elif 605 < x < 700 and 350 < y < 415:kind = 'dry'
        elif i%10 == 0 or j%10 == 0:kind = 'cobble'
        else:kind = 'lot'
        kinds[(i,j)] = kind

    reserved,protected,silhouette = set(),[],set()

    def reserve(i,j,wi,wj):
        for a in range(math.floor(i),math.ceil(i+wi)):
            for b in range(math.floor(j),math.ceil(j+wj)):
                reserved.add((a,b))
                if kinds.get((a,b)) == 'lot':kinds[(a,b)] = 'square'

    for name,builder,(wi,wj),_,(x,y),z in rs.SITES:
        ci,cj = tile(x,y)
        i,j = ci-wi/2,cj-wj/2
        builder(scene,i,j,z=z)
        reserve(i-1,j-1,wi+2,wj+2)
        study = iso.Scene(WIDTH+200,HEIGHT+200,(scene.ox+100,scene.oy+100))
        builder(study,i,j,z=z)
        study.paint_objects()
        l,t,r,b = (v-100 for v in study.img.convert('RGB').getbbox())
        assert 0 < l < r < WIDTH and 0 < t < b < HEIGHT,(name,l,t,r,b)
        protected.append((l-4,t-4,r+4,b+5))
        pixels = study.img.convert('RGB').load()
        silhouette.update((sx-100,sy-100) for sy in range(t+100,b+100) for sx in range(l+100,r+100)
                          if pixels[sx,sy] != (0,0,0))

    # Geography is painted before objects. Pale quays frame the small channel; flat central
    # Tirana gets no invented hill. Stone squares, cobbled lanes and gardens have distinct paving.
    for (i,j) in sorted(kinds,key=lambda p:(p[0]+p[1],p[0])):
        kind = kinds[(i,j)]
        def color(x,y,kind=kind):
            if kind == 'water':return rs.WATER[2] if h01(x//3,y,8401)<.025 else rs.WATER[int(h01(x//5,y//2,8402)<.27)]
            if kind == 'square':
                if (x+2*(y//5))%10==0 or y%5==0:return rs.GROUND['joint']
                return rs.GROUND[['square','rose','grey'][int(h01(x//10,y//5,8403)*3)]]
            if kind == 'cobble':return rs.GROUND['cobble_joint'] if (x+2*(y%2))%4==0 else rs.GROUND['cobble']
            if kind == 'grass':return rs.GROUND['garden_light'] if h01(x,y,8404)<.13 else rs.GROUND['garden']
            if kind == 'dry':return rs.GROUND['dry'] if (x+3*y)%13 else rs.ROCK['mid']
            return ground_color('pave' if kind == 'lot' else kind,x,y)
        iso.ground_tile(scene,i,j,color)

    # Painted Ottoman/Italianate villas at the margins frame open landmark forecourts.
    for li in range(-12,112,3):
        for lj in range(-12,112,3):
            cells = [(a,b) for a in range(li,li+3) for b in range(lj,lj+3)]
            if not all(kinds.get(c) == 'lot' and c not in reserved for c in cells):continue
            x,y = scene.screen(li+1.25,lj+1.5)
            seed = int(h01(li,lj,8405)*10000)
            floors = 1+seed%3
            if any(x+34>l and x-34<r and y+18>t and y-floors*11-25<b for l,t,r,b in protected):continue
            rs.townhouse(scene,li,lj,floors=floors,seed=seed)
            reserved.update(cells)

    trees = [round_tree(k,'#658A49','#2D472D') for k in range(3)]
    for (i,j),kind in kinds.items():
        if kind not in ('grass','quay') or (i,j) in reserved or h01(i,j,8406)>(.17 if kind == 'grass' else .045):continue
        x,y = scene.screen(i+.5,j+.5)
        if any((sx,sy) in silhouette for sx in range(int(x)-11,int(x)+12) for sy in range(int(y)-23,int(y)+6)):continue
        scene.add(i+j+1.5,lambda s,x=x,y=y,im=trees[(i+j)%3]:s.sprite(im,x,y+3))
    scene.paint_objects()
    return scene.img.convert('RGB')


def skopje():
    import landmarks_macedonia as mk

    scene = new_scene()

    def tile(x,y):
        return tile_of((x-WIDTH/2)/8,(y-scene.oy)/4)

    # Vardar enters NW, then follows +i (SE) through Stone Bridge. The bridge runs +j.
    # All four left-bank landmarks remain NE of the water, cathedral/gate SW.
    river = [(-120,110),(110,225),(70,245),(820,620)]
    segments = [(tile(*a),tile(*b)) for a,b in zip(river,river[1:])]

    def water_distance(i,j):
        best = float('inf')
        for (a,b),(c,d) in segments:
            di,dj = c-a,d-b
            t = max(0,min(1,((i-a)*di+(j-b)*dj)/(di*di+dj*dj)))
            best = min(best,math.hypot(i-a-t*di,j-b-t*dj))
        return best

    kinds,elevation = {},{}
    for i,j in visible_tiles(scene):
        x,y = scene.screen(i+.5,j+.5)
        distance = water_distance(i+.5,j+.5)
        # Raised promontory and smaller mosque terrace, both on the left bank.
        kale_hill = ((x-405)/115)**2+((y-222)/65)**2
        mosque_hill = ((x-555)/65)**2+((y-140)/50)**2
        elev = 30 if kale_hill<.65 else 18 if kale_hill<1.15 else 8 if kale_hill<1.55 else 0
        if mosque_hill<1:elev=max(elev,16)
        elevation[i,j] = elev
        if distance<2.25:kind='water'
        elif distance<3.1:kind='quay'
        elif distance<4.4:kind='grass'
        elif elev:kind='grass'
        elif 220<x<435 and 425<y<520:kind='square'  # Macedonia Square/Pella forecourt
        elif 50<x<210 and 285<y<380:kind='square'  # Cathedral yard
        elif i%10==0 or j%10==0:kind='cobble'
        else:kind='lot'
        kinds[i,j] = kind

    reserved,protected,silhouette = set(),[],set()

    def reserve(i,j,wi,wj):
        for a in range(math.floor(i),math.ceil(i+wi)):
            for b in range(math.floor(j),math.ceil(j+wj)):
                reserved.add((a,b))
                if kinds.get((a,b))=='lot':kinds[a,b]='square'

    for name,builder,(wi,wj),_,(x,y),z in mk.SITES:
        ci,cj = tile(x,y)
        i,j = ci-wi/2,cj-wj/2
        builder(scene,i,j,z=z)
        reserve(i-1,j-1,wi+2,wj+2)
        # Use each builder's actual silhouette for house/tree clearance, including the belfry.
        study = iso.Scene(WIDTH+200,HEIGHT+200,(scene.ox+100,scene.oy+100))
        builder(study,i,j,z=z);study.paint_objects()
        l,t,r,b = (v-100 for v in study.img.convert('RGB').getbbox())
        assert 0<l<r<WIDTH and 0<t<b<HEIGHT,(name,l,t,r,b)
        protected.append((l-4,t-4,r+4,b+5))
        pixels=study.img.convert('RGB').load()
        silhouette.update((sx-100,sy-100) for sy in range(t+100,b+100) for sx in range(l+100,r+100)
                          if pixels[sx,sy]!=(0,0,0))
        # Every tile directly under an elevated building belongs to its own level terrace.
        if z:
            for a in range(math.floor(i)-1,math.ceil(i+wi)+1):
                for b in range(math.floor(j)-1,math.ceil(j+wj)+1):
                    elevation[a,b]=max(elevation.get((a,b),0),z)

    for i,j in sorted(kinds,key=lambda p:(sum(p),p[0])):
        kind=kinds[i,j]
        def color(x,y,kind=kind):
            if kind=='water':return mk.WATER[2] if h01(x//3,y,8501)<.03 else mk.WATER[int(h01(x//5,y//2,8502)<.3)]
            if kind=='square':return mk.GROUND['joint'] if (x+2*(y//5))%10==0 or y%5==0 else mk.GROUND['square' if h01(x//10,y//5,8503)>.15 else 'rose']
            if kind=='cobble':return mk.GROUND['cobble_joint'] if (x+2*(y%2))%4==0 else mk.GROUND['cobble']
            if kind=='grass':return mk.GROUND['garden_light'] if h01(x,y,8504)<.13 else mk.GROUND['garden']
            return ground_color('pave' if kind=='lot' else kind,x,y)
        elev=elevation[i,j]
        iso.ground_tile(scene,i,j,color,elev,lambda x,y,lit:mk.ROCK['line'] if y%5==0 else mk.ROCK['lit' if lit else 'dark'])

    for li in range(-12,112,3):
        for lj in range(-12,112,3):
            cells=[(a,b) for a in range(li,li+3) for b in range(lj,lj+3)]
            if not all(kinds.get(c)=='lot' and c not in reserved for c in cells):continue
            x,y=scene.screen(li+1.25,lj+1.5)
            seed=int(h01(li,lj,8505)*10000);floors=1+seed%3
            if any(x+35>l and x-35<r and y+18>t and y-floors*11-26<b for l,t,r,b in protected):continue
            mk.townhouse(scene,li,lj,floors=floors,seed=seed)
            reserved.update(cells)

    trees=[round_tree(k,'#698C4B','#2F482E') for k in range(3)]
    for (i,j),kind in kinds.items():
        if kind not in ('grass','quay') or (i,j) in reserved or h01(i,j,8506)>(.16 if kind=='grass' else .045):continue
        x,y=scene.screen(i+.5,j+.5,elevation[i,j])
        if any((sx,sy) in silhouette for sx in range(int(x)-11,int(x)+12) for sy in range(int(y)-23,int(y)+6)):continue
        scene.add(i+j+1.5,lambda s,x=x,y=y,im=trees[(i+j)%3]:s.sprite(im,x,y+3))
    scene.paint_objects()
    return scene.img.convert('RGB')


CAPITALS = [
    {"id": "lisbon", "name": "Lisbon", "country": "Portugal", "longitude": -9.1365, "latitude": 38.7100,
     "render": lisbon},
    {"id": "madrid", "name": "Madrid", "country": "Spain", "longitude": -3.7038, "latitude": 40.4168,
     "render": madrid},
    {"id": "paris", "name": "Paris", "country": "France", "longitude": 2.3522, "latitude": 48.8566,
     "render": paris},
    {"id": "berlin", "name": "Berlin", "country": "Germany", "longitude": 13.4050, "latitude": 52.5200,
     "render": berlin},
    {"id": "amsterdam", "name": "Amsterdam", "country": "Netherlands", "longitude": 4.8952, "latitude": 52.3702,
     "render": amsterdam},
    {"id": "brussels", "name": "Brussels", "country": "Belgium", "longitude": 4.3517, "latitude": 50.8503,
     "render": brussels},
    {"id": "london", "name": "London", "country": "United Kingdom", "longitude": -0.1276, "latitude": 51.5072,
     "render": london},
    {"id": "dublin", "name": "Dublin", "country": "Ireland", "longitude": -6.2603, "latitude": 53.3498,
     "render": dublin},
    {"id": "rome", "name": "Rome", "country": "Italy", "longitude": 12.4964, "latitude": 41.9028,
     "render": rome},
    {"id": "copenhagen", "name": "Copenhagen", "country": "Denmark", "longitude": 12.5683, "latitude": 55.6761,
     "render": copenhagen},
    {"id": "stockholm", "name": "Stockholm", "country": "Sweden", "longitude": 18.0686, "latitude": 59.3293,
     "render": stockholm},
    {"id": "oslo", "name": "Oslo", "country": "Norway", "longitude": 10.7522, "latitude": 59.9139,
     "render": oslo},
    {"id": "helsinki", "name": "Helsinki", "country": "Finland", "longitude": 24.9384, "latitude": 60.1699,
     "render": helsinki},
    {"id": "reykjavik", "name": "Reykjavík", "country": "Iceland", "longitude": -21.9426, "latitude": 64.1466,
     "render": reykjavik},
    {"id": "bern", "name": "Bern", "country": "Switzerland", "longitude": 7.4474, "latitude": 46.9480,
     "render": bern},
    {"id": "vienna", "name": "Vienna", "country": "Austria", "longitude": 16.3738, "latitude": 48.2082,
     "render": vienna},
    {"id": "valletta", "name": "Valletta", "country": "Malta", "longitude": 14.5146, "latitude": 35.8992,
     "render": valletta},
    {"id": "prague", "name": "Prague", "country": "Czechia", "longitude": 14.4378, "latitude": 50.0755,
     "render": prague},
    {"id": "warsaw", "name": "Warsaw", "country": "Poland", "longitude": 21.0122, "latitude": 52.2297,
     "render": warsaw},
    {"id": "luxembourg", "name": "Luxembourg City", "country": "Luxembourg", "longitude": 6.1319, "latitude": 49.6117,
     "render": luxembourg},
    {"id": "bratislava", "name": "Bratislava", "country": "Slovakia", "longitude": 17.1077, "latitude": 48.1486,
     "render": bratislava},
    {"id": "budapest", "name": "Budapest", "country": "Hungary", "longitude": 19.0402, "latitude": 47.4979,
     "render": budapest},
    {"id": "tallinn", "name": "Tallinn", "country": "Estonia", "longitude": 24.7536, "latitude": 59.4370,
     "render": tallinn},
    {"id": "riga", "name": "Riga", "country": "Latvia", "longitude": 24.1052, "latitude": 56.9496,
     "render": riga},
    {"id": "vilnius", "name": "Vilnius", "country": "Lithuania", "longitude": 25.2797, "latitude": 54.6872,
     "render": vilnius},
    {"id": "ljubljana", "name": "Ljubljana", "country": "Slovenia", "longitude": 14.5061, "latitude": 46.0514,
     "render": ljubljana},
    {"id": "zagreb", "name": "Zagreb", "country": "Croatia", "longitude": 15.9819, "latitude": 45.8150,
     "render": zagreb},
    {"id": "sarajevo", "name": "Sarajevo", "country": "Bosnia and Herzegovina", "longitude": 18.4131, "latitude": 43.8564,
     "render": sarajevo},
    {"id": "belgrade", "name": "Belgrade", "country": "Serbia", "longitude": 20.4600, "latitude": 44.8125,
     "render": belgrade},
    {"id": "podgorica", "name": "Podgorica", "country": "Montenegro", "longitude": 19.2628, "latitude": 42.4414,
     "render": podgorica},
    {"id": "tirane", "name": "Tirane", "country": "Albania", "longitude": 19.8189, "latitude": 41.3275,
     "render": tirane},
    {"id": "skopje", "name": "Skopje", "country": "North Macedonia", "longitude": 21.433462, "latitude": 42.000006,
     "render": skopje},
]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    entries = []
    for capital in CAPITALS:
        image = capital["render"]()
        path = OUT / f"{capital['id']}.png"
        # Expo may be watching during art iteration: publish complete PNGs, never an empty file
        # while Pillow is still encoding it.
        temporary = path.with_suffix(".tmp")
        image.save(temporary, format="PNG", optimize=True)
        temporary.replace(path)
        entries.append({k: v for k, v in capital.items() if k != "render"} | {
            "width": image.width, "height": image.height})
        print(capital["name"], image.size, path.stat().st_size, "bytes")
    DATA.write_text(json.dumps(entries, indent=2) + "\n")
    # Metro only bundles literal require() paths, so the image index is generated code.
    lines = ["// Generated by scripts/art/build_capitals.py. Do not edit.", "export const CAPITAL_IMAGES = {"]
    lines += [f"  {e['id']}: require('@/assets/world/capitals/{e['id']}.png')," for e in entries]
    lines += ["} as const;", ""]
    IMAGES.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
