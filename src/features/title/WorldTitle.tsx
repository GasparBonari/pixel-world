import { TITLE_LOGO } from '@/data/title-logo.generated';
import { TitleLayer } from '@/ui';

export function WorldTitle({ onExplore }: { onExplore: () => void }) {
  return <TitleLayer logo={TITLE_LOGO} tagline="Explore · Discover · Collect" onExplore={onExplore} />;
}
