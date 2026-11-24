import { StyleSheet } from 'react-native';

import { Space } from '@/constants/theme';

import { PixelFrame } from './PixelFrame';
import { PixelIcon, type IconName } from './PixelIcon';
import { PixelText } from './PixelText';

export type ChipProps = {
  label: string;
  /** A second line, e.g. "9 / 12" under a continent name. */
  detail?: string;
  icon?: IconName;
  /** light: a place name over the map. navy: a continent/region label with a count. gold: selected. */
  skin?: 'light' | 'navy' | 'gold';
};

/** A small, non-interactive label: map place names, counts, tags. */
export function Chip({ label, detail, icon, skin = 'light' }: ChipProps) {
  const frame = skin === 'light' ? 'chip' : skin;
  const tone = skin === 'navy' ? 'light' : 'ink';
  return (
    <PixelFrame skin={frame} style={styles.wrap} contentStyle={styles.content}>
      {icon && <PixelIcon name={icon} />}
      <PixelText variant="label" tone={tone} align="center">
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
}

const styles = StyleSheet.create({
  wrap: { alignSelf: 'flex-start' },
  content: { flexDirection: 'row', alignItems: 'center', gap: Space.xs, paddingHorizontal: Space.sm, paddingVertical: Space.xs },
});
