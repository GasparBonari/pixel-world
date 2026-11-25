import { FilterMode, MipmapMode, Skia, rect, type SkImage } from '@shopify/react-native-skia';
import { useMemo } from 'react';

import { CollectibleCard, PixelModal } from '@/ui';

import type { LandmarkBounds } from './challenge';
import type { FoundLandmark } from './use-find-it';

function cropLandmark(image: SkImage, [x, y, width, height]: LandmarkBounds) {
  // Pre-scale the crop with nearest-neighbour sampling for a crisp card on high-density screens.
  const crop = rect(0, 0, width * 4, height * 4);
  const surface = Skia.Surface.Make(crop.width, crop.height);
  if (!surface) return;
  surface.getCanvas().drawImageRectOptions(image, rect(x, y, width, height), crop, FilterMode.Nearest, MipmapMode.None);
  const png = surface.makeImageSnapshot().encodeToBase64();
  return { uri: `data:image/png;base64,${png}` };
}

export function FoundLandmarkDialog({ found, sceneImage, onClose }: {
  found: FoundLandmark;
  sceneImage: SkImage;
  onClose: () => void;
}) {
  const { landmark, shape } = found.prompt;
  const image = useMemo(() => cropLandmark(sceneImage, shape.bbox), [sceneImage, shape]);

  return (
    <PixelModal visible label={landmark.name} onClose={onClose}>
      <CollectibleCard
        name={landmark.name}
        kind={landmark.kind}
        image={image}
        imageFit="contain"
        description={landmark.fact.text}
        source={landmark.fact.sources[0]}
        foundOn={found.date}
        justFound
        onClose={onClose}
      />
    </PixelModal>
  );
}
