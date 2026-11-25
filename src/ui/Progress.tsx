import { StyleSheet, View } from 'react-native';

import { Palette, Space, px } from '@/constants/theme';

import { PixelFrame } from './PixelFrame';
import { PixelIcon, type IconName } from './PixelIcon';
import { PixelText, type TextTone } from './PixelText';

export type ProgressBarProps = {
  value: number;
  /** The real denominator. A total of 0 means "no content yet" and never reads as complete. */
  total: number;
  /** Visible title and accessibility label, e.g. "Country progress". */
  title: string;
  icon?: IconName;
  /** Show only the title and numerical count in one row. */
  compact?: boolean;
  /** Dividers in the bar; defaults to one per item up to 10. */
  segments?: number;
  /** Text colour for the title and count: ink on parchment, light on navy. */
  tone?: Extract<TextTone, 'ink' | 'light'>;
};

/**
 * A segmented green bar with its count always written beside it ("6 / 10"), so progress never
 * relies on colour alone.
 */
export function ProgressBar({ value, total, title, icon, compact, segments, tone = 'ink' }: ProgressBarProps) {
  const ratio = total > 0 ? Math.min(1, Math.max(0, value / total)) : 0;
  const parts = segments ?? (total > 0 && total <= 10 ? total : 0);
  const count = total > 0 ? `${value} / ${total}` : 'Coming soon';
  return (
    <View
      style={styles.progress}
      accessible
      accessibilityRole="progressbar"
      accessibilityLabel={title}
      aria-valuemin={total > 0 ? 0 : undefined}
      aria-valuemax={total > 0 ? total : undefined}
      aria-valuenow={total > 0 ? value : undefined}
      aria-valuetext={total > 0 ? `${value} of ${total}` : count}>
      {icon && <PixelIcon name={icon} />}
      <View style={styles.wrap}>
        <View style={styles.row}>
          <PixelText variant="label" tone={tone} style={styles.grow}>
            {title}
          </PixelText>
          <PixelText variant="label" tone={tone}>
            {count}
          </PixelText>
        </View>
        {!compact && (
          <PixelFrame skin="track" contentStyle={styles.track}>
            <View style={[styles.fill, { width: `${ratio * 100}%` }]}>
              <View style={styles.fillHighlight} />
              <View style={styles.fillShade} />
            </View>
            {Array.from({ length: Math.max(0, parts - 1) }, (_, i) => (
              <View key={i} style={[styles.divider, { left: `${((i + 1) / parts) * 100}%` }]} />
            ))}
          </PixelFrame>
        )}
      </View>
    </View>
  );
}

/** A row of steps for a short goal, e.g. today's 3 of 5 discoveries. */
export function StepDots({ done, total, label }: { done: number; total: number; label: string }) {
  return (
    <View
      style={styles.dots}
      accessible
      accessibilityLabel={`${label}: ${done} of ${total}`}>
      {Array.from({ length: total }, (_, i) =>
        i < done ? (
          <PixelFrame key={i} skin="green" contentStyle={styles.dot}>
            <PixelIcon name="check" />
          </PixelFrame>
        ) : (
          <PixelFrame key={i} skin="track" contentStyle={styles.dot} />
        )
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  progress: { flexDirection: 'row', alignItems: 'center', alignSelf: 'stretch', gap: Space.sm },
  wrap: { flex: 1, gap: Space.xs },
  row: { flexDirection: 'row', alignItems: 'baseline', gap: Space.sm },
  grow: { flex: 1 },
  track: { padding: px(1), height: px(8) },
  fill: { height: '100%', backgroundColor: Palette.green },
  fillHighlight: { height: px(1), backgroundColor: Palette.greenLight },
  fillShade: { position: 'absolute', bottom: 0, left: 0, right: 0, height: px(1), backgroundColor: Palette.greenShade },
  divider: { position: 'absolute', top: px(1), bottom: px(1), width: px(1), backgroundColor: Palette.navyDeep },
  dots: { flexDirection: 'row', gap: Space.sm, justifyContent: 'center' },
  dot: { width: px(16), height: px(16), alignItems: 'center', justifyContent: 'center', padding: 0 },
});
