import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { inflateSync } from 'node:zlib';
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

// Country-tier placement (build_map_icons.py: assign_appearance), checked with the app's own projection.
const PHONE = { width: 390, height: 844 };
// GlobeCanvas: one icon pixel is max(1.25, min(width, height) / CELLS_ACROSS) * 2 / 3 points.
const ICON_POINTS = (Math.max(1.25, Math.min(PHONE.width, PHONE.height) / 130) * 2) / 3;
const COUNTRY_FULL = 5.0; // COUNTRY_ZOOM.full: the first country icons are fully visible
const STRUCTURES = new Set(['church', 'house', 'oak', 'pine', 'olive', 'boat']);

/** Each frame's opaque pixels (alpha > 128) around the drawing anchor, from the RGBA sprite sheet. */
function solidBoxes() {
  const bytes = readFileSync(new URL('../assets/world/map-icons.png', import.meta.url));
  const width = bytes.readUInt32BE(16);
  const height = bytes.readUInt32BE(20);
  assert.deepEqual([bytes[24], bytes[25], bytes[28]], [8, 6, 0], '8-bit RGBA, not interlaced');
  const chunks = [];
  for (let at = 8; at < bytes.length; ) {
    const length = bytes.readUInt32BE(at);
    if (bytes.toString('latin1', at + 4, at + 8) === 'IDAT') chunks.push(bytes.subarray(at + 8, at + 8 + length));
    at += length + 12;
  }
  const raw = inflateSync(Buffer.concat(chunks));
  const stride = width * 4;
  const pixels = Buffer.alloc(stride * height);
  for (let y = 0; y < height; y++) {
    const filter = raw[y * (stride + 1)];
    for (let x = 0; x < stride; x++) {
      const value = raw[y * (stride + 1) + 1 + x];
      const left = x >= 4 ? pixels[y * stride + x - 4] : 0;
      const up = y > 0 ? pixels[(y - 1) * stride + x] : 0;
      const corner = x >= 4 && y > 0 ? pixels[(y - 1) * stride + x - 4] : 0;
      const p = left + up - corner; // PNG filters: none, sub, up, average, Paeth
      const predictor = [0, left, up, (left + up) >> 1,
        Math.abs(p - left) <= Math.abs(p - up) && Math.abs(p - left) <= Math.abs(p - corner) ? left
          : Math.abs(p - up) <= Math.abs(p - corner) ? up : corner][filter];
      pixels[y * stride + x] = (value + predictor) & 255;
    }
  }
  return icons.frames.map(([fx, fy, w, h]) => {
    let [left, top, right, bottom] = [w, h, 0, 0];
    for (let y = 0; y < h; y++)
      for (let x = 0; x < w; x++)
        if (pixels[((fy + y) * width + fx + x) * 4 + 3] > 128) {
          left = Math.min(left, x); right = Math.max(right, x + 1);
          top = Math.min(top, y); bottom = Math.max(bottom, y + 1);
        }
    return [left - w / 2, top - h + 1, right - w / 2, bottom - h + 1];
  });
}
const boxes = solidBoxes();
const country = icons.icons.filter((i) => i[5] === 1);
/** Screen rectangle (points) of an icon's opaque pixels, as MapIcons draws it. */
function screenBox(icon, camera) {
  const point = globeCamera.globePoint(icon[1], icon[2], camera, PHONE);
  const [left, top, right, bottom] = boxes[icon[0]];
  const x = Math.round(point.x + icon[3] * ICON_POINTS);
  const y = Math.round(point.y + icon[4] * ICON_POINTS);
  return [x + left * ICON_POINTS, y + top * ICON_POINTS, x + right * ICON_POINTS, y + bottom * ICON_POINTS];
}
/** Overlap in points of two icons on a camera centred between them (positive means they overlap). */
function overlap(a, b, zoom) {
  const camera = {
    longitude: a[1] + (((b[1] - a[1] + 540) % 360) - 180) / 2,
    latitude: (a[2] + b[2]) / 2,
    zoom,
  };
  const [al, at, ar, ab] = screenBox(a, camera);
  const [bl, bt, br, bb] = screenBox(b, camera);
  return Math.min(Math.min(ar, br) - Math.max(al, bl), Math.min(ab, bb) - Math.max(at, bt));
}
const near = (a, b) =>
  Math.abs(a[2] - b[2]) < 3 && Math.abs(((b[1] - a[1] + 540) % 360) - 180) * Math.cos((a[2] * Math.PI) / 180) < 3;

