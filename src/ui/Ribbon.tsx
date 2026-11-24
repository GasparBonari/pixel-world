import { StyleSheet, View } from 'react-native';

import { Frames, Space, px } from '@/constants/theme';

import { PixelFrame } from './PixelFrame';
import { PixelIcon, type IconName } from './PixelIcon';
import { PixelText } from './PixelText';

export type RibbonProps = {
  label: string;
  icon?: IconName;
  /** parchment: screen titles ("PORTUGAL"). gold: a featured block ("Daily place"). */
  skin?: 'parchment' | 'gold';
};

/** A title banner with folded tails, centred over a panel or at the top of a screen. */
export function Ribbon({ label, icon, skin = 'parchment' }: RibbonProps) {
  const f = Frames[skin];
  return (
    <View style={styles.wrap} accessibilityRole="header">
      <View style={[styles.tail, styles.left, { backgroundColor: f.shade, borderColor: f.outline }]} />
      <View style={[styles.tail, styles.right, { backgroundColor: f.shade, borderColor: f.outline }]} />
      <PixelFrame skin={skin} depth={1} contentStyle={styles.content}>
        {icon && <PixelIcon name={icon} />}
        <PixelText variant="title" numberOfLines={1}>
          {label}
        </PixelText>
      </PixelFrame>
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { alignSelf: 'center', paddingHorizontal: px(6) },
  tail: { position: 'absolute', top: px(4), bottom: 0, width: px(10), borderWidth: px(1) },
  left: { left: 0 },
  right: { right: 0 },
  content: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Space.sm,
    paddingHorizontal: Space.lg,
    paddingVertical: Space.xs,
  },
});
