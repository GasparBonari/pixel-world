import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import ts from 'typescript';

const source = readFileSync(new URL('../src/features/style-study/scene.ts', import.meta.url), 'utf8');
const { outputText } = ts.transpileModule(source, {
  compilerOptions: { module: ts.ModuleKind.ES2022, target: ts.ScriptTarget.ES2022 },
});
const scene = await import(
  `data:text/javascript;base64,${Buffer.from(outputText).toString('base64')}`
);

function pngSize(name) {
  const bytes = readFileSync(
    new URL(`../assets/style-study/ninja-adventure/${name}.png`, import.meta.url)
  );
  return { width: bytes.readUInt32BE(16), height: bytes.readUInt32BE(20) };
}

test('every sprite source lies inside its sheet', () => {
  const sizes = {};
  for (const item of scene.buildScene()) {
    const size = (sizes[item.sheet] ??= pngSize(item.sheet));
    const [x, y, w, h] = item.source;
    assert.ok(x >= 0 && y >= 0 && w > 0 && h > 0, `${item.sheet} ${item.source}`);
    assert.ok(x + w <= size.width && y + h <= size.height, `${item.sheet} ${item.source}`);
  }
});

test('ground covers every scene tile exactly once', () => {
  const ground = scene.buildScene().filter((item) => item.layer === 'ground');
  const cells = new Set(ground.map((item) => `${item.x},${item.y}`));
  assert.equal(ground.length, scene.SCENE_COLUMNS * scene.SCENE_ROWS);
  assert.equal(cells.size, ground.length);
});

test('draw batches keep layer order', () => {
  const batches = scene.drawBatches(scene.buildScene());
  const order = batches.map((batch) => scene.LAYERS.indexOf(batch.layer));
  assert.deepEqual(
    order,
    [...order].sort((a, b) => a - b)
  );
  assert.equal(
    batches.reduce((sum, batch) => sum + batch.items.length, 0),
    scene.buildScene().length
  );
});

test('scene scale is a whole number of at least 2', () => {
  assert.equal(scene.sceneScale(320, 400), 2);
  assert.equal(scene.sceneScale(390, 506), 2);
  assert.equal(scene.sceneScale(1440, 540), 3);
});

test('recoloured sheets keep the original dimensions', () => {
  for (const name of ['floor', 'water', 'nature']) {
    const recolored = readFileSync(
      new URL(`../assets/style-study/globe-palette/${name}.png`, import.meta.url)
    );
    assert.deepEqual(
      { width: recolored.readUInt32BE(16), height: recolored.readUInt32BE(20) },
      pngSize(name),
      name
    );
  }
});
