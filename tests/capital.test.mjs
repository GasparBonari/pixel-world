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
  assert.equal(maxZoomAt(12.5, 41.9), MAX_GLOBE_ZOOM); // Rome: no detail yet
  assert.equal(maxZoomAt(2.35, 48.86), CAPITAL_ZOOM.full); // Paris
  assert.equal(maxZoomAt(14.5, 35.9), MAX_GLOBE_ZOOM); // Malta
  assert.equal(constrainGlobe({ longitude: 20, latitude: 0, zoom: 7 }).zoom, MAX_GLOBE_ZOOM);
});

test('panning at country or capital zoom stops at the covered area instead of zooming out', () => {
  const panned = constrainGlobe({ longitude: -11.5, latitude: 40, zoom: 6 }); // out in the Atlantic
  assert.equal(panned.zoom, 6);
  assert.equal(panned.longitude, -10.0);
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

test('every country with a capital scene has coverage, an image, and an index entry', () => {
  const index = readFileSync(new URL('../src/data/capital-images.ts', import.meta.url), 'utf8');
  assert.deepEqual(scenes.map((s) => s.id).sort(), COVERAGE.map((c) => c.id).sort());
  for (const scene of scenes) {
    assert.match(index, new RegExp(`${scene.id}: require\\('@/assets/world/capitals/${scene.id}\\.png'\\)`));
    const png = readFileSync(new URL(`../assets/world/capitals/${scene.id}.png`, import.meta.url));
    assert.deepEqual([png.readUInt32BE(16), png.readUInt32BE(20)], [scene.width, scene.height]);
  }
});

test('Madrid: Spain allows country zoom, Madrid capital zoom, and panning clamps to Madrid', () => {
  assert.equal(maxZoomAt(-3.70, 40.42), CAPITAL_ZOOM.full);
  assert.equal(maxZoomAt(2.17, 41.39), COUNTRY_ZOOM.max); // Barcelona
  const madrid = scenes.find((s) => s.id === 'madrid');
  let current = { longitude: -3.7038, latitude: 40.4168, zoom: CAPITAL_ZOOM.full };
  for (let k = 0; k < 80; k++)
    current = capitals.clampToCapitals(camera.rotateGlobe(current, 50, 40, view), scenes, view, 2);
  const rect = capitals.capitalRect(madrid, current, view, 2);
  assert.ok(rect.x <= 0.5 && rect.y <= 0.5 && rect.x + rect.width >= view.width - 0.5);
  assert.ok(Math.abs(current.longitude - madrid.longitude) < 2, 'stays at Madrid, not Lisbon');
});

test("Spain's country tier marks Madrid and the La Mancha windmills, and stays in Spain", () => {
  const tier = icons.icons.filter((i) => i[5] === 1);
  const near = (lon, lat, kind) =>
    tier.some((i) => icons.names[i[0]] === kind && Math.abs(i[1] - lon) < 0.2 && Math.abs(i[2] - lat) < 0.2);
  assert.ok(near(-3.685, 40.402, 'castle'), 'Madrid');
  assert.ok(near(-3.6085, 39.4566, 'windmill') && near(-3.1235, 39.4049, 'windmill'));
  assert.ok(near(-9.147, 38.725, 'castle'), 'Lisbon still marked');
});

test("France's country tier marks Paris, Mont-Saint-Michel and Saint-Émilion", () => {
  const tier = icons.icons.filter((i) => i[5] === 1);
  const near = (lon, lat, kind) =>
    tier.some((i) => icons.names[i[0]] === kind && Math.abs(i[1] - lon) < 0.2 && Math.abs(i[2] - lat) < 0.2);
  assert.ok(near(2.331, 48.869, 'castle'), 'Paris');
  assert.ok(near(-1.5115, 48.6361, 'mont-saint-michel') && near(-0.155, 44.894, 'vineyard'));
});

test("Germany's country tier marks Berlin, spaced cities and Neuschwanstein within its own bounds", () => {
  const germany = COVERAGE.find((c) => c.id === 'berlin');
  assert.ok(germany);
  assert.deepEqual(germany.bounds, [5.8, 47.2, 15.1, 55.1]);
  const tier = icons.icons.filter((i) => i[5] === 1);
  const at = (lon, lat) => tier.filter((i) => Math.abs(i[1] - lon) < 0.001 && Math.abs(i[2] - lat) < 0.001);
  // Pinned Natural Earth populated-place coordinate, rather than the capital illustration anchor.
  const berlin = at(13.3996, 52.5238);
  assert.equal(berlin.filter((i) => icons.names[i[0]] === 'castle').length, 1);
  assert.equal(berlin.filter((i) => icons.names[i[0]] === 'house').length, 2);
  const landmark = at(10.7492, 47.5576).find((i) => icons.names[i[0]] === 'neuschwanstein');
  assert.ok(landmark, 'Neuschwanstein at Hohenschwangau');
  const cities = [
    [13.3996, 52.5238], [9.2, 48.78], [8.675, 50.1], [9.9981, 53.552],
    [7.0166, 51.45], [11.573, 48.1319], [6.97, 49.2504], [11.08, 49.45], [8.8, 53.08],
  ];
  const [w, s, e, n] = germany.bounds;
  for (const [rank, [lon, lat]] of cities.entries()) {
    const kinds = at(lon, lat).map((i) => icons.names[i[0]]).sort();
    assert.deepEqual(kinds, rank === 0 ? ['castle', 'house', 'house'] : rank <= 2
      ? ['church', 'house', 'house'] : rank % 2 ? ['church'] : ['house', 'house']);
    assert.ok(w <= lon && lon <= e && s <= lat && lat <= n);
    for (const [otherLon, otherLat] of cities.slice(0, rank)) {
      const rad = Math.PI / 180;
      const km = 6371 * Math.acos(Math.sin(lat * rad) * Math.sin(otherLat * rad)
        + Math.cos(lat * rad) * Math.cos(otherLat * rad) * Math.cos((lon - otherLon) * rad));
      assert.ok(km >= 75, `${lon},${lat} and ${otherLon},${otherLat}: ${km} km`);
    }
  }
  assert.ok(w <= landmark[1] && landmark[1] <= e && s <= landmark[2] && landmark[2] <= n);
});

test('Berlin: country zoom, capital arrival and panning stay with the Berlin scene', () => {
  assert.equal(maxZoomAt(13.405, 52.52), CAPITAL_ZOOM.full);
  assert.equal(maxZoomAt(9.99, 53.55), COUNTRY_ZOOM.max); // Hamburg
  assert.equal(maxZoomAt(11.58, 48.14), COUNTRY_ZOOM.max); // Munich
  assert.equal(maxZoomAt(12.5, 41.9), MAX_GLOBE_ZOOM); // Rome remains uncovered
  const berlin = scenes.find((s) => s.id === 'berlin');
  assert.deepEqual([berlin.width, berlin.height], [720, 520]);
  let arriving = { longitude: 12.7, latitude: 52.3, zoom: 5 };
  const focal = globePoint(berlin.longitude, berlin.latitude, arriving, view);
  for (let step = 0; step < 8; step++)
    arriving = zoomGlobe(arriving, arriving.zoom + 0.3, focal.x, focal.y, view);
  assert.equal(arriving.zoom, CAPITAL_ZOOM.full);
  const after = globePoint(berlin.longitude, berlin.latitude, arriving, view);
  assert.ok(Math.hypot(after.x - focal.x, after.y - focal.y) < 1);
});

test('every capital keeps portrait and landscape viewports covered after long drags', () => {
  for (const scene of scenes) {
    for (const viewport of [view, { width: 844, height: 390 }]) {
      let current = { longitude: scene.longitude, latitude: scene.latitude, zoom: CAPITAL_ZOOM.full };
      for (const [dx, dy] of [[50, 0], [-50, 0], [0, 50], [0, -50]]) {
        for (let step = 0; step < 100; step++)
          current = capitals.clampToCapitals(camera.rotateGlobe(current, dx, dy, viewport), scenes, viewport, 2);
        const rect = capitals.capitalRect(scene, current, viewport, 2);
        assert.ok(rect.x <= .5 && rect.y <= .5 && rect.x + rect.width >= viewport.width - .5
          && rect.y + rect.height >= viewport.height - .5, JSON.stringify(rect));
        assert.equal(current.zoom, CAPITAL_ZOOM.full);
        assert.equal(current.capitalId, scene.id, 'a long drag cannot change the visited capital');
        assert.ok(Math.abs(current.longitude - scene.longitude) < 2, 'stays at the visited capital');
      }
    }
  }
});

test("Netherlands marks Amsterdam before nearby larger metros, spaced towns and Kinderdijk", () => {
  const netherlands = COVERAGE.find((c) => c.id === 'amsterdam');
  assert.ok(netherlands);
  assert.deepEqual(netherlands.bounds, [3.2, 50.7, 7.3, 53.6]);
  const tier = icons.icons.filter((i) => i[5] === 1);
  const at = (lon, lat) => tier.filter((i) => Math.abs(i[1] - lon) < .001 && Math.abs(i[2] - lat) < .001);
  // Natural Earth ranks The Hague above Amsterdam. It must not displace the capital at 75 km spacing.
  const cities = [[4.9147, 52.3519], [5.5, 51.43], [6.58, 53.2204], [6.097, 52.524], [3.61, 51.502]];
  const [w, s, e, n] = netherlands.bounds;
  for (const [rank, [lon, lat]] of cities.entries()) {
    const kinds = at(lon, lat).map((i) => icons.names[i[0]]).sort();
    assert.deepEqual(kinds, rank === 0 ? ['castle', 'house', 'house'] : rank <= 2
      ? ['church', 'house', 'house'] : rank % 2 ? ['church'] : ['house', 'house']);
    assert.ok(w <= lon && lon <= e && s <= lat && lat <= n);
    for (const [otherLon, otherLat] of cities.slice(0, rank)) {
      const rad = Math.PI / 180;
      const km = 6371 * Math.acos(Math.sin(lat * rad) * Math.sin(otherLat * rad)
        + Math.cos(lat * rad) * Math.cos(otherLat * rad) * Math.cos((lon - otherLon) * rad));
      assert.ok(km >= 75, `${lon},${lat} and ${otherLon},${otherLat}: ${km} km`);
    }
  }
  assert.equal(at(4.27, 52.08).length, 0, 'The Hague respects capital spacing');
  assert.equal(at(4.64, 51.8833).filter((i) => icons.names[i[0]] === 'kinderdijk').length, 1);
  const landmark = at(4.64, 51.8833)[0];
  assert.ok(w <= landmark[1] && landmark[1] <= e && s <= landmark[2] && landmark[2] <= n);
});

test('Amsterdam: focal zoom arrives at its own scene while Groningen keeps country detail', () => {
  const amsterdam = scenes.find((s) => s.id === 'amsterdam');
  assert.deepEqual([amsterdam.width, amsterdam.height], [720, 520]);
  assert.equal(maxZoomAt(4.8952, 52.3702), CAPITAL_ZOOM.full);
  assert.equal(maxZoomAt(6.58, 53.22), COUNTRY_ZOOM.max); // Groningen, outside capital reach
  assert.equal(maxZoomAt(12.5, 41.9), MAX_GLOBE_ZOOM); // Rome remains uncovered
  let arriving = { longitude: 5.3, latitude: 52.1, zoom: 5 };
  const focal = globePoint(amsterdam.longitude, amsterdam.latitude, arriving, view);
  for (let step = 0; step < 8; step++)
    arriving = zoomGlobe(arriving, arriving.zoom + .3, focal.x, focal.y, view);
  assert.equal(arriving.zoom, CAPITAL_ZOOM.full);
  const after = globePoint(amsterdam.longitude, amsterdam.latitude, arriving, view);
  assert.ok(Math.hypot(after.x - focal.x, after.y - focal.y) < 1);
});

test("Belgium marks Brussels, spaced cities and Gravensteen within its own bounds", () => {
  const belgium = COVERAGE.find((c) => c.id === 'brussels');
  assert.deepEqual(belgium.bounds, [2.5, 49.45, 6.4, 51.6]);
  const tier = icons.icons.filter((i) => i[5] === 1);
  const at = (lon, lat) => tier.filter((i) => Math.abs(i[1] - lon) < .001 && Math.abs(i[2] - lat) < .001);
  // The nearby Antwerp/Ghent metropolitan populations cannot override Brussels or the 75 km rule.
  const cities = [[4.3314, 50.8353], [5.58, 50.63], [3.23, 51.2204], [5.8167, 49.6833]];
  const [w, s, e, n] = belgium.bounds;
  for (const [rank, [lon, lat]] of cities.entries()) {
    const kinds = at(lon, lat).map((i) => icons.names[i[0]]).sort();
    assert.deepEqual(kinds, rank === 0 ? ['castle', 'house', 'house'] : rank <= 2
      ? ['church', 'house', 'house'] : ['church']);
    assert.ok(w <= lon && lon <= e && s <= lat && lat <= n);
    for (const [otherLon, otherLat] of cities.slice(0, rank)) {
      const rad = Math.PI / 180;
      const km = 6371 * Math.acos(Math.sin(lat * rad) * Math.sin(otherLat * rad)
        + Math.cos(lat * rad) * Math.cos(otherLat * rad) * Math.cos((lon - otherLon) * rad));
      assert.ok(km >= 75, `${lon},${lat} and ${otherLon},${otherLat}: ${km} km`);
    }
  }
  assert.equal(at(4.4131, 51.2223).length, 0, 'Antwerp respects capital spacing');
  assert.equal(at(3.7, 51.03).length, 0, 'Ghent respects capital spacing');
  const landmark = at(3.7206, 51.0572).find((i) => icons.names[i[0]] === 'gravensteen');
  assert.ok(landmark, 'Gravensteen at its real site, separate from the excluded Ghent city group');
  assert.ok(w <= landmark[1] && landmark[1] <= e && s <= landmark[2] && landmark[2] <= n);
});

test('Brussels: focal zoom arrives at its scene, and Eupen keeps country detail', () => {
  const brussels = scenes.find((s) => s.id === 'brussels');
  assert.deepEqual([brussels.width, brussels.height], [720, 520]);
  assert.equal(maxZoomAt(4.3517, 50.8503), CAPITAL_ZOOM.full);
  assert.equal(maxZoomAt(6.03, 50.63), COUNTRY_ZOOM.max); // Eupen, beyond capital reach
  assert.equal(maxZoomAt(12.5, 41.9), MAX_GLOBE_ZOOM); // Rome remains uncovered
  let arriving = { longitude: 4.8, latitude: 50.6, zoom: 5 };
  const focal = globePoint(brussels.longitude, brussels.latitude, arriving, view);
  for (let step = 0; step < 8; step++)
    arriving = zoomGlobe(arriving, arriving.zoom + .3, focal.x, focal.y, view);
  assert.equal(arriving.zoom, CAPITAL_ZOOM.full);
  assert.equal(arriving.capitalId, 'brussels');
  const after = globePoint(brussels.longitude, brussels.latitude, arriving, view);
  assert.ok(Math.hypot(after.x - focal.x, after.y - focal.y) < 1);
});

test('United Kingdom marks London, nine spaced cities and Stonehenge within its bounds', () => {
  const uk = COVERAGE.find((c) => c.id === 'london');
  assert.deepEqual(uk.bounds, [-8.3, 49.8, 2.0, 60.9]);
  const tier = icons.icons.filter((i) => i[5] === 1);
  const at = (lon, lat) => tier.filter((i) => Math.abs(i[1] - lon) < .001 && Math.abs(i[2] - lat) < .001);
  // Pinned Natural Earth coordinates, in capital-first population order.
  const cities = [[-.1187, 51.5019], [-1.9219, 52.4769], [-2.2499, 53.5024],
    [-4.2527, 55.8764], [-1.6019, 55.0023], [-3.225, 51.5], [-5.96, 54.6],
    [-1.08, 50.8003], [-.33, 53.7504]];
  const [w, s, e, n] = uk.bounds;
  for (const [rank, [lon, lat]] of cities.entries()) {
    const kinds = at(lon, lat).map((i) => icons.names[i[0]]).sort();
    assert.deepEqual(kinds, rank === 0 ? ['castle', 'house', 'house'] : rank <= 2
      ? ['church', 'house', 'house'] : rank % 2 ? ['church'] : ['house', 'house']);
    assert.ok(w <= lon && lon <= e && s <= lat && lat <= n);
    for (const [otherLon, otherLat] of cities.slice(0, rank)) {
      const rad = Math.PI / 180;
      const km = 6371 * Math.acos(Math.sin(lat * rad) * Math.sin(otherLat * rad)
        + Math.cos(lat * rad) * Math.cos(otherLat * rad) * Math.cos((lon - otherLon) * rad));
      assert.ok(km >= 75, `${lon},${lat} and ${otherLon},${otherLat}: ${km} km`);
    }
  }
  const landmark = at(-1.8262, 51.1789).find((i) => icons.names[i[0]] === 'stonehenge');
  assert.ok(landmark, 'Stonehenge at its real Salisbury Plain site');
  assert.ok(w <= landmark[1] && landmark[1] <= e && s <= landmark[2] && landmark[2] <= n);
});

test('London: focal zoom reaches its scene while Scotland and Northern Ireland keep country detail', () => {
  const london = scenes.find((s) => s.id === 'london');
  assert.equal(london.country, 'United Kingdom');
  assert.deepEqual([london.width, london.height], [720, 520]);
  assert.equal(maxZoomAt(-.1276, 51.5072), CAPITAL_ZOOM.full);
  assert.equal(maxZoomAt(-4.2527, 55.8764), COUNTRY_ZOOM.max); // Glasgow
  assert.equal(maxZoomAt(-7.3086, 54.9975), COUNTRY_ZOOM.max); // Derry, outside Dublin's capital reach
  assert.equal(maxZoomAt(12.5, 41.9), MAX_GLOBE_ZOOM); // Rome stays uncovered
  let arriving = { longitude: -.6, latitude: 51.8, zoom: 5 };
  const focal = globePoint(london.longitude, london.latitude, arriving, view);
  for (let step = 0; step < 8; step++)
    arriving = zoomGlobe(arriving, arriving.zoom + .3, focal.x, focal.y, view);
  assert.equal(arriving.zoom, CAPITAL_ZOOM.full);
  assert.equal(arriving.capitalId, 'london');
  const after = globePoint(london.longitude, london.latitude, arriving, view);
  assert.ok(Math.hypot(after.x - focal.x, after.y - focal.y) < 1);
});

test('overlapping Brussels/Amsterdam visits keep one capital until zooming back to the country', () => {
  for (const id of ['brussels', 'amsterdam']) {
    const scene = scenes.find((s) => s.id === id);
    let current = constrainGlobe({ longitude: scene.longitude, latitude: scene.latitude, zoom: CAPITAL_ZOOM.full });
    current = constrainGlobe({ ...current, longitude: 4.6, latitude: 51.6 }); // both capital areas
    assert.equal(camera.activeCapital(current).id, id, 'the visible scene and the clamp use the same visit');
    current = capitals.clampToCapitals(current, scenes, view, 2);
    assert.equal(current.capitalId, id);
    const other = scenes.find((s) => s.id === (id === 'brussels' ? 'amsterdam' : 'brussels'));
    const pulled = constrainGlobe({ ...current, longitude: other.longitude, latitude: other.latitude });
    assert.ok(Math.abs(pulled.longitude - scene.longitude) <= camera.CAPITAL_REACH);
    assert.ok(Math.abs(pulled.latitude - scene.latitude) <= camera.CAPITAL_REACH);
    const country = zoomGlobe(current, 5, view.width / 2, view.height / 2, view);
    assert.equal(country.capitalId, undefined);
    assert.equal(camera.activeCapital(country), undefined);
    const nextVisit = constrainGlobe({ ...country, longitude: other.longitude, latitude: other.latitude, zoom: 7 });
    assert.equal(camera.activeCapital(nextVisit).id, other.id);
  }
});

test('Ireland marks Dublin first, spaced cities and the Rock of Cashel within its bounds', () => {
  const ireland = COVERAGE.find((c) => c.id === 'dublin');
  assert.deepEqual(ireland.bounds, [-10.8, 51.35, -5.9, 55.5]);
  const tier = icons.icons.filter((i) => i[5] === 1);
  const at = (lon, lat) => tier.filter((i) => Math.abs(i[1] - lon) < .001 && Math.abs(i[2] - lat) < .001);
  // Pinned Natural Earth coordinates, in capital-first population order.
  const cities = [[-6.2509, 53.335], [-8.4958, 51.8986], [-8.623, 52.6647],
    [-7.1119, 52.2583], [-9.7167, 52.2667], [-8.4833, 54.2671], [-6.9667, 54.25]];
  const decorations = [[-7.8902, 52.52], [-7.875, 54.625], [-9.625, 54.125], [-6.375, 53.875],
    [-8.375, 53.375], [-6.625, 52.625], [-10.375, 52.125], [-9.375, 51.875],
    [-10.125, 53.125], [-6.125, 52.625]];
  const [w, s, e, n] = ireland.bounds;
  for (const [rank, [lon, lat]] of cities.entries()) {
    const kinds = at(lon, lat).map((i) => icons.names[i[0]]).sort();
    assert.deepEqual(kinds, rank === 0 ? ['castle', 'house', 'house'] : rank <= 2
      ? ['church', 'house', 'house'] : rank % 2 ? ['church'] : ['house', 'house']);
    for (const [otherLon, otherLat] of cities.slice(0, rank)) {
      const rad = Math.PI / 180;
      const km = 6371 * Math.acos(Math.sin(lat * rad) * Math.sin(otherLat * rad)
        + Math.cos(lat * rad) * Math.cos(otherLat * rad) * Math.cos((lon - otherLon) * rad));
      assert.ok(km >= 75, `${lon},${lat} and ${otherLon},${otherLat}: ${km} km`);
    }
  }
  const all = [...cities, ...decorations].flatMap(([lon, lat]) => at(lon, lat));
  assert.equal(all.length, 25);
  for (const [, lon, lat] of all) assert.ok(w <= lon && lon <= e && s <= lat && lat <= n);
  assert.equal(at(-7.8902, 52.52).filter((i) => icons.names[i[0]] === 'rock-of-cashel').length, 1);
  assert.equal(at(-9.0488, 53.2724).length, 0, 'Galway respects the spacing from Limerick');
  assert.equal(at(-6.3478, 53.7193).length, 0, 'Drogheda respects the spacing from Dublin');
});

test('Dublin: focal zoom arrives at its scene while Cork retains country detail', () => {
  const dublin = scenes.find((s) => s.id === 'dublin');
  assert.deepEqual([dublin.width, dublin.height], [720, 520]);
  assert.equal(maxZoomAt(-6.2603, 53.3498), CAPITAL_ZOOM.full);
  assert.equal(maxZoomAt(-8.4958, 51.8986), COUNTRY_ZOOM.max);
  assert.equal(maxZoomAt(12.5, 41.9), MAX_GLOBE_ZOOM); // Rome remains uncovered.
  let arriving = { longitude: -6.7, latitude: 53.1, zoom: 5 };
  const focal = globePoint(dublin.longitude, dublin.latitude, arriving, view);
  for (let step = 0; step < 8; step++)
    arriving = zoomGlobe(arriving, arriving.zoom + .3, focal.x, focal.y, view);
  assert.equal(arriving.zoom, CAPITAL_ZOOM.full);
  assert.equal(arriving.capitalId, 'dublin');
  const after = globePoint(dublin.longitude, dublin.latitude, arriving, view);
  assert.ok(Math.hypot(after.x - focal.x, after.y - focal.y) < 1);
});
