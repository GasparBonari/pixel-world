/** Icons fade in over the second half of the globe-to-board transition. */
export function iconOpacity(zoom: number, start: number, end: number) {
  'worklet';
  const t = Math.max(0, Math.min(1, (zoom - (start + end) / 2) / ((end - start) / 2)));
  return t * t * (3 - 2 * t);
}
