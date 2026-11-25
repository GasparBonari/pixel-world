import { Panel, PixelText, Screen, TopBar } from '@/ui';

export function QuestsView() {
  return (
    <Screen header={<TopBar title="Quests" compact />} bottomInset={false}>
      <Panel>
        <PixelText>Today’s featured place and open challenges will appear here.</PixelText>
      </Panel>
    </Screen>
  );
}
