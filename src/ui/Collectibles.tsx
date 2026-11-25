import { Image, Pressable, StyleSheet, View, type ImageSourcePropType } from 'react-native';

import { Palette, Size, Space, px } from '@/constants/theme';

import { PixelFrame } from './PixelFrame';
import { PixelIcon, type IconName } from './PixelIcon';
import { PixelText } from './PixelText';

/** found: earned. missing: can be found now. locked: not reachable yet. */
export type CollectibleState = 'found' | 'missing' | 'locked';

export type CollectibleTileProps = {
  name: string;
  state: CollectibleState;
  /** A crop of the capital scene or its 4× study. Pixel art: keep whole-number scales. */
  image?: ImageSourcePropType;
  onPress?: () => void;
};

const StateLabel: Record<CollectibleState, string> = {
  found: 'found',
  missing: 'not found yet',
  locked: 'locked',
};
const StateIcon: Record<CollectibleState, IconName> = {
  found: 'star',
  missing: 'help',
  locked: 'lock',
};

/** A collection card: picture, name, and a check (found) or lock (locked) badge. */
export function CollectibleTile({ name, state, image, onPress }: CollectibleTileProps) {
  const hidden = state !== 'found';
  return (
    <Pressable
      onPress={onPress}
      disabled={!onPress}
      accessibilityRole="button"
      accessibilityLabel={`${name}, ${StateLabel[state]}`}
      style={styles.tile}>
      {({ pressed }) => (
        <>
          <PixelFrame
            skin={state === 'found' ? 'gold' : 'navy'}
            depth={1}
            pressed={pressed}
            contentStyle={styles.content}>
            <View style={styles.picture}>
              {image && !(state === 'locked') ? (
                <Image source={image} style={[styles.image, hidden && styles.dim]} resizeMode="cover" />
              ) : (
                <PixelIcon name={StateIcon[state]} />
              )}
            </View>
            <PixelText variant="caption" tone={state === 'found' ? 'ink' : 'light'} align="center" numberOfLines={2}>
              {state === 'locked' ? '???' : name}
            </PixelText>
          </PixelFrame>
          {state !== 'missing' && (
            <View style={styles.badge}>
              <Badge icon={state === 'found' ? 'check' : 'lock'} />
            </View>
          )}
        </>
      )}
    </Pressable>
  );
}

/** A small icon badge, pinned to a corner of a tile or button. */
export function Badge({ icon }: { icon: IconName }) {
  return (
    <PixelFrame skin="chip" contentStyle={styles.badgeContent}>
      <PixelIcon name={icon} />
    </PixelFrame>
  );
}

export type QuestRowProps = {
  title: string;
  description: string;
  icon: IconName;
  done: boolean;
  /** Honest progress text, e.g. "2 / 3 animals". */
  progress?: string;
  onPress?: () => void;
};

/** One challenge in a quest list: icon, title, one line of description, and a done box. */
export function QuestRow({ title, description, icon, done, progress, onPress }: QuestRowProps) {
  return (
    <Pressable
      onPress={onPress}
      disabled={!onPress}
      accessibilityRole="button"
      accessibilityLabel={`${title}. ${description}`}
      accessibilityState={{ checked: done }}>
      {({ pressed }) => (
        <PixelFrame skin="cream" depth={1} pressed={pressed} contentStyle={styles.quest}>
          <PixelFrame skin="parchment" contentStyle={styles.questIcon}>
            <PixelIcon name={icon} />
          </PixelFrame>
          <View style={styles.questText}>
            <PixelText variant="label">{title}</PixelText>
            <PixelText variant="caption" tone="inkSoft">
              {description}
            </PixelText>
            {progress && (
              <PixelText variant="caption" tone="success">
                {progress}
              </PixelText>
            )}
          </View>
          <PixelFrame skin={done ? 'green' : 'chip'} contentStyle={styles.box}>
            {done && <PixelIcon name="check" />}
          </PixelFrame>
        </PixelFrame>
      )}
    </Pressable>
  );
}

const TILE = px(44);

const styles = StyleSheet.create({
  tile: { width: TILE },
  content: { gap: Space.xs, padding: px(2) },
  picture: {
    height: px(32),
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: Palette.navyDeep,
    overflow: 'hidden',
  },
  image: { width: '100%', height: '100%' },
  dim: { opacity: 0.35 },
  badge: { position: 'absolute', top: -px(3), right: -px(3) },
  badgeContent: { padding: 0 },
  quest: { flexDirection: 'row', alignItems: 'center', gap: Space.md, padding: Space.sm },
  questIcon: { width: Size.touch - px(4), height: Size.touch - px(4), alignItems: 'center', justifyContent: 'center', padding: 0 },
  questText: { flex: 1, gap: px(1) },
  box: { width: px(16), height: px(16), alignItems: 'center', justifyContent: 'center', padding: 0 },
});
