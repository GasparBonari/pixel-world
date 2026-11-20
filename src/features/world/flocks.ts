/**
 * Flocks of birds crossing the board (ART_CONTRACT.md §9). Each flock flies its own great circle
 * round the planet, so it never appears or vanishes mid-screen: it simply comes over the horizon.
 * Deterministic: the same flocks fly the same routes on every device.
 */

export type Vector = [number, number, number];
export type Flock = { u: Vector; w: Vector; start: number; speed: number };

export const FLOCK_COUNT = 48;
/** Leader, then two birds behind and to either side, in icon pixels with the flock heading east. */
export const FORMATION: [number, number][] = [
  [0, 0],
  [-6, -3],
  [-6, 3],
];
/** Birds fly this many icon pixels above their shadow, which falls a little east (light from the west). */
export const ALTITUDE = 14;
export const SHADOW_SHIFT = 2;

function random(index: number, salt: number) {
  const value = Math.sin(index * 127.1 + salt * 311.7) * 43758.5453;
  return value - Math.floor(value);
}

function cross(a: Vector, b: Vector): Vector {
  return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
}

function normalize(v: Vector): Vector {
  const length = Math.hypot(v[0], v[1], v[2]);
  return [v[0] / length, v[1] / length, v[2] / length];
}

/** A flock's route: the great circle around a random pole, a start point on it and a speed. */
export function makeFlock(index: number): Flock {
  const z = 2 * random(index, 1) - 1;
  const around = 2 * Math.PI * random(index, 2);
  const ring = Math.sqrt(1 - z * z);
  const pole: Vector = [ring * Math.cos(around), ring * Math.sin(around), z];
  const u = normalize(cross(pole, Math.abs(z) > 0.99 ? [1, 0, 0] : [0, 0, 1]));
  const w = cross(pole, u);
  // 0.5–0.9 degrees of arc a second, either way round.
  const degrees = 0.5 + 0.4 * random(index, 3);
  const speed = ((random(index, 4) < 0.5 ? -1 : 1) * degrees * Math.PI) / 180;
  return { u, w, start: 2 * Math.PI * random(index, 5), speed };
}

export const FLOCKS = Array.from({ length: FLOCK_COUNT }, (_, index) => makeFlock(index));

/** Where a flock is at `time` (degrees) and whether it is heading east. */
export function flockAt(flock: Flock, time: number) {
  'worklet';
  const { u, w, start, speed } = flock;
  const angle = start + speed * time;
  const c = Math.cos(angle);
  const s = Math.sin(angle);
  const x = u[0] * c + w[0] * s;
  const y = u[1] * c + w[1] * s;
  const z = u[2] * c + w[2] * s;
  const longitude = (Math.atan2(y, x) * 180) / Math.PI;
  const latitude = (Math.asin(Math.max(-1, Math.min(1, z))) * 180) / Math.PI;
  // Velocity along the circle, projected on the local east direction (-sin lon, cos lon, 0).
  const vx = speed * (-u[0] * s + w[0] * c);
  const vy = speed * (-u[1] * s + w[1] * c);
  const lon = Math.atan2(y, x);
  const east = -Math.sin(lon) * vx + Math.cos(lon) * vy >= 0;
  return { longitude, latitude, east };
}
