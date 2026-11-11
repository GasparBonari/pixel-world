import {
  CAPITAL_ZOOM,
  globePoint,
  rotateGlobe,
  type GlobeCamera,
  type GlobeViewport,
} from './globe-camera';

export type CapitalScene = { longitude: number; latitude: number; width: number; height: number };

/** Points per scene pixel: the icon pixel (2/3 of a terrain pixel) at full capital zoom. */
export function capitalScale(zoom: number, iconScale: number) {
  'worklet';
  return iconScale * 2 ** (zoom - CAPITAL_ZOOM.full);
}

/** The scene fades in while it grows out of the capital's location. */
export function capitalOpacity(zoom: number) {
  'worklet';
  const t = Math.max(0, Math.min(1, (zoom - CAPITAL_ZOOM.in) / 0.35));
  return t * t * (3 - 2 * t);
}

/** Screen rectangle of a capital scene, centred on the capital's location. */
export function capitalRect(
  scene: CapitalScene,
  camera: GlobeCamera,
  viewport: GlobeViewport,
  iconScale: number
) {
  'worklet';
  const point = globePoint(scene.longitude, scene.latitude, camera, viewport);
  const scale = capitalScale(camera.zoom, iconScale);
  const width = scene.width * scale;
  const height = scene.height * scale;
  return { x: point.x - width / 2, y: point.y - height / 2, width, height };
}

/**
 * Once a capital scene is larger than the screen, keep it covering the screen: panning stops at
 * the scene's edges instead of revealing the board underneath.
 */
export function clampToCapital(
  camera: GlobeCamera,
  scene: CapitalScene,
  viewport: GlobeViewport,
  iconScale: number
) {
  'worklet';
  if (camera.zoom < CAPITAL_ZOOM.in) return camera;
  const rect = capitalRect(scene, camera, viewport, iconScale);
  let dx = 0;
  let dy = 0;
  if (rect.width >= viewport.width) {
    if (rect.x > 0) dx = -rect.x;
    else if (rect.x + rect.width < viewport.width) dx = viewport.width - rect.x - rect.width;
  }
  if (rect.height >= viewport.height) {
    if (rect.y > 0) dy = -rect.y;
    else if (rect.y + rect.height < viewport.height) dy = viewport.height - rect.y - rect.height;
  }
  return dx || dy ? rotateGlobe(camera, dx, dy, viewport) : camera;
}

/** Clamp to whichever capital the camera is visiting (the nearest one within reach). */
export function clampToCapitals(
  camera: GlobeCamera,
  scenes: readonly CapitalScene[],
  viewport: GlobeViewport,
  iconScale: number
) {
  'worklet';
  if (camera.zoom < CAPITAL_ZOOM.in) return camera;
  let nearest: CapitalScene | null = null;
  let best = Infinity;
  for (const scene of scenes) {
    const distance = Math.hypot(scene.longitude - camera.longitude, scene.latitude - camera.latitude);
    if (distance < best) {
      best = distance;
      nearest = scene;
    }
  }
  return nearest ? clampToCapital(camera, nearest, viewport, iconScale) : camera;
}
