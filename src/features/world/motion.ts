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
