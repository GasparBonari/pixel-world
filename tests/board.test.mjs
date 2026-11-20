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

const globeCamera = await loadLogic('globe-camera');
const { cameraFromParams, OPENING_CAMERA, MAX_GLOBE_ZOOM } = globeCamera;
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
  const clamped = cameraFromParams({ lon: '210', lat: '95', zoom: '99' });
  assert.equal(clamped.longitude, -150);
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
  assert.equal(icons.names.length, icons.frames.length);
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

// Rough continent boxes [west, south, east, north], enough to tell continents apart.
const CONTINENTS = {
  Europe: [-25, 35, 45, 72],
  Africa: [-20, -36, 52, 37],
  Asia: [60, 0, 180, 78],
  'North America': [-170, 15, -50, 75],
  'South America': [-82, -56, -34, 13],
  Oceania: [110, -48, 180, 0],
  Antarctica: [-180, -90, 180, -60],
};
const NATIVE = {
  deer: 'Europe', fox: 'Europe', elephant: 'Africa', zebra: 'Africa', panda: 'Asia',
  tiger: 'Asia', bison: 'North America', moose: 'North America', jaguar: 'South America',
  capybara: 'South America', kangaroo: 'Oceania', kiwi: 'Oceania', penguin: 'Antarctica',
  seal: 'Antarctica', 'brown-bear': 'Europe', 'wild-boar': 'Europe', lion: 'Africa',
  giraffe: 'Africa', rhinoceros: 'Africa', camel: 'Asia', orangutan: 'Asia', 'snow-leopard': 'Asia',
  wolf: 'North America', alligator: 'North America', guanaco: 'South America',
  toucan: 'South America', koala: 'Oceania', emu: 'Oceania', orca: 'Antarctica',
};
const inside = ([, lon, lat], [w, s, e, n]) => lon >= w && lon <= e && lat >= s && lat <= n;
const kindOf = ([frame]) => icons.names[frame];

test('animals appear only on their native continent, and every continent has its own animals', () => {
  for (const icon of icons.icons) {
    const continent = NATIVE[kindOf(icon)];
    if (continent) assert.ok(inside(icon, CONTINENTS[continent]), `${kindOf(icon)} at ${icon[1]},${icon[2]}`);
  }
  for (const continent of Object.keys(CONTINENTS)) {
    const animals = icons.icons.filter((i) => NATIVE[kindOf(i)] === continent);
    assert.ok(animals.length >= 8, continent);
    assert.ok(new Set(animals.map(kindOf)).size >= 3, `${continent} has at least three species`);
  }
});

test('each continent has its own flora rather than one shared set', () => {
  const flora = (continent) =>
    new Set(
      icons.icons
        .filter((i) => inside(i, CONTINENTS[continent]) && !NATIVE[kindOf(i)])
        .map(kindOf)
        .filter((k) => !['mountain', 'hill'].includes(k))
    );
  assert.ok(flora('Africa').has('acacia') && flora('Africa').has('baobab'));
  assert.ok(flora('Asia').has('bamboo'));
  assert.ok(flora('North America').has('cactus'));
  assert.ok(flora('Oceania').has('eucalyptus') && flora('Oceania').has('red-rock'));
  assert.ok(flora('Europe').has('olive') && flora('Europe').has('oak'));
  assert.ok(flora('Antarctica').has('iceberg') && !flora('Antarctica').has('palm'));
  assert.ok(!flora('Europe').has('acacia') && !flora('Africa').has('bamboo'));
});

test('every continent view at board zoom shows local animals and plants on the near side', () => {
  const { globePoint } = globeCamera;
  const view = { width: 390, height: 844 };
  for (const [continent, longitude, latitude] of [
    ['Europe', 10, 48], ['Africa', 28, -5], ['Asia', 100, 32], ['North America', -100, 45],
    ['South America', -62, -15], ['Oceania', 140, -30], ['Antarctica', 30, -72],
  ]) {
    const camera = { longitude, latitude, zoom: 2.4 };
    const visible = icons.icons.filter(([, lon, lat]) => {
      const p = globePoint(lon, lat, camera, view);
      return p.depth > 0.15 && p.x >= 0 && p.x <= view.width && p.y >= 0 && p.y <= view.height;
    });
    const species = new Set(visible.filter((i) => NATIVE[kindOf(i)] === continent).map(kindOf));
    assert.ok(species.size >= 2, `${continent} shows several species: ${[...species]}`);
    assert.ok(visible.some((i) => !NATIVE[kindOf(i)] && kindOf(i) !== 'mountain'), `${continent} plants`);
  }
});
