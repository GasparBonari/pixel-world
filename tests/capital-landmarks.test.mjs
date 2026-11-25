import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import test from 'node:test';

const scenes = JSON.parse(readFileSync(new URL('../src/data/capitals.json', import.meta.url), 'utf8'));
const landmarkDir = new URL('../src/data/capital-landmarks/', import.meta.url);

// CapitalLayer uses capitals.ts's capitalScale, which equals GlobeCanvas's iconScale at
// full zoom. On a 390×844 phone viewport, iconScale = max(1.25, 390 / 130) * 2 / 3.
const pointsPerPixel = (Math.max(1.25, 390 / 130) * 2) / 3;

function readLandmarks(id) {
  return JSON.parse(readFileSync(new URL(`${id}.json`, landmarkDir), 'utf8')).landmarks;
}

test('capital landmark exports match the scene registry', () => {
  const files = readdirSync(landmarkDir).filter((name) => name.endsWith('.json')).sort();
  assert.deepEqual(files, scenes.map(({ id }) => `${id}.json`).sort());
  const ids = new Set();
  for (const scene of scenes) {
    for (const { id } of readLandmarks(scene.id)) {
      assert.ok(!ids.has(id), `${scene.id}: duplicate landmark id ${id}`);
      ids.add(id);
    }
  }
});

for (const scene of scenes) {
  test(`${scene.id}: landmark shapes fit the scene PNG`, (t) => {
    const png = readFileSync(new URL(`../assets/world/capitals/${scene.id}.png`, import.meta.url));
    assert.equal(png.toString('ascii', 12, 16), 'IHDR');
    const [imageWidth, imageHeight] = [png.readUInt32BE(16), png.readUInt32BE(20)];
    assert.deepEqual([scene.width, scene.height], [imageWidth, imageHeight]);

    const landmarks = readLandmarks(scene.id);
    assert.ok(Array.isArray(landmarks) && landmarks.length > 0);
    for (const { id, name, bbox, mask } of landmarks) {
      assert.match(id, /^[a-z0-9]+(?:-[a-z0-9]+)*$/);
      assert.ok(typeof name === 'string' && name.trim(), `${id}: missing display name`);
      assert.ok(bbox.length === 4 && bbox.every(Number.isInteger), `${id}: invalid box`);
      const [x, y, width, height] = bbox;
      assert.ok(width > 0 && height > 0, `${id}: empty box`);
      // The scene builders keep landmarks clear of the edges. A cropped silhouette can
      // otherwise appear to fit if its box was calculated after cropping.
      assert.ok(x > 0 && y > 0 && x + width < imageWidth && y + height < imageHeight,
        `${id}: box touches or extends beyond a scene edge`);

      const bytes = Buffer.from(mask, 'base64');
      assert.equal(bytes.length, Math.ceil(width * height / 8), `${id}: invalid mask length`);
      assert.equal(bytes.toString('base64'), mask, `${id}: invalid Base64`);
      let minX = width;
      let maxX = -1;
      let minY = height;
      let maxY = -1;
      for (let bit = 0; bit < bytes.length * 8; bit++) {
        if (!(bytes[bit >> 3] & (1 << (bit & 7)))) continue;
        assert.ok(bit < width * height, `${id}: set bit outside box`);
        const col = bit % width;
        const row = Math.floor(bit / width);
        minX = Math.min(minX, col);
        maxX = Math.max(maxX, col);
        minY = Math.min(minY, row);
        maxY = Math.max(maxY, row);
      }
      assert.deepEqual([minX, minY, maxX, maxY], [0, 0, width - 1, height - 1],
        `${id}: mask is empty or box does not tightly enclose it`);

      const [widthPt, heightPt] = [width * pointsPerPixel, height * pointsPerPixel];
      if (Math.min(widthPt, heightPt) < 48) {
        t.diagnostic(`${name} (${id}) is under 48 pt on a phone (${widthPt}×${heightPt} pt)`);
      }
    }
  });
}

test('the Luxor Obelisk mask accepts painted pixels and rejects empty pixels inside its box', () => {
  const { bbox: [x, y, width], mask } = readLandmarks('paris').find(({ id }) => id === 'luxor-obelisk');
  const bytes = Buffer.from(mask, 'base64');
  const hits = (px, py) => {
    const bit = (py - y) * width + px - x;
    return Boolean(bytes[bit >> 3] & (1 << (bit & 7)));
  };
  assert.equal(hits(252, 175), true);
  assert.equal(hits(249, 175), false);
});
