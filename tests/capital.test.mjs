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

test('Estonia marks Tallinn, five spaced cities and Kuressaare within its bounds', () => {
  const region = COVERAGE.find((c) => c.id === 'tallinn');
  assert.deepEqual(region.bounds, [21.7, 57.45, 28.25, 59.85]);
  const tier = icons.icons.filter((i) => i[5] === 1);
  const at = (lon, lat) => tier.filter((i) => Math.abs(i[1]-lon) < .0001 && Math.abs(i[2]-lat) < .0001);
  // Pinned Natural Earth coordinates and population order, after the 75 km filter.
  const cities = [[24.728, 59.4339], [26.7099, 58.3839], [28.1603, 59.3776],
    [24.5136, 58.3747], [23.5414, 58.9431]];
  const sites = [...cities, [22.4792, 58.247], [26.875, 59.375], [22.625, 59.125],
    [25.625, 59.125], [25.375, 58.375], [24.375, 57.875], [26.375, 57.875],
    [27.875, 57.875], [27.125, 59.625], [22.125, 58.625]];
  const country = sites.flatMap((site) => at(...site));
  assert.equal(country.length, 22);
  for (const [, lon, lat] of country) {
    const [w, s, e, n] = region.bounds;
    assert.ok(w <= lon && lon <= e && s <= lat && lat <= n, `${lon},${lat} inside Estonia bounds`);
  }
  for (const [rank, site] of cities.entries()) {
    assert.deepEqual(at(...site).map((i) => icons.names[i[0]]).sort(), rank === 0
      ? ['castle', 'house', 'house'] : rank <= 2 ? ['church', 'house', 'house']
        : rank % 2 ? ['church'] : ['house', 'house']);
    for (const other of cities.slice(rank+1)) {
      const radians = (n) => n*Math.PI/180;
      const h = Math.sin(radians(other[1]-site[1])/2)**2 + Math.cos(radians(site[1]))
        * Math.cos(radians(other[1])) * Math.sin(radians(other[0]-site[0])/2)**2;
      assert.ok(6371*2*Math.atan2(Math.sqrt(h), Math.sqrt(1-h)) >= 75);
    }
  }
  assert.equal(at(22.4792, 58.247).filter((i) => icons.names[i[0]] === 'kuressaare').length, 1);
  assert.equal(country.filter((i) => icons.names[i[0]] === 'pine').length, 7);
  assert.equal(country.filter((i) => icons.names[i[0]] === 'boat').length, 2);
});

test('Tallinn supports focal arrival and retains its scene beside Helsinki', () => {
  const city = scenes.find((s) => s.id === 'tallinn');
  assert.equal(city.name, 'Tallinn');
  assert.equal(city.country, 'Estonia');
  assert.deepEqual([city.longitude, city.latitude, city.width, city.height], [24.7536, 59.437, 720, 520]);
  assert.equal(maxZoomAt(city.longitude, city.latitude), CAPITAL_ZOOM.full);
  assert.equal(maxZoomAt(26.7099, 58.3839), COUNTRY_ZOOM.max); // Tartu
  assert.equal(maxZoomAt(28.1603, 59.3776), COUNTRY_ZOOM.max); // Narva
  assert.equal(maxZoomAt(22.4792, 58.247), COUNTRY_ZOOM.max); // Saaremaa
  assert.equal(maxZoomAt(24.5136, 58.3747), CAPITAL_ZOOM.full); // Pärnu shares the standard 1.5° reach.
  assert.equal(maxZoomAt(23.7275, 37.9838), MAX_GLOBE_ZOOM); // Athens remains uncovered.
  for (const viewport of [view, { width: 1000, height: 780 }]) {
    let current = { longitude: 25, latitude: 59.2, zoom: 5 };
    const focal = globePoint(city.longitude, city.latitude, current, viewport);
    for (let step = 0; step < 8; step++)
      current = zoomGlobe(current, current.zoom+.3, focal.x, focal.y, viewport);
    assert.equal(current.zoom, CAPITAL_ZOOM.full);
    assert.equal(camera.activeCapital(current).id, 'tallinn');
    const after = globePoint(city.longitude, city.latitude, current, viewport);
    assert.ok(Math.hypot(after.x-focal.x, after.y-focal.y) < 1);
    assert.equal(camera.activeCapital({ ...current, longitude: 24.9384, latitude: 60.1699 }).id, 'tallinn');
    assert.equal(camera.activeCapital({ longitude: 24.9384, latitude: 60.1699, zoom: 7 }).id, 'helsinki');
    assert.equal(camera.activeCapital({ ...current, zoom: 6.2 }), undefined);
  }
});

test('Hungary marks Budapest, spaced cities and Tihany Abbey within its bounds', () => {
  const region = COVERAGE.find((c) => c.id === 'budapest');
  assert.deepEqual(region.bounds, [16.05, 45.7, 22.95, 48.65]);
  const tier = icons.icons.filter((i) => i[5] === 1);
  const at = (lon, lat) => tier.filter((i) => Math.abs(i[1]-lon) < .0001 && Math.abs(i[2]-lat) < .0001);
  // Pinned Natural Earth order, retaining the existing 75 km city-spacing rule.
  const cities = [[19.0814, 47.502], [20.78, 48.1004], [21.63, 47.5305],
    [20.15, 46.2504], [18.22, 46.0804], [17.63, 47.7004], [19.7, 46.9],
    [16.6287, 47.2253], [21.101, 46.672]];
  assert.deepEqual(at(...cities[0]).map((i) => icons.names[i[0]]).sort(), ['castle', 'house', 'house']);
  for (const site of cities.slice(1, 3))
    assert.deepEqual(at(...site).map((i) => icons.names[i[0]]).sort(), ['church', 'house', 'house']);
  for (const [rank, site] of cities.entries()) {
    if (rank > 2) assert.deepEqual(at(...site).map((i) => icons.names[i[0]]), rank % 2 ? ['church'] : ['house', 'house']);
    const [west, south, east, north] = region.bounds;
    assert.ok(west <= site[0] && site[0] <= east && south <= site[1] && site[1] <= north);
    for (const other of cities.slice(rank+1)) {
      const radians = (n) => n*Math.PI/180;
      const h = Math.sin(radians(other[1]-site[1])/2)**2 + Math.cos(radians(site[1]))
        * Math.cos(radians(other[1])) * Math.sin(radians(other[0]-site[0])/2)**2;
      assert.ok(6371*2*Math.atan2(Math.sqrt(h), Math.sqrt(1-h)) >= 75);
    }
  }
  assert.equal(at(17.8894, 46.9139).filter((i) => icons.names[i[0]] === 'tihany-abbey').length, 1);
  const [west, south, east, north] = region.bounds;
  const own = tier.filter((i) => west <= i[1] && i[1] <= east && south <= i[2] && i[2] <= north);
  assert.equal(own.filter((i) => icons.names[i[0]] === 'boat').length, 0, 'Hungary is landlocked');
  for (const site of [[20.625, 48.625], [18.875, 48.125], [19.875, 47.875],
    [16.875, 47.625], [20.875, 47.625], [18.875, 46.875], [16.625, 46.625]])
    assert.equal(at(...site).filter((i) => icons.names[i[0]] === 'oak').length, 1);
});

test('Budapest supports focal arrival and retains its scene while panning near Slovakia', () => {
  const city = scenes.find((s) => s.id === 'budapest');
  assert.equal(city.name, 'Budapest');
  assert.equal(city.country, 'Hungary');
  assert.deepEqual([city.width, city.height], [720, 520]);
  assert.equal(maxZoomAt(city.longitude, city.latitude), CAPITAL_ZOOM.full);
  assert.equal(maxZoomAt(21.63, 47.5305), COUNTRY_ZOOM.max); // Debrecen stays country-only.
  assert.equal(maxZoomAt(20.15, 46.2504), CAPITAL_ZOOM.full); // Szeged lies inside the shared 1.5° reach.
  assert.equal(maxZoomAt(23.7275, 37.9838), MAX_GLOBE_ZOOM); // Athens stays uncovered.
  for (const viewport of [view, { width: 1000, height: 780 }]) {
    let current = { longitude: 19.3, latitude: 47.7, zoom: 5 };
    const focal = globePoint(city.longitude, city.latitude, current, viewport);
    for (let step = 0; step < 8; step++)
      current = zoomGlobe(current, current.zoom+.3, focal.x, focal.y, viewport);
    assert.equal(current.zoom, CAPITAL_ZOOM.full);
    assert.equal(camera.activeCapital(current).id, 'budapest');
    const arrived = globePoint(city.longitude, city.latitude, current, viewport);
    assert.ok(Math.hypot(arrived.x-focal.x, arrived.y-focal.y) < 1);
    assert.equal(camera.activeCapital({ ...current, longitude: 17.1077, latitude: 48.1486 }).id, 'budapest');
    for (const [dx, dy] of [[50, 0], [-50, 0], [0, 50], [0, -50]]) {
      for (let step = 0; step < 100; step++)
        current = capitals.clampToCapitals(camera.rotateGlobe(current, dx, dy, viewport), scenes, viewport, 2);
      assert.equal(camera.activeCapital(current).id, 'budapest');
      const rect = capitals.capitalRect(city, current, viewport, 2);
      assert.ok(rect.x <= .5 && rect.y <= .5);
      assert.ok(rect.x+rect.width >= viewport.width-.5 && rect.y+rect.height >= viewport.height-.5);
      const beyond = capitals.clampToCapitals(camera.rotateGlobe(current, dx, dy, viewport), scenes, viewport, 2);
      const stopped = capitals.capitalRect(city, beyond, viewport, 2);
      assert.ok(Math.abs(stopped.x-rect.x) < .01 && Math.abs(stopped.y-rect.y) < .01);
    }
    assert.equal(camera.activeCapital({ ...current, zoom: 6.2 }), undefined);
  }
});

