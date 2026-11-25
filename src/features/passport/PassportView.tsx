import { useSyncExternalStore } from 'react';

import { catalogEntries } from '@/features/catalog/catalog';
import { landmarkProgress } from '@/features/find-it/landmark-progress';
import { Panel, PixelText, ProgressBar, Screen, TopBar } from '@/ui';

const landmarks = catalogEntries.filter((entry) => entry.kind === 'landmark' && entry.fact?.status === 'checked');

export function PassportView() {
  const found = useSyncExternalStore(landmarkProgress.subscribe, landmarkProgress.getSnapshot);

  return (
    <Screen header={<TopBar title="Passport" compact />} bottomInset={false}>
      <Panel>
        <PixelText>Your stamps, visited places, and wishlist will appear here.</PixelText>
        <ProgressBar
          title="Landmarks found this session"
          value={landmarks.filter(({ id }) => found.has(id)).length}
          total={landmarks.length}
          compact
        />
      </Panel>
    </Screen>
  );
}
