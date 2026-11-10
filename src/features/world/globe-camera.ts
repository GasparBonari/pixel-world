export type GlobeCamera = { longitude: number; latitude: number; zoom: number };
export type GlobeViewport = { width: number; height: number };
// 32x: continent scale (~20 km per terrain pixel at 2.6) with room to look closer.
// Country packs (Malta) will raise this.
export const MAX_GLOBE_ZOOM = 5;

export function globeRadius(viewport: GlobeViewport) {
  'worklet';
  return Math.min(viewport.width, viewport.height) * 0.41;
}

export function constrainGlobe(camera: GlobeCamera): GlobeCamera {
  'worklet';
  return {
    longitude: ((((camera.longitude + 180) % 360) + 360) % 360) - 180,
    latitude: Math.max(-80, Math.min(80, camera.latitude)),
    zoom: Math.max(0, Math.min(MAX_GLOBE_ZOOM, camera.zoom)),
  };
}

export const OPENING_CAMERA: GlobeCamera = { longitude: -15, latitude: 20, zoom: 0 };

/** Optional opening view from URL/search params (e.g. ?lon=14.5&lat=35.9&zoom=2.6). */
export function cameraFromParams(params: Record<string, string | string[] | undefined>) {
  const read = (key: string) => {
    const raw = params[key];
    const value = Number(Array.isArray(raw) ? raw[0] : raw);
    return raw === undefined || raw === '' || !Number.isFinite(value) ? undefined : value;
  };
  const longitude = read('lon'), latitude = read('lat'), zoom = read('zoom');
  if (longitude === undefined && latitude === undefined && zoom === undefined) return undefined;
  return constrainGlobe({
    longitude: longitude ?? OPENING_CAMERA.longitude,
    latitude: latitude ?? OPENING_CAMERA.latitude,
    zoom: zoom ?? OPENING_CAMERA.zoom,
  });
}

export function rotateGlobe(
  camera: GlobeCamera,
  dx: number,
  dy: number,
  viewport: GlobeViewport
) {
  'worklet';
  const degrees = 180 / (Math.PI * globeRadius(viewport) * 2 ** camera.zoom);
  return constrainGlobe({
    ...camera,
    longitude: camera.longitude - dx * degrees,
    latitude: camera.latitude + dy * degrees,
  });
}

export function globePoint(
  longitude: number,
  latitude: number,
  camera: GlobeCamera,
  viewport: GlobeViewport
) {
  'worklet';
  const radians = Math.PI / 180;
  const delta = (longitude - camera.longitude) * radians;
  const lat = latitude * radians;
  const center = camera.latitude * radians;
  const radius = globeRadius(viewport) * 2 ** camera.zoom;
  return {
    x: viewport.width / 2 + radius * Math.cos(lat) * Math.sin(delta),
    y:
      viewport.height / 2 -
      radius *
        (Math.cos(center) * Math.sin(lat) - Math.sin(center) * Math.cos(lat) * Math.cos(delta)),
    depth:
      Math.sin(center) * Math.sin(lat) + Math.cos(center) * Math.cos(lat) * Math.cos(delta),
  };
}

export function globeLocation(
  x: number,
  y: number,
  camera: GlobeCamera,
  viewport: GlobeViewport
) {
  'worklet';
  const radius = globeRadius(viewport) * 2 ** camera.zoom;
  const nx = (x - viewport.width / 2) / radius;
  const ny = -(y - viewport.height / 2) / radius;
  const distance = nx * nx + ny * ny;
  if (distance >= 1) return null;
  const z = Math.sqrt(1 - distance);
  const center = (camera.latitude * Math.PI) / 180;
  return {
    longitude:
      camera.longitude +
      (Math.atan2(nx, z * Math.cos(center) - ny * Math.sin(center)) * 180) / Math.PI,
    latitude: (Math.asin(ny * Math.cos(center) + z * Math.sin(center)) * 180) / Math.PI,
  };
}

export function zoomGlobe(
  camera: GlobeCamera,
  zoom: number,
  x: number,
  y: number,
  viewport: GlobeViewport
) {
  'worklet';
  const anchor = globeLocation(x, y, camera, viewport);
  let next = constrainGlobe({ ...camera, zoom });
  if (!anchor) return next;
  // Keep the chosen surface location under the pointer as the sphere grows.
  for (let step = 0; step < 5; step++) {
    const point = globeLocation(x, y, next, viewport);
    if (!point) break;
    next = constrainGlobe({
      ...next,
      longitude: next.longitude + anchor.longitude - point.longitude,
      latitude: next.latitude + anchor.latitude - point.latitude,
    });
  }
  return next;
}
