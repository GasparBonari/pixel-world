import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import test from 'node:test';
import { compileFunction } from 'node:vm';
import ts from 'typescript';

function loadLogic(path) {
  const { outputText } = ts.transpileModule(readFileSync(path, 'utf8'), {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022, esModuleInterop: true },
  });
  const exports = {};
  const require = createRequire(path);
  compileFunction(outputText, ['require', 'exports'])(
    (id) => id.endsWith('.json') ? require(id) : loadLogic(new URL(`${id}.ts`, path)),
    exports
  );
  return exports;
}

const { classifyTap, getChallenge, maskContains, nextPrompt, recordMiss, screenToScenePixel, showAssist } =
  loadLogic(new URL('../src/features/find-it/challenge.ts', import.meta.url));
const { createLandmarkProgress } = loadLogic(new URL('../src/features/find-it/landmark-progress.ts', import.meta.url));
const { capitalScreenRect } = loadLogic(new URL('../src/features/world/capitals.ts', import.meta.url));
const { getCheckedLandmarks } = loadLogic(new URL('../src/features/catalog/catalog.ts', import.meta.url));
const scenes = JSON.parse(readFileSync(new URL('../src/data/capitals.json', import.meta.url), 'utf8'));

test('mask includes its painted edges and excludes clear pixels and the pixels just beyond it', () => {
  const { shapes } = getChallenge('paris');
  const obelisk = shapes.find(({ id }) => id === 'luxor-obelisk');
  const [x, y, width, height] = obelisk.bbox;
  const bytes = Buffer.from(obelisk.mask, 'base64');
  for (let row = 0; row < height; row++) {
    for (let col = 0; col < width; col++) {
      const bit = row * width + col;
      assert.equal(maskContains(obelisk, { x: x + col, y: y + row }), Boolean(bytes[bit >> 3] & (1 << (bit % 8))));
    }
  }
  assert.equal(maskContains(obelisk, { x: x - 1, y: y + 15 }), false);
  assert.equal(maskContains(obelisk, { x: x + width, y: y + 15 }), false);
  assert.equal(maskContains(obelisk, { x: x + 3, y: y - 1 }), false);
  assert.equal(maskContains(obelisk, { x: x + 3, y: y + height }), false);
  assert.equal(classifyTap({ x: 252, y: 175 }, obelisk, shapes), 'hit');
  assert.equal(classifyTap({ x: 249, y: 175 }, obelisk, shapes), 'miss');
  assert.equal(classifyTap({ x: 252, y: 175 }, shapes.find(({ id }) => id === 'louvre'), shapes), 'other');
});

test('tap projection follows the rendered scene at different zooms and after panning', () => {
  const scene = scenes.find(({ id }) => id === 'paris');
  const viewport = { width: 390, height: 844 };
  const target = getChallenge('paris').shapes.find(({ id }) => id === 'luxor-obelisk');
  for (const zoom of [6.3, 6.82, 7]) {
    for (const iconScale of [2, 2.375]) {
      const camera = { longitude: scene.longitude - 0.5, latitude: scene.latitude + 0.18, zoom };
      const area = capitalScreenRect(scene, camera, viewport, iconScale);
      const screen = (x, y) => ({
        x: area.x + x * (area.width / scene.width),
        y: area.y + y * (area.height / scene.height),
      });
      const pixel = screenToScenePixel(screen(252.5, 175.5), area, scene);
      assert.deepEqual(pixel, { x: 252, y: 175 });
      assert.ok(maskContains(target, pixel));
      assert.deepEqual(screenToScenePixel(screen(0, 0), area, scene), { x: 0, y: 0 });
      assert.equal(screenToScenePixel({ x: area.x + area.width, y: area.y }, area, scene), undefined);
      assert.equal(screenToScenePixel({ x: area.x, y: area.y + area.height }, area, scene), undefined);
      assert.equal(screenToScenePixel(screen(-0.1, 0), area, scene), undefined);
    }
  }
});

test('prompts cover the checked pack in a fixed order and stop when it is complete', () => {
  for (const [id, first] of [['lisbon', 'belem-tower'], ['paris', 'arc-de-triomphe'], ['athens', 'academy-of-athens']]) {
    const progress = createLandmarkProgress();
    const { prompts } = getChallenge(id);
    const ids = prompts.map(({ landmark }) => landmark.id);
    const checkedIds = getCheckedLandmarks(id).map(({ id }) => id).sort();
    assert.deepEqual(ids, [first, ...checkedIds.filter((id) => id !== first)]);
    for (const prompt of prompts) {
      assert.equal(nextPrompt(prompts, progress.getSnapshot()), prompt);
      progress.markFound(prompt.landmark.id, new Date());
    }
    assert.equal(nextPrompt(prompts, progress.getSnapshot()), undefined);
  }
  assert.equal(getChallenge('reykjavik'), undefined);
});

test('each prompt earns its own assist after exactly three misses', () => {
  let misses = new Map();
  for (const count of [1, 2, 3, 4]) {
    misses = recordMiss(misses, 'belem-tower');
    assert.equal(misses.get('belem-tower'), count);
    assert.equal(showAssist(count), count >= 3);
  }
  assert.equal(misses.has('arco-rua-augusta'), false);
  misses = recordMiss(misses, 'arco-rua-augusta');
  assert.equal(misses.get('arco-rua-augusta'), 1);
  assert.equal(misses.get('belem-tower'), 4);
});

test('progress keeps the original date and only notifies on a new find', () => {
  const progress = createLandmarkProgress();
  const date = new Date(2026, 10, 25);
  let notifications = 0;
  const unsubscribe = progress.subscribe(() => { notifications++; });
  const empty = progress.getSnapshot();
  progress.markFound('belem-tower', date);
  const found = progress.getSnapshot();
  progress.markFound('belem-tower', new Date(2026, 10, 26));
  assert.equal(notifications, 1);
  assert.equal(empty.size, 0);
  assert.equal(progress.getSnapshot(), found);
  assert.equal(found.get('belem-tower'), date);
  unsubscribe();
  progress.markFound('arco-rua-augusta', date);
  assert.equal(notifications, 1);
});