test('Slovakia marks Bratislava, spaced cities and Spiš Castle within its bounds', () => {
  const region = COVERAGE.find((c) => c.id === 'bratislava');
  assert.deepEqual(region.bounds, [16.8, 47.7, 22.6, 49.65]);
  const tier = icons.icons.filter((i) => i[5] === 1);
  const at = (lon, lat) => tier.filter((i) => Math.abs(i[1]-lon) < .0001 && Math.abs(i[2]-lat) < .0001);
  // Pinned Natural Earth capital and population order; the 75 km filter also
  // excludes Prešov near Košice and Banská Bystrica near Zvolen.
  const cities = [[17.117, 48.15], [21.25, 48.7304], [18.7494, 49.2198], [19.1332, 48.5837]];
  assert.deepEqual(at(...cities[0]).map((i) => icons.names[i[0]]).sort(), ['castle', 'house', 'house']);
  for (const site of cities.slice(1, 3))
    assert.deepEqual(at(...site).map((i) => icons.names[i[0]]).sort(), ['church', 'house', 'house']);
  assert.deepEqual(at(...cities[3]).map((i) => icons.names[i[0]]), ['church']);
  assert.equal(at(20.7683, 49.0006).filter((i) => icons.names[i[0]] === 'spis-castle').length, 1);
  const trees = [[19.375, 49.375], [21.375, 49.375], [18.375, 48.875], [22.375, 48.875],
    [17.375, 48.625], [19.875, 48.625], [18.375, 48.125]];
  for (const site of trees)
    assert.equal(at(...site).filter((i) => icons.names[i[0]] === 'oak').length, 1);
  for (const [lon, lat] of [...cities, ...trees, [20.7683, 49.0006]]) {
    const [w, south, e, north] = region.bounds;
    assert.ok(w <= lon && lon <= e && south <= lat && lat <= north);
  }
  for (let a = 0; a < cities.length; a++) for (let b = a+1; b < cities.length; b++) {
    const radians = (n) => n*Math.PI/180;
    const [lon, lat] = cities[a], [otherLon, otherLat] = cities[b];
    const h = Math.sin(radians(otherLat-lat)/2)**2 + Math.cos(radians(lat))*Math.cos(radians(otherLat))
      * Math.sin(radians(otherLon-lon)/2)**2;
    assert.ok(6371*2*Math.atan2(Math.sqrt(h), Math.sqrt(1-h)) >= 75);
  }
  assert.deepEqual(icons.frames[icons.names.indexOf('spis-castle')].slice(2), [50, 52]);
  const [w, south, e, north] = region.bounds;
  assert.equal(tier.filter((i) => icons.names[i[0]] === 'boat'
    && w <= i[1] && i[1] <= e && south <= i[2] && i[2] <= north).length, 0);
});

test('Bratislava arrival and panning keep the selected scene beside Vienna', () => {
  const city = scenes.find((s) => s.id === 'bratislava');
  assert.equal(city.name, 'Bratislava');
  assert.equal(city.country, 'Slovakia');
  assert.deepEqual([city.width, city.height], [720, 520]);
  assert.equal(maxZoomAt(city.longitude, city.latitude), CAPITAL_ZOOM.full);
  assert.equal(maxZoomAt(21.25, 48.7304), COUNTRY_ZOOM.max); // Košice remains country-only.
  assert.equal(maxZoomAt(23.7275, 37.9838), MAX_GLOBE_ZOOM); // Athens stays uncovered.
  for (const viewport of [view, { width: 1000, height: 780 }]) {
    let current = { longitude: city.longitude, latitude: city.latitude, zoom: 5 };
    const focal = globePoint(city.longitude, city.latitude, current, viewport);
    for (let step = 0; step < 8; step++)
      current = zoomGlobe(current, current.zoom+.3, focal.x, focal.y, viewport);
    assert.equal(current.zoom, CAPITAL_ZOOM.full);
    assert.equal(camera.activeCapital(current).id, 'bratislava');
    assert.equal(camera.activeCapital({ ...current, longitude: 16.3738, latitude: 48.2082 }).id, 'bratislava');
    const arrived = globePoint(city.longitude, city.latitude, current, viewport);
    assert.ok(Math.hypot(arrived.x-focal.x, arrived.y-focal.y) < 1);
    for (const [dx, dy] of [[50, 0], [-50, 0], [0, 50], [0, -50]]) {
      for (let step = 0; step < 100; step++)
        current = capitals.clampToCapitals(camera.rotateGlobe(current, dx, dy, viewport), scenes, viewport, 2);
      assert.equal(camera.activeCapital(current).id, 'bratislava');
      const rect = capitals.capitalRect(city, current, viewport, 2);
      assert.ok(rect.x <= .5 && rect.y <= .5);
      assert.ok(rect.x+rect.width >= viewport.width-.5 && rect.y+rect.height >= viewport.height-.5);
      const beyond = capitals.clampToCapitals(camera.rotateGlobe(current, dx, dy, viewport), scenes, viewport, 2);
      const stopped = capitals.capitalRect(city, beyond, viewport, 2);
      assert.ok(Math.abs(stopped.x-rect.x) < .01 && Math.abs(stopped.y-rect.y) < .01);
    }
    assert.equal(camera.activeCapital({ ...current, zoom: 6.2 }), undefined);
  }
});

test('Luxembourg marks its capital, Vianden and only domestic decorations', () => {
  const region = COVERAGE.find((c) => c.id === 'luxembourg');
  assert.deepEqual(region.bounds, [5.7, 49.4, 6.55, 50.2]);
  const tier = icons.icons.filter((i) => i[5] === 1);
  const at = (lon, lat) => tier.filter((i) => Math.abs(i[1]-lon) < .0001 && Math.abs(i[2]-lat) < .0001);
  // The pinned Natural Earth capital is named Luxembourg. Its other two cities
  // are less than 75 km away, so the existing city-spacing rule retains only it.
  assert.deepEqual(at(6.13, 49.6117).map((i) => icons.names[i[0]]).sort(), ['castle', 'house', 'house']);
  assert.equal(at(6.2022, 49.935).filter((i) => icons.names[i[0]] === 'vianden').length, 1);
  for (const [lon, lat] of [[6.1667, 49.8833], [6.3333, 49.7]])
    assert.equal(at(lon, lat).length, 0, 'nearby towns must respect the 75 km spacing rule');
  const [w, s, e, n] = region.bounds;
  const own = tier.filter((i) => w <= i[1] && i[1] <= e && s <= i[2] && i[2] <= n);
  // Belgium's pre-existing Arlon group also lies in these rectangular bounds.
  assert.equal(own.filter((i) => icons.names[i[0]] === 'boat').length, 0, 'Luxembourg is landlocked');
  for (const [lon, lat] of [[5.9125, 49.9125], [5.9875, 49.7875], [5.8125, 49.7625]])
    assert.equal(at(lon, lat).filter((i) => icons.names[i[0]] === 'oak').length, 1);
  const frame = icons.frames[icons.names.indexOf('vianden')];
  assert.deepEqual(frame.slice(2), [38, 46]);
});

