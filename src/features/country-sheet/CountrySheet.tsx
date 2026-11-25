import type { SkImage } from '@shopify/react-native-skia';
import { useMemo, useState, useSyncExternalStore } from 'react';
import { ScrollView, StyleSheet } from 'react-native';

import { Space } from '@/constants/theme';
import { CAPITAL_IMAGES } from '@/data/capital-images';
import { BottomSheet, CollectibleTile, Panel, PixelButton, ProgressBar, SectionHeader } from '@/ui';

import { getChallenge } from '../find-it/challenge';
import { cropLandmark } from '../find-it/landmark-image';
import { landmarkProgress } from '../find-it/landmark-progress';
import { getCountryProgress, type SelectableCountry } from './country-selection';

type Props = {
  selection: SelectableCountry;
  sceneImage?: SkImage;
  onClose: () => void;
  onExplore: () => void;
};

export function CountrySheet({ selection, sceneImage, onClose, onExplore }: Props) {
  const [expanded, setExpanded] = useState(false);
  const { country, continent, capital } = selection;
  const found = useSyncExternalStore(landmarkProgress.subscribe, landmarkProgress.getSnapshot);
  const { landmarks, value, total } = getCountryProgress(capital.id, found);
  const artwork = CAPITAL_IMAGES[capital.id as keyof typeof CAPITAL_IMAGES];
  const thumbnails = useMemo(() => {
    if (!expanded || !sceneImage) return;
    const prompts = getChallenge(capital.id)?.prompts;
    return prompts && new Map(prompts.map(({ landmark, shape }) => [landmark.id, cropLandmark(sceneImage, shape.bbox, 2)]));
  }, [capital.id, expanded, sceneImage]);

  return (
    <BottomSheet
      title={country.name}
      subtitle={`${continent.name} · Capital: ${capital.name}`}
      icon="pin"
      artwork={artwork}
      expanded={expanded}
      onExpandedChange={setExpanded}
      onClose={onClose}
      action={<PixelButton variant="primary" icon="globe" label={`Explore ${capital.name}`} onPress={onExplore} block />}>
      <Panel contentStyle={styles.progress}>
        <ProgressBar title="Country progress" value={value} total={total} />
      </Panel>
      {landmarks.length > 0 && (
        <>
          <SectionHeader title="Landmarks" icon="landmark" tone="light" />
          <ScrollView horizontal contentContainerStyle={styles.tiles}>
            {landmarks.map((landmark) => (
              <CollectibleTile
                key={landmark.id}
                name={landmark.name}
                image={thumbnails?.get(landmark.id)}
                imageFit="contain"
                compact
                state={found.has(landmark.id) ? 'found' : 'missing'}
              />
            ))}
          </ScrollView>
        </>
      )}
    </BottomSheet>
  );
}

const styles = StyleSheet.create({
  progress: { padding: Space.xs },
  tiles: { gap: Space.sm },
});
