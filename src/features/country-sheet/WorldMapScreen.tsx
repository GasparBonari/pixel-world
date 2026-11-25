import type { PropsWithChildren, ReactNode } from 'react';

import { Screen, TopBar } from '@/ui';

import { CountrySheet } from './CountrySheet';
import type { SelectableCountry } from './country-selection';

type Props = PropsWithChildren<{
  selection?: SelectableCountry;
  capitalName?: string;
  prompt?: ReactNode;
  onBack?: () => void;
  onClose: () => void;
  onExplore: () => void;
}>;

export function WorldMapScreen({ selection, capitalName, prompt, onBack, onClose, onExplore, children }: Props) {
  return (
    <Screen
      background="none"
      scroll={false}
      fullBleed
      header={onBack && (
        <TopBar
          title={prompt ? undefined : capitalName ?? 'World'}
          backLabel={capitalName ? 'Back to country' : 'Back to continent'}
          onBack={onBack}
        >
          {prompt}
        </TopBar>
      )}
      overlay={selection && (
        <CountrySheet
          key={selection.country.id}
          selection={selection}
          onClose={onClose}
          onExplore={onExplore}
        />
      )}>
      {children}
    </Screen>
  );
}
