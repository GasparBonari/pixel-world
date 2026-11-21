/**
 * What moves inside a capital scene (ART_CONTRACT.md section 9), in scene pixels: glints on its
 * water (spots found by scripts/art/capital_motion.py), gulls crossing it, and cloud shadows
 * drifting over it. Pure functions of the clock, so every device shows the same thing.
 */

/** Gulls per scene, and cloud shadows per scene. */
export const GULLS = 3;
export const CLOUD_SHADOWS = 2;
/** A gull's shadow falls this far below it (scene pixels) and a little east. */
export const GULL_ALTITUDE = 26;
export const GULL_SHADOW_SHIFT = 4;

/**
 * A water glint at `time`: whether it shows, its pose (0 a dash, 1 broken in two) and a one-pixel
 * drift. Each glint shows for a third of its own 2.5-second cycle.
 */
export function glintAt(time: number, phase: number) {
  'worklet';
  if (time <= 0) return { visible: false, pose: 0, dx: 0 };
  const cycle = time / 2.5 + phase;
  const visible = cycle - Math.floor(cycle) < 0.34;
  const pose = Math.floor(time * 4 + phase * 4) % 2;
  const dx = Math.floor(time / 2.5 + phase) % 2;
  return { visible, pose, dx };
}

/**
 * Gull `index` crossing a `width` x `height` scene: alternate gulls fly east and west at their own
 * height and speed (18-30 px a second), leaving one side as they reach the other.
 */
export function gullAt(index: number, time: number, width: number, height: number) {
  'worklet';
  const east = index % 2 === 0;
  const speed = 18 + 6 * index;
  const lane = width + 80;
  const travelled = (time * speed + index * 211) % lane;
  const x = east ? travelled - 40 : width + 40 - travelled;
  const y = height * (0.2 + 0.27 * index) + 8 * Math.sin(time * 0.6 + index);
  return { x: Math.round(x), y: Math.round(y), east };
}

/**
 * Cloud shadow `index` drifting east over a `width` x `height` scene at 6-8 px a second, wrapping
 * round once it has fully left the east edge. Positions are the shadow sprite's top-left corner.
 */
export function cloudShadowAt(index: number, time: number, width: number, height: number, size: [number, number]) {
  'worklet';
  const [w, h] = size;
  const lane = width + w;
  const x = ((time * (6 + 2 * index) + index * 397) % lane) - w;
  const y = height * (0.15 + 0.45 * index) + ((index * 53) % 40) - h / 2;
  return { x: Math.round(x), y: Math.round(y) };
}
