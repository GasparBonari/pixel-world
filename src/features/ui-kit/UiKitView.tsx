import { useState } from 'react';
import { ScrollView, StyleSheet, View } from 'react-native';

import { Size, Space } from '@/constants/theme';
import { CAPITAL_IMAGES } from '@/data/capital-images';
import {
  BottomSheet,
  Chip,
  CollectibleCard,
  CollectibleTile,
  ConfirmDialog,
  Divider,
  IconButton,
  Panel,
  PixelButton,
  PixelIcon,
  PixelModal,
  PixelText,
  ProgressBar,
  QuestRow,
  Ribbon,
  Screen,
  SectionHeader,
  SegmentedTabs,
  StepDots,
  TabBar,
  TopBar,
  useNotice,
  type IconName,
} from '@/ui';
import { UI_ICONS } from '@/ui/icons.generated';

/*
 * Development showcase of the pixel UI kit (docs/ui/UI_KIT.md). Every number below is DEMO
 * DATA for judging the components; real screens derive counts from saved records.
 */

const TABS = [
  { key: 'world', label: 'World', icon: 'globe' },
  { key: 'quests', label: 'Quests', icon: 'scroll' },
  { key: 'passport', label: 'Passport', icon: 'passport' },
] as const;

const SECTIONS = [
  { key: 'discover', label: 'Discover', icon: 'mountain' },
  { key: 'challenges', label: 'Find it', icon: 'star' },
  { key: 'info', label: 'Info', icon: 'book' },
] as const;

const ANSWERS = ['Lisbon', 'Porto', 'Coimbra', 'Faro'] as const;

const BELEM = {
  name: 'Belém Tower',
  kind: 'landmark',
  description:
    'A fortified tower built in the early 1500s at the mouth of the Tagus. Demo text: real cards take checked sentences from the content catalog.',
  source: { label: 'UNESCO World Heritage List', url: 'https://whc.unesco.org/en/list/263' },
} as const;