test('Luxembourg supports focal arrival and keeps its visit across neighbouring coverage', () => {
  const city = scenes.find((s) => s.id === 'luxembourg');
  assert.equal(city.name, 'Luxembourg City');
  assert.equal(city.country, 'Luxembourg');
  assert.deepEqual([city.width, city.height], [720, 520]);
  assert.equal(maxZoomAt(city.longitude, city.latitude), CAPITAL_ZOOM.full);
  assert.equal(maxZoomAt(23.7275, 37.9838), MAX_GLOBE_ZOOM); // Athens remains uncovered.
  for (const viewport of [view, { width: 1000, height: 780 }]) {
    let current = { longitude: 6.4, latitude: 49.8, zoom: 5 };
    const focal = globePoint(city.longitude, city.latitude, current, viewport);
    for (let step = 0; step < 8; step++)
      current = zoomGlobe(current, current.zoom+.3, focal.x, focal.y, viewport);
    assert.equal(current.zoom, CAPITAL_ZOOM.full);
    assert.equal(current.capitalId, 'luxembourg');
    const arrived = globePoint(city.longitude, city.latitude, current, viewport);
    assert.ok(Math.hypot(arrived.x-focal.x, arrived.y-focal.y) < 1);
    for (const [dx, dy] of [[50, 0], [-50, 0], [0, 50], [0, -50]]) {
      for (let step = 0; step < 100; step++)
        current = capitals.clampToCapitals(camera.rotateGlobe(current, dx, dy, viewport), scenes, viewport, 2);
      assert.equal(camera.activeCapital(current).id, 'luxembourg');
      const rect = capitals.capitalRect(city, current, viewport, 2);
      assert.ok(rect.x <= .5 && rect.y <= .5);
      assert.ok(rect.x+rect.width >= viewport.width-.5 && rect.y+rect.height >= viewport.height-.5);
      const beyond = capitals.clampToCapitals(camera.rotateGlobe(current, dx, dy, viewport), scenes, viewport, 2);
      const stopped = capitals.capitalRect(city, beyond, viewport, 2);
      assert.ok(Math.abs(stopped.x-rect.x) < .01 && Math.abs(stopped.y-rect.y) < .01);
    }
  }
});

test('Poland marks Warsaw, spaced city groups and Malbork inside its own bounds', () => {
  const poland = COVERAGE.find((c) => c.id === 'warsaw');
  assert.deepEqual(poland.bounds, [14.05, 49.0, 24.2, 55.1]);
  const tier = icons.icons.filter((i) => i[5] === 1);
  const at = (lon, lat) => tier.filter((i) => Math.abs(i[1] - lon) < .0001 && Math.abs(i[2] - lat) < .0001);
  // Pinned Natural Earth names/sites: Warsaw, Katowice, Łódź, Gdańsk, Wrocław,
  // Poznań, Szczecin, Bydgoszcz and Lublin. The capital is selected first.
  const cities = [[20.9981, 52.2519], [19.02, 50.2604], [19.4494, 51.7769],
    [18.64, 54.36], [17.03, 51.1104], [16.8999, 52.4058], [14.53, 53.4204],
    [18.01, 53.1204], [22.5727, 51.2504]];
  for (const [rank, [lon, lat]] of cities.entries()) {
    const names = at(lon, lat).map((i) => icons.names[i[0]]).sort();
    assert.deepEqual(names, rank === 0 ? ['castle', 'house', 'house']
      : rank <= 2 ? ['church', 'house', 'house'] : rank % 2 ? ['church'] : ['house', 'house']);
    for (const [otherLon, otherLat] of cities.slice(0, rank)) {
      const rad = Math.PI / 180;
      const km = 6371 * Math.acos(Math.sin(lat * rad) * Math.sin(otherLat * rad)
        + Math.cos(lat * rad) * Math.cos(otherLat * rad) * Math.cos((lon - otherLon) * rad));
      assert.ok(km >= 75, `${lon},${lat} and ${otherLon},${otherLat}: ${km} km`);
    }
  }
  assert.equal(at(19.0278, 54.0397).filter((i) => icons.names[i[0]] === 'malbork').length, 1);
  const trees = [[19.125, 53.375], [20.375, 52.875], [23.875, 52.875], [22.125, 51.875],
    [16.375, 51.625], [17.875, 50.875], [23.875, 50.625]];
  for (const [lon, lat] of trees)
    assert.equal(at(lon, lat).filter((i) => icons.names[i[0]] === (lat > 53 ? 'pine' : 'oak')).length, 1);
  const boats = [[15.375, 54.625], [19.625, 54.625]];
  for (const [lon, lat] of boats) assert.equal(at(lon, lat).filter((i) => icons.names[i[0]] === 'boat').length, 1);
  const country = [...cities, ...trees, ...boats, [19.0278, 54.0397]].flatMap(([lon, lat]) => at(lon, lat));
  assert.equal(country.length, 28);
  const [w, s, e, n] = poland.bounds;
  for (const [, lon, lat] of country) assert.ok(w <= lon && lon <= e && s <= lat && lat <= n);
});

test('Warsaw supports focal arrival and stops panning at all scene edges', () => {
  const warsaw = scenes.find((s) => s.id === 'warsaw');
  assert.equal(warsaw.name, 'Warsaw');
  assert.equal(warsaw.country, 'Poland');
  assert.deepEqual([warsaw.width, warsaw.height], [720, 520]);
  assert.equal(maxZoomAt(warsaw.longitude, warsaw.latitude), CAPITAL_ZOOM.full);
  assert.equal(maxZoomAt(18.64, 54.36), COUNTRY_ZOOM.max); // Gdańsk
  assert.equal(maxZoomAt(17.03, 51.1104), COUNTRY_ZOOM.max); // Wrocław
  assert.equal(maxZoomAt(23.7275, 37.9838), MAX_GLOBE_ZOOM); // Athens stays uncovered
  for (const viewport of [view, { width: 1000, height: 780 }]) {
    let current = { longitude: 21.7, latitude: 52.8, zoom: 5 };
    const focal = globePoint(warsaw.longitude, warsaw.latitude, current, viewport);
    for (let step = 0; step < 8; step++)
      current = zoomGlobe(current, current.zoom + .3, focal.x, focal.y, viewport);
    assert.equal(current.zoom, CAPITAL_ZOOM.full);
    assert.equal(current.capitalId, 'warsaw');
    const after = globePoint(warsaw.longitude, warsaw.latitude, current, viewport);
    assert.ok(Math.hypot(after.x - focal.x, after.y - focal.y) < 1);
    for (const [dx, dy] of [[50, 0], [-50, 0], [0, 50], [0, -50]]) {
      for (let step = 0; step < 100; step++)
        current = capitals.clampToCapitals(camera.rotateGlobe(current, dx, dy, viewport), scenes, viewport, 2);
      assert.equal(camera.activeCapital(current).id, 'warsaw');
      const rect = capitals.capitalRect(warsaw, current, viewport, 2);
      assert.ok(rect.x <= .5 && rect.y <= .5);
      assert.ok(rect.x + rect.width >= viewport.width - .5 && rect.y + rect.height >= viewport.height - .5);
      const beyond = capitals.clampToCapitals(camera.rotateGlobe(current, dx, dy, viewport), scenes, viewport, 2);
      const stopped = capitals.capitalRect(warsaw, beyond, viewport, 2);
      assert.ok(Math.abs(stopped.x - rect.x) < .01 && Math.abs(stopped.y - rect.y) < .01);
    }
  }
});

test('Czechia marks Prague, spaced city groups and Karlštejn inside its country bounds', () => {
  const czechia = COVERAGE.find((c) => c.id === 'prague');
  assert.deepEqual(czechia.bounds, [12.05, 48.5, 18.9, 51.1]);
  const tier = icons.icons.filter((i) => i[5] === 1);
  const at = (lon, lat) => tier.filter((i) => Math.abs(i[1]-lon) < .0001 && Math.abs(i[2]-lat) < .0001);
  // Names/sites from the pinned Natural Earth populated places, including its 'Pizen' spelling.
  const cities = [[14.464, 50.0853], [18.25, 49.8304], [16.61, 49.2004], [13.36, 49.7404],
    [17.65, 49.2304], [15.76, 50.0404], [15.08, 50.8], [14.46, 48.98]];
  for (const [rank, [lon, lat]] of cities.entries()) {
    const names = at(lon, lat).map((i) => icons.names[i[0]]).sort();
    assert.deepEqual(names, rank === 0 ? ['castle', 'house', 'house']
      : rank <= 2 ? ['church', 'house', 'house'] : rank % 2 ? ['church'] : ['house', 'house']);
    for (const [otherLon, otherLat] of cities.slice(0, rank)) {
      const rad = Math.PI / 180;
      const km = 6371 * Math.acos(Math.sin(lat*rad)*Math.sin(otherLat*rad)
        + Math.cos(lat*rad)*Math.cos(otherLat*rad)*Math.cos((lon-otherLon)*rad));
      assert.ok(km >= 75, `${lon},${lat} and ${otherLon},${otherLat}: ${km} km`);
    }
  }
  assert.equal(at(14.1881, 49.9394).filter((i) => icons.names[i[0]] === 'karlstejn').length, 1);
  const trees = [[13.625, 50.375], [12.375, 50.125], [17.625, 49.875], [15.125, 49.375],
    [18.375, 49.375], [13.375, 49.125], [16.125, 48.875]];
  for (const [lon, lat] of trees) assert.equal(at(lon, lat).filter((i) => icons.names[i[0]] === 'oak').length, 1);
  const country = [...cities, ...trees, [14.1881, 49.9394]].flatMap(([lon, lat]) => at(lon, lat));
  assert.equal(country.length, 24);
  const [w, s, e, n] = czechia.bounds;
  for (const [, lon, lat] of country) assert.ok(w <= lon && lon <= e && s <= lat && lat <= n);
  assert.equal(tier.filter((i) => icons.names[i[0]] === 'boat'
    && w <= i[1] && i[1] <= e && s <= i[2] && i[2] <= n).length, 0, 'Czechia is landlocked');
  for (const [lon, lat] of [[14.081, 50.663], [15.812, 50.206], [17.25, 49.63], [15.5833, 49.4004]])
    assert.equal(at(lon, lat).length, 0, 'nearby cities respect the 75 km spacing rule');
});

