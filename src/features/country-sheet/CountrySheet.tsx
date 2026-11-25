import { useState, useSyncExternalStore } from 'react';
import { ScrollView, StyleSheet } from 'react-native';

import { Space } from '@/constants/theme';
import { BottomSheet, CollectibleTile, PixelButton, ProgressBar, SectionHeader } from '@/ui';

import { landmarkProgress } from '../find-it/landmark-progress';
import { getCountryProgress, type SelectableCountry } from './country-selection';

type Props = {
  selection: SelectableCountry;
  onClose: () => void;
  onExplore: () => void;
};

export function CountrySheet({ selection, onClose, onExplore }: Props) {
  const [expanded, setExpanded] = useState(false);
  const { country, continent, capital } = selection;
  const found = useSyncExternalStore(landmarkProgress.subscribe, landmarkProgress.getSnapshot);
  const { landmarks, value, total } = getCountryProgress(capital.id, found);

  return (
    <BottomSheet
      title={country.name}
      subtitle={`${continent.name} · Capital: ${capital.name}`}
      icon="pin"
      expanded={expanded}
      onExpandedChange={setExpanded}
      onClose={onClose}
      action={<PixelButton variant="primary" label={`Explore ${capital.name}`} onPress={onExplore} block />}>
      <ProgressBar title="Country progress" value={value} total={total} tone="light" />
      {landmarks.length > 0 && (
        <>
          <SectionHeader title="Landmarks" icon="landmark" tone="light" />
          <ScrollView horizontal contentContainerStyle={styles.tiles}>
            {landmarks.map((landmark) => (
              <CollectibleTile key={landmark.id} name={landmark.name} state={found.has(landmark.id) ? 'found' : 'missing'} />
            ))}
          </ScrollView>
        </>
      )}
    </BottomSheet>
  );
}

const styles = StyleSheet.create({ tiles: { gap: Space.sm } });
