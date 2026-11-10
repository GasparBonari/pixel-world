import { EmptyState } from '@/components/empty-state';
import { Screen } from '@/components/screen';

export default function ExploreScreen() {
  return (
    <Screen title="Explore" description="Find the places that will become part of your story.">
      <EmptyState
        label="DESTINATIONS"
        title="No destinations yet"
        description="Countries and cities will appear here as the world opens up. Your first adventure is still ahead."
        actionLabel="Back to world"
        href="/"
      />
    </Screen>
  );
}
