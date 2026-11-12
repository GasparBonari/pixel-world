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
    river = lambda i, j: j > 76 + 2 * math.sin(i / 7) and i < 44  # the Manzanares, in the corner
    lake = lambda i, j: math.hypot((i - 78) * 0.8, j - 53) < 4.2
    retiro = lambda i, j: i >= 64 and j >= 47
    squares = [((22, 43), 6.5), ((56, 42), 4.5), ((68, 44), 3.2), ((78, 44), 3.5)]  # Armería, Sol, Cibeles, Alcalá

    kinds = {}
    for i, j in visible_tiles(scene):
        if river(i, j):
            kind = "water"
        elif river(i, j - 1.5):
            kind = "quay"
        elif lake(i, j):
            kind = "water"
        elif retiro(i, j):
            ring = abs(math.hypot((i - 78) * 0.8, j - 53) - 5.5) < 0.9
            kind = "gravel" if ring or (i - 64) % 9 == 0 or (j - 47) % 11 == 0 else "grass"
        elif any(math.hypot(i - c[0], j - c[1]) < r for c, r in squares):
            kind = "pave"
        elif (j in (44, 45) and 28 <= i <= 90) or (abs((i - 60) + (j - 40)) < 1.1 and i >= 56 and j <= 40):
            kind = "cobble"  # Calle Mayor and Calle de Alcalá; the Gran Vía climbing north-east
        else:
            kind = "lot"
        kinds[(i, j)] = kind

    reserved = set()

    def reserve(i, j, wi, wj, ground="court"):
        for a in range(int(i), int(math.ceil(i + wi))):
            for b in range(int(j), int(math.ceil(j + wj))):
                reserved.add((a, b))
                if kinds.get((a, b)) == "lot":
                    kinds[(a, b)] = ground

    lb.palacio_real(scene, 14, 27)
    reserve(13, 26, 18, 11)
    lb.almudena(scene, 16.5, 47)
    reserve(14, 45, 13, 17)  # with the open square before it
    reserve(14, 37, 16, 9)  # Plaza de la Armería
    lb.plaza_mayor(scene, 36, 48)
    reserve(34, 46, 15, 15, ground="pave")  # the streets around the square keep it in view
    lb.casa_correos(scene, 52, 34.5)
    reserve(52, 34, 9, 5)
    lb.metropolis(scene, 63, 35)
    reserve(60, 33, 5, 4)
    lb.cibeles(scene, 68, 44.5)
    lb.puerta_alcala(scene, 74, 43.2)
    reserve(73, 42, 10, 4)
    lb.palacio_cristal(scene, 66, 55)
    reserve(66, 55, 7, 5)
    lb.alfonso_xii(scene, 81, 48.5)
    for i0 in (24,):
        start = 76 + 2 * math.sin(i0 / 7) - 1.5
        lp.stone_bridge(scene, i0, start, 9)

    paint_ground(scene, kinds, {}, TAGUS, lb.GRANITE["dark"])

    for li in range(-12, 110, 3):
        for lj in range(-12, 110, 3):
            for wi, wj in ((3, 3), (3, 2), (2, 3)):
                cells = [(a, b) for a in range(li, li + wi) for b in range(lj, lj + wj)]
                if all(kinds.get(c) == "lot" and c not in reserved for c in cells):
                    reserved.update(cells)
                    seed = int(h01(li, lj, 27) * 1000)
                    wall = MADRID_WALLS[int(h01(seed, 25) * len(MADRID_WALLS))]
                    lb.madrid_house(scene, li, lj, wi, wj, 4 + int(h01(seed, 29) * 2), wall, seed,
                                    mansard_roof=h01(seed, 26) < 0.75, corner_dome=h01(seed, 28) < 0.07)
                    break

    green = [round_tree(n) for n in range(3)]
    dark = [round_tree(n, "#4E9A3E", "#1E3A22") for n in range(2)]
    for (i, j), kind in kinds.items():
        x, y = scene.screen(i + 0.5, j + 0.5)
        pick = None
        if kind == "grass" and h01(i, j, 31) < 0.42 and (i, j) not in reserved:
            pick = (dark if h01(i, j, 32) < 0.45 else green)[int(h01(i, j, 33) * 2)]
        elif kind == "quay" and i % 3 == 0:
            pick = green[i % 3]
        elif kind == "cobble" and (i + j) % 5 == 0 and h01(i, j, 34) < 0.5:
            pick = green[(i + j) % 3]  # plane trees along the avenues
        if pick is not None:
            scene.add(i + j + 1.5, lambda s, img=pick, x=x, y=y: s.sprite(img, x, y + 6))
    boat = rowboat(0)
    for a, b in ((77, 52), (80, 54), (76, 55)):
        x, y = scene.screen(a, b)
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
    ox = WIDTH / 2
    oy = HEIGHT / 2 - CENTER_TILE * 2 * 4
    scene = iso.Scene(WIDTH, HEIGHT, (ox, oy))

    # The Seine runs along the i axis (so bridges cross it squarely along j): the Right Bank lies at
    # smaller j (upper right), the Left Bank at larger j (lower left). Upstream is smaller i.
    def river_j(i):
        return 44 + 2.5 * math.sin((i - 20) / 14)

    def half_width(i):
        return 2.8 + (4.2 if 17 <= i <= 31 else 0)  # wider around the Île de la Cité

    island = lambda i, j: 18.5 <= i <= 30.5 and abs(j - river_j(i)) <= 5.2
    montmartre = (34, 8)
    bridges = [(33, False), (47, False), (61, True), (73, False)]
    streets_i = [14, 22, 51, 62]  # boulevards running along i (at these j)
    streets_j = [20, 33, 52, 66, 84]  # boulevards running along j (at these i)

    kinds, elev = {}, {}
    for i in range(-20, 120):
        for j in range(-20, 120):
            x, y = scene.screen(i, j)
            if not (-16 < x < WIDTH + 16 and -50 < y < HEIGHT + 8):
                continue
            d = abs(j + 0.5 - river_j(i + 0.5))
            hw = half_width(i)
            hill = math.hypot((i - montmartre[0]) * 0.8, (j - montmartre[1]) * 0.8)
            if island(i, j):
                kind = "pave"
            elif d <= hw:
                kind = "water"
            elif d <= hw + 1.2:
                kind = "quay"
            elif d <= hw + 2.4 or (j > river_j(i) and d <= hw + 8.5):
                kind = "promenade"  # Left Bank kept open so its tall blocks never hide the river
            elif hill < 7:
                kind = "grass"
            elif 49 <= i <= 58 and 26 <= j <= 38:
                kind = "gravel"  # the Tuileries
            elif 66 <= i <= 81 and 54 <= j <= 64:
                kind = "grass"  # the Champ de Mars
            elif any(abs(j - s) <= 0.7 for s in streets_i) or any(abs(i - s) <= 0.7 for s in streets_j) \
                    or (58 <= i <= 64 and 30 <= j <= 32):
                kind = "cobble"  # boulevards and the Champs-Élysées
            else:
                kind = "lot"
            kinds[(i, j)] = kind
            elev[(i, j)] = 14 if hill < 7 and kind == "grass" else 0

    reserved = set()

    def reserve(i, j, wi, wj, ground="pave"):
        for a in range(int(i), int(math.ceil(i + wi))):
            for b in range(int(j), int(math.ceil(j + wj))):
                reserved.add((a, b))
                if kinds.get((a, b)) == "lot":
                    kinds[(a, b)] = ground

    # Landmarks.
    lp.notre_dame(scene, 21.5, 37.0)
    reserve(21, 37, 5, 10)
    lp.louvre(scene, 34, 23)
    reserve(33, 22, 16, 15)
    lp.obelisk(scene, 59.5, 34.5)
    reserve(58, 33, 3, 3)
    lp.arc_de_triomphe(scene, 64.0, 28.5)
    reserve(59, 23, 18, 17)  # Place de l'Étoile: the Arc stands in a wide open circle
    lp.sacre_coeur(scene, montmartre[0] - 2, montmartre[1] - 2, 14)
    lp.eiffel_tower(scene, 73.5, 58.5)
    for i0, gilded in bridges:
        rj = river_j(i0)
        start = rj - half_width(i0) - 1.4
        lp.stone_bridge(scene, i0, start, 2 * half_width(i0) + 2.8, gilded=gilded)
        reserve(i0, start, 2, 2 * half_width(i0) + 2.8, ground="cobble")

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
            if k == "gravel":
                return shade(rgb("#E6DAB8"), -0.08) if h01(x, y, 6) < 0.15 else rgb("#E6DAB8")
            if k == "promenade":
                return ground_color("pave", x, y)
            return ground_color("pave" if k == "lot" else k, x, y)
        iso.ground_tile(scene, i, j, color, e, wall if e else None)
    # The Tuileries' round pond.
    cx, cy = scene.screen(53.5, 32.5)
    for dy in range(-6, 7):
        for dx in range(-12, 13):
            r = (dx / 12) ** 2 + (dy / 6) ** 2
            if r <= 1:
                scene.put(cx + dx, cy + dy, lp.STONE["mid"] if r > 0.78 else SEINE_WATER[2] if (dx + dy) % 5 else rgb("#E4F4FA"))

    # Haussmann blocks fill the remaining lots as continuous street walls.
    for li in range(-12, 110, 4):
        for lj in range(-12, 110, 4):
            for wi, wj in ((3, 3), (3, 2), (2, 3), (2, 2)):
                cells = [(a, b) for a in range(li, li + wi) for b in range(lj, lj + wj)]
                if all(kinds.get(c) == "lot" and c not in reserved for c in cells):
                    reserved.update(cells)
                    seed = int(h01(li, lj, 47) * 1000)
                    lp.haussmann(scene, li, lj, wi, wj, seed, floors=4 + int(h01(seed, 3) * 2))
                    break

    # Trees: rows along the quays, boulevards and in the gardens; rowing the Tuileries' allées.
    green = [round_tree(n) for n in range(3)]
    chestnut = [round_tree(n, "#4E9A3E", "#1E3A22") for n in range(2)]
    for (i, j), kind in kinds.items():
        x, y = scene.screen(i + 0.5, j + 0.5, elev[(i, j)])
        pick = None
        if kind == "promenade" and (i % 3 == 0) and (abs(j - river_j(i)) < half_width(i) + 2.6
                                                      or j % 3 == 0) and (i, j) not in reserved:
            pick = green[i % 3]
        elif kind == "gravel" and (i % 3 == 0) and (j % 3 == 0):
            pick = chestnut[(i + j) % 2]
        elif kind == "grass" and elev[(i, j)] and h01(i, j, 61) < 0.25:
            pick = green[(i + j) % 3]
        elif kind == "grass" and not elev[(i, j)] and (i in (66, 67, 80, 81) or j in (54, 64)) and (i + j) % 2 == 0:
            pick = chestnut[(i + j) % 2]  # the Champ de Mars' tree-lined edges
        if pick is not None:
            scene.add(i + j + 1.5, lambda s, img=pick, x=x, y=y: s.sprite(img, x, y + 6))

    boat = bateau(0)
    for i0 in (12, 40, 55, 68, 84):
        rj = river_j(i0)
        if kinds.get((i0, int(rj))) == "water":
            x, y = scene.screen(i0, rj)
            scene.add(i0 + rj, lambda s, x=x, y=y: s.sprite(boat, x, y))

    scene.paint_objects()
    return scene.img.convert("RGB")


