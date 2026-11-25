import type { SkImage } from '@shopify/react-native-skia';
import { useSyncExternalStore, type PropsWithChildren, type ReactNode } from 'react';

import { landmarkProgress } from '@/features/find-it/landmark-progress';
import { WorldTitle } from '@/features/title/WorldTitle';
import { getWorldProgress } from '@/features/world/world-progress';
import { Panel, ProgressBar, Screen, TopBar } from '@/ui';

import { CountrySheet } from './CountrySheet';
import type { SelectableCountry } from './country-selection';

type Props = PropsWithChildren<{
  earthOverview: boolean;
  selection?: SelectableCountry;
  selectedScene?: SkImage;
  regionalTitle?: string;
  capitalName?: string;
  prompt?: ReactNode;
  onEnterWorld?: () => void;
  onBack?: () => void;
  backLabel: string;
  onClose: () => void;
  onExplore: () => void;
}>;

export function WorldMapScreen({
  earthOverview, selection, selectedScene, regionalTitle, capitalName, prompt, onEnterWorld, onBack, backLabel, onClose, onExplore, children,
}: Props) {
  return (
    <Screen
      background="none"
      scroll={false}
      fullBleed
      floatingHeader={earthOverview || !!regionalTitle}
      bottomInset={!!onEnterWorld}
      header={!onEnterWorld && (
        onBack ? (
          <TopBar
            title={prompt || selection ? undefined : capitalName ?? regionalTitle}
            ribbon={!!regionalTitle}
            backLabel={backLabel}
            onBack={onBack}>
            {prompt}
          </TopBar>
        ) : <WorldProgressBar earthOverview={earthOverview} />
      )}
      overlay={
        onEnterWorld ? (
          <WorldTitle onExplore={onEnterWorld} />
        ) : selection && (
          <CountrySheet
            key={selection.country.id}
            selection={selection}
            sceneImage={selectedScene}
            onClose={onClose}
            onExplore={onExplore}
          />
        )
      }>
      {children}
    </Screen>
  );
}

function WorldProgressBar({ earthOverview }: { earthOverview: boolean }) {
  const found = useSyncExternalStore(landmarkProgress.subscribe, landmarkProgress.getSnapshot);
  const progress = getWorldProgress(found);
  if (earthOverview) {
    return (
      <Panel skin="navy">
        <ProgressBar title="Countries completed" {...progress} tone="light" icon="globe" />
      </Panel>
    );
  }
  return (
    <TopBar compact>
      <ProgressBar title="Countries completed" {...progress} tone="light" compact />
    </TopBar>
  );
}