test('Prague supports focal arrival and retains its visit across overlapping country coverage', () => {
  const prague = scenes.find((s) => s.id === 'prague');
  assert.equal(prague.name, 'Prague');
  assert.equal(prague.country, 'Czechia');
  assert.deepEqual([prague.width, prague.height], [720, 520]);
  assert.equal(maxZoomAt(prague.longitude, prague.latitude), CAPITAL_ZOOM.full);
  assert.equal(maxZoomAt(18.25, 49.8304), COUNTRY_ZOOM.max); // Ostrava
  assert.equal(maxZoomAt(23.7275, 37.9838), MAX_GLOBE_ZOOM); // Athens remains uncovered
  let current = { longitude: 14.9, latitude: 50.4, zoom: 5 };
  const focal = globePoint(prague.longitude, prague.latitude, current, view);
  for (let step = 0; step < 8; step++)
    current = zoomGlobe(current, current.zoom+.3, focal.x, focal.y, view);
  assert.equal(current.zoom, CAPITAL_ZOOM.full);
  assert.equal(current.capitalId, 'prague');
  const after = globePoint(prague.longitude, prague.latitude, current, view);
  assert.ok(Math.hypot(after.x-focal.x, after.y-focal.y) < 1);
  for (let step = 0; step < 100; step++)
    current = capitals.clampToCapitals(camera.rotateGlobe(current, 50, 40, view), scenes, view, 2);
  assert.equal(current.capitalId, 'prague');
  assert.equal(camera.activeCapital(current).id, 'prague');
});

