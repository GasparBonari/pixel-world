export type GlobeCamera = { longitude: number; latitude: number; zoom: number; capitalId?: string };
export type GlobeViewport = { width: number; height: number };
// 32x: continent scale (~20 km per terrain pixel at 2.6) with room to look closer. Countries and
// capitals with detail allow more (COVERAGE).
export const MAX_GLOBE_ZOOM = 5;

/** Zoom tiers beyond the continent board (ART_CONTRACT.md): a country's buildings, then its capital. */
export const COUNTRY_ZOOM = { in: 4.4, full: 5.0, max: 6.4 };
export const CAPITAL_ZOOM = { in: 6.3, full: 7.0 };
/** How far (degrees) the camera centre may be from a capital at capital zoom. */
export const CAPITAL_REACH = 1.5;
/** How far (degrees) outside a covered region the centre is pulled back rather than zoomed out. */
const PULL_BACK = 2.5;

/** Countries with detail: their bounds (west, south, east, north) and capital. Matches capitals.json. */
export const COVERAGE = [
  { id: 'lisbon', country: 'Portugal', longitude: -9.1365, latitude: 38.71, bounds: [-10.0, 36.8, -6.0, 42.2] },
  { id: 'madrid', country: 'Spain', longitude: -3.7038, latitude: 40.4168, bounds: [-9.4, 35.9, 3.4, 43.8] },
  { id: 'paris', country: 'France', longitude: 2.3522, latitude: 48.8566, bounds: [-5.2, 41.3, 9.6, 51.1] },
  { id: 'berlin', country: 'Germany', longitude: 13.405, latitude: 52.52, bounds: [5.8, 47.2, 15.1, 55.1] },
  { id: 'amsterdam', country: 'Netherlands', longitude: 4.8952, latitude: 52.3702, bounds: [3.2, 50.7, 7.3, 53.6] },
  { id: 'brussels', country: 'Belgium', longitude: 4.3517, latitude: 50.8503, bounds: [2.5, 49.45, 6.4, 51.6] },
  { id: 'london', country: 'United Kingdom', longitude: -0.1276, latitude: 51.5072, bounds: [-8.3, 49.8, 2.0, 60.9] },
  { id: 'dublin', country: 'Ireland', longitude: -6.2603, latitude: 53.3498, bounds: [-10.8, 51.35, -5.9, 55.5] },
  { id: 'rome', country: 'Italy', longitude: 12.4964, latitude: 41.9028, bounds: [6.6, 35.4, 18.6, 47.1] },
  { id: 'copenhagen', country: 'Denmark', longitude: 12.5683, latitude: 55.6761, bounds: [8.0, 54.5, 15.3, 57.8] },
  { id: 'stockholm', country: 'Sweden', longitude: 18.0686, latitude: 59.3293, bounds: [11.0, 55.3, 24.2, 69.2] },
  { id: 'oslo', country: 'Norway', longitude: 10.7522, latitude: 59.9139, bounds: [4.5, 57.8, 31.3, 71.3] },
] as const;

/** Keep the visited capital while panning across overlapping capital areas. Zooming out releases it. */
export function activeCapital(camera: GlobeCamera) {
  'worklet';
  if (camera.zoom < CAPITAL_ZOOM.in) return undefined;
  let nearest: (typeof COVERAGE)[number] | undefined;
  let best = Infinity;
  for (const region of COVERAGE) {
    if (region.id === camera.capitalId) return region;
    const dx = region.longitude - camera.longitude;
    const dy = region.latitude - camera.latitude;
    const distance = dx * dx + dy * dy;
    if (Math.abs(dx) <= CAPITAL_REACH && Math.abs(dy) <= CAPITAL_REACH && distance < best) {
      nearest = region;
      best = distance;
    }
  }
  return nearest;
}

/** The deepest zoom detail allows at a location. */
export function maxZoomAt(longitude: number, latitude: number) {
  'worklet';
  let max = MAX_GLOBE_ZOOM;
  for (const region of COVERAGE) {
    const [west, south, east, north] = region.bounds;
    if (longitude >= west && longitude <= east && latitude >= south && latitude <= north)
      max = Math.max(max, COUNTRY_ZOOM.max);
    if (
      Math.abs(longitude - region.longitude) <= CAPITAL_REACH &&
      Math.abs(latitude - region.latitude) <= CAPITAL_REACH
    )
      max = Math.max(max, CAPITAL_ZOOM.full);
  }
  return max;
}

export function globeRadius(viewport: GlobeViewport) {
  'worklet';
  return Math.min(viewport.width, viewport.height) * 0.41;
}