test('country icons appear in 0.2 zoom steps between full country zoom and 6.2, nudged at most 40 icon pixels', () => {
  assert.ok(country.length > 500 && country.length < 700, `${country.length} country icons`);
  for (const [frame, lon, lat, dx, dy, , appear] of country) {
    assert.ok(appear >= COUNTRY_FULL && appear <= 6.2, `${icons.names[frame]} at ${lon},${lat}: ${appear}`);
    assert.ok(Math.abs(appear * 5 - Math.round(appear * 5)) < 1e-9, `${appear} is on the 0.2 grid`);
    assert.ok(Math.hypot(dx, dy) <= 40, `${icons.names[frame]} at ${lon},${lat} drawn ${dx},${dy} away`);
  }
  // Most of each country is there as soon as the tier is fully in.
  assert.ok(country.filter((i) => i[6] === COUNTRY_FULL).length > country.length * 0.6);
});

test('no two country icons overlap once both are fully visible, up to the deepest country zoom', () => {
  for (const [index, a] of country.entries()) {
    for (const b of country.slice(index + 1)) {
      if (!near(a, b)) continue;
      for (const zoom of [Math.max(a[6], b[6]), 6.4]) {
        const amount = overlap(a, b, zoom);
        assert.ok(amount <= 1, `${icons.names[a[0]]} ${a[1]},${a[2]} and ${icons.names[b[0]]} ${b[1]},${b[2]} overlap ${amount.toFixed(1)} pt at ${zoom}`);
      }
    }
  }
});

test('country icons clear the continent icons that stay; covered continent icons make way', () => {
  const continent = icons.icons.filter((i) => i[5] === 0);
  const yielding = continent.filter((i) => i[6] === 1);
  assert.ok(yielding.length > 0 && yielding.length < 30, `${yielding.length} continent icons make way`);
  for (const a of country) {
    for (const b of continent) {
      if (b[6] === 1 || !near(a, b)) continue;
      const amount = overlap(a, b, a[6]);
      assert.ok(amount <= 1, `${icons.names[a[0]]} ${a[1]},${a[2]} covers ${icons.names[b[0]]} ${b[1]},${b[2]} by ${amount.toFixed(1)} pt`);
    }
  }
  // Each one that makes way really sat on a capital or landmark at full country zoom.
  for (const b of yielding) {
    assert.ok(country.some((a) => !STRUCTURES.has(icons.names[a[0]]) && near(a, b) && overlap(a, b, COUNTRY_FULL) > -2),
      `${icons.names[b[0]]} at ${b[1]},${b[2]}`);
  }
});

test('every capital and landmark is drawn; only towns and decoration are omitted, and only for lack of room', () => {
  assert.ok(icons.omitted.length < 80, `${icons.omitted.length} omitted`);
  for (const icon of icons.omitted) {
    const kind = icons.names[icon[0]];
    assert.ok(STRUCTURES.has(kind), `${kind} at ${icon[1]},${icon[2]} must be drawn`);
    // At the last appearance step it would still touch a drawn icon (or a continent icon that stays).
    const blockers = icons.icons.filter((other) => (other[5] === 1 || other[6] !== 1) && near(icon, other));
    assert.ok(blockers.some((other) => overlap(icon, other, 6.2) > -2 * ICON_POINTS),
      `${kind} at ${icon[1]},${icon[2]} would fit by zoom 6.2`);
  }
  const drawn = new Set(country.map((i) => icons.names[i[0]]));
  for (const kind of icons.names.filter((name) => !STRUCTURES.has(name) && name !== 'castle'))
    if (country.some((i) => icons.names[i[0]] === kind) || icons.omitted.some((i) => icons.names[i[0]] === kind))
      assert.ok(drawn.has(kind), kind);
  assert.equal(country.filter((i) => icons.names[i[0]] === 'castle').length, 44, 'one castle per capital');
});