# ------------------------------------------------------------------ Berlin --

import landmarks_berlin as be


def berlin():
    scene = new_scene()
    # A north-up illustration, with distances compressed. The Spree runs north-west to south-east
    # along +i; its southern arm encloses Museum Island. Tiergarten stays west of the Gate.
    # Screen-space anchors make the real cardinal relationships explicit (see the coordinate table
    # in DEVELOPMENT_PLAN.md). Buildings themselves always use the 16×8 isometric tile axes.
    def at(x, y):
        return tile_of((x - WIDTH / 2) / 8, (y - scene.oy) / 4)

    def river(i, j):
        return abs(j - 25) < 2 or (37 <= i <= 52 and abs(j - 38) < 1.4) \
            or (abs(i - 37) < 1.3 and 25 <= j <= 38) \
            or (abs(i - 52) < 1.3 and 25 <= j <= 38)

    kinds = {}
    for i, j in visible_tiles(scene):
        x, y = scene.screen(i + .5, j + .5)
        island = 38.3 < i < 50.7 and 27 < j < 36.6
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

    landmark(be.reichstag, 237, 275, 10, 6, 75)
    landmark(be.brandenburg_gate, 267, 345, 8.2, 2, 70, forecourt=6)
    landmark(be.berlin_cathedral, 469, 237, 7.4, 6.2, 85)
    landmark(be.rotes_rathaus, 572, 293, 7, 5, 95)
    landmark(be.konzerthaus, 389, 440, 8.5, 5.2, 70, forecourt=6)
    for builder, x, y, height in ((be.victory_column, 113, 410, 93), (be.tv_tower, 600, 191, 165)):
        i, j = at(x, y)
        builder(scene, i, j)
        reserve(i - 2, j - 2, 5, 7)
        protected.append((x - 23, y - height, x + 23, y + 22))

    # Open cobbled forecourts keep the Gate, Gendarmenmarkt and Alexanderplatz readable.
    for x, y, wi, wj in ((284, 369, 5, 6), (406, 473, 8, 6), (610, 219, 4, 6)):
        i, j = at(x, y)
        reserve(i - wi / 2, j - wj / 2, wi, wj)
    for i, j, length in ((24, 22, 6), (46, 22, 6), (56, 22, 6), (43, 36, 4)):
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
    for i in (14, 31, 42, 62, 70):
        x, y = scene.screen(i, 25)
        scene.add(i + 25, lambda s, x=x, y=y: s.sprite(bateau(0), x, y))

    scene.paint_objects()
    return scene.img.convert("RGB")


