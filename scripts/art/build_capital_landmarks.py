"""Export src/data/capital-landmarks/<capital-id>.json from the capital scene builders.

Each file contains a landmarks array. Each landmark has a globally unique stable id, a
display name, and a bbox [x, y, width, height] in scene pixels from the top-left. The box
includes its origin and excludes its right and bottom edges. The mask is a Base64-encoded
bitset with one bit per box pixel, row-major from the top-left. Bit i = local_y * width +
local_x is 1 for a visible painted pixel (least significant bit first in each byte). Rows
are packed without padding and unused bits in the last byte are zero.

    .venv/bin/python scripts/art/build_capital_landmarks.py [capital-id ...]
"""

import argparse
import base64
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from PIL import Image, ImageChops

from build_capitals import CAPITALS, OUT as SCENES, ROOT
from capital_landmark_names import NAMES
from check_capital import measure_landmarks

OUT = ROOT / 'src' / 'data' / 'capital-landmarks'


def encode_landmark(mark, landmark_id, name):
    columns, rows = zip(*mark['visible'])
    x, y = min(columns), min(rows)
    width, height = max(columns) - x + 1, max(rows) - y + 1
    mask = bytearray((width * height + 7) // 8)
    for px, py in mark['visible']:
        bit = (py - y) * width + px - x
        mask[bit // 8] |= 1 << (bit % 8)
    return {'id': landmark_id, 'name': name, 'bbox': [x, y, width, height],
            'mask': base64.b64encode(mask).decode('ascii')}


def export_capital(capital):
    cap_id = capital['id']
    image, marks = measure_landmarks(capital)
    with Image.open(SCENES / f'{cap_id}.png') as png:
        if png.size != image.size or ImageChops.difference(png.convert('RGB'), image).getbbox():
            raise ValueError(f'{cap_id}: rendered pixels differ from the scene PNG')
    names = NAMES[cap_id]
    if len(marks) != len(names) or {mark['builder'] for mark in marks} != names.keys():
        raise ValueError(f'{cap_id}: measured landmarks differ from the name table')
    landmarks = []
    for mark in marks:
        if mark['clipped'] or not mark['visible']:
            raise ValueError(f"{cap_id}/{mark['builder']}: clipped or empty shape")
        landmarks.append(encode_landmark(mark, *names[mark['builder']]))
    landmarks.sort(key=lambda landmark: landmark['id'])
    filename = OUT / f'{cap_id}.json'
    data = {
        'generatedBy': 'scripts/art/build_capital_landmarks.py',
        'landmarks': landmarks,
    }
    with TemporaryDirectory(dir=OUT) as directory:
        temporary = Path(directory) / filename.name
        temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        temporary.replace(filename)
    print(f'{cap_id}: {len(landmarks)} landmarks')


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('capital_ids', metavar='capital-id', nargs='*')
    args = parser.parse_args()
    capitals = {capital['id']: capital for capital in CAPITALS}
    for cap_id in args.capital_ids:
        if cap_id not in capitals:
            parser.error(f'unknown capital: {cap_id}')
    OUT.mkdir(parents=True, exist_ok=True)
    for cap_id in args.capital_ids or capitals:
        export_capital(capitals[cap_id])


if __name__ == '__main__':
    main()
