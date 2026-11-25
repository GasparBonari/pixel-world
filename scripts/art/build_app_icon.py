"""Build the launcher icons, web favicon and native splash artwork with Pillow.

Run .venv/bin/python scripts/art/build_app_icon.py from the repository root.
Use --previews DIR to also export three icon sizes and a phone splash preview.
"""

import argparse
import hashlib
import json
import re
from math import asin, atan2, cos, degrees, radians, sin, sqrt
from pathlib import Path

from PIL import Image, ImageColor, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "assets/images"
GEOGRAPHY = ROOT / "assets/world/globe.png"

ICON_GRID = 32
ADAPTIVE_GRID = 48
GLOBE_SIZE = 26
SPLASH_WIDTH = 192  # Matches expo-splash-screen's imageWidth in app.json.
VIEW_LONGITUDE = -28
VIEW_LATITUDE = radians(14)

# Daytime globe ramps from globe-shader.ts, phase3_mockups.py and recolor_style_study.py.
ATMOSPHERE = "#62C3DA"
SHALLOWS = "#40A8C4"
OCEAN = "#2973BF"
DEEP_OCEAN = "#174599"
GRASS_LIGHT = "#A3CF4E"
GRASS = "#74AC3D"
FOREST = "#337A40"
SAND = "#D1B363"


def read_theme_colors():
    theme = (ROOT / "src/constants/theme.ts").read_text(encoding="utf-8")
    palette = theme.split("export const Palette = {", 1)[1].split("} as const;", 1)[0]
    colors = dict(re.findall(r"\b(\w+): '(#[\da-fA-F]{6})'", palette))
    return {name: colors[name] for name in ("night", "space", "snow")}


def surface_coordinates(x, y, z):
    """Invert the orthographic view to sample the same map texture as the game."""
    sin_center, cos_center = sin(VIEW_LATITUDE), cos(VIEW_LATITUDE)
    latitude = degrees(asin(y * cos_center + z * sin_center))
    longitude = VIEW_LONGITUDE + degrees(atan2(x, z * cos_center - y * sin_center))
    return longitude, latitude


def draw_globe(geography, colors):
    globe = Image.new("RGBA", (GLOBE_SIZE, GLOBE_SIZE))
    monochrome = Image.new("RGBA", globe.size)
    width, height = geography.size
    sample = geography.load()
    snow = ImageColor.getcolor(colors["snow"], "RGBA")

    for row in range(GLOBE_SIZE):
        for col in range(GLOBE_SIZE):
            x = (2 * col + 1) / GLOBE_SIZE - 1
            y = 1 - (2 * row + 1) / GLOBE_SIZE
            distance_squared = x * x + y * y
            if distance_squared >= 1:
                continue

            z = sqrt(1 - distance_squared)
            lon, lat = surface_coordinates(x, y, z)
            u = (lon + 180) % 360 / 360
            v = (90 - lat) / 180
            red, _, blue = sample[int(u * width), min(int(v * height), height - 1)]
            land = red >= 128 and blue < 128
            # One pixel of stepped atmosphere and lighting from the upper left.
            rim = distance_squared >= 0.85
            light = 0.65 * z + 0.45 * y - 0.55 * x
            if rim:
                color = ATMOSPHERE if light > 0.2 else OCEAN
            elif land:
                if abs(lat) >= 74:
                    color = colors["snow"]
                elif 16 <= lat <= 32 and -17 <= lon <= 42:
                    color = SAND
                elif light >= 0.68:
                    color = GRASS_LIGHT
                else:
                    color = GRASS if light >= 0.24 else FOREST
            elif light >= 0.68:
                color = SHALLOWS
            else:
                color = OCEAN if light >= 0.18 else DEEP_OCEAN
            globe.putpixel((col, row), ImageColor.getcolor(color, "RGBA"))

            # Transparent oceans retain the continent shapes when the launcher applies its tint.
            if rim or (land and distance_squared < 0.7):
                monochrome.putpixel((col, row), snow)

    return globe, monochrome


def center(canvas, sprite):
    offset = ((canvas.width - sprite.width) // 2, (canvas.height - sprite.height) // 2)
    canvas.paste(sprite, offset, sprite)
    return canvas


def draw_icon(globe, colors):
    icon = square(ICON_GRID, colors["night"])
    offset = (ICON_GRID - GLOBE_SIZE) // 2 + 1
    shadow = square(GLOBE_SIZE, colors["space"])
    icon.paste(shadow, (offset, offset), globe.getchannel("A"))
    center(icon, globe)
    draw = ImageDraw.Draw(icon)
    # Three hard-edged stars frame the globe.
    draw.line((5, 2, 5, 6), fill=ATMOSPHERE)
    draw.line((3, 4, 7, 4), fill=ATMOSPHERE)
    draw.point((5, 4), fill=colors["snow"])
    draw.point((27, 27), fill=ATMOSPHERE)
    draw.point((26, 6), fill=colors["snow"])
    return icon


def square(size, color=None):
    return Image.new("RGBA" if color is None else "RGB", (size, size), color)


def scale(image, size):
    return image.resize((size, size), Image.Resampling.NEAREST)


def save_png(image, path):
    image.save(path, optimize=True)


def write_assets(icon, globe, monochrome, colors):
    # 26 of 48 pixels puts the adaptive globe inside Android's 66 of 108 dp safe circle.
    adaptive_size = 864
    assets = {
        "icon.png": scale(icon, 1024),
        "favicon.png": scale(icon, 48),
        "android-icon-foreground.png": scale(center(square(ADAPTIVE_GRID), globe), adaptive_size),
        "android-icon-background.png": scale(square(ADAPTIVE_GRID, colors["night"]), adaptive_size),
        "android-icon-monochrome.png": scale(center(square(ADAPTIVE_GRID), monochrome), adaptive_size),
        "splash-icon.png": scale(center(square(ICON_GRID), globe), 1024),
    }
    manifest = {
        "generatedBy": "scripts/art/build_app_icon.py",
        "license": "MIT (repository LICENSE)",
        "sources": {
            "geography": {
                "path": "assets/world/globe.png",
                "attribution": "Natural Earth, public domain",
                "manifest": "assets/world/manifest.json",
            },
            "palette": [
                "src/constants/theme.ts",
                "src/features/world/globe-shader.ts",
                "scripts/art/phase3_mockups.py",
                "scripts/art/recolor_style_study.py",
            ],
        },
        "images": {},
    }
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for name, image in assets.items():
        path = OUTPUT / name
        save_png(image, path)
        data = path.read_bytes()
        manifest["images"][name] = {
            "width": image.width,
            "height": image.height,
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
        }
    (OUTPUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def write_previews(directory, icon, globe, colors):
    directory.mkdir(parents=True, exist_ok=True)
    for size in (1024, 180, 48):
        save_png(scale(icon, size), directory / f"icon-{size}.png")
    splash = Image.new("RGB", (390, 844), colors["night"])
    splash_icon = scale(center(square(ICON_GRID), globe), SPLASH_WIDTH)
    save_png(center(splash, splash_icon), directory / "splash-preview.png")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--previews", type=Path, metavar="DIR")
    args = parser.parse_args()
    colors = read_theme_colors()
    with Image.open(GEOGRAPHY) as geography:
        globe, monochrome = draw_globe(geography, colors)
    icon = draw_icon(globe, colors)
    write_assets(icon, globe, monochrome, colors)
    if args.previews:
        write_previews(args.previews, icon, globe, colors)


if __name__ == "__main__":
    main()
