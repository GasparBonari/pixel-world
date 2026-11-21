"""Find where each capital scene can move on its own (ART_CONTRACT.md section 9).

Reads the finished scenes in assets/world/capitals/ (it never redraws them) and writes
src/data/capital-motion.json: for each capital, the scene-pixel spots where water glints appear.

Water is found by its colours. Each scene paints its river, lake or harbour in two or three exact
colours of its own (the Tagus blue, the Thames grey-teal, the Tiber green). The largest region of
blue-to-teal pixels is the main water; its dominant colours are the scene's water palette, and
every sizeable patch in exactly those colours is water. Slate roofs and glass use other exact
colours, so they are left alone.

Run: .venv/bin/python scripts/art/capital_motion.py [--preview DIR]
"""

import colorsys
import json
import sys
from collections import Counter
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
SCENES = ROOT / "assets" / "world" / "capitals"
CAPITALS = ROOT / "src" / "data" / "capitals.json"
OUT = ROOT / "src" / "data" / "capital-motion.json"

HUE = (150, 230)  # blue to green-teal water, in degrees
MAIN_WATER = 1500  # the largest candidate region must be at least this many pixels
PALETTE_SHARE = 0.9  # ...and made almost entirely of its top three colours
MIN_PATCH = 120  # smaller patches in the water colours (a window, a fountain rim) are ignored
GLINT_SPACING = 18  # scene pixels between candidate glint spots
GLINT_CLEARANCE = (3, 2)  # a glint needs mostly water this far either side and above/below
MAX_GLINTS = 90
# Scenes whose largest blue-green region is not their water (Madrid's slate roofs, a building in
# Tirane) or mixes it with slate (Andorra, Vaduz): a scene-pixel point on the real water instead.
WATER_AT = {
    "madrid": (210, 502),  # the Manzanares
    "andorra": (289, 472),  # the Valira
    "vaduz": (119, 421),  # the Alpine Rhine
    "tirane": (594, 411),  # the Lana
}


def candidate(color):
    h, s, v = colorsys.rgb_to_hsv(*(c / 255 for c in color[:3]))
    return HUE[0] <= h * 360 <= HUE[1] and s > 0.25 and v > 0.3


def regions(width, height, inside):
    """Four-connected regions of pixels for which inside(x, y) is true."""
    seen = set()
    for y in range(height):
        for x in range(width):
            if (x, y) in seen or not inside(x, y):
                continue
            stack, region = [(x, y)], []
            seen.add((x, y))
            while stack:
                cx, cy = stack.pop()
                region.append((cx, cy))
                for n in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                    if 0 <= n[0] < width and 0 <= n[1] < height and n not in seen and inside(*n):
                        seen.add(n)
                        stack.append(n)
            yield region


def water_of(image, at=None):
    """The scene's water pixels, or an empty set if it has no water. `at` names a point on the
    water when the largest candidate region is something else."""
    px = image.load()
    w, h = image.size
    found = regions(w, h, lambda x, y: candidate(px[x, y]))
    if at:
        largest = next(region for region in found if tuple(at) in region)
    else:
        largest = max(found, key=len, default=[])
        if len(largest) < MAIN_WATER:
            return set()
    colours = Counter(px[p] for p in largest).most_common(3)
    if not at and sum(n for _, n in colours) / len(largest) < PALETTE_SHARE:
        return set()
    palette = {c for c, n in colours if n / len(largest) > 0.05}
    water = set()
    for region in regions(w, h, lambda x, y: px[x, y] in palette):
        if len(region) >= MIN_PATCH:
            water.update(region)
    return water


def glints_of(water, width, height):
    """Evenly spread spots well inside the water, each with room for a short horizontal glint."""
    cx, cy = GLINT_CLEARANCE
    spots = []
    for y in range(GLINT_SPACING // 2, height, GLINT_SPACING):
        # Stagger alternate rows, so the spots don't line up in columns.
        for x in range((y // GLINT_SPACING) % 2 * GLINT_SPACING // 2 + 4, width, GLINT_SPACING):
            # Mostly water around it: rivers are flecked with lighter pixels that aren't in the palette.
            around = [(x + dx, y + dy) in water for dx in range(-cx, cx + 1) for dy in range(-cy, cy + 1)]
            if (x, y) in water and sum(around) >= 0.85 * len(around):
                spots.append([x, y])
    if len(spots) > MAX_GLINTS:  # thin out evenly
        step = len(spots) / MAX_GLINTS
        spots = [spots[int(i * step)] for i in range(MAX_GLINTS)]
    return spots


def main():
    preview = Path(sys.argv[sys.argv.index("--preview") + 1]) if "--preview" in sys.argv else None
    if preview:
        preview.mkdir(parents=True, exist_ok=True)
    motion = {}
    for scene in json.loads(CAPITALS.read_text()):
        image = Image.open(SCENES / f"{scene['id']}.png").convert("RGB")
        water = water_of(image, WATER_AT.get(scene["id"]))
        motion[scene["id"]] = {"glints": glints_of(water, *image.size)}
        print(f"{scene['id']:12s} water {len(water):6d} px, {len(motion[scene['id']]['glints'])} glint spots")
        if preview:
            marked = image.copy()
            for p in water:
                marked.putpixel(p, (255, 0, 255))
            draw = ImageDraw.Draw(marked)
            for x, y in motion[scene["id"]]["glints"]:
                draw.rectangle((x - 1, y, x + 1, y), fill=(255, 255, 0))
            marked.save(preview / f"{scene['id']}.png")
    OUT.write_text(json.dumps(motion, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    main()
