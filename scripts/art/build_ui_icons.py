"""Pixel UI icons for the game interface (docs/ui/UI_KIT.md).

Each icon is a 12x12 grid of palette letters. One icon pixel is one UI pixel (2 points), so an
icon is drawn at 24x24 points. The script writes each icon three times, pre-scaled with nearest
neighbour to every screen density (name.png = 2 px per icon pixel, @2x = 4, @3x = 6), so phones
never smooth the pixels. It also writes src/ui/icons.generated.ts, the require() map.

Add or edit an icon: change ICONS below, then run
    .venv/bin/python scripts/art/build_ui_icons.py
Rules: outline every shape with "o"; light from the upper left (lighter tones top/left, darker
bottom/right); use only the letters in COLORS; keep every row exactly 12 characters.
"""

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "assets" / "ui" / "icons"
TS_OUT = ROOT / "src" / "ui" / "icons.generated.ts"
SIZE = 12
DENSITIES = {"": 2, "@2x": 4, "@3x": 6}  # file suffix -> device pixels per icon pixel

# Same hues as the map art (scripts/art/sprites.py) and the UI tokens (src/constants/theme.ts).
COLORS = {
    "o": "#24161A",  # outline (near-black ink, reads on parchment and navy)
    "w": "#FFFFFF", "v": "#CFD6E4",  # white, white shade
    "p": "#FFF3D6", "P": "#C9A36B",  # parchment light, parchment shadow
    "y": "#FFE58A", "g": "#F6C443", "G": "#C98A1E",  # gold hi, gold, gold shade
    "h": "#FF8E8E", "r": "#E8404A", "R": "#A82634",  # red hi, red, red shade
    "c": "#9FD0F5", "b": "#3F86D0", "B": "#24528F",  # sky, blue, deep blue
    "l": "#9BD04A", "e": "#62AC3C", "E": "#3E7F34",  # green hi, green, green shade
    "n": "#A7764A", "N": "#714E33",  # brown, brown shade
    "s": "#9AA3B5", "S": "#5E6678",  # steel, steel shade
    "q": "#B48AE8", "u": "#8E5CC8", "U": "#5E3A94",  # purple hi, purple, purple shade
}

