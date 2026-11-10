import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import ts from 'typescript';

// Transpile a module and point its './globe-camera' import at an already-loaded data URL.
function transpile(filename, imports = {}) {
  let source = readFileSync(new URL(`../src/features/world/${filename}.ts`, import.meta.url), 'utf8');
  for (const [specifier, url] of Object.entries(imports)) source = source.replaceAll(`'${specifier}'`, `'${url}'`);
  const { outputText } = ts.transpileModule(source, {
    compilerOptions: { module: ts.ModuleKind.ES2022, target: ts.ScriptTarget.ES2022 },
  });
  return `data:text/javascript;base64,${Buffer.from(outputText).toString('base64')}`;
}
const cameraUrl = transpile('globe-camera');
const camera = await import(cameraUrl);
const capitals = await import(transpile('capitals', { './globe-camera': cameraUrl }));
const scenes = JSON.parse(readFileSync(new URL('../src/data/capitals.json', import.meta.url), 'utf8'));
const icons = JSON.parse(readFileSync(new URL('../src/data/map-icons.json', import.meta.url), 'utf8'));
const { maxZoomAt, constrainGlobe, zoomGlobe, globePoint, COVERAGE, COUNTRY_ZOOM, CAPITAL_ZOOM, MAX_GLOBE_ZOOM } = camera;
const view = { width: 390, height: 844 };
const lisbon = scenes.find((s) => s.id === 'lisbon');

test('detail allows deeper zoom only where it exists', () => {
  assert.equal(maxZoomAt(-9.14, 38.71), CAPITAL_ZOOM.full); // Lisbon
  assert.equal(maxZoomAt(-8.62, 41.15), COUNTRY_ZOOM.max); // Porto: Portugal, not the capital
  assert.equal(maxZoomAt(-3.7, 40.4), MAX_GLOBE_ZOOM); // Madrid
  assert.equal(maxZoomAt(14.5, 35.9), MAX_GLOBE_ZOOM); // Malta
  assert.equal(constrainGlobe({ longitude: 20, latitude: 0, zoom: 7 }).zoom, MAX_GLOBE_ZOOM);
});

test('panning at country or capital zoom stops at the covered area instead of zooming out', () => {
  const panned = constrainGlobe({ longitude: -5.5, latitude: 40, zoom: 6 });
  assert.equal(panned.zoom, 6);
  assert.equal(panned.longitude, -6.0);
  const capital = constrainGlobe({ longitude: -7.0, latitude: 38.71, zoom: CAPITAL_ZOOM.full });
  assert.equal(capital.zoom, CAPITAL_ZOOM.full);
  assert.ok(Math.abs(capital.longitude - (-9.1365 + camera.CAPITAL_REACH)) < 1e-9);
});

test('pinching on Lisbon from elsewhere in the view reaches the capital', () => {
  let current = { longitude: -8.0, latitude: 39.6, zoom: 5.4 };
  const lisbonOnScreen = globePoint(-9.1365, 38.71, current, view);
  for (let step = 0; step < 8; step++)
    current = zoomGlobe(current, current.zoom + 0.5, lisbonOnScreen.x, lisbonOnScreen.y, view);
  assert.equal(current.zoom, CAPITAL_ZOOM.full);
  const after = globePoint(-9.1365, 38.71, current, view);
  assert.ok(Math.hypot(after.x - lisbonOnScreen.x, after.y - lisbonOnScreen.y) < 1, 'Lisbon stays under the fingers');
});

test('the capital scene keeps the screen covered while panning', () => {
  const scale = 2;
  let current = { longitude: -9.1365, latitude: 38.71, zoom: CAPITAL_ZOOM.full };
  for (const [dx, dy] of [[3000, 0], [-6000, 0], [0, 3000], [0, -6000], [2500, 2500]]) {
    // A drag arrives as many small moves.
    const steps = Math.max(Math.abs(dx), Math.abs(dy)) / 50;
    for (let k = 0; k < steps; k++)
      current = capitals.clampToCapital(camera.rotateGlobe(current, dx / steps, dy / steps, view), lisbon, view, scale);
    assert.equal(current.zoom, CAPITAL_ZOOM.full);
    const rect = capitals.capitalRect(lisbon, current, view, scale);
    assert.ok(rect.x <= 0.5 && rect.y <= 0.5, `${dx},${dy}: ${JSON.stringify(rect)}`);
    assert.ok(rect.x + rect.width >= view.width - 0.5 && rect.y + rect.height >= view.height - 0.5);
  }
  assert.equal(capitals.capitalScale(CAPITAL_ZOOM.full, 2), 2, 'whole icon pixels at full zoom');
  assert.equal(capitals.capitalOpacity(CAPITAL_ZOOM.in), 0);
  assert.equal(capitals.capitalOpacity(CAPITAL_ZOOM.full), 1);
});

test('capital scenes, camera coverage and country-tier icons agree', () => {
  for (const region of COVERAGE) {
    const scene = scenes.find((s) => s.id === region.id);
    assert.ok(scene, region.id);
    assert.ok(Math.abs(scene.longitude - region.longitude) < 1e-9 && Math.abs(scene.latitude - region.latitude) < 1e-9);
    const [w, s, e, n] = region.bounds;
    assert.ok(w <= scene.longitude && scene.longitude <= e && s <= scene.latitude && scene.latitude <= n);
  }
  const countryTier = icons.icons.filter((i) => i[5] === 1);
  assert.ok(countryTier.length >= 10);
  assert.ok(countryTier.some((i) => icons.names[i[0]] === 'castle'), 'the capital is marked');
  for (const [, lon, lat] of countryTier) {
    assert.ok(COVERAGE.some(({ bounds: [w, s, e, n] }) => lon >= w && lon <= e && lat >= s && lat <= n));
  }
});