export function constrainGlobe(camera: GlobeCamera, coverage = true): GlobeCamera {
  'worklet';
  let longitude = ((((camera.longitude + 180) % 360) + 360) % 360) - 180;
  let latitude = Math.max(-80, Math.min(80, camera.latitude));
  let zoom = Math.max(0, Math.min(CAPITAL_ZOOM.full, camera.zoom));
  const visited = COVERAGE.find((region) => region.id === camera.capitalId);
  if (coverage && visited && zoom > COUNTRY_ZOOM.max) {
    longitude = Math.max(visited.longitude - CAPITAL_REACH, Math.min(visited.longitude + CAPITAL_REACH, longitude));
    latitude = Math.max(visited.latitude - CAPITAL_REACH, Math.min(visited.latitude + CAPITAL_REACH, latitude));
  }
  if (coverage && zoom > maxZoomAt(longitude, latitude)) {
    // Deep zoom only over covered places: pull a nearby centre back inside, else zoom out.
    let best: [number, number] | null = null;
    let bestDistance = PULL_BACK * PULL_BACK;
    for (const region of COVERAGE) {
      const capital = zoom > COUNTRY_ZOOM.max;
      const west = capital ? region.longitude - CAPITAL_REACH : region.bounds[0];
      const east = capital ? region.longitude + CAPITAL_REACH : region.bounds[2];
      const south = capital ? region.latitude - CAPITAL_REACH : region.bounds[1];
      const north = capital ? region.latitude + CAPITAL_REACH : region.bounds[3];
      const lon = Math.max(west, Math.min(east, longitude));
      const lat = Math.max(south, Math.min(north, latitude));
      const distance = (lon - longitude) ** 2 + (lat - latitude) ** 2;
      if (distance <= bestDistance) {
        best = [lon, lat];
        bestDistance = distance;
      }
    }
    if (best) [longitude, latitude] = best;
    else zoom = maxZoomAt(longitude, latitude);
  }
  const next: GlobeCamera = { longitude, latitude, zoom };
  if (zoom >= CAPITAL_ZOOM.in) {
    // Focal zoom first solves the pointer's position without coverage constraints. Select the
    // capital only after that solve, while retaining an existing visit through intermediate steps.
    const capital = coverage ? activeCapital({ ...next, capitalId: camera.capitalId }) : undefined;
    const capitalId = capital?.id ?? camera.capitalId;
    if (capitalId) next.capitalId = capitalId;
  }
  return next;
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

/** Position a known geographic anchor at a screen point, preserving the other screen axis.
 * Active capital scenes use their rectangle for pan bounds, rather than the arrival radius.
 */
export function cameraAtGlobePoint(
  camera: GlobeCamera,
  longitude: number,
  latitude: number,
  x: number,
  y: number,
  viewport: GlobeViewport
) {
  'worklet';
  const radians = Math.PI / 180;
  const radius = globeRadius(viewport) * 2 ** camera.zoom;
  const lat = latitude * radians;
  const nx = (x - viewport.width / 2) / radius;
  const ny = (viewport.height / 2 - y) / radius;
  const delta = Math.asin(Math.max(-1, Math.min(1, nx / Math.cos(lat))));
  const a = Math.sin(lat), b = Math.cos(lat) * Math.cos(delta);
  const center = Math.atan2(a, b) - Math.asin(Math.max(-1, Math.min(1, ny / Math.hypot(a, b))));
  return constrainGlobe({ ...camera, longitude: longitude - delta / radians, latitude: center / radians }, false);
}

export function rotateGlobe(
  camera: GlobeCamera,
  dx: number,
  dy: number,
  viewport: GlobeViewport
) {
  'worklet';
  const capital = activeCapital(camera);
  if (capital) {
    const point = globePoint(capital.longitude, capital.latitude, camera, viewport);
    return cameraAtGlobePoint(camera, capital.longitude, capital.latitude, point.x + dx, point.y + dy, viewport);
  }
  const degrees = 180 / (Math.PI * globeRadius(viewport) * 2 ** camera.zoom);
  return constrainGlobe({
    ...camera,
    longitude: camera.longitude - dx * degrees,
    latitude: camera.latitude + dy * degrees,
  });
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
  const visited = activeCapital(camera);
  // Detail under the fingers counts too, so pinching on Lisbon reaches the capital.
  const limit = visited ? CAPITAL_ZOOM.full : Math.max(
    maxZoomAt(camera.longitude, camera.latitude),
    anchor ? maxZoomAt(anchor.longitude, anchor.latitude) : 0
  );
  let next = constrainGlobe({ ...camera, zoom: Math.min(zoom, limit) }, false);
  if (!anchor) return constrainGlobe(next, !(visited && next.zoom >= CAPITAL_ZOOM.in));
  // Keep the chosen surface location under the pointer as the sphere grows.
  for (let step = 0; step < 5; step++) {
    const point = globeLocation(x, y, next, viewport);
    if (!point) break;
    next = constrainGlobe(
      {
        ...next,
        longitude: next.longitude + anchor.longitude - point.longitude,
        latitude: next.latitude + anchor.latitude - point.latitude,
      },
      false
    );
  }
  return constrainGlobe(next, !(visited && next.zoom >= CAPITAL_ZOOM.in));
}
