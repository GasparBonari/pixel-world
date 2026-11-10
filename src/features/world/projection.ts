export const MAX_LATITUDE = 85.05112878;

export function longitudeLatitudeToWorld(longitude: number, latitude: number) {
  'worklet';
  const radians = (Math.max(-MAX_LATITUDE, Math.min(MAX_LATITUDE, latitude)) * Math.PI) / 180;
  return {
    x: (longitude + 180) / 360,
    y: (1 - Math.asinh(Math.tan(radians)) / Math.PI) / 2,
  };
}

export function worldToLongitudeLatitude(x: number, y: number) {
  'worklet';
  return {
    longitude: (((x % 1) + 1) % 1) * 360 - 180,
    latitude:
      (Math.atan(Math.sinh(Math.PI * (1 - 2 * Math.max(0, Math.min(1, y))))) * 180) / Math.PI,
  };
}
