/**
 * Shared game palette and layout tokens for native and web screens.
 */

import '@/global.css';

import { Platform } from 'react-native';

export const Colors = {
  light: {
    text: '#233C31',
    background: '#F5F3E8',
    backgroundElement: '#FFFEF8',
    backgroundSelected: '#DFE8D4',
    textSecondary: '#626B60',
    accent: '#2E6347',
    textOnAccent: '#FFFEF8',
    border: '#D4DACB',
  },
  dark: {
    text: '#EAF1DF',
    background: '#111F1A',
    backgroundElement: '#192B23',
    backgroundSelected: '#2A4431',
    textSecondary: '#B2C2AF',
    accent: '#A8D59A',
    textOnAccent: '#111F1A',
    border: '#365043',
  },
} as const;

export type ThemeColor = keyof typeof Colors.light & keyof typeof Colors.dark;

export const WorldColors = {
  space: '#090D16',
} as const;

/** Pixelify Sans (OFL 1.1), loaded once by the root layout. Font names, not CSS stacks. */
export const PixelFonts = {
  regular: 'PixelifySans_400Regular',
  bold: 'PixelifySans_700Bold',
} as const;

export const Fonts = Platform.select({
  ios: {
    /** iOS `UIFontDescriptorSystemDesignDefault` */
    sans: 'system-ui',
    /** iOS `UIFontDescriptorSystemDesignSerif` */
    serif: 'ui-serif',
    /** iOS `UIFontDescriptorSystemDesignRounded` */
    rounded: 'ui-rounded',
    /** iOS `UIFontDescriptorSystemDesignMonospaced` */
    mono: 'ui-monospace',
  },
  default: {
    sans: 'normal',
    serif: 'serif',
    rounded: 'normal',
    mono: 'monospace',
  },
  web: {
    sans: 'var(--font-display, system-ui)',
    serif: 'var(--font-serif, serif)',
    rounded: 'var(--font-rounded, system-ui)',
    mono: 'var(--font-mono, monospace)',
  },
});

export const Spacing = {
  half: 2,
  one: 4,
  two: 8,
  three: 16,
  four: 24,
  five: 32,
  six: 64,
} as const;

export const BottomTabInset = Platform.select({ ios: 50, android: 80 }) ?? 0;
export const MaxContentWidth = 800;
