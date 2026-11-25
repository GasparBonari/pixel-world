"""Check one capital scene: are its landmarks where the real city has them, and all fully visible?

Renders the scene, finds each landmark's drawn position and painted pixels, and reports:
  - placement against the real coordinates in the landmark module's SITES table: every pair of
    landmarks more than 120 m apart along an axis must keep its real east/west and north/south
    order, and the rank correlation of drawn against real positions should be 1.00 on both axes;
  - landmark pixels hidden by anything drawn later (houses, trees, other landmarks);
  - landmark pixels clipped at the scene edge, and overlaps between landmarks.

    .venv/bin/python scripts/art/check_capital.py <capital-id> [out.png]

Exit status 1 if anything fails. Read-only for the repository (writes only the optional PNG).
"""
import functools
import importlib
import inspect
import math
import sys
from collections import Counter
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch

import iso
import build_capitals as bc
from capital_sites import SITES as KNOWN

HERE = Path(__file__).resolve().parent
MIN_METRES = 120
# Drawing functions that are part of a larger landmark, not landmarks of their own:
# Dublin Castle draws its round Record Tower with landmarks_ireland.round_tower.
PARTS = {('landmarks_ireland', 'round_tower')}
# Landmarks that really stand in front of one another: Leif Erikson's statue faces Hallgrímskirkja
# from the square right before its door.
TOGETHER = {('reykjavik', frozenset({'hallgrimskirkja', 'leif'}))}
# Repeated fillers that are not landmarks (and are not in SITES).
FILLER = {'tram_28', 'tram', 'belgian_flag', 'winged_figure', 'dome', 'cathedral_roof', 'stone_bridge',
          'funicular', 'stall', 'gazebo', 'arcade', 'townhouse'}
# Drawing helpers that are never landmarks.
HELPERS = {'P', 'seg', 'poly', 'corners', 'facade', 'preview', 'tones', 'palette_of', 'stone_courses',
           'arch_opening', 'new_scene', 'visible_tiles', 'paint_ground', 'tile_of', 'to_s', 'ground_color',
           'main', 'cylinder', 'ellipse', 'block', 'band', 'hip_roof', 'crenellate', 'revolve', 'slab',
           'surface', 'windows', 'gable_roof', 'mansard', 'pediment', 'egg_dome', 'lancet', 'gable', 'pinnacle',
           'spire', 'statue', 'apple', 'flag', 'lamp', 'balustrade', 'round_tree', 'umbrella_pine', 'rowboat',
           'bateau', 'chequy', 'shield', 'cross', 'lifted', 'helm', 'figure', 'clock'}


def render_landmark_calls(capital):
    """Render with temporary wrappers so the checker and exporter can trace any number of scenes."""
    mods = [importlib.import_module(path.stem) for path in sorted(HERE.glob('landmarks_*.py'))]
    mods.append(bc)
    calls, depth, originals = [], 0, {}

    def wrap(modname, name, fn):
        @functools.wraps(fn)
        def inner(*a, **k):
            nonlocal depth
            top = depth == 0 and len(a) >= 3 and isinstance(a[0], iso.Scene)
            depth += 1
            try:
                return fn(*a, **k)
            finally:
                depth -= 1
                if top:
                    calls.append((modname, name, a[1:], k))
        return inner

    capitals = {c['id'] for c in bc.CAPITALS}
    for m in mods:
        for name, fn in list(vars(m).items()):
            if inspect.isfunction(fn) and fn.__module__ == m.__name__ and name not in HELPERS | capitals:
                originals[(m.__name__, name)] = fn
    wrapped, site_of = {}, {}
    with ExitStack() as patches:
        for m in mods:
            for name, fn in list(vars(m).items()):
                key = (getattr(fn, '__module__', None), name)
                if key in originals:
                    if key not in wrapped:
                        wrapped[key] = wrap(key[0], name, originals[key])
                    patches.enter_context(patch.object(m, name, wrapped[key]))
            if hasattr(m, 'SITES'):  # SITES tuples hold direct references to builders.
                new = []
                for site in m.SITES:
                    key = (site[1].__module__, site[1].__name__)
                    if key in wrapped:
                        site_of[key] = (site[0], site[3])  # name, real (longitude, latitude)
                        site = (site[0], wrapped[key]) + tuple(site[2:])
                    new.append(site)
                patches.enter_context(patch.object(m, 'SITES', new))
        image = capital['render']()
    return image, calls, originals, site_of


