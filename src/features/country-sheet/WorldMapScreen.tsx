import type { PropsWithChildren, ReactNode } from 'react';

import { WorldTitle } from '@/features/title/WorldTitle';
import { Screen, TopBar } from '@/ui';

import { CountrySheet } from './CountrySheet';
import type { SelectableCountry } from './country-selection';

type Props = PropsWithChildren<{
  selection?: SelectableCountry;
  capitalName?: string;
  prompt?: ReactNode;
  onEnterWorld?: () => void;
  onBack?: () => void;
  onClose: () => void;
  onExplore: () => void;
}>;

export function WorldMapScreen({
  selection, capitalName, prompt, onEnterWorld, onBack, onClose, onExplore, children,
}: Props) {
  return (
    <Screen
      background="none"
      scroll={false}
      fullBleed
      header={!onEnterWorld && onBack && (
        <TopBar
          title={prompt ? undefined : capitalName ?? 'World'}
          backLabel={capitalName ? 'Back to country' : 'Back to continent'}
          onBack={onBack}
        >
          {prompt}
        </TopBar>
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
