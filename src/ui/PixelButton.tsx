import { Pressable, StyleSheet, type StyleProp, type ViewStyle } from 'react-native';

import { Size, Space, px, type FrameSkin } from '@/constants/theme';

import { PixelFrame } from './PixelFrame';
import { PixelIcon, type IconName } from './PixelIcon';
import { PixelText } from './PixelText';

/**
 * primary: gold, the ONE main action on a screen ("Explore Portugal").
 * secondary: cream, every other action and answer choices.
 * success: green, only for a correct/completed state.
 * navy: actions on the navy frame (top bar, sheets).
 * danger: red, only the confirm button of a destructive ConfirmDialog.
 */
export type ButtonVariant = 'primary' | 'secondary' | 'success' | 'navy' | 'danger';

const Skins: Record<ButtonVariant, FrameSkin> = {
  primary: 'gold',
  secondary: 'cream',
  success: 'green',
  navy: 'navy',
  danger: 'red',
};

export type PixelButtonProps = {
  label: string;
  onPress?: () => void;
  variant?: ButtonVariant;
  /** Icon before the label. Trailing chevrons are not used; the label says where it goes. */
  icon?: IconName;
  /** A letter or number badge before the label, as in answer choices (A, B, C…). */
  marker?: string;
  disabled?: boolean;
  /** Stretch to the parent's width. */
  block?: boolean;
  accessibilityHint?: string;
  style?: StyleProp<ViewStyle>;
};

/**
 * A raised pixel button. Pressing drops it 2 UI pixels onto its lip in one step (no easing),
 * so it needs no reduced-motion handling.
 */
export function PixelButton({
  label,
  onPress,
  variant = 'secondary',
  icon,
  marker,
  disabled = false,
  block = false,
  accessibilityHint,
  style,
}: PixelButtonProps) {
  const skin = disabled ? 'cream' : Skins[variant];
  const tone = variant === 'secondary' || variant === 'primary' ? 'ink' : 'light';
  return (
    <Pressable
      onPress={onPress}
      disabled={disabled}
      accessibilityRole="button"
      accessibilityLabel={label}
      accessibilityHint={accessibilityHint}
      accessibilityState={{ disabled }}
      style={[block && styles.block, disabled && styles.disabled, style]}>
      {({ pressed }) => (
        <PixelFrame skin={skin} depth={Size.buttonDepth} pressed={pressed} contentStyle={styles.content}>
          {marker !== undefined && (
            <PixelFrame skin="chip" contentStyle={styles.marker}>
              <PixelText variant="label" align="center">
                {marker}
              </PixelText>
            </PixelFrame>
          )}
          {icon && <PixelIcon name={icon} />}
          <PixelText
            variant="label"
            tone={disabled ? 'muted' : tone}
            align={marker !== undefined ? 'left' : 'center'}
            style={marker !== undefined && styles.grow}
            numberOfLines={2}>
            {label}
          </PixelText>
        </PixelFrame>
      )}
    </Pressable>
  );
}

export type IconButtonProps = {
  icon: IconName;
  /** Required: icon-only buttons have no visible text. */
  accessibilityLabel: string;
  onPress?: () => void;
  skin?: 'navy' | 'parchment' | 'cream';
  style?: StyleProp<ViewStyle>;
};

/** A square icon button (back, close, zoom), at least 48 pt. */
export function IconButton({ icon, accessibilityLabel, onPress, skin = 'navy', style }: IconButtonProps) {
  return (
    <Pressable onPress={onPress} accessibilityRole="button" accessibilityLabel={accessibilityLabel} style={style}>
      {({ pressed }) => (
        <PixelFrame skin={skin} depth={Size.buttonDepth} pressed={pressed} contentStyle={styles.square}>
          <PixelIcon name={icon} />
        </PixelFrame>
      )}
    </Pressable>
  );
}

const styles = StyleSheet.create({
  block: { alignSelf: 'stretch' },
  disabled: { opacity: 0.7 },
  content: {
    minHeight: Size.touch - px(Size.buttonDepth),
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: Space.sm,
    paddingHorizontal: Space.lg,
    paddingVertical: Space.xs,
  },
  marker: { minWidth: px(12), paddingVertical: 0 },
  grow: { flex: 1 },
  square: {
    width: Size.touch,
    height: Size.touch - px(Size.buttonDepth),
    alignItems: 'center',
    justifyContent: 'center',
    padding: 0,
  },
});

