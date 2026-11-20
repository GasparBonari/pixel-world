/**
 * Timing for the living world (ART_CONTRACT.md §9). One clock drives every animation. It ticks
 * in whole frames of a pixel-art rate, so an idle scene redraws 12 times a second rather than
 * every display frame, and motion steps like hand-drawn animation.
 */

/** Animation frames per second while nothing else is moving. */
export const ANIMATION_FPS = 12;
/** Longest step the clock takes, so a resumed app doesn't jump. */
const MAX_STEP = 0.25;

/** Idle spin of the planet, west to east like the real Earth. */
export const SPIN = {
  /** Degrees of longitude per second at full speed: one turn in two minutes. */
  degreesPerSecond: 3,
  /** Seconds after the last touch, drag, scroll or key before the planet starts turning. */
  idleSeconds: 3,
  /** Seconds to ease from still to full speed. */
  rampSeconds: 2,
  /** Full speed at planet zoom; none from the zoom where the continent board takes over. */
  fullBelowZoom: 0.6,
  noneFromZoom: 1.5,
} as const;

/**
 * When the scene first appears, the last input counts as this long ago (in clock seconds), so the
 * planet eases into its spin straight away instead of waiting as it does after a touch.
 */
export const OPENING_INPUT = -SPIN.idleSeconds;

/** The clock's time for a frame: whole animation frames since the scene started. */
export function animationTime(milliseconds: number) {
  'worklet';
  return Math.floor((milliseconds / 1000) * ANIMATION_FPS) / ANIMATION_FPS;
}

/** Seconds between two clock ticks, capped so a long pause becomes one ordinary step. */
export function animationStep(previous: number, next: number) {
  'worklet';
  return Math.min(MAX_STEP, Math.max(0, next - previous));
}

/** Spin speed (degrees per second) at a zoom, `idle` seconds after the last input. */
export function spinSpeed(zoom: number, idle: number) {
  'worklet';
  const ramp = Math.max(0, Math.min(1, (idle - SPIN.idleSeconds) / SPIN.rampSeconds));
  const reach = Math.max(
    0,
    Math.min(1, (SPIN.noneFromZoom - zoom) / (SPIN.noneFromZoom - SPIN.fullBelowZoom))
  );
  // Smoothstep both, so the planet neither lurches into motion nor stops abruptly.
  const ease = (t: number) => t * t * (3 - 2 * t);
  return SPIN.degreesPerSecond * ease(ramp) * ease(reach);
}

/** Kinds of icon motion; build_map_icons.py stores one per animated sprite with its pose frames. */
export type Motion = 'animal' | 'sway' | 'turn' | 'smoke' | 'flap';

/** A stable per-icon number in [0, 1) from its site, so neighbours don't move in step. */
export function phaseAt(longitude: number, latitude: number) {
  'worklet';
  const value = Math.sin(longitude * 12.9898 + latitude * 78.233) * 43758.5453;
  return value - Math.floor(value);
}

/**
 * The pose an animated icon shows at `time` (0 is its still frame, which reduce motion keeps).
 * - animal: still most of the time; a two-frame blink, and a 1.5 s weight shift, once per 5–8 s.
 * - sway: gusts of wind sweep east across the map every 7 s, leaning each tree for 0.7 s.
 * - turn: windmill sails, 30 degrees every third of a second.
 * - smoke: volcano ash, a new puff every 2 s.
 * - flap: bird wings, four beats a second.
 */
export function poseAt(motion: Motion, time: number, phase: number, longitude: number) {
  'worklet';
  if (time <= 0) return 0;
  if (motion === 'animal') {
    const cycle = 5 + 3 * phase;
    const t = (time + phase * 31) % cycle;
    if (t < 2 / ANIMATION_FPS) return 1;
    return t >= cycle * 0.55 && t < cycle * 0.55 + 1.5 ? 2 : 0;
  }
  if (motion === 'sway') {
    const gust = time / 7 - longitude / 40 + phase * 0.04;
    return gust - Math.floor(gust) < 0.1 ? 1 : 0;
  }
  if (motion === 'turn') return Math.floor(time * 3) % 3;
  if (motion === 'smoke') return Math.floor(time * 1.5) % 3;
  return Math.floor(time * 4 + phase * 2) % 2;
}

/** A moored boat's bob in icon pixels: down one pixel for half of each 1.6 s swell. */
export function bobAt(time: number, phase: number) {
  'worklet';
  if (time <= 0) return 0;
  const swell = time / 1.6 + phase;
  return swell - Math.floor(swell) < 0.5 ? 0 : 1;
}
