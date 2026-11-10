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


# ---------------------------------------------------------------- landmarks --

STONE_OUTLINE = rgb("#4A3E30")


def stone_box(scene, i, j, wi, wj, height, elevation, color, crenels=True, cover=None):
    own = cover if cover is not None else set()
    box = Box(scene, i, j, wi, wj, height, elevation)
    box.walls(color, own, windows=False)
    box.flat_top(shade(color, 0.12), own, crenels=crenels)
    if cover is None:
        iso.outline(scene, own, STONE_OUTLINE)
    return box


def castle(scene, i, j, elev):
    """São Jorge: crenellated curtain walls, four corner towers, a keep flying Portugal's flag."""
    stone = C["stone"]
    size = 9
    parts = []
    # Back walls and towers first, front ones last (depth order inside the landmark).
    parts.append((i + j, lambda s: stone_box(s, i, j, size, 1, 14, elev, stone)))
    parts.append((i + j, lambda s: stone_box(s, i, j, 1, size, 14, elev, stone)))
    parts.append((i + j + 1, lambda s: stone_box(s, i - 1, j - 1, 3, 3, 26, elev, stone)))
    parts.append((i + j + size, lambda s: stone_box(s, i + size - 2, j - 1, 3, 3, 26, elev, stone)))
    parts.append((i + j + size, lambda s: stone_box(s, i - 1, j + size - 2, 3, 3, 26, elev, stone)))
    parts.append((i + j + size + 2, lambda s: keep(s, i + 3, j + 3, elev)))
    parts.append((i + j + 2 * size - 1, lambda s: stone_box(s, i + size - 1, j, 1, size, 12, elev, stone)))
    parts.append((i + j + 2 * size - 1, lambda s: stone_box(s, i, j + size - 1, size, 1, 12, elev, stone)))
    parts.append((i + j + 2 * size, lambda s: stone_box(s, i + size - 2, j + size - 2, 3, 3, 24, elev, stone)))
    for depth, draw in parts:
        scene.add(depth, draw)


def keep(scene, i, j, elev):
    box = stone_box(scene, i, j, 3, 3, 34, elev, shade(C["stone"], 0.05))
    x, y = box.up(box.T)
    for dy in range(4, 14):
        scene.put(x, y - dy, rgb("#3A3530"))
    for dy in range(9, 14):  # Portuguese flag: green at the hoist, red in the fly
        scene.put(x + 1, y - dy, rgb("#2E7D32"))
        for dx in range(2, 6):
            scene.put(x + dx, y - dy, rgb("#D32F2F"))


def cathedral(scene, i, j):
    """Sé de Lisboa: a stone nave under a tiled roof, two crenellated towers and a rose window."""
    def nave(s):
        cover = set()
        box = Box(s, i, j, 3, 5, 24)
        box.walls(C["limestone"], cover, windows=False)
        box.gable_roof(C["roof"], C["limestone"], cover)
        iso.outline(s, cover, STONE_OUTLINE)

    def towers(s):
        for ti in (i - 0.75, i + 2.25):
            stone_box(s, ti, j + 4, 1.6, 2.2, 50, 0, C["limestone"])
        # Rose window and portal on the façade between the towers.
        x, y = s.screen(i + 1.5, j + 6)
        for dx in range(-3, 4):
            for dy in range(-3, 4):
                if dx * dx + dy * dy <= 10:
                    s.put(x + dx, y - 30 + dy, rgb("#3F4A6B") if (dx + dy) % 2 else rgb("#C9A0E0"))
        for dy in range(0, 9):
            for dx in range(-2, 3):
                if dy < 7 or abs(dx) < 2:
                    s.put(x + dx, y - dy - 1, rgb("#4A3426"))

    scene.add(i + j + 5, nave)
    scene.add(i + j + 7, towers)


