import type { SkImage } from '@shopify/react-native-skia';
import { useMemo } from 'react';

import { CollectibleCard, PixelModal } from '@/ui';

import { cropLandmark } from './landmark-image';
import type { FoundLandmark } from './use-find-it';

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
