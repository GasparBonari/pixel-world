type RoutePoint = readonly [longitude: number, latitude: number, progress: number];

export type FerryRoute = {
  id: string;
  fullZoom: number;
  crossingSeconds: number;
  spriteScale?: number;
  points: readonly RoutePoint[];
};

// Crossings are schematic. Waiting spots and waypoints sit offshore so the hull clears the
// coarse coastline and the country icons. Each point gives the fraction of the crossing.
export const FERRY_ROUTES: readonly FerryRoute[] = [
  {
    id: 'valletta-mgarr',
    fullZoom: 5.9,
    crossingSeconds: 8,
    spriteScale: 0.8,
    points: [
      [14.908, 35.895, 0],
      [14.907, 36.122, 0.32],
      [14.861, 36.289, 0.59],
      [14.425, 36.276, 1],
    ],
  },
  {
    id: 'portsmouth-caen',
    fullZoom: 5,
    crossingSeconds: 9,
    points: [
      [-0.35, 50.22, 0],
      [-0.32, 49.99, 0.44],
      [-0.22, 49.84, 0.75],
      [-0.15, 49.82, 1],
    ],
  },
  {
    id: 'bari-durres',
    fullZoom: 5,
    crossingSeconds: 12,
    points: [
      [17.13, 41.4, 0],
      [17.59, 41.874, 0.32],
      [18.655, 41.82, 0.76],
      [18.88, 41.42, 1],
    ],
  },
  {
    id: 'hirtshals-kristiansand',
    fullZoom: 5,
    crossingSeconds: 11,
    points: [
      [9.9, 58.06, 0],
      [9.42, 57.98, 0.26],
      [8.84, 57.65, 0.62],
      [8.17, 57.58, 1],
    ],
  },
];
const WAIT_SECONDS = 2;

/** Each ferry runs a round trip, pausing at both ends. Time zero is the reduced-motion pose. */
export function ferryAt(time: number, crossingSeconds: number) {
  'worklet';
  const legSeconds = WAIT_SECONDS + crossingSeconds;
  const returning = Math.floor(time / legSeconds) % 2 === 1;
  const elapsed = (time % legSeconds) - WAIT_SECONDS;
  const t = Math.max(0, elapsed / crossingSeconds);
  const distance = t * t * (3 - 2 * t);
  return { progress: returning ? 1 - distance : distance, returning, underway: elapsed > 0 };
}

export function ferryFacesEast(points: readonly RoutePoint[], returning: boolean) {
  'worklet';
  return (points[points.length - 1][0] > points[0][0]) !== returning;
}

export function ferryRoutePoint(points: readonly RoutePoint[], progress: number) {
  'worklet';
  for (let i = 1; i < points.length; i++) {
    const [longitude, latitude, end] = points[i];
    if (progress <= end) {
      const [fromLongitude, fromLatitude, start] = points[i - 1];
      const t = (progress - start) / (end - start);
      return {
        longitude: fromLongitude + (longitude - fromLongitude) * t,
        latitude: fromLatitude + (latitude - fromLatitude) * t,
      };
    }
  }
  const [longitude, latitude] = points[points.length - 1];
  return { longitude, latitude };
}
