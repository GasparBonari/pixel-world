import type { PropsWithChildren, ReactNode } from 'react';
import { ScrollView, StyleSheet, View, type StyleProp, type ViewStyle } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { Frames, Palette, Size, Space, px } from '@/constants/theme';

import { IconButton } from './PixelButton';
import { PixelText } from './PixelText';
import { Ribbon } from './Ribbon';

export type ScreenProps = PropsWithChildren<{
  /** Fixed at the top, under the status bar: usually a `TopBar`. */
  header?: ReactNode;
  /** Give a framed header in a full-bleed scene space around it. */
  floatingHeader?: boolean;
  /** Fixed at the bottom, above the home indicator: usually the `TabBar`. */
  footer?: ReactNode;
  /** Drawn over the body, between header and footer: a `BottomSheet`, notices pinned to a screen. */
  overlay?: ReactNode;
  /** Scroll the body (default) or let it fill the space (the map). */
  scroll?: boolean;
  /** Let a non-scrolling scene fill the screen, with the header over it. */
  fullBleed?: boolean;
  /** Set false when an outer navigator already reserves the bottom safe area. */
  bottomInset?: boolean;
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
  floatingHeader = false,
  footer,
  overlay,
  scroll = true,
  fullBleed = false,
  bottomInset = true,
  background = 'night',
  contentStyle,
  children,
}: ScreenProps) {
  const insets = useSafeAreaInsets();
  const bottom = bottomInset ? insets.bottom : 0;
  const sides = { paddingLeft: insets.left, paddingRight: insets.right };
  const column = fullBleed && !scroll
    ? contentStyle
    : [styles.column, !footer && { paddingBottom: bottom + Space.lg }, contentStyle];
  const floating = fullBleed && floatingHeader;

  return (
    <View style={[styles.root, { backgroundColor: Backgrounds[background] }]}>
      {header ? (
        <View
          pointerEvents={floating ? 'box-none' : undefined}
          style={[!floating && styles.header, fullBleed && styles.overlaidHeader, sides, { paddingTop: insets.top }]}>
          {floating ? <View style={styles.floatingHeader} pointerEvents="box-none">{header}</View> : header}
        </View>
      ) : (
        !fullBleed && <View style={{ height: insets.top }} />
      )}
      <View style={[styles.body, !fullBleed && sides]}>
        {scroll ? (
          <ScrollView contentContainerStyle={column} keyboardShouldPersistTaps="handled">
            {children}
          </ScrollView>
        ) : (
          <View style={[styles.fill, column]}>{children}</View>
        )}
        {overlay && (
          <View
            style={[StyleSheet.absoluteFill, fullBleed && sides, !footer && { bottom }]}
            pointerEvents="box-none">
            {overlay}
          </View>
        )}
      </View>
      {footer && <View style={[styles.footer, sides, { paddingBottom: bottom }]}>{footer}</View>}
    </View>
  );
}

export type TopBarProps = PropsWithChildren<{
  /** Shows a back button when given. */
  onBack?: () => void;
  /** Name the destination when a screen has multiple levels. */
  backLabel?: string;
  /** A screen title; omit when the bar holds progress instead. */
  title?: string;
  /** Centre a parchment title and use a cream back button over the map. */
  ribbon?: boolean;
  /** Use the height of the content for a one-line label or count. */
  compact?: boolean;
  /** Right-side controls (an IconButton for settings or help). */
  actions?: ReactNode;
}>;

/**
 * The thin navy bar at the top of a screen: back, title or progress (children), actions.
 * Keep it to one line; no avatars, currencies, or levels.
 */
export function TopBar({ onBack, backLabel = 'Back', title, ribbon, compact, actions, children }: TopBarProps) {
  if (ribbon) {
    return (
      <View style={styles.ribbonBar} pointerEvents="box-none">
        {onBack && <IconButton icon="back" skin="cream" accessibilityLabel={backLabel} onPress={onBack} />}
        {title && (
          <View style={styles.fill} pointerEvents="none">
            <Ribbon label={title} />
          </View>
        )}
        {actions ?? <View style={styles.ribbonEnd} pointerEvents="none" />}
      </View>
    );
  }

  return (
    <View style={[styles.bar, !compact && styles.barHeight]}>
      {onBack && <IconButton icon="back" accessibilityLabel={backLabel} onPress={onBack} />}
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
  overlaidHeader: { position: 'absolute', top: 0, left: 0, right: 0, zIndex: 1 },
  floatingHeader: { width: '100%', maxWidth: Size.maxContentWidth, alignSelf: 'center', padding: Space.md },
  footer: { backgroundColor: Palette.navyDeep },
  bar: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Space.md,
    paddingHorizontal: Space.lg,
    paddingVertical: Space.sm,
  },
  barHeight: { minHeight: Size.touch + Space.lg },
  ribbonBar: { minHeight: Size.touch, flexDirection: 'row', alignItems: 'center', gap: Space.sm },
  ribbonEnd: { width: Size.touch },
});
