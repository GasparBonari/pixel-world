import { FilterMode, MipmapMode, Skia, rect, type SkImage } from '@shopify/react-native-skia';

import type { LandmarkBounds } from './challenge';

export function cropLandmark(image: SkImage, [x, y, width, height]: LandmarkBounds, scale = 4) {
  // Pre-scale with nearest-neighbour sampling to retain the scene's pixel edges.
  const crop = rect(0, 0, width * scale, height * scale);
  const surface = Skia.Surface.Make(crop.width, crop.height);
  if (!surface) return;
  surface.getCanvas().drawImageRectOptions(image, rect(x, y, width, height), crop, FilterMode.Nearest, MipmapMode.None);
  const png = surface.makeImageSnapshot().encodeToBase64();
  return { uri: `data:image/png;base64,${png}` };
}