# --------------------------------------------------------------- Amsterdam --

import landmarks_amsterdam as am


def amsterdam():
    scene = new_scene()
    def at(x, y):
        return tile_of((x - WIDTH / 2) / 8, (y - scene.oy) / 4)

    # North-up illustration. IJ/Oosterdok at the north; three compressed canal-belt elbows
    # surround Dam. Each waterway segment follows i or j, including the Amstel at Magere Brug.
    def water(i, j):
        return i + j < 34 or (i > 48 and j < 30) \
            or any((i <= corner and abs(j - bank) < 1.1)
                   or (j <= bank and abs(i - corner) < 1.1)
                   for corner, bank in ((58, 56), (70, 68), (82, 80))) \
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
    landmark(am.anne_frank_house, 242, 155, 2.8, 4.3, 48)
    landmark(am.westerkerk, 198, 235, 6.5, 5, 103)
    landmark(am.oude_kerk, 468, 245, 5.8, 7.2, 93)
    landmark(am.royal_palace, 350, 300, 9.5, 5, 77, front=4)
    landmark(am.nemo, 612, 266, 8, 4.2, 45)
    landmark(am.rijksmuseum, 318, 457, 12, 5.8, 73)

    # Dam Square lies east of the palace. Noordermarkt/Jordaan lanes stay open around the Westertoren.
    for x, y, wi, wj in ((407, 320, 6, 6), (200, 273, 5, 4)):
        i, j = at(x, y)
        reserve(i - wi / 2, j - wj / 2, wi, wj)

    # Stone canal bridges along +j and the white double drawbridge across the wider Amstel.
    for i, j, length in ((29, 53, 6), (43, 65, 6), (53, 77, 6)):
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
    for i, j in ((17, 56), (35, 68), (50, 80), (64, 48), (87, 48), (36, 12), (60, 14)):
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
    landmark(irl.four_courts, 150, 235, 12, 5, front=3)
    landmark(irl.hapenny_bridge, 365, 227.5, 2.2, 8.5, front=1)
    landmark(irl.christ_church, 105, 355, 11, 5, front=2)
    landmark(irl.dublin_castle, 310, 395, 13.8, 8, front=2)
    landmark(irl.trinity, 535, 330, 11, 8.8, front=2)
    landmark(irl.st_patricks, 228, 478, 14.2, 6, front=2, ground='gravel')
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
    landmark(it.st_peters, 108, 190, 12, 13)
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
    ni, nj = at(450, 300)
    ni, nj = ni - 11.4 / 2, nj - 6.5 / 2
    def water(i, j):
        return (i > 28 and j < 5) or (52 < i < 58 and j < 35) or (52 < i < 67 and 29 < j < 35) \
            or (61 < i < 67 and j >= 29) \
            or (ni < i < 65 and nj + 2.9 < j < nj + 6.2) \
            or (48 < i < 61 and 61 < j < 63)  # Slotsholmen's southern canal

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
    landmark(dk.marble_church, 470, 165, 7.2, 8)
    landmark(dk.amalienborg, 560, 220, 9.4, 9.4)
    landmark(dk.round_tower, 245, 255, 5.2, 7)
    landmark(dk.nyhavn, 450, 300, 11.4, 6.5)
    landmark(dk.christiansborg, 345, 405, 8.6, 7.1)
    landmark(dk.city_hall, 140, 435, 8, 4.8)
    landmark(dk.our_saviour, 570, 477, 5.6, 7.6)
    # Rådhuspladsen and Kongens Nytorv remain paved/open in front of their buildings.
    for x, y, wi, wj in ((115, 470, 7, 5), (400, 270, 5, 4)):
        i, j = at(x, y)
        reserve(i - wi / 2, j - wj / 2, wi, wj)
    paint_ground(scene, {cell: 'pave' if kind == 'promenade' else kind for cell, kind in kinds.items()},
                 {}, dk.WATER, dk.STONE['dark'])

    # Square crossings on the isometric harbour reaches; low decks keep water visible.
    lp.stone_bridge(scene, 55.5, 58.5, 7, width=1.4, deck=5)
    reserve(54.5, 57.5, 4, 9)
    def harbour_bridge(s):
        dk.block(s, 59.5, 49, 9, 1.4, 5, dk.STONE,
                 lambda u, v, lit: dk.WATER[1] if lit and 2 < int(u) % 18 < 14 and v < 3 else None)
        for jj in (49, 50.4):
            dk.block(s, 59.5, jj, 9, .12, 2, dk.STONE, z=5)
    scene.add(59.5 + 49 + 9 + 1.4, harbour_bridge)
    reserve(59, 48, 11, 4)

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

    # Compressed north-up island groups. Every bank follows i/j axes: Mälaren west,
    # Norrström north of Gamla Stan, Riddarholmen west and Djurgården to the east.
    def water(i, j):
        mainland = i < 36 or (i < 40 and 19 < j < 30)
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
    landmark(se.nordiska, 640, 150, 5.2, 8.5)
    landmark(se.nationalmuseum, 450, 175, 7.8, 5)
    landmark(se.vasa_museum, 555, 225, 7.5, 6)
    landmark(se.city_hall, 105, 225, 8.4, 5.4)
    landmark(se.royal_palace, 385, 300, 9, 7)
    landmark(se.storkyrkan, 285, 390, 4.3, 6.3)
    landmark(se.riddarholmen, 190, 420, 4.8, 6.5)
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
    landmark(no.cathedral,565,280,5,6.8)
    landmark(no.city_hall,195,340,8.4,5.3)
    landmark(no.akershus,340,465,9.2,6.4)
    landmark(no.opera_house,535,410,9.5,6.3)
    landmark(no.munch,660,480,3.2,2.9)
    # Open Rådhusplassen, Løvebakken and Stortorvet; never put tall houses before them.
    for x,y,wi,wj in ((195,380,8,3),(430,280,6,3),(520,302,5,3)):
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
