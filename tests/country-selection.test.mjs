import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import test from 'node:test';
import { compileFunction } from 'node:vm';
import ts from 'typescript';

function loadLogic(path) {
  const { outputText } = ts.transpileModule(readFileSync(path, 'utf8'), {
    compilerOptions: {
      module: ts.ModuleKind.CommonJS,
      target: ts.ScriptTarget.ES2022,
      esModuleInterop: true,
    },
  });
  const exports = {};
  const require = createRequire(path);
  compileFunction(outputText, ['require', 'exports'])(
    (id) => id.endsWith('.json') ? require(id) : loadLogic(new URL(`${id}.ts`, path)),
    exports
  );
  return exports;
}

const { getSelectableCountry, getCountryProgress, selectCountryAtTap } = loadLogic(
  new URL('../src/features/country-sheet/country-selection.ts', import.meta.url)
);
const { boardContinentAt, boardCountryAt, boardCountryIndex } = loadLogic(new URL('../src/features/world/board-country-lookup.ts', import.meta.url));
const { globeLocation, globePoint, COUNTRY_ZOOM, CAPITAL_ZOOM } = loadLogic(
  new URL('../src/features/world/globe-camera.ts', import.meta.url)
);
const { getWorldProgress } = loadLogic(new URL('../src/features/world/world-progress.ts', import.meta.url));

test('only catalog countries with a playable capital can be selected', () => {
  const portugal = getSelectableCountry('PRT');
  assert.equal(portugal.country.name, 'Portugal');
  assert.equal(portugal.continent.name, 'Europe');
  assert.equal(portugal.capital.name, 'Lisbon');
  assert.equal(getSelectableCountry('ISL').capital.name, 'Reykjavík');
  assert.equal(getSelectableCountry('BRA'), undefined);
  assert.equal(getSelectableCountry('lisbon'), undefined);
});

test('country-tier taps select or replace a country, and sea clears it', () => {
  const camera = { longitude: -8, latitude: 39.5, zoom: COUNTRY_ZOOM.full };
  assert.equal(selectCountryAtTap(null, camera, 'PRT'), 'PRT');
  assert.equal(selectCountryAtTap('PRT', camera, 'ESP'), 'ESP');
  assert.equal(selectCountryAtTap('PRT', camera, null), null);
  assert.equal(selectCountryAtTap('PRT', camera, 'BRA'), 'PRT');
  assert.equal(selectCountryAtTap(null, { ...camera, zoom: COUNTRY_ZOOM.in - 0.01 }, 'PRT'), null);
  assert.equal(selectCountryAtTap('PRT', { ...camera, zoom: CAPITAL_ZOOM.full, capitalId: 'lisbon' }, null), 'PRT');
});

test('landmark progress counts checked catalog entries against the shared records', () => {
  const { createLandmarkProgress } = loadLogic(new URL('../src/features/find-it/landmark-progress.ts', import.meta.url));
  const records = createLandmarkProgress();
  for (const [capital, total] of [['lisbon', 4], ['paris', 6], ['athens', 7], ['reykjavik', 0], ['unknown', 0]]) {
    const progress = getCountryProgress(capital, records.getSnapshot());
    assert.equal(progress.value, 0, capital);
    assert.equal(progress.total, total, capital);
    assert.equal(progress.landmarks.length, total, capital);
    assert.ok(progress.landmarks.every((entry) => entry.kind === 'landmark' && entry.fact.status === 'checked'));
  }
  records.markFound('belem-tower', new Date(2026, 10, 25));
  records.markFound('arco-rua-augusta', new Date(2026, 10, 25));
  assert.equal(getCountryProgress('lisbon', records.getSnapshot()).value, 2);
  assert.equal(getCountryProgress('paris', records.getSnapshot()).value, 0);
});

test('World counts a country only when its released pack is complete', () => {
  const { catalogEntries, hasContent } = loadLogic(new URL('../src/features/catalog/catalog.ts', import.meta.url));
  const { landmarks } = getCountryProgress('lisbon', new Set());
  const total = catalogEntries.filter(({ id }) => hasContent(id)).length;
  const found = new Set(landmarks.slice(1).map(({ id }) => id));

  assert.ok(landmarks.length > 1);
  assert.deepEqual(getWorldProgress(found), { value: 0, total });
  found.add(landmarks[0].id);
  assert.deepEqual(getWorldProgress(found), { value: 1, total });
});

test('projected screen positions find the board country, including borders, islands and sea', () => {
  const camera = { longitude: -8, latitude: 39.5, zoom: COUNTRY_ZOOM.full };
  const viewport = { width: 390, height: 844 };
  for (const [longitude, latitude, id] of [[-8.5, 39.5, 'PRT'], [-6.4, 39.5, 'ESP'], [-10.25, 39.5, null]]) {
    const { x, y } = globePoint(longitude, latitude, camera, viewport);
    const location = globeLocation(x, y, camera, viewport);
    assert.equal(boardCountryAt(location.longitude, location.latitude), id);
  }
  assert.equal(boardCountryAt(14.5146, 35.8989), 'MLT');
  assert.equal(boardCountryAt(179, 66), 'RUS');
  assert.equal(boardCountryAt(-181, 66), 'RUS');
  assert.equal(boardCountryAt(0, -90), 'ATA');
});

test('the country highlight uses the board index associated with a tapped country', () => {
  const { countryIds } = JSON.parse(readFileSync(new URL('../src/data/board-country-lookup.json', import.meta.url), 'utf8'));
  for (const [longitude, latitude, id] of [[-8.5, 39.5, 'PRT'], [14.5146, 35.8989, 'MLT']]) {
    assert.equal(countryIds[boardCountryIndex(boardCountryAt(longitude, latitude))], id);
  }
  assert.equal(boardCountryIndex('unmapped'), 0);
});

test('continent names follow geographic outlines through a transcontinental country', () => {
  assert.equal(boardCountryAt(105, 60), 'RUS');
  assert.equal(boardContinentAt(105, 60), 'Asia');
  assert.equal(boardContinentAt(37.6173, 55.7558), 'Europe');
  assert.equal(boardContinentAt(-55, -10), 'South America');
  assert.equal(boardContinentAt(-39, 39), null);
});
