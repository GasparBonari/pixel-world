import { Image, type ImageStyle, type StyleProp } from 'react-native';

import { Size } from '@/constants/theme';

import { UI_ICONS, type IconName } from './icons.generated';

export type { IconName };

/**
 * A pixel icon from assets/ui/icons (built by scripts/art/build_ui_icons.py). Always 12×12 UI
 * pixels (24 pt); each screen density gets its own pre-scaled file, so the pixels stay sharp.
 * Decorative by default: give the button or row around it the accessibility label.
 */
export function PixelIcon({ name, style }: { name: IconName; style?: StyleProp<ImageStyle> }) {
  return (
    <Image
      source={UI_ICONS[name]}
      style={[{ width: Size.icon, height: Size.icon }, style]}
      accessibilityElementsHidden
      importantForAccessibility="no"
    />
  );
}