export function UiKitView() {
  const [tab, setTab] = useState<(typeof TABS)[number]['key']>('world');
  const [section, setSection] = useState<(typeof SECTIONS)[number]['key']>('discover');
  const [answer, setAnswer] = useState<string>();
  const [sheet, setSheet] = useState<'closed' | 'collapsed' | 'expanded'>('closed');
  const [cardOpen, setCardOpen] = useState(false);
  const [confirmOpen, setConfirmOpen] = useState(false);
  const notify = useNotice();

  return (
    <Screen
      header={
        <TopBar onBack={() => {}} actions={<IconButton icon="settings" accessibilityLabel="Settings" />}>
          <ProgressBar title="Europe discovered" value={18} total={44} segments={0} tone="light" />
        </TopBar>
      }
      footer={<TabBar items={TABS} value={tab} onChange={setTab} />}
      overlay={
        sheet !== 'closed' && (
          <BottomSheet
            title="Portugal"
            subtitle="Europe · Capital: Lisbon"
            icon="pin"
            expanded={sheet === 'expanded'}
            onExpandedChange={(open) => setSheet(open ? 'expanded' : 'collapsed')}
            onClose={() => setSheet('closed')}
            action={<PixelButton variant="primary" label="Explore Lisbon" icon="globe" block />}>
            <ProgressBar title="Country progress" value={3} total={7} tone="light" />
            <SectionHeader title="Landmarks" icon="landmark" count="3 / 5 found" tone="light" />
            <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.tiles}>
              <CollectibleTile name="Belém Tower" state="found" image={CAPITAL_IMAGES.lisbon} />
              <CollectibleTile name="Jerónimos" state="found" image={CAPITAL_IMAGES.lisbon} />
              <CollectibleTile name="Tram 28" state="found" image={CAPITAL_IMAGES.lisbon} />
              <CollectibleTile name="São Jorge Castle" state="missing" image={CAPITAL_IMAGES.lisbon} />
            </ScrollView>
          </BottomSheet>
        )
      }>
        <PixelText variant="caption" tone="lightSoft" align="center">
          UI kit preview — demo data
        </PixelText>

        {/* Overlays: sheet, dialogs, notices. */}
        <Panel skin="navy">
          <SectionHeader title="Overlays" icon="info" tone="light" />
          <PixelButton variant="navy" label="Country sheet" icon="pin" onPress={() => setSheet('collapsed')} />
          <PixelButton variant="navy" label="Find a collectible" icon="star" onPress={() => setCardOpen(true)} />
          <PixelButton
            variant="navy"
            label="Remove a visit (Undo)"
            icon="undo"
            onPress={() =>
              notify({
                message: 'Visit to Portugal removed.',
                icon: 'passport',
                action: { label: 'Undo', onPress: () => notify({ message: 'Visit restored.', icon: 'check' }) },
              })
            }
          />
          <PixelButton variant="navy" label="Reset progress" icon="settings" onPress={() => setConfirmOpen(true)} />
        </Panel>

        <Ribbon label="PORTUGAL" icon="pin" />

        {/* Country sheet. */}
        <Panel>
          <View style={styles.row}>
            <View style={styles.grow}>
              <PixelText variant="display">Portugal</PixelText>
              <PixelText variant="body" tone="inkSoft">
                Europe · Capital: Lisbon
              </PixelText>
            </View>
            <Chip label="Discovered" icon="check" />
          </View>
          <ProgressBar title="Country progress" value={3} total={7} />
          <SegmentedTabs items={SECTIONS} value={section} onChange={setSection} />
          <SectionHeader title="Landmarks" icon="landmark" count="3 / 5 found" />
          <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.tiles}>
            <CollectibleTile name="Belém Tower" state="found" image={CAPITAL_IMAGES.lisbon} onPress={() => {}} />
            <CollectibleTile name="Jerónimos" state="found" image={CAPITAL_IMAGES.lisbon} onPress={() => {}} />
            <CollectibleTile name="Tram 28" state="found" image={CAPITAL_IMAGES.lisbon} onPress={() => {}} />
            <CollectibleTile name="São Jorge Castle" state="missing" image={CAPITAL_IMAGES.lisbon} onPress={() => {}} />
            <CollectibleTile name="Hidden" state="locked" />
          </ScrollView>
          <Divider />
          <PixelButton variant="primary" label="Explore Lisbon" icon="globe" block />
        </Panel>

        {/* Challenge card. */}
        <Ribbon label="Daily place" icon="star" skin="gold" />
        <Panel>
          <PixelText variant="heading">Tap the capital of Portugal on the map.</PixelText>
          <PixelText variant="body" tone="inkSoft">
            Answer choices are for map questions only; most challenges are “find it” taps on the scene.
          </PixelText>
          <View style={styles.answers}>
            {ANSWERS.map((name, i) => (
              <PixelButton
                key={name}
                label={name}
                marker={'ABCD'[i]}
                variant={answer === name && name === 'Lisbon' ? 'success' : 'secondary'}
                onPress={() => setAnswer(name)}
                style={styles.answer}
              />
            ))}
          </View>
          <StepDots label="Today's discoveries" done={3} total={5} />
          <PixelText variant="label" align="center">
            Today: 3 / 5
          </PixelText>
        </Panel>

        {/* Quest list. */}
        <SectionHeader title="Country quests" icon="scroll" count="1 / 3 done" tone="light" />
        <QuestRow title="Find Belém Tower" description="Spot it on the Lisbon waterfront." icon="landmark" done />
        <QuestRow
          title="Wildlife of Portugal"
          description="Find 3 native animals on the board."
          icon="paw"
          done={false}
          progress="1 / 3 animals"
        />
        <QuestRow title="Serra da Estrela" description="Find the highest mountain." icon="mountain" done={false} />

        {/* Navy panel, chips over the map. */}
        <Panel skin="navy">
          <SectionHeader title="Map labels" icon="pin" tone="light" />
          <View style={styles.wrap}>
            <Chip label="Lisbon" icon="pin" />
            <Chip label="Europe" detail="18 / 44" skin="navy" />
            <Chip label="Selected" skin="gold" />
          </View>
          <PixelButton variant="navy" label="Navy action" icon="book" />
        </Panel>

        {/* Buttons. */}
        <Panel>
          <SectionHeader title="Buttons" />
          <PixelButton variant="primary" label="Primary (one per screen)" />
          <PixelButton variant="secondary" label="Secondary" icon="passport" />
          <PixelButton variant="success" label="Success" icon="check" />
          <PixelButton label="Disabled" disabled />
          <View style={styles.wrap}>
            <IconButton icon="back" accessibilityLabel="Back" skin="cream" />
            <IconButton icon="close" accessibilityLabel="Close" />
            <IconButton icon="plus" accessibilityLabel="Zoom in" />
            <IconButton icon="minus" accessibilityLabel="Zoom out" />
            <IconButton icon="help" accessibilityLabel="Help" skin="parchment" />
          </View>
        </Panel>

        {/* Type and icons. */}
        <Panel>
          <SectionHeader title="Type and icons" />
          <PixelText variant="display">Display 32</PixelText>
          <PixelText variant="title">Title 24</PixelText>
          <PixelText variant="heading">Heading 20</PixelText>
          <PixelText variant="label">Label 16</PixelText>
          <PixelText variant="body">Body 16: one or two checked sentences about a place.</PixelText>
          <PixelText variant="caption">Caption 12</PixelText>
          <View style={styles.wrap}>
            {(Object.keys(UI_ICONS) as IconName[]).map((name) => (
              <View key={name} style={styles.iconCell}>
                <PixelIcon name={name} />
                <PixelText variant="caption" tone="inkSoft">
                  {name}
                </PixelText>
              </View>
            ))}
          </View>
        </Panel>

      <PixelModal visible={cardOpen} onClose={() => setCardOpen(false)} label={BELEM.name}>
        <CollectibleCard
          {...BELEM}
          image={CAPITAL_IMAGES.lisbon}
          foundOn={new Date()}
          justFound
          onClose={() => setCardOpen(false)}
        />
      </PixelModal>
      <ConfirmDialog
        visible={confirmOpen}
        title="Reset all progress?"
        message="This removes every discovery, visit and stamp on this device. It can't be undone."
        confirmLabel="Reset progress"
        destructive
        onCancel={() => setConfirmOpen(false)}
        onConfirm={() => {
          setConfirmOpen(false);
          notify({ message: 'Demo only: nothing was reset.', icon: 'info' });
        }}
      />
    </Screen>
  );
}

const styles = StyleSheet.create({
  row: { flexDirection: 'row', alignItems: 'center', gap: Space.md },
  grow: { flex: 1 },
  tiles: { gap: Space.md, paddingTop: Space.sm, paddingRight: Space.sm },
  answers: { flexDirection: 'row', flexWrap: 'wrap', gap: Space.sm },
  answer: { flexGrow: 1, flexBasis: '45%' },
  wrap: { flexDirection: 'row', flexWrap: 'wrap', gap: Space.sm, alignItems: 'center' },
  iconCell: { alignItems: 'center', width: Size.touch + Space.lg, gap: Space.xs },
});
