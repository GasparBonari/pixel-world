import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import ts from 'typescript';

async function loadLogic(filename) {
  const source = readFileSync(new URL(`../src/features/world/${filename}.ts`, import.meta.url), 'utf8');
  const { outputText } = ts.transpileModule(source, {
    compilerOptions: { module: ts.ModuleKind.ES2022, target: ts.ScriptTarget.ES2022 },
  });
  return import(`data:text/javascript;base64,${Buffer.from(outputText).toString('base64')}`);
}

const { cameraFromParams, OPENING_CAMERA, MAX_GLOBE_ZOOM } = await loadLogic('globe-camera');
const { iconOpacity } = await loadLogic('map-icons');
const icons = JSON.parse(readFileSync(new URL('../src/data/map-icons.json', import.meta.url), 'utf8'));

function pngSize(path) {
  const bytes = readFileSync(new URL(path, import.meta.url));
  return { width: bytes.readUInt32BE(16), height: bytes.readUInt32BE(20) };
}

test('URL params open a constrained camera, and absent params keep the default opening', () => {
  assert.equal(cameraFromParams({}), undefined);
  assert.equal(cameraFromParams({ lon: '', zoom: undefined }), undefined);
  assert.deepEqual(cameraFromParams({ lon: '14.5', lat: '35.9', zoom: '2.6' }), {
    longitude: 14.5,
    latitude: 35.9,
    zoom: 2.6,
  });
  const clamped = cameraFromParams({ lon: '190', lat: '95', zoom: '99' });
  assert.equal(clamped.longitude, -170);
  assert.equal(clamped.latitude, 80);
  assert.equal(clamped.zoom, MAX_GLOBE_ZOOM);
  assert.deepEqual(cameraFromParams({ zoom: 'abc', lat: ['40'] }), { ...OPENING_CAMERA, latitude: 40 });
});

test('board icons fade in over the second half of the transition', () => {
  assert.equal(iconOpacity(1.5, 1.5, 2.5), 0);
  assert.equal(iconOpacity(2.0, 1.5, 2.5), 0);
  assert.ok(iconOpacity(2.25, 1.5, 2.5) > 0 && iconOpacity(2.25, 1.5, 2.5) < 1);
  assert.equal(iconOpacity(2.5, 1.5, 2.5), 1);
  assert.equal(iconOpacity(5, 1.5, 2.5), 1);
});

test('map icons reference frames inside the sprite sheet and real coordinates, north to south', () => {
  const sheet = pngSize('../assets/world/map-icons.png');
  for (const [x, y, w, h] of icons.frames) {
    assert.ok(x >= 0 && y >= 0 && w > 0 && h > 0 && x + w <= sheet.width && y + h <= sheet.height);
  }
  assert.ok(icons.icons.length > 500);
  let previous = Infinity;
  for (const [frame, longitude, latitude, dx, dy] of icons.icons) {
    assert.ok(Number.isInteger(frame) && frame >= 0 && frame < icons.frames.length);
    assert.ok(Math.abs(longitude) <= 180 && Math.abs(latitude) <= 90);
    assert.ok(Number.isInteger(dx) && Number.isInteger(dy));
    assert.ok(latitude - dy * 0.01 <= previous + 1e-9, 'icons draw back to front');
    previous = latitude - dy * 0.01;
  }
});

test('board texture matches the shader sampling size', () => {
  assert.deepEqual(pngSize('../assets/world/board.png'), { width: 2048, height: 1024 });
  assert.deepEqual(pngSize('../assets/world/globe.png'), { width: 4096, height: 2048 });
});
