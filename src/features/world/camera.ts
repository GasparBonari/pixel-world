export type Camera = { x: number; y: number; zoom: number };
export type Viewport = { width: number; height: number };
export const TILE_SIZE = 256;
export const MAX_ZOOM = 5;

export function minimumZoom(viewport: Viewport) {
  'worklet';
  return Math.log2(Math.min(viewport.width, viewport.height) / TILE_SIZE);
}

export function constrainCamera(camera: Camera, viewport: Viewport): Camera {
  'worklet';
  const zoom = Math.max(minimumZoom(viewport), Math.min(MAX_ZOOM, camera.zoom));
  const worldSize = TILE_SIZE * 2 ** zoom;
  const halfHeight = viewport.height / (2 * worldSize);
  return {
    x: worldSize <= viewport.width ? 0.5 : ((camera.x % 1) + 1) % 1,
    y: halfHeight >= 0.5 ? 0.5 : Math.max(halfHeight, Math.min(1 - halfHeight, camera.y)),
    zoom,
  };
}

export function initialCamera(viewport: Viewport): Camera {
  'worklet';
  return { x: 0.5, y: 0.5, zoom: minimumZoom(viewport) };
}

export function panCamera(camera: Camera, dx: number, dy: number, viewport: Viewport): Camera {
  'worklet';
  const worldSize = TILE_SIZE * 2 ** camera.zoom;
  return constrainCamera(
    { ...camera, x: camera.x - dx / worldSize, y: camera.y - dy / worldSize },
    viewport
  );
}

export function zoomCamera(
  camera: Camera,
  zoom: number,
  x: number,
  y: number,
  viewport: Viewport
): Camera {
  'worklet';
  const nextZoom = Math.max(minimumZoom(viewport), Math.min(MAX_ZOOM, zoom));
  const previousSize = TILE_SIZE * 2 ** camera.zoom;
  const nextSize = TILE_SIZE * 2 ** nextZoom;
  const offsetX = x - viewport.width / 2;
  const offsetY = y - viewport.height / 2;
  return constrainCamera(
    {
      x: camera.x + offsetX / previousSize - offsetX / nextSize,
      y: camera.y + offsetY / previousSize - offsetY / nextSize,
      zoom: nextZoom,
    },
    viewport
  );
}

export function tileWindow(camera: Camera, viewport: Viewport) {
  'worklet';
  const level = Math.max(0, Math.min(MAX_ZOOM, Math.floor(camera.zoom)));
  const count = 2 ** level;
  const worldSize = TILE_SIZE * 2 ** camera.zoom;
  const tileSize = worldSize / count;
  const horizontalWrap = worldSize > viewport.width;
  return {
    level,
    left: Math.max(
      horizontalWrap ? -count : 0,
      Math.floor((camera.x * worldSize - viewport.width / 2) / tileSize) - 1
    ),
    right: Math.min(
      horizontalWrap ? count * 2 - 1 : count - 1,
      Math.floor((camera.x * worldSize + viewport.width / 2) / tileSize) + 1
    ),
    top: Math.max(0, Math.floor((camera.y * worldSize - viewport.height / 2) / tileSize) - 1),
    bottom: Math.min(
      count - 1,
      Math.floor((camera.y * worldSize + viewport.height / 2) / tileSize) + 1
    ),
  };
}

export function tileWindowKey(camera: Camera, viewport: Viewport) {
  'worklet';
  const window = tileWindow(camera, viewport);
  return `${window.level}:${window.left}:${window.right}:${window.top}:${window.bottom}`;
}

export function visibleTiles(camera: Camera, viewport: Viewport) {
  const window = tileWindow(camera, viewport);
  const count = 2 ** window.level;
  const tiles = [];
  for (let row = window.top; row <= window.bottom; row++) {
    for (let column = window.left; column <= window.right; column++) {
      const sourceColumn = ((column % count) + count) % count;
      tiles.push({
        key: `${window.level}/${sourceColumn}/${row}`,
        drawKey: `${window.level}/${column}/${row}`,
        x: column / count,
        y: row / count,
        size: 1 / count,
      });
    }
  }
  return tiles;
}
