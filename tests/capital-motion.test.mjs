import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import ts from 'typescript';

const source = readFileSync(new URL('../src/features/world/capital-motion.ts', import.meta.url), 'utf8');
const { outputText } = ts.transpileModule(source, {
  compilerOptions: { module: ts.ModuleKind.ES2022, target: ts.ScriptTarget.ES2022 },
});
const { GULLS, CLOUD_SHADOWS, glintAt, gullAt, cloudShadowAt } = await import(
  `data:text/javascript;base64,${Buffer.from(outputText).toString('base64')}`
);
const scenes = JSON.parse(readFileSync(new URL('../src/data/capitals.json', import.meta.url), 'utf8'));
const motion = JSON.parse(readFileSync(new URL('../src/data/capital-motion.json', import.meta.url), 'utf8'));

test('every capital has its water glint spots, inside its scene', () => {
  assert.deepEqual(Object.keys(motion).sort(), scenes.map((s) => s.id).sort());
  for (const scene of scenes) {
    for (const [x, y] of motion[scene.id].glints) {
      assert.ok(x >= 1 && x < scene.width - 2 && y >= 0 && y < scene.height, `${scene.id} ${x},${y}`);
    }
  }
  // Rivers, canals and harbours are found; inland scenes without water have none.
  for (const id of ['lisbon', 'amsterdam', 'budapest', 'valletta', 'stockholm']) assert.ok(motion[id].glints.length >= 50, id);
  for (const id of ['paris', 'london', 'rome', 'bern', 'ljubljana', 'madrid', 'vaduz', 'andorra']) assert.ok(motion[id].glints.length >= 15, id);
  for (const id of ['athens', 'sofia', 'pristina', 'ankara']) assert.equal(motion[id].glints.length, 0, id);
});

test('glints twinkle on their own rhythm; nothing shows while the clock is still', () => {
  const shown = Array.from({ length: 300 }, (_, i) => glintAt((i + 1) / 12, 0.3).visible).filter(Boolean).length;
  assert.ok(shown / 300 > 0.25 && shown / 300 < 0.45, `${shown / 300}`);
  const a = Array.from({ length: 60 }, (_, i) => glintAt((i + 1) / 12, 0.1).visible);
  const b = Array.from({ length: 60 }, (_, i) => glintAt((i + 1) / 12, 0.6).visible);
  assert.notDeepEqual(a, b, 'neighbouring glints are out of step');
  assert.deepEqual(glintAt(0, 0.3), { visible: false, pose: 0, dx: 0 });
});

test('gulls cross the scene both ways and cloud shadows drift east across it', () => {
  const [width, height] = [720, 520];
  for (let gull = 0; gull < GULLS; gull++) {
    const xs = Array.from({ length: 200 }, (_, i) => gullAt(gull, i / 2, width, height).x);
    assert.ok(Math.min(...xs) < 0 && Math.max(...xs) > width, `gull ${gull} crosses the whole scene`);
    const { y } = gullAt(gull, 10, width, height);
    assert.ok(y > 0 && y < height);
  }
  assert.notEqual(gullAt(0, 5, width, height).east, gullAt(1, 5, width, height).east);
  for (let shadow = 0; shadow < CLOUD_SHADOWS; shadow++) {
    const a = cloudShadowAt(shadow, 10, width, height, [120, 50]);
    const b = cloudShadowAt(shadow, 11, width, height, [120, 50]);
    assert.ok(b.x > a.x, 'moves east');
    const xs = Array.from({ length: 400 }, (_, i) => cloudShadowAt(shadow, i, width, height, [120, 50]).x);
    assert.ok(Math.min(...xs) >= -120 && Math.max(...xs) <= width, 'wraps round just outside the scene');
  }
});
