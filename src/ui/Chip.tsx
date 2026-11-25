import type { PropsWithChildren } from 'react';
import { Pressable, StyleSheet, View } from 'react-native';
import { GestureDetector, useTapGesture, type TapGesture } from 'react-native-gesture-handler';
import type { SharedValue } from 'react-native-reanimated';

import { Size, Space, px } from '@/constants/theme';

import { PixelFrame } from './PixelFrame';
import { PixelIcon, type IconName } from './PixelIcon';
import { PixelText } from './PixelText';

export type ChipProps = {
  label: string;
  /** A second line, e.g. "9 / 12" under a continent name. */
  detail?: string;
  icon?: IconName;
  /** Use a caption-size label where map space is limited. */
  compact?: boolean;
  /** light: a place name over the map. navy: a continent/region label with a count. gold: selected. */
  skin?: 'light' | 'navy' | 'gold';
  onPress?: () => void;
  accessibilityLabel?: string;
  /** Use the containing map's tap gesture and suppress presses during its pan and pinch gestures. */
  mapTap?: { gesture: TapGesture; suppressed: SharedValue<boolean> };
};

/** A small label for map place names, counts and tags. */
export function Chip({ label, detail, icon, compact, skin = 'light', onPress, accessibilityLabel, mapTap }: ChipProps) {
  const frame = skin === 'light' ? 'chip' : skin;
  const tone = skin === 'navy' ? 'light' : 'ink';
  const content = (
    <PixelFrame skin={frame} style={styles.wrap} contentStyle={[styles.content, compact && styles.compact]}>
      {icon && <PixelIcon name={icon} />}
      <PixelText variant={compact ? 'caption' : 'label'} tone={tone} align="center">
        {label}
        {detail !== undefined && (
          <PixelText variant="caption" tone={skin === 'navy' ? 'lightSoft' : 'inkSoft'}>
            {'\n'}
            {detail}
          </PixelText>
        )}
      </PixelText>
    </PixelFrame>
  );
  if (!onPress) return content;
  const button = (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel={accessibilityLabel ?? label}
      onPress={onPress}
      pointerEvents={mapTap ? 'none' : undefined}
      style={styles.touch}>
      {content}
    </Pressable>
  );
  // For map chips, the tap gesture handles pointers and the button handles keyboard and assistive input.
  return mapTap ? <MapChipTap onPress={onPress} mapTap={mapTap}>{button}</MapChipTap> : button;
}

function MapChipTap({ onPress, mapTap, children }: PropsWithChildren<{
  onPress: () => void;
  mapTap: NonNullable<ChipProps['mapTap']>;
}>) {
  const tap = useTapGesture({
    block: mapTap.gesture,
    runOnJS: true,
    maxDistance: px(3),
    onDeactivate: (event) => {
      if (!event.canceled && !mapTap.suppressed.get()) onPress();
    },
  });

  return (
    <GestureDetector gesture={tap} touchAction="none">
      <View collapsable={false} style={styles.mapTouch}>
        {children}
      </View>
    </GestureDetector>
  );
}

const styles = StyleSheet.create({
  touch: { minHeight: Size.touch, minWidth: Size.touch, maxWidth: '100%', justifyContent: 'center', alignItems: 'center' },
  mapTouch: { maxWidth: '100%', cursor: 'pointer' },
  wrap: { alignSelf: 'flex-start' },
  content: { flexDirection: 'row', alignItems: 'center', gap: Space.xs, paddingHorizontal: Space.sm, paddingVertical: Space.xs },
  compact: { paddingVertical: px(1), paddingHorizontal: Space.xs },
});
