import assert from 'node:assert/strict';
import { existsSync, readFileSync, readdirSync } from 'node:fs';
import { createRequire } from 'node:module';
import test from 'node:test';
import { compileFunction } from 'node:vm';
import ts from 'typescript';

const root = new URL('../', import.meta.url);
const read = (path) => JSON.parse(readFileSync(new URL(path, root), 'utf8'));
const catalogDirectory = new URL('src/data/catalog/', root);
const catalogModule = new URL('src/features/catalog/catalog.ts', root);
const { outputText } = ts.transpileModule(readFileSync(catalogModule, 'utf8'), {
  compilerOptions: {
    module: ts.ModuleKind.CommonJS,
    target: ts.ScriptTarget.ES2022,
    esModuleInterop: true,
  },
});
const evaluateCatalog = compileFunction(outputText, ['require', 'exports']);
const requirePack = createRequire(catalogModule);

function loadCatalog(loadPack = requirePack) {
  const catalog = {};
  evaluateCatalog(loadPack, catalog);
  return catalog;
}

const { catalogEntries, getCatalogEntry, getCatalogChildren, hasContent } = loadCatalog();
const capitals = read('src/data/capitals.json');
const countryLabels = read('src/data/country-labels.json');
const landmarks = catalogEntries.filter(({ kind }) => kind === 'landmark');

function checkSource({ label, url }) {
  assert.ok(label?.trim(), 'missing source label');
  assert.equal(new URL(url).protocol, 'https:', url);
}

test('the loader indexes all catalog files by unique ID and direct parent', () => {
  const files = readdirSync(catalogDirectory).filter((name) => name.endsWith('.json'));
  const fileEntries = files.flatMap((name) => read(`src/data/catalog/${name}`));
  const byId = (a, b) => a.id.localeCompare(b.id);
  assert.deepEqual([...catalogEntries].sort(byId), fileEntries.sort(byId));
  assert.equal(new Set(catalogEntries.map(({ id }) => id)).size, catalogEntries.length);

  const parentKinds = {
    country: ['continent'],
    capital: ['country'],
    landmark: ['capital'],
    wildlife: ['continent', 'country'],
    landscape: ['continent', 'country'],
  };
  for (const entry of catalogEntries) {
    assert.ok(entry.id.trim(), 'missing ID');
    assert.ok(entry.name.trim(), `${entry.id}: missing name`);
    assert.equal(getCatalogEntry(entry.id), entry);
    if (entry.kind === 'continent') {
      assert.equal(entry.parentId, undefined);
      continue;
    }
    const parent = getCatalogEntry(entry.parentId);
    assert.ok(parentKinds[entry.kind]?.includes(parent?.kind), `${entry.id}: invalid parent`);
    assert.ok(getCatalogChildren(parent.id).includes(entry));
  }
  assert.equal(getCatalogEntry('unknown'), undefined);
  assert.deepEqual(getCatalogChildren('unknown'), []);
});

test('country and capital entries match the existing scene coverage', () => {
  const countries = catalogEntries.filter(({ kind }) => kind === 'country');
  const capitalEntries = catalogEntries.filter(({ kind }) => kind === 'capital');
  assert.equal(countries.length, capitals.length);
  assert.equal(capitalEntries.length, capitals.length);
  const countryIds = new Set();
  for (const scene of capitals) {
    const capital = getCatalogEntry(scene.id);
    assert.equal(capital?.kind, 'capital', scene.id);
    assert.equal(capital.name, scene.name);
    assert.equal(capital.longitude, scene.longitude);
    assert.equal(capital.latitude, scene.latitude);
    const label = countryLabels.find(({ name }) =>
      name === (scene.id === 'sarajevo' ? 'Bosnia and Herz.' : scene.country)
    );
    assert.equal(capital.parentId, label.id, scene.id);
    assert.equal(getCatalogEntry(label.id).name, label.name);
    countryIds.add(label.id);
  }
  assert.equal(countryIds.size, countries.length);
});

test('every exported landmark maps to exactly one catalog landmark', () => {
  const directory = new URL('src/data/capital-landmarks/', root);
  const files = readdirSync(directory).filter((name) => name.endsWith('.json'));
  let expectedCount = 0;
  for (const name of files) {
    const parentId = name.slice(0, -'.json'.length);
    const { landmarks: exported } = read(`src/data/capital-landmarks/${name}`);
    expectedCount += exported.length;
    for (const { id, name } of exported) {
      const entry = getCatalogEntry(id);
      assert.equal(entry?.kind, 'landmark', id);
      assert.equal(entry.name, name, id);
      assert.equal(entry.parentId, parentId, id);
      assert.ok(Number.isFinite(entry.longitude) && Math.abs(entry.longitude) <= 180, id);
      assert.ok(Number.isFinite(entry.latitude) && Math.abs(entry.latitude) <= 90, id);
      assert.ok(entry.coordinateSource.key.trim(), id);
      assert.ok(existsSync(new URL(entry.coordinateSource.path, root)), id);
    }
  }
  assert.equal(landmarks.length, expectedCount);
});

test('wildlife entries match the Europe board species and their existing sources', () => {
  const scenery = read('scripts/geography/scenery.json');
  const species = [...new Set(scenery.animals
    .filter(({ continent }) => continent === 'Europe')
    .map(({ kind }) => kind))].sort();
  const wildlife = catalogEntries.filter(({ kind }) => kind === 'wildlife');
  assert.deepEqual(wildlife.map(({ id }) => id).sort(), species);
  for (const entry of wildlife) {
    assert.equal(entry.parentId, 'europe');
    assert.deepEqual(entry.sources.map(({ url }) => url), [scenery.sources[entry.id]]);
    checkSource(entry.sources[0]);
  }
});

test('Phase 5 facts cover the three slice capitals and follow the fact rules', () => {
  const slice = new Set(['lisbon', 'paris', 'athens']);
  for (const entry of catalogEntries) {
    assert.equal(Boolean(entry.fact), entry.kind === 'landmark' && slice.has(entry.parentId), entry.id);
    if (!entry.fact) continue;
    const { text, status, sources } = entry.fact;
    assert.ok(text.trim().length > 0 && [...text].length <= 220, entry.id);
    assert.ok(['checked', 'unchecked'].includes(status), entry.id);
    assert.ok(sources.length >= 1 && sources.length <= 2, entry.id);
    for (const source of sources) checkSource(source);
  }
});

test('hasContent requires a checked collectible belonging to the country', () => {
  const checkedCountryIds = new Set();
  for (const entry of catalogEntries.filter(({ fact }) => fact?.status === 'checked')) {
    const parent = getCatalogEntry(entry.parentId);
    const country = parent.kind === 'capital' ? getCatalogEntry(parent.parentId) : parent;
    if (country.kind === 'country') checkedCountryIds.add(country.id);
  }
  for (const { id } of catalogEntries) {
    assert.equal(hasContent(id), checkedCountryIds.has(id), id);
  }
  assert.equal(hasContent('unknown'), false);
});

test('a pack of unchecked drafts cannot make a country eligible for completion', () => {
  const draftCatalog = loadCatalog((path) => {
    const entries = requirePack(path);
    if (!path.endsWith('/PRT.json')) return entries;
    return entries.map((entry) =>
      entry.fact ? { ...entry, fact: { ...entry.fact, status: 'unchecked' } } : entry
    );
  });

  assert.equal(hasContent('PRT'), true);
  assert.equal(draftCatalog.hasContent('PRT'), false);
});
