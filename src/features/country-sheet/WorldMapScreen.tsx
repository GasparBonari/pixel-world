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
  capitalName?: string;
  prompt?: ReactNode;
  onEnterWorld?: () => void;
  onBack?: () => void;
  onClose: () => void;
  onExplore: () => void;
}>;

export function WorldMapScreen({
  earthOverview, selection, capitalName, prompt, onEnterWorld, onBack, onClose, onExplore, children,
}: Props) {
  return (
    <Screen
      background="none"
      scroll={false}
      fullBleed
      floatingHeader={earthOverview}
      bottomInset={!!onEnterWorld}
      header={!onEnterWorld && (
        onBack ? (
          <TopBar
            title={prompt ? undefined : capitalName ?? 'World'}
            backLabel={capitalName ? 'Back to country' : 'Back to continent'}
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
