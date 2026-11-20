import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import ts from 'typescript';

const source = readFileSync(new URL('../src/features/world/flocks.ts', import.meta.url), 'utf8');
const { outputText } = ts.transpileModule(source, {
  compilerOptions: { module: ts.ModuleKind.ES2022, target: ts.ScriptTarget.ES2022 },
});
const { FLOCKS, FLOCK_COUNT, FORMATION, flockAt, makeFlock } = await import(
  `data:text/javascript;base64,${Buffer.from(outputText).toString('base64')}`
);
const radians = Math.PI / 180;
const arc = (a, b) =>
  Math.acos(
    Math.min(1, Math.sin(a.latitude * radians) * Math.sin(b.latitude * radians)
      + Math.cos(a.latitude * radians) * Math.cos(b.latitude * radians)
        * Math.cos((b.longitude - a.longitude) * radians))
  ) / radians;

test('flocks are fixed: the same routes on every device, three birds each', () => {
  assert.equal(FLOCKS.length, FLOCK_COUNT);
  assert.deepEqual(makeFlock(7), FLOCKS[7]);
  assert.equal(FORMATION.length, 3);
  // Spread over the planet: starting points in both hemispheres and all around.
  const starts = FLOCKS.map((flock) => flockAt(flock, 0));
  assert.ok(starts.some((p) => p.latitude > 20) && starts.some((p) => p.latitude < -20));
  assert.ok(starts.some((p) => p.longitude > 90) && starts.some((p) => p.longitude < -90));
});

test('each flock flies its great circle at 0.5 to 0.9 degrees a second without jumping', () => {
  for (const flock of FLOCKS) {
    let previous = flockAt(flock, 0);
    for (let t = 1; t <= 900; t += 1) {
      const next = flockAt(flock, t);
      assert.ok(Number.isFinite(next.longitude) && Math.abs(next.latitude) <= 90);
      const step = arc(previous, next);
      assert.ok(step > 0.49 && step < 0.91, `${step} degrees in a second`);
      previous = next;
    }
  }
});

test('the heading flag matches which way the flock actually moves', () => {
  let checked = 0;
  for (const flock of FLOCKS) {
    for (let t = 0; t < 600; t += 37) {
      const here = flockAt(flock, t);
      const next = flockAt(flock, t + 0.5);
      const moved = ((next.longitude - here.longitude + 540) % 360) - 180;
      if (Math.abs(moved) < 0.05 || Math.abs(here.latitude) > 80) continue; // nearly due north/south
      assert.equal(here.east, moved > 0, `flock at ${here.longitude},${here.latitude}`);
      checked++;
    }
  }
  assert.ok(checked > 500);
});