def measure_landmarks(capital):
    """Return the rendered scene and its landmark silhouettes in scene pixels."""
    cap_id = capital['id']
    image, calls, originals, site_of = render_landmark_calls(capital)
    final = image.convert('RGB').load()
    W, H = image.size

    count = Counter(name for _, name, _, _ in calls)
    seen, marks = set(), []
    for modname, name, args, kw in calls:
        key = (name, repr(args), repr(sorted(kw.items())))
        if key in seen or count[name] > 3 or name in FILLER or (modname, name) in PARTS:
            continue
        seen.add(key)
        # Large canvas: full silhouette (for clipping). Same frame: exact pixels (for hiding),
        # since some textures are keyed to absolute pixel positions.
        base = bc.new_scene()
        big = iso.Scene(W + 400, H + 400, (base.ox + 200, base.oy + 200))
        originals[(modname, name)](big, *args, **kw)
        big.paint_objects()
        same = bc.new_scene()
        originals[(modname, name)](same, *args, **kw)
        same.paint_objects()
        big_rgb = big.img.convert('RGB')
        big_px, box = big_rgb.load(), big_rgb.getbbox()
        if not box:
            continue
        pixels = {(x - 200, y - 200) for x in range(box[0], box[2]) for y in range(box[1], box[3])
                  if big_px[x, y] != (0, 0, 0)}
        inside = {p for p in pixels if 0 <= p[0] < W and 0 <= p[1] < H}
        same_rgb = same.img.convert('RGB')
        same_px = same_rgb.load()
        painted = {p for p in inside if same_px[p] != (0, 0, 0)}
        visible = {p for p in painted if final[p] == same_px[p]}
        left, right, bottom = box[0] - 200, box[2] - 200, box[3] - 200
        site = site_of.get((modname, name))
        if not site and name in KNOWN.get(cap_id, {}):  # capitals built before SITES tables
            site = (name, KNOWN[cap_id][name][:2])
        marks.append({'builder': name, 'name': site[0] if site else name, 'real': site[1] if site else None,
                      'base': ((left + right) / 2, bottom), 'pixels': pixels, 'visible': visible,
                      'hidden': len(painted) - len(visible), 'clipped': len(pixels) - len(inside)})
    return image, marks


def main():
    cap_id = sys.argv[1]
    capital = next(c for c in bc.CAPITALS if c['id'] == cap_id)
    image, marks = measure_landmarks(capital)
    if len(sys.argv) > 2:
        image.save(HERE / sys.argv[2])

    failures = 0
    print(f'{cap_id}: {len(marks)} landmarks')
    for a in range(len(marks)):
        for c in range(a + 1, len(marks)):
            overlap = len(marks[a]['pixels'] & marks[c]['pixels'])
            if overlap and (cap_id, frozenset({marks[a]['name'], marks[c]['name']})) not in TOGETHER:
                failures += 1
                print(f"  OVERLAP {marks[a]['name']} / {marks[c]['name']}: {overlap} px")
    for m in marks:
        bad = m['hidden'] or m['clipped']
        failures += bool(bad)
        print(f"  {m['name']:22s} base=({m['base'][0]:.0f},{m['base'][1]}) hidden={m['hidden']} "
              f"clipped={m['clipped']}{'  <-- FAIL' if bad else ''}")

    placed = [m for m in marks if m['real']]
    if len(placed) < 3:
        print('  placement not checked: give the landmark module a SITES table with each landmark\'s real '
              '(longitude, latitude), as in landmarks_croatia.py')
        failures += 1
    else:
        lat0 = sum(m['real'][1] for m in placed) / len(placed)
        east = [m['real'][0] * 111320 * math.cos(math.radians(lat0)) for m in placed]
        south = [-m['real'][1] * 110540 for m in placed]
        xs = [m['base'][0] for m in placed]
        ys = [m['base'][1] for m in placed]

        def rank_correlation(a, b):
            ra = {k: r for r, k in enumerate(sorted(range(len(a)), key=lambda k: a[k]))}
            rb = {k: r for r, k in enumerate(sorted(range(len(b)), key=lambda k: b[k]))}
            n = len(a)
            return 1 - 6 * sum((ra[k] - rb[k]) ** 2 for k in range(n)) / (n * (n * n - 1))
        print(f'  rank correlation east/x = {rank_correlation(east, xs):.2f}, '
              f'south/y = {rank_correlation(south, ys):.2f}')
        for a in range(len(placed)):
            for c in range(a + 1, len(placed)):
                for axis, real, drawn in (('east-west', east, xs), ('north-south', south, ys)):
                    d = real[c] - real[a]
                    if abs(d) > MIN_METRES and (drawn[c] - drawn[a]) * d < 0:
                        failures += 1
                        print(f"  REVERSED {axis}: {placed[a]['name']} / {placed[c]['name']} "
                              f"(really {abs(d):.0f} m apart, drawn {abs(drawn[c] - drawn[a]):.0f} px the wrong way)")
    print('  OK' if not failures else f'  {failures} problem(s)')
    sys.exit(1 if failures else 0)


if __name__ == '__main__':
    main()
