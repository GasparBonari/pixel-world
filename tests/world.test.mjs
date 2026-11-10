import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import ts from 'typescript';

// Use the installed compiler; some Node distributions omit built-in TS support.
async function loadLogic(filename) {
  const source = readFileSync(
    new URL(`../src/features/world/${filename}.ts`, import.meta.url),
    'utf8'
  );
  const { outputText } = ts.transpileModule(source, {
    compilerOptions: {
      module: ts.ModuleKind.ES2022,
      target: ts.ScriptTarget.ES2022,
    },
  });
  return import(`data:text/javascript;base64,${Buffer.from(outputText).toString('base64')}`);
}

const { longitudeLatitudeToWorld, worldToLongitudeLatitude, MAX_LATITUDE } =
  await loadLogic('projection');
const { constrainCamera, initialCamera, panCamera, zoomCamera } = await loadLogic('camera');
const { ImageCache } = await loadLogic('image-cache');
const { globePoint, globeLocation, rotateGlobe, zoomGlobe, MAX_GLOBE_ZOOM, constrainGlobe } =
  await loadLogic('globe-camera');

const viewport = { width: 390, height: 360 };
const close = (a, b) => assert.ok(Math.abs(a - b) < 1e-7, `${a} != ${b}`);

test('geographic projection round-trips real places and the antimeridian', () => {
  for (const [longitude, latitude] of [
    [14.5146, 35.8989],
    [12.4964, 41.9028],
    [179.9, -16],
    [-179.9, 65],
    [0, 0],
  ]) {
    const point = longitudeLatitudeToWorld(longitude, latitude);
    const result = worldToLongitudeLatitude(point.x, point.y);
    close(result.longitude, longitude);
    close(result.latitude, latitude);
  }
  close(longitudeLatitudeToWorld(0, 90).y, longitudeLatitudeToWorld(0, MAX_LATITUDE).y);
  close(longitudeLatitudeToWorld(0, -90).y, 1);
});

test('zoom preserves the geographic point under the pointer', () => {
  const camera = { x: 0.52, y: 0.45, zoom: 2 };
  const pointer = { x: 120, y: 140 };
  const next = zoomCamera(camera, 3.5, pointer.x, pointer.y, viewport);
  for (const [axis, dimension] of [
    ['x', 'width'],
    ['y', 'height'],
  ]) {
    const before =
      camera[axis] + (pointer[axis] - viewport[dimension] / 2) / (256 * 2 ** camera.zoom);
    const after = next[axis] + (pointer[axis] - viewport[dimension] / 2) / (256 * 2 ** next.zoom);
    close(before, after);
  }
});

test('pan wraps longitude, clamps polar edges, and respects zoom limits', () => {
  const next = panCamera({ x: 0.99, y: 0.5, zoom: 3 }, -100, 100000, viewport);
  assert.ok(next.x < 0.1 && next.x >= 0);
  assert.ok(next.y >= viewport.height / (2 * 256 * 2 ** 3));
  assert.equal(constrainCamera({ x: 0.5, y: 0.5, zoom: 99 }, viewport).zoom, 5);
  assert.deepEqual(
    constrainCamera({ x: 20, y: -10, zoom: -99 }, viewport),
    initialCamera(viewport)
  );
});

test('cache evicts the least recently used unprotected image and releases resources', () => {
  const released = [];
  const cache = new ImageCache(8, (value) => released.push(value));
  cache.set('a', 'A', 4);
  cache.set('b', 'B', 4);
  cache.get('a');
  cache.set('c', 'C', 4);
  cache.trim(new Set(['c']));
  assert.equal(cache.get('b'), undefined);
  assert.equal(cache.byteLength, 8);
  assert.deepEqual(released, ['B']);
  cache.clear();
  assert.equal(cache.byteLength, 0);
  assert.equal(cache.size, 0);
  assert.deepEqual(released.sort(), ['A', 'B', 'C']);
});

test('globe projection round-trips visible places and rejects the far hemisphere', () => {
  const camera = { longitude: 22, latitude: 24, zoom: 1 };
  for (const [longitude, latitude] of [
    [14.5146, 35.8989],
    [12.4964, 41.9028],
    [40, -5],
  ]) {
    const point = globePoint(longitude, latitude, camera, viewport);
    assert.ok(point.depth > 0);
    const location = globeLocation(point.x, point.y, camera, viewport);
    close(location.longitude, longitude);
    close(location.latitude, latitude);
  }
  assert.ok(globePoint(-158, -24, camera, viewport).depth < 0);
  assert.equal(globeLocation(-999, -999, camera, viewport), null);
});

test('spinning wraps longitude, limits tilt, and zoom preserves its surface anchor', () => {
  const camera = { longitude: 170, latitude: 24, zoom: 0.5 };
  const spun = rotateGlobe(camera, -5000, 5000, viewport);
  assert.ok(spun.longitude >= -180 && spun.longitude < 180);
  assert.equal(spun.latitude, 80);
  const point = { x: 210, y: 150 };
  const before = globeLocation(point.x, point.y, camera, viewport);
  const next = zoomGlobe(camera, 1.5, point.x, point.y, viewport);
  const projected = globePoint(before.longitude, before.latitude, next, viewport);
  assert.ok(Math.hypot(projected.x - point.x, projected.y - point.y) < 0.1);
});