def belem_tower(scene, i, j):
    """Torre de Belém: a limestone bastion in the water, corner turrets, and a tall tower."""
    def draw(s):
        cover = set()
        base = Box(s, i, j, 5, 4, 12)
        base.walls(C["limestone"], cover, windows=False)
        base.flat_top(shade(C["limestone"], 0.1), cover, crenels=True)
        iso.outline(s, cover, STONE_OUTLINE)
        tower = stone_box(s, i + 0.5, j + 0.5, 2.5, 2.5, 42, 0, C["limestone"])
        # Arched windows with balconies on the tower's lit face.
        x, y = s.screen(i + 0.5, j + 3)
        for level in (16, 26, 34):
            for dx in (4, 8):
                for dy in range(0, 4):
                    s.put(x + dx, y - level - dy + dx // 2, rgb("#3F4A5E"))
        for ci, cj in ((i, j + 4), (i + 5, j + 4), (i + 5, j)):  # domed corner turrets
            tx, ty = s.screen(ci, cj, 12)
            for dy in range(0, 7):
                for dx in range(-2, 3):
                    s.put(tx + dx, ty - dy, C["limestone"] if dx < 1 else shade(C["limestone"], -0.2))
            for dx in range(-2, 3):
                s.put(tx + dx, ty - 7 - (2 - abs(dx)), shade(C["limestone"], -0.1))
    scene.add(i + j + 9, draw)


def arch(scene, i, j):
    """Arco da Rua Augusta: a tall triumphal arch with a deep vault, columns and a statue group."""
    def draw(s):
        cover = set()
        box = Box(s, i, j, 6, 1.5, 40)
        box.walls(C["limestone"], cover, windows=False)
        box.flat_top(shade(C["limestone"], 0.1), cover)
        iso.outline(s, cover, STONE_OUTLINE)
        lx, ly = box.L
        bx, by = box.B
        for u in range(int(bx - lx)):
            x, foot = lx + u, ly + u * 0.5
            centre = (bx - lx) / 2
            span = abs(u - centre)
            if span <= 8:  # the vault: dark, round-headed
                top = 22 + int(math.sqrt(max(0, 64 - span * span)))
                for v in range(1, top):
                    s.put(x, foot - v, rgb("#3A3026") if v < top - 1 else shade(C["limestone"], -0.3))
            elif span in (11, 15, 19):  # columns
                for v in range(1, 28):
                    s.put(x, foot - v, shade(C["limestone"], 0.2))
        stone_box(s, i + 2, j, 2, 1.5, 9, 40, shade(C["limestone"], -0.05), crenels=False)
        tx, ty = s.screen(i + 3, j + 0.75, 49)
        for v in range(0, 7):  # the statue group's central figure
            for dx in (-1, 0, 1):
                if v < 5 or dx == 0:
                    s.put(tx + dx, ty - v, rgb("#8C8478") if dx else rgb("#A69E90"))
    scene.add(i + j + 7, draw)


def tram(scene, i, j, along_i=True):
    """Lisbon's yellow tram: yellow body, white roof, a band of windows, trolley pole."""
    def draw(s):
        cover = set()
        wi, wj = (3, 1.2) if along_i else (1.2, 3)
        box = Box(s, i, j, wi, wj, 12)
        box.walls(C["yellow"], cover, windows=False)
        box.flat_top(rgb("#F4F0E6"), cover)
        for face_start, face_end in ((box.L, box.B), (box.B, box.R)):
            steps = int(abs(face_end[0] - face_start[0]))
            for k in range(1, steps - 1):
                if k % 3 == 0:
                    continue
                x = face_start[0] + (face_end[0] - face_start[0]) * k / steps
                y = face_start[1] + (face_end[1] - face_start[1]) * k / steps
                for dy in (6, 7, 8):
                    s.put(x, y - dy, rgb("#34405A") if dy != 8 else rgb("#8FB4D8"))
                s.put(x, y - 1, rgb("#8A3A26"))
        top = box.up(box.T)
        iso.line(s, (top[0] + 6, top[1] + 3), (top[0] + 12, top[1] - 6), rgb("#2E2A28"))
        iso.outline(s, cover, rgb("#3A2A22"))
    scene.add(i + j + 3, draw)


# -------------------------------------------------------------------- scene --

def lisbon():
    ox = WIDTH / 2
    oy = HEIGHT / 2 - CENTER_TILE * 2 * 4
    scene = iso.Scene(WIDTH, HEIGHT, (ox, oy))

    def river(sx, sy):
        return sy > 121 - 0.42 * sx + 2 * math.sin(sx / 6)

    street = [(-50, 124), (-34, 110), (-18, 96), (-4, 86), (6, 76), (12, 66), (18, 56), (22, 48)]

    def near_street(sx, sy):
        best = 99
        for (ax, ay), (bx, by) in zip(street, street[1:]):
            dx, dy = bx - ax, by - ay
            t = max(0, min(1, ((sx - ax) * dx + (sy - ay) * dy) / (dx * dx + dy * dy)))
            best = min(best, math.hypot(sx - ax - t * dx, (sy - ay - t * dy) * 0.5))
        return best

    hill = (26, 36)  # castle hill centre (sx, sy)
    plaza_i, plaza_j = tile_of(-10, 104)
    plaza_i, plaza_j = int(plaza_i), int(plaza_j)

    kinds, elev = {}, {}
    for i in range(-20, 110):
        for j in range(-20, 110):
            sx, sy = to_s(i, j)
            x, y = scene.screen(i, j)
            if not (-16 < x < WIDTH + 16 and -40 < y < HEIGHT + 8):
                continue
            hill_r = math.hypot((sx - hill[0]) * 0.55, sy - hill[1])
            if river(sx, sy):
                kind = "shallow" if not river(sx, sy - 3) else "water"
            elif river(sx, sy + 3):
                kind = "quay"
            elif plaza_i - 4 <= i <= plaza_i + 4 and plaza_j - 4 <= j <= plaza_j + 4:
                kind = "calcada"
            elif i >= plaza_i - 4 and j >= plaza_j - 4 and abs((i - plaza_i) - (j - plaza_j)) <= 4:
                kind = "calcada"  # the square opens onto the Tagus
            elif near_street(sx, sy) < 2.6:
                kind = "cobble"
            elif hill_r < 13:
                kind = "grass"
            else:
                kind = "pave"
            kinds[(i, j)] = kind
            elev[(i, j)] = 12 if hill_r < 13 and kind == "grass" else 0

    # Lots: houses on a jittered grid; about one lot in eight becomes a small garden.
    lots, gardens = [], []
    for li in range(-10, 100, 4):
        for lj in range(-10, 100, 4):
            i = li + int(h01(li, lj, 1) * 2)
            j = lj + int(h01(li, lj, 2) * 2)
            wi = 2 + int(h01(li, lj, 3) * 2)
            wj = 2 + int(h01(li, lj, 4) * 2)
            cells = [(a, b) for a in range(i, i + wi) for b in range(j, j + wj)]
            if any(kinds.get(c) != "pave" for c in cells):
                continue
            x, y = scene.screen(i, j)
            if not (-60 < x < WIDTH + 60 and -10 < y < HEIGHT + 60):
                continue
            (gardens if h01(i, j, 8) < 0.12 else lots).append((i, j, wi, wj))
    for i, j, wi, wj in gardens:
        for a in range(i, i + wi):
            for b in range(j, j + wj):
                kinds[(a, b)] = "grass"

    # Ground pass, back to front.
    wall = iso.stone_wall(C["stone"])
    for (i, j) in sorted(kinds, key=lambda t: (t[0] + t[1], t[0])):
        kind = kinds[(i, j)]
        e = elev[(i, j)]
        iso.ground_tile(scene, i, j, lambda x, y, k=kind: ground_color(k, x, y), e, wall if e else None)

    # Tram rails along the street.
    pts = [scene.screen(*tile_of(sx, sy)) for sx, sy in street]
    pts = [(x, y + 4) for x, y in pts]
    for offset in (-2, 2):
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            length = math.hypot(bx - ax, by - ay)
            nx, ny = -(by - ay) / length * offset, (bx - ax) / length * offset
            iso.line(scene, (ax + nx, ay + ny), (bx + nx, by + ny), C["rail"])

    reserved = set()

    def reserve(i, j, wi, wj, pad=0):
        cells = {(a, b) for a in range(int(i) - pad, int(i + wi) + pad) for b in range(int(j) - pad, int(j + wj) + pad)}
        if cells & reserved:
            return False
        reserved.update(cells)
        return True

    # Landmarks.
    ci, cj = tile_of(hill[0], hill[1])
    castle(scene, int(ci) - 4, int(cj) - 4, 12)
    reserve(int(ci) - 6, int(cj) - 6, 13, 13)
    si, sj = tile_of(4, 66)
    cathedral(scene, int(si) + 2, int(sj) - 3)
    reserve(int(si) + 1, int(sj) - 4, 5, 9)
    bi, bj = tile_of(34, 116)
    belem_tower(scene, int(bi), int(bj))
    reserve(int(bi), int(bj), 5, 4)
    arch(scene, plaza_i - 2, plaza_j - 6)
    reserve(plaza_i - 5, plaza_j - 7, 11, 13)
    for n in range(3):  # the yellow arcades around Praça do Comércio
        house_i, house_j = plaza_i - 7, plaza_j - 4 + n * 3
        scene.add(house_i + house_j + 4, lambda s, a=house_i, b=house_j, n=n:
                  iso.house(s, a, b, 2, 3, 2, C["yellow"], C["roof"], n))
        house_i2, house_j2 = plaza_i - 4 + n * 3, plaza_j - 9
        scene.add(house_i2 + house_j2 + 4, lambda s, a=house_i2, b=house_j2, n=n:
                  iso.house(s, a, b, 3, 2, 2, C["yellow"], C["roof"], n + 5))
    for i, j in ((int(t[0]), int(t[1])) for t in (tile_of(-30, 108), tile_of(10, 74))):
        tram(scene, i, j, along_i=False)

    # Houses, leaving streets, the plaza and landmarks clear.
    for i, j, wi, wj in lots:
        if not reserve(i, j, wi, wj, 0):
            continue
        sx, sy = to_s(i + wi, j + wj)
        seed = int(h01(i, j, 7) * 1000)
        alfama = sx > 4 and sy < 96
        floors = 2 + int(h01(seed, 9) * (2 if alfama else 3))
        wall = FACADES[int(h01(seed, 5) * len(FACADES))]
        roof = ROOFS[int(h01(seed, 6) * len(ROOFS))]
        scene.add(i + wi + j + wj, lambda s, i=i, j=j, wi=wi, wj=wj, f=floors, w=wall, r=roof, sd=seed:
                  iso.house(s, i, j, wi, wj, f, w, r, sd))

    # Trees: green and jacaranda in the gaps, umbrella pines on the castle hill, a row on the quay.
    jacaranda = [round_tree(n, "#A98BD8", "#3E2A5E") for n in range(3)]
    blossom = [round_tree(n, "#F2A6C8", "#6E2A4A") for n in range(2)]
    green = [round_tree(n) for n in range(3)]
    pines = [umbrella_pine(n) for n in range(2)]
    for (i, j), kind in kinds.items():
        if kind != "grass" or (i, j) in reserved:
            continue
        x, y = scene.screen(i + 0.5, j + 0.5, elev[(i, j)])
        r = h01(i, j, 11)
        if elev[(i, j)] and r < 0.18:
            img = pines[int(r * 100) % 2]
        elif not elev[(i, j)] and r < 0.45:
            pick = h01(i, j, 12)
            img = jacaranda[int(pick * 3)] if pick < 0.35 else blossom[int(pick * 2) % 2] if pick < 0.5 else green[int(pick * 3) % 3]
        else:
            continue
        scene.add(i + j + 1.5, lambda s, img=img, x=x, y=y: s.sprite(img, x, y + 6))
    for (i, j), kind in kinds.items():
        if kind == "quay" and (i - j) % 5 == 0:
            x, y = scene.screen(i + 0.5, j + 0.5)
            scene.add(i + j + 1.5, lambda s, x=x, y=y, n=i: s.sprite(green[n % 3], x, y + 6))

    boat = sprites.sailboat(0)
    for sx, sy in ((-22, 140), (12, 128), (-44, 150), (38, 108)):
        i, j = tile_of(sx, sy)
        if kinds.get((int(i), int(j))) == "water":
            x, y = scene.screen(i, j)
            scene.add(i + j, lambda s, x=x, y=y: s.sprite(boat, x, y))

    scene.paint_objects()
    return scene.img.convert("RGB")


CAPITALS = [
    {"id": "lisbon", "name": "Lisbon", "country": "Portugal", "longitude": -9.1365, "latitude": 38.7100,
     "render": lisbon},
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


if __name__ == "__main__":
    main()
