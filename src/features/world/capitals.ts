import {
  CAPITAL_ZOOM,
  activeCapital,
  constrainGlobe,
  globeLocation,
  globePoint,
  type GlobeCamera,
  type GlobeViewport,
} from './globe-camera';

export type CapitalScene = { id: string; longitude: number; latitude: number; width: number; height: number };

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
  if (!dx && !dy) return camera;
  const x = rect.x + rect.width / 2 + dx;
  const y = rect.y + rect.height / 2 + dy;
  let next = camera;
  // Match the globe projection, as focal zoom does: a screen delta is not a longitude delta,
  // especially this far north. A single rotateGlobe correction leaves a gap at the scene edge.
  for (let step = 0; step < 5; step++) {
    const point = globeLocation(x, y, next, viewport);
    if (!point) break;
    next = constrainGlobe({
      ...next,
      longitude: next.longitude + scene.longitude - point.longitude,
      latitude: next.latitude + scene.latitude - point.latitude,
    });
  }
  return next;
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
  const capital = activeCapital(camera);
  const scene = scenes.find((candidate) => candidate.id === capital?.id);
  return scene ? clampToCapital({ ...camera, capitalId: scene.id }, scene, viewport, iconScale) : camera;
}
