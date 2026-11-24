import type { PropsWithChildren, ReactNode } from 'react';
import { StyleSheet, View, type StyleProp, type ViewStyle } from 'react-native';

import { Frames, Size, Space, px } from '@/constants/theme';

import { PixelFrame } from './PixelFrame';
import { PixelIcon, type IconName } from './PixelIcon';
import { PixelText } from './PixelText';

export type PanelProps = PropsWithChildren<{
  /** parchment: content (cards, challenges). navy: frame (sheets, bars over the map). */
  skin?: 'parchment' | 'navy';
  style?: StyleProp<ViewStyle>;
  contentStyle?: StyleProp<ViewStyle>;
}>;

/** A raised content surface. Children are laid out in a column with `Space.md` gaps. */
export function Panel({ skin = 'parchment', style, contentStyle, children }: PanelProps) {
  return (
    <PixelFrame skin={skin} depth={Size.panelDepth} style={style} contentStyle={[styles.panel, contentStyle]}>
      {children}
    </PixelFrame>
  );
}

export type SectionHeaderProps = {
  title: string;
  icon?: IconName;
  /** Honest count, e.g. "3 / 5 found". */
  count?: string;
  /** e.g. a "See all" link button. */
  action?: ReactNode;
  tone?: 'ink' | 'light';
};

/** A row heading inside a panel or sheet: icon, title, count, optional action on the right. */
export function SectionHeader({ title, icon, count, action, tone = 'ink' }: SectionHeaderProps) {
  return (
    <View style={styles.header} accessibilityRole="header">
      {icon && <PixelIcon name={icon} />}
      <PixelText variant="heading" tone={tone}>
        {title}
      </PixelText>
      {count && (
        <PixelText variant="caption" tone={tone === 'ink' ? 'inkSoft' : 'lightSoft'}>
          {count}
        </PixelText>
      )}
      <View style={styles.spacer} />
      {action}
    </View>
  );
}

/** A 1 UI pixel rule between rows. */
export function Divider({ skin = 'parchment' }: { skin?: 'parchment' | 'navy' }) {
  return <View style={{ height: px(1), backgroundColor: Frames[skin].shade }} />;
}

const styles = StyleSheet.create({
  panel: { padding: Space.lg, gap: Space.md },
  header: { flexDirection: 'row', alignItems: 'center', gap: Space.sm },
  spacer: { flex: 1 },
});
