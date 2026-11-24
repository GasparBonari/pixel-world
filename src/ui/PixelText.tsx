import { StyleSheet, Text, type TextProps } from 'react-native';

import { Palette, Type, type TypeVariant } from '@/constants/theme';

const Tones = {
  /** Dark text on parchment, cream, gold, and chips. */
  ink: Palette.ink,
  inkSoft: Palette.inkSoft,
  /** Light text on navy and over the map. */
  light: Palette.snow,
  lightSoft: Palette.mist,
  gold: Palette.goldLight,
  success: Palette.greenShade,
  danger: Palette.redShade,
  muted: Palette.muted,
} as const;

export type TextTone = keyof typeof Tones;

export type PixelTextProps = TextProps & {
  variant?: TypeVariant;
  tone?: TextTone;
  align?: 'left' | 'center' | 'right';
  /** A 1 UI pixel dark edge so light text reads over the busy map. */
  outlined?: boolean;
};

/** All interface text. Sizes come from the fixed `Type` scale; there is no fontSize prop. */
export function PixelText({ variant = 'body', tone = 'ink', align, outlined, style, ...rest }: PixelTextProps) {
  return (
    <Text
      {...rest}
      style={[
        Type[variant],
        styles.base,
        { color: Tones[tone] },
        align && { textAlign: align },
        outlined && styles.outlined,
        style,
      ]}
    />
  );
}

const styles = StyleSheet.create({
  // Custom font files carry their own weight; a synthetic fontWeight would blur the pixels.
  base: { fontWeight: 'normal' },
  outlined: {
    textShadowColor: Palette.space,
    textShadowOffset: { width: 0, height: 2 },
    textShadowRadius: 0.1,
  },
});
