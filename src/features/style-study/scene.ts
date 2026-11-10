// P2-06 style study: a small seaside street built from Ninja Adventure (CC0) tiles.
// Pure layout data. Coordinates are source-art pixels; the canvas applies one integer scale.

export const TILE = 16;
export const SCENE_COLUMNS = 12;
export const SCENE_ROWS = 11;
export const SCENE_WIDTH = SCENE_COLUMNS * TILE;
export const SCENE_HEIGHT = SCENE_ROWS * TILE;

export type Sheet = 'floor' | 'water' | 'house' | 'nature' | 'inspector' | 'villager' | 'boat';
/** Draw order. Each layer draws completely before the next. */
export const LAYERS = ['ground', 'backdrop', 'buildings', 'props', 'actors'] as const;
export type Layer = (typeof LAYERS)[number];

export type Placement = {
  layer: Layer;
  sheet: Sheet;
  /** Source rectangle in the sheet: x, y, width, height. */
  source: [number, number, number, number];
  x: number;
  y: number;
};

const tile = (column: number, row: number): Placement['source'] => [
  column * TILE,
  row * TILE,
  TILE,
  TILE,
];

// Plain grass and its sparse detail variants (TilesetFloor, light-green set).
const GRASS = tile(0, 12);
const GRASS_DETAIL = [tile(1, 12), tile(2, 12), tile(3, 12), tile(4, 12), tile(2, 11), tile(3, 11)];
const STREET_TOP = tile(1, 7);
const STREET_BOTTOM = tile(1, 9);
// Grass-edged water (TilesetWater).
const SHORE = tile(1, 6);
const WATER = tile(1, 7);

const HOUSES: Placement['source'][] = [
  [0, 0, 64, 48], // orange roof
  [192, 0, 64, 48], // red tiled roof
  [128, 0, 64, 48], // orange roof, wider windows
];

/** Deterministic, well-mixed per-tile value so grass detail is stable between renders. */
export function tileNoise(column: number, row: number) {
  let h = Math.imul(column + 1, 374761393) ^ Math.imul(row + 1, 668265263);
  h = Math.imul(h ^ (h >>> 13), 1274126177);
  return ((h ^ (h >>> 16)) >>> 0) / 4294967296;
}

function ground(): Placement[] {
  const out: Placement[] = [];
  for (let row = 0; row < SCENE_ROWS; row++) {
    for (let column = 0; column < SCENE_COLUMNS; column++) {
      let sheet: Sheet = 'floor';
      let source = GRASS;
      if (row === 5) source = STREET_TOP;
      else if (row === 6) source = STREET_BOTTOM;
      else if (row === 8) [sheet, source] = ['water', SHORE];
      else if (row > 8) [sheet, source] = ['water', WATER];
      else {
        const n = tileNoise(column, row);
        if (n < 0.3) source = GRASS_DETAIL[Math.floor((n / 0.3) * GRASS_DETAIL.length)];
      }
      out.push({ layer: 'ground', sheet, source, x: column * TILE, y: row * TILE });
    }
  }
  return out;
}

// A band of trees behind the houses, back (higher) rows first.
const TREES: [number, number, number][] = [
  // [sheet x, x, y]
  [32, 6, -14],
  [256, 46, -12],
  [32, 98, -13],
  [256, 150, -12],
  [0, -10, -2],
  [224, 22, 0],
  [288, 74, -3],
  [224, 122, 0],
  [0, 170, -1],
];

const PROPS: Placement[] = [
  // Bushes and flowers on the strip between the street and the water.
  { layer: 'props', sheet: 'nature', source: tile(0, 10), x: 4, y: 112 },
  { layer: 'props', sheet: 'nature', source: tile(0, 11), x: 22, y: 112 },
  { layer: 'props', sheet: 'nature', source: tile(1, 10), x: 54, y: 113 },
  { layer: 'props', sheet: 'nature', source: tile(3, 11), x: 72, y: 112 },
  { layer: 'props', sheet: 'nature', source: tile(6, 11), x: 150, y: 112 },
  { layer: 'props', sheet: 'nature', source: tile(0, 10), x: 172, y: 113 },
];

const ACTORS: Placement[] = [
  // Character sheets: columns face down/up/left/right; row 0 is the idle frame.
  { layer: 'actors', sheet: 'inspector', source: [0, 0, 16, 16], x: 86, y: 80 },
  { layer: 'actors', sheet: 'villager', source: [32, 0, 16, 16], x: 140, y: 86 },
  { layer: 'actors', sheet: 'boat', source: [0, 0, 80, 32], x: 98, y: 144 },
];

export function buildScene(): Placement[] {
  const trees = TREES.map(
    ([sx, x, y]): Placement => ({
      layer: 'backdrop',
      sheet: 'nature',
      source: [sx, 0, 32, 32],
      x,
      y,
    })
  );
  const houses = HOUSES.map(
    (source, i): Placement => ({ layer: 'buildings', sheet: 'house', source, x: i * 64, y: 32 })
  );
  return [...ground(), ...trees, ...houses, ...PROPS, ...ACTORS];
}

/** Groups placements into draw batches: layer order first, then first-seen sheet order. */
export function drawBatches(placements: Placement[]) {
  const batches: { layer: Layer; sheet: Sheet; items: Placement[] }[] = [];
  for (const layer of LAYERS) {
    for (const item of placements) {
      if (item.layer !== layer) continue;
      let batch = batches.find((b) => b.layer === layer && b.sheet === item.sheet);
      if (!batch) batches.push((batch = { layer, sheet: item.sheet, items: [] }));
      batch.items.push(item);
    }
  }
  return batches;
}

/** Largest whole-pixel scale that fits; never below 2 so phone pixels stay visible. */
export function sceneScale(width: number, height: number) {
  return Math.max(2, Math.floor(Math.min(width / SCENE_WIDTH, height / SCENE_HEIGHT)));
}

/** Colours sampled from the globe shader and from the pack, for side-by-side comparison. */
export const PALETTES = {
  globe: [
    ['Grass', '#8AC240'],
    ['Forest', '#337A40'],
    ['Sand', '#D1B363'],
    ['Shallows', '#40A8C4'],
    ['Ocean', '#2973BF'],
    ['Deep', '#174599'],
  ],
  pack: [
    ['Grass', '#ADBC3A'],
    ['Grass alt', '#74A334'],
    ['Path', '#D3865F'],
    ['Water', '#71DDEE'],
    ['Roof', '#E66A3A'],
    ['Outline', '#141B1B'],
  ],
} as const;