ICONS = {
    "back": [
        "............",
        ".....oo.....",
        "....owo.....",
        "...owwoooooo",
        "..owwwwwwwwo",
        ".owwwwwwwwwo",
        ".ovvvvvvvvvo",
        "..ovvvvvvvvo",
        "...ovvoooooo",
        "....ovo.....",
        ".....oo.....",
        "............",
    ],
    "close": [
        "............",
        ".oo......oo.",
        "owwo....owwo",
        "owwwo..owwwo",
        ".owwwoowwwo.",
        "..owwwwwwo..",
        "..ovvvvvvo..",
        ".ovvvoovvvo.",
        "ovvvo..ovvvo",
        "ovvo....ovvo",
        ".oo......oo.",
        "............",
    ],
    "check": [
        "............",
        ".........oo.",
        "........olEo",
        ".......oleEo",
        ".oo...oleEo.",
        "olEo.oleEo..",
        "oleEooleEo..",
        ".oleEleEo...",
        "..oleeEo....",
        "...oleo.....",
        "....oo......",
        "............",
    ],
    "lock": [
        "...oooooo...",
        "..osssssso..",
        "..oso..oSo..",
        "..oso..oSo..",
        ".oooooooooo.",
        ".oyyyyyyyyo.",
        ".oggggggggo.",
        ".ogggooggGo.",
        ".ogggooggGo.",
        ".oggggggGGo.",
        ".oGGGGGGGGo.",
        ".oooooooooo.",
    ],
    "pin": [
        "...oooooo...",
        "..ohhrrrro..",
        ".ohrroorrRo.",
        ".orrowwoRRo.",
        ".orrowwoRRo.",
        ".orrroorRRo.",
        "..orrrrRRo..",
        "..orrrRRRo..",
        "...oRRRRo...",
        "....oRRo....",
        ".....oo.....",
        "............",
    ],
    "star": [
        ".....oo.....",
        "....oygo....",
        "....oygo....",
        "oooooyggoooo",
        "oyyyyygggGGo",
        ".oyyygggGGo.",
        "..oyggggGo..",
        "..oygggGGo..",
        ".oyggooGGGo.",
        ".ogGo..oGGo.",
        ".ooo....ooo.",
        "............",
    ],
    "globe": [
        "....oooo....",
        "..oobbccoo..",
        ".obbleebcbo.",
        ".obleeeebbo.",
        "obbbeeebbbBo",
        "obbbbeebbbBo",
        "obbbbbbeeBBo",
        "obeebbbeeBBo",
        ".obeebbbBBo.",
        ".oBbebbBBBo.",
        "..ooBBBBoo..",
        "....oooo....",
    ],
    "scroll": [
        ".oooooooooo.",
        "onnnnnnnnnNo",
        ".oooooooooo.",
        "..opppppPo..",
        "..opNNNNPo..",
        "..opppppPo..",
        "..opNNNpPo..",
        "..opppppPo..",
        "..opNNNNPo..",
        ".oooooooooo.",
        "onnnnnnnnnNo",
        ".oooooooooo.",
    ],
    "passport": [
        "ooooooooooo.",
        "oBbbbbbbbbo.",
        "oBbbbggbbbo.",
        "oBbbgbbgbbo.",
        "oBbgbggbgbo.",
        "oBbgbggbgbo.",
        "oBbbgbbgbbo.",
        "oBbbbggbbbo.",
        "oBbbbbbbbbo.",
        "oBbbgggggbo.",
        "oBbbbbbbbbo.",
        "ooooooooooo.",
    ],
    "book": [
        ".oooooooooo.",
        ".ouuuuuuuUo.",
        ".ouqquuuuUo.",
        ".ouuuyyuuUo.",
        ".ouuyggyuUo.",
        ".ouuyggyuUo.",
        ".ouuuyyuuUo.",
        ".ouuuuuuuUo.",
        ".oUUUUUUUUo.",
        ".opppppppPo.",
        ".oPPPPPPPPo.",
        ".oooooooooo.",
    ],
    "landmark": [
        ".....oo.....",
        "...oowwoo...",
        ".oowwwwwwoo.",
        "ovvvvvvvvvvo",
        "oooooooooooo",
        ".owoowwoowo.",
        ".owoowwoowo.",
        ".owoowwoowo.",
        ".owoowwoowo.",
        "oooooooooooo",
        "ovvvvvvvvvvo",
        "oooooooooooo",
    ],
    "paw": [
        "...oo..oo...",
        "..onnoonno..",
        "..oNNooNNo..",
        "oo.oo..oo.oo",
        "onno....onno",
        "oNNo.oo.oNNo",
        ".oo.onno.oo.",
        "...onnnno...",
        "..onnnnnno..",
        "..oNnnnnNo..",
        "...oNNNNo...",
        "....oooo....",
    ],
    "mountain": [
        "............",
        ".....oo.....",
        "....owvo....",
        "...owwvvo...",
        "...onwvNo...",
        "..onnnNNNo..",
        "..onnnnNNo..",
        ".onnnnnNNNo.",
        ".onnnnnNNNo.",
        "olleeeeeeEEo",
        "oleeeeeeeEEo",
        "oooooooooooo",
    ],
    "help": [
        "...oooooo...",
        "..owwwwwwo..",
        ".owwoooowwo.",
        ".oowo..owwo.",
        "..oo..owwo..",
        ".....owwo...",
        "....owwo....",
        "....owvo....",
        "....oooo....",
        "....owwo....",
        "....ovvo....",
        "....oooo....",
    ],
    "plus": [
        "............",
        "....oooo....",
        "....owwo....",
        "....owwo....",
        ".oooowwoooo.",
        ".owwwwwwwwo.",
        ".ovvvwwvvvo.",
        ".oooowwoooo.",
        "....owwo....",
        "....ovvo....",
        "....oooo....",
        "............",
    ],
    "info": [
        "....oooo....",
        "..oobbbboo..",
        ".obbbwwbbbo.",
        ".obbbwwbbBo.",
        "obbbbbbbbbBo",
        "obbbwwwbbbBo",
        "obbbbwwbbbBo",
        "obbbbwwbbBBo",
        ".obbwwwwbBo.",
        ".oBbbbbbBBo.",
        "..ooBBBBoo..",
        "....oooo....",
    ],
    "undo": [
        "............",
        "...o........",
        "..owo.......",
        ".owwooooo...",
        "owwwwwwwwoo.",
        ".ovvvvvvvwwo",
        "..ovooooovwo",
        "...o....ovwo",
        "........ovwo",
        "...ooooovwwo",
        "...owwwwwwo.",
        "...ooooooo..",
    ],
    "settings": [
        "....oooo....",
        ".oooovvoooo.",
        ".oovvvvssoo.",
        ".ovvvvvssSo.",
        "ovvvoooosSSo",
        "ovvvo..osSSo",
        "ovvso..oSSSo",
        "osssooooSSSo",
        ".osssssSSSo.",
        ".oosSSSSSoo.",
        ".ooooSSoooo.",
        "....oooo....",
    ],
    "chevron": [
        "............",
        "...oo.......",
        "...owo......",
        "...owwo.....",
        "....owwo....",
        ".....owwo...",
        ".....ovvo...",
        "....ovvo....",
        "...ovvo.....",
        "...ovo......",
        "...oo.......",
        "............",
    ],
    "minus": [
        "............",
        "............",
        "............",
        "............",
        ".oooooooooo.",
        ".owwwwwwwwo.",
        ".ovvvvvvvvo.",
        ".oooooooooo.",
        "............",
        "............",
        "............",
        "............",
    ],
}


def rgba(value):
    return tuple(int(value[i : i + 2], 16) for i in (1, 3, 5)) + (255,)


def render(name, rows):
    if len(rows) != SIZE or any(len(row) != SIZE for row in rows):
        raise ValueError(f"{name}: every icon is {SIZE} rows of {SIZE} characters")
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch == ".":
                continue
            if ch not in COLORS:
                raise ValueError(f"{name}: unknown colour letter {ch!r} at {x},{y}")
            img.putpixel((x, y), rgba(COLORS[ch]))
    return img


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.png"):
        old.unlink()
    for name, rows in ICONS.items():
        img = render(name, rows)
        for suffix, scale in DENSITIES.items():
            img.resize((SIZE * scale, SIZE * scale), Image.NEAREST).save(OUT / f"{name}{suffix}.png", optimize=True)
    lines = [
        "// Generated by scripts/art/build_ui_icons.py. Do not edit.",
        "export const UI_ICONS = {",
        *[f"  {name}: require('@/assets/ui/icons/{name}.png')," for name in ICONS],
        "} as const;",
        "",
        "export type IconName = keyof typeof UI_ICONS;",
        "",
    ]
    TS_OUT.write_text("\n".join(lines))
    print(f"{len(ICONS)} icons -> {OUT.relative_to(ROOT)}, {TS_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
