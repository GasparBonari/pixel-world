"""Remap the style-study tiles' grass and water colours onto the globe shader's palette.

Reads the original Ninja Adventure (CC0) subset in assets/style-study/ninja-adventure/ and
writes recoloured copies to assets/style-study/globe-palette/. Only exact colours listed below
change; roofs, paths, outlines, flowers and characters keep the pack's colours. Run:

    python3 scripts/art/recolor_style_study.py
"""

from hashlib import sha256
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "assets/style-study/ninja-adventure"
OUTPUT = ROOT / "assets/style-study/globe-palette"
SHEETS = ["floor.png", "water.png", "nature.png"]

# Pack colour -> globe colour. Targets come from globe-shader.ts: grass #8AC240 and forest
# #337A40 (land ramp), shallows #40A8C4 and ocean #2973BF (water ramp).
PALETTE = {
    # Grass and foliage, lightest to darkest.
    "#ADBC3A": "#8AC240",  # main grass / light leaves -> globe grass
    "#91AE45": "#7DB443",
    "#A8A129": "#74AC3D",  # grass detail strokes
    "#74A334": "#5E9F40",  # mid leaves / darker grass set
    "#4A8526": "#428C38",
    "#56864C": "#3F7E42",
    "#4A7F4B": "#337A40",  # dark leaves -> globe forest
    "#7A7A3E": "#4F7039",
    "#546626": "#2F5E33",
    # Water, lightest to darkest.
    "#D4F5FA": "#CDEBF2",  # surface sparkle
    "#8FEFF1": "#62C3DA",
    "#71DDEE": "#40A8C4",  # main water -> globe shallows
    "#79B8CE": "#3793C2",  # shaded band near banks
    "#54A0BF": "#2E7FB8",
}


def rgb(hex_color):
    return tuple(int(hex_color[i : i + 2], 16) for i in (1, 3, 5))


def recolor(path):
    table = {rgb(k): rgb(v) for k, v in PALETTE.items()}
    image = Image.open(path).convert("RGBA")
    pixels = image.load()
    changed = 0
    for y in range(image.height):
        for x in range(image.width):
            r, g, b, a = pixels[x, y]
            target = table.get((r, g, b)) if a else None
            if target:
                pixels[x, y] = (*target, a)
                changed += 1
    return image, changed


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    files = {}
    for name in SHEETS:
        image, changed = recolor(SOURCE / name)
        temporary = OUTPUT / f".{name}.tmp"
        image.save(temporary, format="PNG", optimize=True)
        temporary.replace(OUTPUT / name)  # atomic, so a running Metro never reads half a file
        data = (OUTPUT / name).read_bytes()
        files[name] = {
            "source": f"../ninja-adventure/{name}",
            "changedPixels": changed,
            "bytes": len(data),
            "sha256": sha256(data).hexdigest(),
        }
        print(f"{name}: {changed} pixels remapped")
    manifest = {
        "purpose": "Style study: Ninja Adventure tiles remapped to the globe palette",
        "license": "CC0-1.0 (see ../ninja-adventure/LICENSE.txt)",
        "generator": "scripts/art/recolor_style_study.py",
        "palette": PALETTE,
        "files": files,
    }
    (OUTPUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
