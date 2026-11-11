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


CAPITALS = [
    {"id": "lisbon", "name": "Lisbon", "country": "Portugal", "longitude": -9.1365, "latitude": 38.7100,
     "render": lisbon},
    {"id": "madrid", "name": "Madrid", "country": "Spain", "longitude": -3.7038, "latitude": 40.4168,
     "render": madrid},
    {"id": "paris", "name": "Paris", "country": "France", "longitude": 2.3522, "latitude": 48.8566,
     "render": paris},
]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    entries = []
    for capital in CAPITALS:
        image = capital["render"]()
        path = OUT / f"{capital['id']}.png"
        image.save(path, optimize=True)
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