test('country zoom stays on the same globe projection beyond the previous handoff', () => {
  const camera = { longitude: 14.5146, latitude: 35.8989, zoom: 1.5 };
  const pointer = { x: viewport.width / 2 + 20, y: viewport.height / 2 - 25 };
  const anchor = globeLocation(pointer.x, pointer.y, camera, viewport);
  for (const zoom of [2, 2.5, 3, MAX_GLOBE_ZOOM]) {
    const next = zoomGlobe(camera, zoom, pointer.x, pointer.y, viewport);
    assert.equal(next.zoom, zoom);
    const point = globePoint(anchor.longitude, anchor.latitude, next, viewport);
    assert.ok(Math.hypot(point.x - pointer.x, point.y - pointer.y) < 0.1);
  }
  assert.equal(constrainGlobe({ ...camera, zoom: 99 }).zoom, MAX_GLOBE_ZOOM);
  assert.equal(constrainGlobe({ ...camera, zoom: -99 }).zoom, 0);
});

const { spriteArt } = await loadLogic('sprite-art');
const { selectScenery, sceneryOpacity, sceneryScale, MAX_SCENERY } = await loadLogic('scenery');
const scenery = JSON.parse(
  readFileSync(new URL('../src/data/scenery.json', import.meta.url), 'utf8')
);

test('continent scenery has drawable original art, stable IDs, and appropriate native wildlife', () => {
  assert.equal(new Set(scenery.map((point) => point.id)).size, scenery.length);
  const regions = [
    'Europe',
    'Africa',
    'Asia',
    'North America',
    'South America',
    'Oceania',
    'Antarctica',
  ];
  const native = {
    deer: 'Europe',
    fox: 'Europe',
    elephant: 'Africa',
    zebra: 'Africa',
    panda: 'Asia',
    tiger: 'Asia',
    bison: 'North America',
    moose: 'North America',
    jaguar: 'South America',
    capybara: 'South America',
    kangaroo: 'Oceania',
    kiwi: 'Oceania',
    penguin: 'Antarctica',
    seal: 'Antarctica',
  };
  for (const point of scenery) {
    const art = spriteArt[point.kind];
    assert.ok(art, point.kind);
    assert.ok(regions.includes(point.continent));
    assert.ok(Math.abs(point.longitude) <= 180 && Math.abs(point.latitude) <= 90);
    if (point.animal) assert.equal(point.continent, native[point.kind]);
    if (point.continent === 'Antarctica')
      assert.ok(['penguin', 'seal', 'glacier', 'iceberg'].includes(point.kind));
  }
  for (const [name, art] of Object.entries(spriteArt)) {
    assert.equal(art.height, art.rows.length);
    for (const row of art.rows)
      for (const pixel of row) {
        if (pixel !== '.')
          assert.match(art.colors[pixel] ?? '', /^#[\da-f]{6}([\da-f]{2})?$/i, name);
      }
  }
  for (const continent of regions) {
    assert.ok(scenery.some((p) => p.continent === continent && p.animal));
    assert.ok(scenery.some((p) => p.continent === continent && !p.animal));
  }
});

test('scenery reveals gradually with zoom and bounds frame density, overlap and the far hemisphere', () => {
  assert.equal(sceneryOpacity(0), 0);
  assert.ok(sceneryOpacity(1.1) > 0 && sceneryOpacity(1.1) < 1);
  assert.equal(sceneryOpacity(1.4), 1);
  assert.ok(sceneryScale(4, { width: 1440, height: 900 }) <= 3);
  const feature = { id: 'tree', kind: 'pine', animal: false };
  const animal = { id: 'deer', kind: 'deer', animal: true };
  const points = [
    { feature, x: 120, y: 160, depth: 1 },
    { feature: animal, x: 120, y: 160, depth: 1 },
    { feature: { ...feature, id: 'hidden' }, x: 250, y: 160, depth: -1 },
    { feature: { ...feature, id: 'outside' }, x: 9999, y: 160, depth: 1 },
  ];
  assert.deepEqual(selectScenery(points, viewport, 0.5), []);
  assert.deepEqual(
    selectScenery(points, viewport, 1.5).map((p) => p.feature.id),
    ['deer']
  );
  const grid = Array.from({ length: 180 }, (_, i) => ({
    feature: { ...feature, id: String(i) },
    x: (i % 18) * 80,
    y: Math.floor(i / 18) * 80,
    depth: 1,
  }));
  assert.equal(selectScenery(grid, { width: 1440, height: 900 }, 1.5).length, MAX_SCENERY);
  assert.deepEqual(
    points.map((p) => p.feature.id),
    ['tree', 'deer', 'hidden', 'outside']
  );
});

test('all seven continent views retain local scenery and wildlife through geographic projection', () => {
  for (const [name, longitude, latitude, zoom] of [
    ['Europe', 13, 52, 1.65],
    ['Africa', 23, -5, 1.3],
    ['Asia', 105, 33, 1.3],
    ['North America', -105, 45, 1.3],
    ['South America', -63, -16, 1.3],
    ['Oceania', 145, -28, 1.2],
    ['Antarctica', 30, -77, 1.4],
  ]) {
    const camera = { longitude, latitude, zoom };
    const selected = selectScenery(
      scenery.map((feature) => ({
        feature,
        ...globePoint(feature.longitude, feature.latitude, camera, { width: 390, height: 844 }),
      })),
      { width: 390, height: 844 },
      zoom
    );
    assert.ok(selected.length > 0 && selected.length <= MAX_SCENERY, name);
    assert.ok(
      selected.some((p) => p.feature.continent === name && p.feature.animal),
      name
    );
    assert.ok(
      selected.every((p) => p.depth > 0.3),
      name
    );
  }
});
