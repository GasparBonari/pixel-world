import type { PropsWithChildren, ReactNode } from 'react';
import { ScrollView, StyleSheet, View, type StyleProp, type ViewStyle } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { Frames, Palette, Size, Space, px } from '@/constants/theme';

import { IconButton } from './PixelButton';
import { PixelText } from './PixelText';

export type ScreenProps = PropsWithChildren<{
  /** Fixed at the top, under the status bar: usually a `TopBar`. */
  header?: ReactNode;
  /** Fixed at the bottom, above the home indicator: usually the `TabBar`. */
  footer?: ReactNode;
  /** Drawn over the body, between header and footer: a `BottomSheet`, notices pinned to a screen. */
  overlay?: ReactNode;
  /** Scroll the body (default) or let it fill the space (the map). */
  scroll?: boolean;
  /**
   * night: the night-sea colour, for Quests, Passport and other non-map screens.
   * none: transparent, for content drawn over the map.
   */
  background?: 'night' | 'space' | 'none';
  /** Extra layout for the body column (gaps, alignment). Padding and max width are already set. */
  contentStyle?: StyleProp<ViewStyle>;
}>;

const Backgrounds = { night: Palette.night, space: Palette.space, none: 'transparent' } as const;

/**
 * Every screen's outer layout: safe areas, background, a centred column no wider than
 * `Size.maxContentWidth`, an optional fixed header and footer, and an overlay layer.
 */
export function Screen({
  header,
  footer,
  overlay,
  scroll = true,
  background = 'night',
  contentStyle,
  children,
}: ScreenProps) {
  const insets = useSafeAreaInsets();
  const sides = { paddingLeft: insets.left, paddingRight: insets.right };
  const column = [styles.column, !footer && { paddingBottom: insets.bottom + Space.lg }, contentStyle];

  return (
    <View style={[styles.root, { backgroundColor: Backgrounds[background] }]}>
      {header ? (
        <View style={[styles.header, sides, { paddingTop: insets.top }]}>{header}</View>
      ) : (
        <View style={{ height: insets.top }} />
      )}
      <View style={[styles.body, sides]}>
        {scroll ? (
          <ScrollView contentContainerStyle={column} keyboardShouldPersistTaps="handled">
            {children}
          </ScrollView>
        ) : (
          <View style={[styles.fill, column]}>{children}</View>
        )}
        {overlay && (
          <View style={[StyleSheet.absoluteFill, !footer && { bottom: insets.bottom }]} pointerEvents="box-none">
            {overlay}
          </View>
        )}
      </View>
      {footer && <View style={[styles.footer, sides, { paddingBottom: insets.bottom }]}>{footer}</View>}
    </View>
  );
}

export type TopBarProps = PropsWithChildren<{
  /** Shows a back button when given. */
  onBack?: () => void;
  /** A screen title; omit when the bar holds progress instead. */
  title?: string;
  /** Right-side controls (an IconButton for settings or help). */
  actions?: ReactNode;
}>;

/**
 * The thin navy bar at the top of a screen: back, title or progress (children), actions.
 * Keep it to one line; no avatars, currencies, or levels.
 */
export function TopBar({ onBack, title, actions, children }: TopBarProps) {
  return (
    <View style={styles.bar}>
      {onBack && <IconButton icon="back" accessibilityLabel="Back" onPress={onBack} />}
      <View style={styles.fill}>
        {title && (
          <PixelText variant="heading" tone="light" numberOfLines={1} accessibilityRole="header">
            {title}
          </PixelText>
        )}
        {children}
      </View>
      {actions}
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1 },
  fill: { flex: 1 },
  body: { flex: 1 },
  column: {
    width: '100%',
    maxWidth: Size.maxContentWidth,
    alignSelf: 'center',
    padding: Space.lg,
    gap: Space.lg,
  },
  header: {
    backgroundColor: Palette.navyDeep,
    borderBottomWidth: px(1),
    borderBottomColor: Frames.navy.highlight,
  },
  footer: { backgroundColor: Palette.navyDeep },
  bar: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Space.md,
    paddingHorizontal: Space.lg,
    paddingVertical: Space.sm,
    minHeight: Size.touch + Space.lg,
  },
});