test('detail allows deeper zoom only where it exists', () => {
  assert.equal(maxZoomAt(-9.14, 38.71), CAPITAL_ZOOM.full); // Lisbon
  assert.equal(maxZoomAt(-8.62, 41.15), COUNTRY_ZOOM.max); // Porto: Portugal, not the capital
  assert.equal(maxZoomAt(16.3738, 48.2082), CAPITAL_ZOOM.full); // Vienna
  assert.equal(maxZoomAt(2.35, 48.86), CAPITAL_ZOOM.full); // Paris
  assert.equal(maxZoomAt(23.7275, 37.9838), MAX_GLOBE_ZOOM); // Athens, outside covered country bounds
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
  assert.equal(maxZoomAt(23.7275, 37.9838), MAX_GLOBE_ZOOM); // Athens remains uncovered
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
        // The rectangle and retained visit bound panning; 1.5° is only the arrival radius.
        assert.equal(camera.activeCapital(current).id, scene.id, 'stays at the visited capital');
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
  assert.equal(maxZoomAt(23.7275, 37.9838), MAX_GLOBE_ZOOM); // Athens remains uncovered
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

test('Brussels: focal zoom arrives at its scene, and De Panne keeps country detail', () => {
  const brussels = scenes.find((s) => s.id === 'brussels');
  assert.deepEqual([brussels.width, brussels.height], [720, 520]);
  assert.equal(maxZoomAt(4.3517, 50.8503), CAPITAL_ZOOM.full);
  assert.equal(maxZoomAt(2.59, 51.10), COUNTRY_ZOOM.max); // De Panne, beyond Brussels/Luxembourg reach
  assert.equal(maxZoomAt(23.7275, 37.9838), MAX_GLOBE_ZOOM); // Athens remains uncovered
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
  assert.equal(maxZoomAt(23.7275, 37.9838), MAX_GLOBE_ZOOM); // Athens stays uncovered
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
  assert.equal(maxZoomAt(23.7275, 37.9838), MAX_GLOBE_ZOOM); // Athens remains uncovered.
  let arriving = { longitude: -6.7, latitude: 53.1, zoom: 5 };
  const focal = globePoint(dublin.longitude, dublin.latitude, arriving, view);
  for (let step = 0; step < 8; step++)
    arriving = zoomGlobe(arriving, arriving.zoom + .3, focal.x, focal.y, view);
  assert.equal(arriving.zoom, CAPITAL_ZOOM.full);
  assert.equal(arriving.capitalId, 'dublin');
  const after = globePoint(dublin.longitude, dublin.latitude, arriving, view);
  assert.ok(Math.hypot(after.x - focal.x, after.y - focal.y) < 1);
});

test('Italy marks Rome first, nine spaced cities and Pisa inside its own bounds', () => {
  const italy = COVERAGE.find((c) => c.id === 'rome');
  assert.deepEqual(italy.bounds, [6.6, 35.4, 18.6, 47.1]);
  const tier = icons.icons.filter((i) => i[5] === 1);
  const at = (lon, lat) => tier.filter((i) => Math.abs(i[1] - lon) < .001 && Math.abs(i[2] - lat) < .001);
  // Pinned Natural Earth coordinates, capital first and then population order.
  const cities = [[12.4813, 41.8979], [9.2031, 45.4719], [14.2431, 40.842],
    [7.668, 45.0723], [11.25, 43.78], [13.3481, 38.127], [15.08, 37.5],
    [8.93, 44.41], [16.8728, 41.1142]];
  for (const [rank, [lon, lat]] of cities.entries()) {
    assert.deepEqual(at(lon, lat).map((i) => icons.names[i[0]]).sort(), rank === 0
      ? ['castle', 'house', 'house'] : rank <= 2 ? ['church', 'house', 'house']
        : rank % 2 ? ['church'] : ['house', 'house']);
    for (const [otherLon, otherLat] of cities.slice(0, rank)) {
      const rad = Math.PI / 180;
      const km = 6371 * Math.acos(Math.sin(lat * rad) * Math.sin(otherLat * rad)
        + Math.cos(lat * rad) * Math.cos(otherLat * rad) * Math.cos((lon - otherLon) * rad));
      assert.ok(km >= 75, `${lon},${lat} and ${otherLon},${otherLat}: ${km} km`);
    }
  }
  assert.equal(at(10.3966, 43.723).filter((i) => icons.names[i[0]] === 'leaning-tower-pisa').length, 1);
  const [w, s, e, n] = italy.bounds;
  const decorations = [[10.3966, 43.723], [9.875, 45.875], [10.625, 44.875],
    [12.125, 43.125], [13.625, 41.625], [16.875, 39.625], [8.625, 39.125],
    [13.875, 37.375], [18.125, 41.375], [12.375, 38.375]];
  const italyIcons = cities.concat(decorations).flatMap(([lon, lat]) => at(lon, lat));
  assert.equal(italyIcons.length, 28);
  for (const [, lon, lat] of italyIcons) assert.ok(w <= lon && lon <= e && s <= lat && lat <= n);
  assert.deepEqual(italyIcons.filter((i) => ['pine', 'oak', 'olive'].includes(icons.names[i[0]]))
    .map((i) => icons.names[i[0]]).sort(), ['oak', 'oak', 'olive', 'olive', 'olive', 'pine', 'pine']);
});

test('Rome: focal arrival and all pan edges stay in its scene; Milan retains country zoom', () => {
  const rome = scenes.find((s) => s.id === 'rome');
  assert.equal(rome.country, 'Italy');
  assert.deepEqual([rome.width, rome.height], [720, 520]);
  assert.equal(maxZoomAt(12.4964, 41.9028), CAPITAL_ZOOM.full);
  assert.equal(maxZoomAt(9.2031, 45.4719), COUNTRY_ZOOM.max);
  assert.equal(maxZoomAt(15.08, 37.5), COUNTRY_ZOOM.max); // Sicily
  assert.equal(maxZoomAt(9.12, 39.22), COUNTRY_ZOOM.max); // Sardinia
  assert.equal(maxZoomAt(23.7275, 37.9838), MAX_GLOBE_ZOOM); // Athens
  let current = { longitude: 12.1, latitude: 42.2, zoom: 5 };
  const focal = globePoint(rome.longitude, rome.latitude, current, view);
  for (let step = 0; step < 8; step++)
    current = zoomGlobe(current, current.zoom + .3, focal.x, focal.y, view);
  assert.equal(current.zoom, CAPITAL_ZOOM.full);
  assert.equal(current.capitalId, 'rome');
  const after = globePoint(rome.longitude, rome.latitude, current, view);
  assert.ok(Math.hypot(after.x - focal.x, after.y - focal.y) < 1);
  for (const [dx, dy] of [[50, 0], [-50, 0], [0, 50], [0, -50]]) {
    for (let k = 0; k < 100; k++)
      current = capitals.clampToCapitals(camera.rotateGlobe(current, dx, dy, view), scenes, view, 2);
    const rect = capitals.capitalRect(rome, current, view, 2);
    assert.equal(current.capitalId, 'rome');
    assert.ok(rect.x <= .5 && rect.y <= .5 && rect.x + rect.width >= view.width - .5
      && rect.y + rect.height >= view.height - .5, JSON.stringify(rect));
    const stopped = capitals.clampToCapitals(camera.rotateGlobe(current, dx, dy, view), scenes, view, 2);
    assert.ok(Math.abs(stopped.longitude - current.longitude) < 1e-9);
    assert.ok(Math.abs(stopped.latitude - current.latitude) < 1e-9);
  }
});

test('Denmark marks København first, five spaced cities and Kronborg inside its bounds', () => {
  const denmark = COVERAGE.find((c) => c.id === 'copenhagen');
  assert.deepEqual(denmark.bounds, [8.0, 54.5, 15.3, 57.8]);
  const tier = icons.icons.filter((i) => i[5] === 1);
  const at = (lon, lat) => tier.filter((i) => Math.abs(i[1] - lon) < .001 && Math.abs(i[2] - lat) < .001);
  // Pinned Natural Earth calls the capital København and Aarhus Århus.
  const cities = [[12.5615, 55.6805], [10.2107, 56.1572], [10.3833, 55.4004],
    [9.9166, 57.0337], [8.45, 55.467]];
  for (const [rank, [lon, lat]] of cities.entries()) {
    assert.deepEqual(at(lon, lat).map((i) => icons.names[i[0]]).sort(), rank === 0
      ? ['castle', 'house', 'house'] : rank <= 2 ? ['church', 'house', 'house']
        : rank % 2 ? ['church'] : ['house', 'house']);
    for (const [otherLon, otherLat] of cities.slice(0, rank)) {
      const rad = Math.PI / 180;
      const km = 6371 * Math.acos(Math.sin(lat * rad) * Math.sin(otherLat * rad)
        + Math.cos(lat * rad) * Math.cos(otherLat * rad) * Math.cos((lon - otherLon) * rad));
      assert.ok(km >= 75, `${lon},${lat} and ${otherLon},${otherLat}: ${km} km`);
    }
  }
  assert.equal(at(12.0833, 55.65).length, 0, 'Roskilde respects capital spacing');
  assert.equal(at(9.535, 55.709).length, 0, 'Vejle respects spacing from Odense');
  assert.equal(at(12.6218, 56.0388).filter((i) => icons.names[i[0]] === 'kronborg').length, 1);
  const decorations = [[12.6218, 56.0388], [10.125, 57.625], [10.875, 56.375],
    [9.125, 56.125], [8.875, 55.125], [12.125, 55.125], [14.875, 55.125],
    [10.625, 54.875], [8.125, 57.125], [11.875, 56.625]];
  const denmarkIcons = cities.concat(decorations).flatMap(([lon, lat]) => at(lon, lat));
  assert.equal(denmarkIcons.length, 22);
  const [w, s, e, n] = denmark.bounds;
  for (const [, lon, lat] of denmarkIcons) assert.ok(w <= lon && lon <= e && s <= lat && lat <= n);
  assert.deepEqual(denmarkIcons.filter((i) => ['pine', 'oak'].includes(icons.names[i[0]]))
    .map((i) => icons.names[i[0]]).sort(), ['oak', 'oak', 'oak', 'oak', 'pine', 'pine', 'pine']);
});

test('Copenhagen: focal arrival and pan edges keep its scene; Jutland and Bornholm keep country detail', () => {
  const copenhagen = scenes.find((s) => s.id === 'copenhagen');
  assert.equal(copenhagen.country, 'Denmark');
  assert.deepEqual([copenhagen.width, copenhagen.height], [720, 520]);
  assert.equal(maxZoomAt(12.5683, 55.6761), CAPITAL_ZOOM.full);
  assert.equal(maxZoomAt(9.9166, 57.0337), COUNTRY_ZOOM.max); // Aalborg
  assert.equal(maxZoomAt(8.45, 55.467), COUNTRY_ZOOM.max); // Esbjerg
  assert.equal(maxZoomAt(14.7, 55.1), COUNTRY_ZOOM.max); // Bornholm
  assert.equal(maxZoomAt(23.7275, 37.9838), MAX_GLOBE_ZOOM); // Athens stays outside covered bounds.
  let current = { longitude: 12.1, latitude: 55.9, zoom: 5 };
  const focal = globePoint(copenhagen.longitude, copenhagen.latitude, current, view);
  for (let step = 0; step < 8; step++)
    current = zoomGlobe(current, current.zoom + .3, focal.x, focal.y, view);
  assert.equal(current.zoom, CAPITAL_ZOOM.full);
  assert.equal(current.capitalId, 'copenhagen');
  const after = globePoint(copenhagen.longitude, copenhagen.latitude, current, view);
  assert.ok(Math.hypot(after.x - focal.x, after.y - focal.y) < 1);
  for (const [dx, dy] of [[50, 0], [-50, 0], [0, 50], [0, -50]]) {
    for (let k = 0; k < 100; k++)
      current = capitals.clampToCapitals(camera.rotateGlobe(current, dx, dy, view), scenes, view, 2);
    const rect = capitals.capitalRect(copenhagen, current, view, 2);
    assert.equal(current.capitalId, 'copenhagen');
    assert.ok(rect.x <= .5 && rect.y <= .5 && rect.x + rect.width >= view.width - .5
      && rect.y + rect.height >= view.height - .5, JSON.stringify(rect));
    const stopped = capitals.clampToCapitals(camera.rotateGlobe(current, dx, dy, view), scenes, view, 2);
    assert.ok(Math.abs(stopped.longitude - current.longitude) < 1e-9);
    assert.ok(Math.abs(stopped.latitude - current.latitude) < 1e-9);
  }
});

test('Sweden marks Stockholm first, nine spaced cities and Gripsholm inside its bounds', () => {
  const sweden = COVERAGE.find((c) => c.id === 'stockholm');
  assert.deepEqual(sweden.bounds, [11.0, 55.3, 24.2, 69.2]);
  const tier = icons.icons.filter((i) => i[5] === 1);
  const at = (lon, lat) => tier.filter((i) => Math.abs(i[1] - lon) < .001 && Math.abs(i[2] - lat) < .001);
  // Pinned Natural Earth coordinates, capital first, followed by population and 75 km spacing.
  const cities = [[18.0954, 59.3527], [12.0, 57.75], [13.0333, 55.5833],
    [16.54, 59.63], [15.22, 59.2803], [15.6299, 58.41], [14.165, 57.7713],
    [20.24, 63.83], [13.4999, 59.3671]];
  for (const [rank, [lon, lat]] of cities.entries()) {
    assert.deepEqual(at(lon, lat).map((i) => icons.names[i[0]]).sort(), rank === 0
      ? ['castle', 'house', 'house'] : rank <= 2 ? ['church', 'house', 'house']
        : rank % 2 ? ['church'] : ['house', 'house']);
    for (const [otherLon, otherLat] of cities.slice(0, rank)) {
      const rad = Math.PI / 180;
      const km = 6371 * Math.acos(Math.sin(lat * rad) * Math.sin(otherLat * rad)
        + Math.cos(lat * rad) * Math.cos(otherLat * rad) * Math.cos((lon - otherLon) * rad));
      assert.ok(km >= 75, `${lon},${lat} and ${otherLon},${otherLat}: ${km} km`);
    }
  }
  assert.equal(at(17.2192, 59.2561).filter((i) => icons.names[i[0]] === 'gripsholm').length, 1);
  assert.equal(at(17.64, 59.8601).length, 0, 'Uppsala respects capital spacing');
  const decorations = [[17.2192, 59.2561], [16.875, 67.375], [22.375, 67.125],
    [20.625, 66.625], [18.375, 63.875], [14.625, 58.875], [18.375, 57.625],
    [14.125, 56.625], [19.625, 63.125], [18.125, 61.125]];
  const swedenIcons = cities.concat(decorations).flatMap(([lon, lat]) => at(lon, lat));
  assert.equal(swedenIcons.length, 28);
  const [w, s, e, n] = sweden.bounds;
  for (const [, lon, lat] of swedenIcons) assert.ok(w <= lon && lon <= e && s <= lat && lat <= n);
  assert.deepEqual(swedenIcons.filter((i) => ['pine', 'oak'].includes(icons.names[i[0]]))
    .map((i) => icons.names[i[0]]).sort(), ['oak', 'oak', 'oak', 'pine', 'pine', 'pine', 'pine']);
  assert.equal(swedenIcons.filter((i) => icons.names[i[0]] === 'boat').length, 2);
});

test('Stockholm: focal arrival and pan edges keep its scene; northern Sweden and Gotland retain country zoom', () => {
  const stockholm = scenes.find((s) => s.id === 'stockholm');
  assert.equal(stockholm.country, 'Sweden');
  assert.deepEqual([stockholm.width, stockholm.height], [720, 520]);
  assert.equal(maxZoomAt(18.0686, 59.3293), CAPITAL_ZOOM.full);
  assert.equal(maxZoomAt(20.24, 63.83), COUNTRY_ZOOM.max); // Umeå
  assert.equal(maxZoomAt(20.225, 67.855), COUNTRY_ZOOM.max); // Kiruna
  assert.equal(maxZoomAt(18.3, 57.6), COUNTRY_ZOOM.max); // Gotland
  assert.equal(maxZoomAt(23.7275, 37.9838), MAX_GLOBE_ZOOM); // Athens remains outside covered bounds.
  let current = { longitude: 17.7, latitude: 59.6, zoom: 5 };
  const focal = globePoint(stockholm.longitude, stockholm.latitude, current, view);
  for (let step = 0; step < 8; step++)
    current = zoomGlobe(current, current.zoom + .3, focal.x, focal.y, view);
  assert.equal(current.zoom, CAPITAL_ZOOM.full);
  assert.equal(current.capitalId, 'stockholm');
  const after = globePoint(stockholm.longitude, stockholm.latitude, current, view);
  assert.ok(Math.hypot(after.x - focal.x, after.y - focal.y) < 1);
  for (const [dx, dy] of [[50, 0], [-50, 0], [0, 50], [0, -50]]) {
    for (let k = 0; k < 100; k++)
      current = capitals.clampToCapitals(camera.rotateGlobe(current, dx, dy, view), scenes, view, 2);
    const rect = capitals.capitalRect(stockholm, current, view, 2);
    assert.equal(current.capitalId, 'stockholm');
    assert.ok(rect.x <= .5 && rect.y <= .5 && rect.x + rect.width >= view.width - .5
      && rect.y + rect.height >= view.height - .5, JSON.stringify(rect));
    const stopped = capitals.clampToCapitals(camera.rotateGlobe(current, dx, dy, view), scenes, view, 2);
    assert.ok(Math.abs(stopped.longitude - current.longitude) < 1e-9);
    assert.ok(Math.abs(stopped.latitude - current.latitude) < 1e-9);
  }
});

test('Norway marks Oslo first, nine spaced cities and Borgund inside its mainland bounds', () => {
  const norway = COVERAGE.find((c) => c.id === 'oslo');
  assert.deepEqual(norway.bounds, [4.5, 57.8, 31.3, 71.3]);
  const tier = icons.icons.filter((i) => i[5] === 1);
  const at = (lon, lat) => tier.filter((i) => Math.abs(i[1] - lon) < .001 && Math.abs(i[2] - lat) < .001);
  // Pinned Natural Earth city anchors: Oslo, Bergen, Stavanger, Trondheim, Skien,
  // Kristiansand, Tromsø, Ålesund and Bodø, in population/spacing selection order.
  const cities = [[10.748, 59.9186], [5.3245, 60.391], [5.68, 58.97],
    [10.4167, 63.4167], [9.6, 59.2], [8, 58.1666], [18.992, 69.6351],
    [6.388, 62.5454], [14.4293, 67.2764]];
  for (const [rank, [lon, lat]] of cities.entries()) {
    assert.deepEqual(at(lon, lat).map((i) => icons.names[i[0]]).sort(), rank === 0
      ? ['castle', 'house', 'house'] : rank <= 2 ? ['church', 'house', 'house']
        : rank % 2 ? ['church'] : ['house', 'house']);
    for (const [otherLon, otherLat] of cities.slice(0, rank)) {
      const rad = Math.PI / 180;
      const km = 6371 * Math.acos(Math.sin(lat * rad) * Math.sin(otherLat * rad)
        + Math.cos(lat * rad) * Math.cos(otherLat * rad) * Math.cos((lon - otherLon) * rad));
      assert.ok(km >= 75, `${lon},${lat} and ${otherLon},${otherLat}: ${km} km`);
    }
  }
  assert.equal(at(7.8124, 61.0473).filter((i) => icons.names[i[0]] === 'borgund').length, 1);
  const decorations = [[7.8124, 61.0473], [20.875, 69.375], [12.375, 65.375],
    [13.875, 64.875], [11.875, 63.375], [8.375, 62.375], [7.375, 60.125],
    [7.125, 59.125], [17.125, 69.875], [4.875, 58.625]];
  const norwayIcons = cities.concat(decorations).flatMap(([lon, lat]) => at(lon, lat));
  assert.equal(norwayIcons.length, 28);
  const [w, s, e, n] = norway.bounds;
  for (const [, lon, lat] of norwayIcons) assert.ok(w <= lon && lon <= e && s <= lat && lat <= n);
  assert.deepEqual(norwayIcons.filter((i) => ['pine', 'oak'].includes(icons.names[i[0]]))
    .map((i) => icons.names[i[0]]).sort(), ['oak', 'pine', 'pine', 'pine', 'pine', 'pine', 'pine']);
  assert.equal(norwayIcons.filter((i) => icons.names[i[0]] === 'boat').length, 2);
});

test('Oslo has a capital scene while western and Arctic Norway retain country zoom', () => {
  const oslo = scenes.find((s) => s.id === 'oslo');
  assert.equal(oslo.country, 'Norway');
  assert.deepEqual([oslo.width, oslo.height], [720, 520]);
  assert.equal(maxZoomAt(oslo.longitude, oslo.latitude), CAPITAL_ZOOM.full);
  assert.equal(maxZoomAt(5.3245, 60.391), COUNTRY_ZOOM.max); // Bergen
  assert.equal(maxZoomAt(18.992, 69.6351), COUNTRY_ZOOM.max); // Tromsø
  assert.equal(maxZoomAt(25.784, 71.17), COUNTRY_ZOOM.max); // Nordkapp
  assert.equal(maxZoomAt(31.104, 70.371), COUNTRY_ZOOM.max); // Vardø
  let current = { longitude: 10.4, latitude: 60.2, zoom: 5 };
  const focal = globePoint(oslo.longitude, oslo.latitude, current, view);
  for (let step = 0; step < 8; step++)
    current = zoomGlobe(current, current.zoom + .3, focal.x, focal.y, view);
  assert.equal(current.zoom, CAPITAL_ZOOM.full);
  assert.equal(current.capitalId, 'oslo');
  const after = globePoint(oslo.longitude, oslo.latitude, current, view);
  assert.ok(Math.hypot(after.x - focal.x, after.y - focal.y) < 1);
});

test('Finland marks Helsinki first, nine spaced cities and Olavinlinna within its bounds', () => {
  const finland = COVERAGE.find((c) => c.id === 'helsinki');
  assert.deepEqual(finland.bounds, [19.0, 59.7, 31.6, 70.2]);
  const at = (lon, lat) => icons.icons.filter((i) => i[5] === 1 && i[1] === lon && i[2] === lat);
  // Natural Earth's pinned city coordinates, rather than the illustrative scene anchor.
  const cities = [[24.9322, 60.1775], [23.75, 61.5], [22.255, 60.4539],
    [25.47, 65], [25.6649, 60.9939], [25.75, 62.2603], [27.6949, 62.8943],
    [21.7749, 61.4789], [28.1833, 61.0671]];
  for (const [rank, [lon, lat]] of cities.entries()) {
    const names = at(lon, lat).map((i) => icons.names[i[0]]);
    assert.deepEqual(names, rank === 0 ? ['house', 'house', 'castle']
      : rank <= 2 ? ['church', 'house', 'house']
        : rank % 2 ? ['church'] : ['house', 'house']);
    for (const [otherLon, otherLat] of cities.slice(0, rank)) {
      const rad = Math.PI / 180;
      const km = 6371 * Math.acos(Math.sin(lat * rad) * Math.sin(otherLat * rad)
        + Math.cos(lat * rad) * Math.cos(otherLat * rad) * Math.cos((lon - otherLon) * rad));
      assert.ok(km >= 75, `${lon},${lat} and ${otherLon},${otherLat}: ${km} km`);
    }
  }
  assert.equal(at(28.9013, 61.8638).filter((i) => icons.names[i[0]] === 'olavinlinna').length, 1);
  const decorations = [[28.9013, 61.8638], [27.625, 69.125], [21.375, 68.625],
    [23.625, 67.625], [26.875, 67.625], [26.125, 64.625], [24.875, 62.125],
    [27.125, 60.875], [22.875, 64.125], [28.125, 60.375]];
  const finlandIcons = cities.concat(decorations).flatMap(([lon, lat]) => at(lon, lat));
  assert.equal(finlandIcons.length, 28);
  const [w, s, e, n] = finland.bounds;
  for (const [, lon, lat] of finlandIcons) assert.ok(w <= lon && lon <= e && s <= lat && lat <= n);
  assert.equal(finlandIcons.filter((i) => icons.names[i[0]] === 'pine').length, 7);
  assert.equal(finlandIcons.filter((i) => icons.names[i[0]] === 'boat').length, 2);
});

test('Helsinki has a capital scene while inland and Arctic Finland retain country zoom', () => {
  const helsinki = scenes.find((s) => s.id === 'helsinki');
  assert.equal(helsinki.country, 'Finland');
  assert.deepEqual([helsinki.width, helsinki.height], [720, 520]);
  assert.equal(maxZoomAt(helsinki.longitude, helsinki.latitude), CAPITAL_ZOOM.full);
  assert.equal(maxZoomAt(23.75, 61.5), CAPITAL_ZOOM.full); // Tampere shares Helsinki's 1.5° arrival reach
  assert.equal(maxZoomAt(27.6949, 62.8943), COUNTRY_ZOOM.max); // Kuopio
  assert.equal(maxZoomAt(25.47, 65), COUNTRY_ZOOM.max); // Oulu
  assert.equal(maxZoomAt(27.03, 69.9), COUNTRY_ZOOM.max); // Utsjoki
  assert.equal(maxZoomAt(19.94, 60.1), COUNTRY_ZOOM.max); // Mariehamn, Åland
  let current = { longitude: 24.5, latitude: 60.5, zoom: 5 };
  const focal = globePoint(helsinki.longitude, helsinki.latitude, current, view);
  for (let step = 0; step < 8; step++)
    current = zoomGlobe(current, current.zoom + .3, focal.x, focal.y, view);
  assert.equal(current.zoom, CAPITAL_ZOOM.full);
  assert.equal(current.capitalId, 'helsinki');
  const after = globePoint(helsinki.longitude, helsinki.latitude, current, view);
  assert.ok(Math.hypot(after.x - focal.x, after.y - focal.y) < 1);
});

test('Iceland marks Reykjavík, five spaced city groups and Gullfoss within its own bounds', () => {
  const iceland = COVERAGE.find((c) => c.id === 'reykjavik');
  assert.deepEqual(iceland.bounds, [-24.6, 63.2, -13.4, 66.6]);
  const [w, s, e, n] = iceland.bounds;
  // Iceland has no overlapping country boxes: inspect every generated Iceland icon.
  const tier = icons.icons.filter((i) => i[5] === 1 && w <= i[1] && i[1] <= e && s <= i[2] && i[2] <= n);
  const at = (lon, lat) => tier.filter((i) => Math.abs(i[1] - lon) < .001 && Math.abs(i[2] - lat) < .001);
  // Natural Earth's exact accented name selects the capital before population/spacing.
  const cities = [[-21.95, 64.15], [-18.1, 65.6666], [-23.15, 66.0833],
    [-14.395, 65.2674], [-15.2139, 64.2723]];
  for (const [rank, [lon, lat]] of cities.entries()) {
    const names = at(lon, lat).map((i) => icons.names[i[0]]);
    assert.deepEqual(names, rank === 0 ? ['house', 'house', 'castle']
      : rank <= 2 ? ['church', 'house', 'house'] : rank % 2 ? ['church'] : ['house', 'house']);
    for (const [otherLon, otherLat] of cities.slice(0, rank)) {
      const rad = Math.PI / 180;
      const km = 6371 * Math.acos(Math.sin(lat * rad) * Math.sin(otherLat * rad)
        + Math.cos(lat * rad) * Math.cos(otherLat * rad) * Math.cos((lon - otherLon) * rad));
      assert.ok(km >= 75, `${lon},${lat} and ${otherLon},${otherLat}: ${km} km`);
    }
  }
  assert.equal(at(-20.1225, 64.3271).filter((i) => icons.names[i[0]] === 'gullfoss').length, 1);
  assert.equal(tier.length, 22);
  assert.equal(tier.filter((i) => icons.names[i[0]] === 'pine').length, 7);
  assert.equal(tier.filter((i) => icons.names[i[0]] === 'boat').length, 2);
});

test('Reykjavík supports capital arrival while northern and eastern Iceland retain country zoom', () => {
  const reykjavik = scenes.find((s) => s.id === 'reykjavik');
  assert.equal(reykjavik.name, 'Reykjavík');
  assert.equal(reykjavik.country, 'Iceland');
  assert.deepEqual([reykjavik.width, reykjavik.height], [720, 520]);
  assert.equal(maxZoomAt(reykjavik.longitude, reykjavik.latitude), CAPITAL_ZOOM.full);
  assert.equal(maxZoomAt(-18.1, 65.6666), COUNTRY_ZOOM.max); // Akureyri
  assert.equal(maxZoomAt(-14.395, 65.2674), COUNTRY_ZOOM.max); // Egilsstaðir
  assert.equal(maxZoomAt(-18.0, 66.54), COUNTRY_ZOOM.max); // Grímsey
  let current = { longitude: -22.4, latitude: 64.5, zoom: 5 };
  const focal = globePoint(reykjavik.longitude, reykjavik.latitude, current, view);
  for (let step = 0; step < 8; step++)
    current = zoomGlobe(current, current.zoom + .3, focal.x, focal.y, view);
  assert.equal(current.zoom, CAPITAL_ZOOM.full);
  assert.equal(current.capitalId, 'reykjavik');
  const after = globePoint(reykjavik.longitude, reykjavik.latitude, current, view);
  assert.ok(Math.hypot(after.x - focal.x, after.y - focal.y) < 1);
});

test('Switzerland marks Bern first, six spaced city groups and Chillon within its own bounds', () => {
  const switzerland = COVERAGE.find((c) => c.id === 'bern');
  assert.deepEqual(switzerland.bounds, [5.95, 45.8, 10.55, 47.85]);
  const [w, s, e, n] = switzerland.bounds;
  const tier = icons.icons.filter((i) => i[5] === 1);
  const at = (lon, lat) => tier.filter((i) => Math.abs(i[1] - lon) < .001 && Math.abs(i[2] - lat) < .001);
  // Exact pinned Natural Earth sites. Bern must survive larger Geneva/Zürich,
  // while nearby Basel, Lausanne and Luzern obey the existing 75 km filter.
  const cities = [[7.467, 46.9167], [6.14, 46.21], [8.5481, 47.3819],
    [8.9667, 46.0004], [9.5, 46.85], [7.354, 46.239]];
  for (const [rank, [lon, lat]] of cities.entries()) {
    assert.ok(w <= lon && lon <= e && s <= lat && lat <= n);
    const names = at(lon, lat).map((i) => icons.names[i[0]]);
    assert.deepEqual(names, rank === 0 ? ['house', 'house', 'castle']
      : rank <= 2 ? ['church', 'house', 'house'] : rank % 2 ? ['church'] : ['house', 'house']);
    for (const [otherLon, otherLat] of cities.slice(0, rank)) {
      const rad = Math.PI / 180;
      const km = 6371 * Math.acos(Math.sin(lat * rad) * Math.sin(otherLat * rad)
        + Math.cos(lat * rad) * Math.cos(otherLat * rad) * Math.cos((lon - otherLon) * rad));
      assert.ok(km >= 75, `${lon},${lat} and ${otherLon},${otherLat}: ${km} km`);
    }
  }
  for (const [lon, lat, kind] of [[6.9275, 46.4142, 'chillon'],
    [7.625, 47.375, 'pine'], [9.375, 47.375, 'pine'], [6.875, 46.875, 'pine'], [8.625, 46.625, 'pine']]) {
    assert.ok(w <= lon && lon <= e && s <= lat && lat <= n);
    assert.equal(at(lon, lat).filter((i) => icons.names[i[0]] === kind).length, 1);
  }
});

test('Bern supports focal capital arrival while eastern Switzerland retains country zoom', () => {
  const bern = scenes.find((s) => s.id === 'bern');
  assert.equal(bern.name, 'Bern');
  assert.equal(bern.country, 'Switzerland');
  assert.deepEqual([bern.width, bern.height], [720, 520]);
  assert.equal(maxZoomAt(bern.longitude, bern.latitude), CAPITAL_ZOOM.full);
  assert.equal(maxZoomAt(9.5, 46.85), COUNTRY_ZOOM.max); // Chur, outside Bern's 1.5° arrival reach
  assert.equal(maxZoomAt(10.45, 46.8), COUNTRY_ZOOM.max); // eastern Graubünden
  let current = { longitude: 7.1, latitude: 47.1, zoom: 5 };
  const focal = globePoint(bern.longitude, bern.latitude, current, view);
  for (let step = 0; step < 8; step++)
    current = zoomGlobe(current, current.zoom + .3, focal.x, focal.y, view);
  assert.equal(current.zoom, CAPITAL_ZOOM.full);
  assert.equal(current.capitalId, 'bern');
  const after = globePoint(bern.longitude, bern.latitude, current, view);
  assert.ok(Math.hypot(after.x - focal.x, after.y - focal.y) < 1);
});

test('capital panning reaches actual scene edges and zooms out gradually at phone and desktop scales', () => {
  for (const scene of scenes) {
    for (const viewport of [{ width: 390, height: 844 }, { width: 1000, height: 780 }]) {
      // Same responsive icon-pixel scale as GlobeCanvas, rather than an assumed two points.
      const scale = Math.max(1.25, Math.min(viewport.width, viewport.height) / 130) * 2 / 3;
      for (const [dx, dy] of [[50, 0], [-50, 0], [0, 50], [0, -50]]) {
        let current = constrainGlobe({ longitude: scene.longitude, latitude: scene.latitude, zoom: 7 });
        for (let k = 0; k < 150; k++)
          current = capitals.clampToCapitals(camera.rotateGlobe(current, dx, dy, viewport), scenes, viewport, scale);
        const rect = capitals.capitalRect(scene, current, viewport, scale);
        const edge = dx > 0 ? rect.x : dx < 0 ? rect.x + rect.width - viewport.width
          : dy > 0 ? rect.y : rect.y + rect.height - viewport.height;
        assert.ok(Math.abs(edge) < .5, `${scene.id}, ${viewport.width}, ${dx},${dy}: ${JSON.stringify(rect)}`);
        assert.equal(current.capitalId, scene.id);
        const stopped = capitals.clampToCapitals(camera.rotateGlobe(current, dx, dy, viewport), scenes, viewport, scale);
        assert.ok(Math.abs(stopped.longitude - current.longitude) < 1e-9);
        assert.ok(Math.abs(stopped.latitude - current.latitude) < 1e-9);
        const zoomed = zoomGlobe(current, 6.9, viewport.width / 2, viewport.height / 2, viewport);
        assert.equal(zoomed.zoom, 6.9, 'zooming out at an outer edge stays gradual');
        assert.equal(zoomed.capitalId, scene.id);
        assert.equal(zoomGlobe(current, 5, viewport.width / 2, viewport.height / 2, viewport).capitalId, undefined);
      }
    }
  }
});


test('Austria marks Vienna first, seven spaced cities and Melk Abbey within its own bounds', () => {
  const austria = COVERAGE.find((c) => c.id === 'vienna');
  assert.deepEqual(austria.bounds, [9.5, 46.35, 17.2, 49.05]);
  const [w, s, e, n] = austria.bounds;
  const tier = icons.icons.filter((i) => i[5] === 1);
  const at = (lon, lat) => tier.filter((i) => Math.abs(i[1] - lon) < .001 && Math.abs(i[2] - lat) < .001);
  const cities = [[16.3647, 48.202], [14.2888, 48.3192], [15.41, 47.0778],
    [13.04, 47.8105], [11.41, 47.2804], [14.31, 46.6203], [9.7667, 47.5167]];
  const sites = [...cities, [15.3315, 48.2286], [16.375, 48.625], [13.625, 47.625],
    [10.625, 47.375], [12.375, 47.375], [14.625, 47.375], [16.375, 47.375], [12.875, 46.625]];
  const country = sites.flatMap(([lon, lat]) => at(lon, lat));
  assert.equal(country.length, 23);
  for (const [, lon, lat] of country)
    assert.ok(w <= lon && lon <= e && s <= lat && lat <= n, `${lon},${lat} inside Austria bounds`);
  for (const [rank, [lon, lat]] of cities.entries()) {
    const names = at(lon, lat).map((i) => icons.names[i[0]]);
    assert.deepEqual(names, rank === 0 ? ['house', 'house', 'castle']
      : rank <= 2 ? ['church', 'house', 'house'] : rank % 2 ? ['church'] : ['house', 'house']);
    for (const [otherLon, otherLat] of cities.slice(0, rank)) {
      const rad = Math.PI / 180;
      const km = 6371 * Math.acos(Math.sin(lat * rad) * Math.sin(otherLat * rad)
        + Math.cos(lat * rad) * Math.cos(otherLat * rad) * Math.cos((lon - otherLon) * rad));
      assert.ok(km >= 75, `${lon},${lat} and ${otherLon},${otherLat}: ${km} km`);
    }
  }
  assert.equal(at(15.3315, 48.2286).filter((i) => icons.names[i[0]] === 'melk-abbey').length, 1);
  assert.equal(country.filter((i) => icons.names[i[0]] === 'pine').length, 7);
  assert.equal(country.filter((i) => icons.names[i[0]] === 'boat').length, 0, 'Austria is landlocked');
  assert.equal(at(16.25, 47.816).length, 0, 'Wiener Neustadt respects Vienna spacing');
  assert.equal(at(16.5333, 47.8333).length, 0, 'Eisenstadt respects Vienna spacing');
});

test('Vienna supports focal arrival while western and southern Austria retain country zoom', () => {
  const vienna = scenes.find((s) => s.id === 'vienna');
  assert.equal(vienna.name, 'Vienna');
  assert.equal(vienna.country, 'Austria');
  assert.deepEqual([vienna.width, vienna.height], [720, 520]);
  assert.equal(maxZoomAt(vienna.longitude, vienna.latitude), CAPITAL_ZOOM.full);
  assert.equal(maxZoomAt(11.41, 47.2804), COUNTRY_ZOOM.max); // Innsbruck
  assert.equal(maxZoomAt(14.31, 46.6203), COUNTRY_ZOOM.max); // Klagenfurt
  assert.equal(maxZoomAt(23.7275, 37.9838), MAX_GLOBE_ZOOM); // Athens stays uncovered
  let current = { longitude: 15.8, latitude: 48.6, zoom: 5 };
  const focal = globePoint(vienna.longitude, vienna.latitude, current, view);
  for (let step = 0; step < 8; step++)
    current = zoomGlobe(current, current.zoom + .3, focal.x, focal.y, view);
  assert.equal(current.zoom, CAPITAL_ZOOM.full);
  assert.equal(current.capitalId, 'vienna');
  const after = globePoint(vienna.longitude, vienna.latitude, current, view);
  assert.ok(Math.hypot(after.x - focal.x, after.y - focal.y) < 1);
});

test('Malta marks Valletta and Gozo Citadel, with island decorations inside its own bounds', () => {
  const malta = COVERAGE.find((c) => c.id === 'valletta');
  assert.deepEqual(malta.bounds, [14.05, 35.75, 14.65, 36.12]);
  const [w, s, e, n] = malta.bounds;
  const tier = icons.icons.filter((i) => i[5] === 1 && w <= i[1] && i[1] <= e && s <= i[2] && i[2] <= n);
  const at = (lon, lat) => tier.filter((i) => Math.abs(i[1]-lon) < .0001 && Math.abs(i[2]-lat) < .0001);
  // Pinned Natural Earth spelling/site. No other city in this small archipelago
  // clears the unchanged 75 km city-spacing rule.
  assert.deepEqual(at(14.5147, 35.8997).map((i) => icons.names[i[0]]).sort(), ['castle', 'house', 'house']);
  assert.equal(tier.filter((i) => icons.names[i[0]] === 'castle').length, 1);
  assert.equal(tier.filter((i) => icons.names[i[0]] === 'house').length, 2);
  assert.equal(tier.filter((i) => icons.names[i[0]] === 'church').length, 0);
  assert.equal(at(14.2394, 36.0464).filter((i) => icons.names[i[0]] === 'gozo-citadel').length, 1);
  assert.equal(tier.filter((i) => icons.names[i[0]] === 'olive').length, 2);
  assert.equal(tier.filter((i) => icons.names[i[0]] === 'boat').length, 2);
  assert.equal(tier.length, 8);
  for (const [lon, lat, kind] of [[14.3875,35.9125,'olive'], [14.5125,35.7875,'olive'],
    [14.6375,35.9625,'boat'], [14.3625,35.7625,'boat']])
    assert.equal(at(lon,lat).filter((i) => icons.names[i[0]] === kind).length, 1);
});

test('Valletta supports focal arrival within Malta and keeps its capital visit while panning', () => {
  const valletta = scenes.find((s) => s.id === 'valletta');
  assert.equal(valletta.name, 'Valletta');
  assert.equal(valletta.country, 'Malta');
  assert.deepEqual([valletta.width, valletta.height], [720, 520]);
  assert.equal(maxZoomAt(valletta.longitude,valletta.latitude), CAPITAL_ZOOM.full);
  assert.equal(maxZoomAt(14.2394,36.0464), CAPITAL_ZOOM.full); // Gozo shares the standard 1.5° reach.
  assert.equal(maxZoomAt(23.7275,37.9838), MAX_GLOBE_ZOOM); // Athens remains uncovered.
  let current = { longitude: 14.35, latitude: 35.98, zoom: 5 };
  const focal = globePoint(valletta.longitude,valletta.latitude,current,view);
  for (let step = 0; step < 8; step++)
    current = zoomGlobe(current,current.zoom+.3,focal.x,focal.y,view);
  assert.equal(current.zoom,CAPITAL_ZOOM.full);
  assert.equal(current.capitalId,'valletta');
  const after = globePoint(valletta.longitude,valletta.latitude,current,view);
  assert.ok(Math.hypot(after.x-focal.x,after.y-focal.y) < 1);
  for (let step = 0; step < 100; step++)
    current = capitals.clampToCapitals(camera.rotateGlobe(current,50,40,view),scenes,view,2);
  assert.equal(current.capitalId,'valletta');
  assert.equal(camera.activeCapital(current).id,'valletta');
});
