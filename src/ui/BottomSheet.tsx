import { useEffect, useRef, useState, type ComponentRef, type PropsWithChildren, type ReactNode } from 'react';
import { AccessibilityInfo, Image, Platform, Pressable, ScrollView, StyleSheet, View, useWindowDimensions, type ImageSourcePropType } from 'react-native';
import { GestureDetector, usePanGesture } from 'react-native-gesture-handler';

import { Frames, Motion, Palette, Size, Space, px } from '@/constants/theme';

import { IconButton } from './PixelButton';
import { PixelFrame } from './PixelFrame';
import { PixelIcon, type IconName } from './PixelIcon';
import { PixelText } from './PixelText';

export type BottomSheetProps = PropsWithChildren<{
  title: string;
  subtitle?: string;
  icon?: IconName;
  /** A wide scene illustration at the top of the expanded scrolling body. */
  artwork?: ImageSourcePropType;
  /** Controlled: the screen owns whether the sheet is open, so it survives re-renders. */
  expanded: boolean;
  onExpandedChange: (expanded: boolean) => void;
  /** Shows a close button; swiping down on a collapsed sheet also closes it. */
  onClose?: () => void;
  /** Always visible under the title, even collapsed: usually the screen's one primary button. */
  action?: ReactNode;
}>;

/** A swipe counts when it moves this far or this fast (points, points per second). */
const SWIPE_DISTANCE = px(12);
const SWIPE_SPEED = 600;

/**
 * A navy sheet anchored to the bottom of its parent, over the map. Collapsed it shows the title
 * and the action; expanded it adds the scrolling children between them, never taller than half the screen.
 * Tap or swipe the handle to change state. The state jumps in one step (stepped motion), so
 * reduce motion needs nothing extra. Render it in `Screen`'s `overlay` so the map stays mounted.
 */
export function BottomSheet({
  title,
  subtitle,
  icon,
  artwork,
  expanded,
  onExpandedChange,
  onClose,
  action,
  children,
}: BottomSheetProps) {
  const { height } = useWindowDimensions();
  const titleButton = useRef<ComponentRef<typeof Pressable>>(null);
  const [headerHeight, setHeaderHeight] = useState(0);
  const [actionHeight, setActionHeight] = useState(0);
  const bodyMax = Math.max(0, height * Motion.sheetMaxShare - headerHeight - actionHeight - Space.lg);

  useEffect(() => {
    if (Platform.OS === 'web') {
      // Web can send a follow-up mouse event after a touch. Focus after that tap sequence.
      let frame = requestAnimationFrame(() => {
        frame = requestAnimationFrame(() => titleButton.current?.focus());
      });
      return () => cancelAnimationFrame(frame);
    }
    AccessibilityInfo.announceForAccessibility(title);
  }, [title]);

  const swipe = usePanGesture({
    runOnJS: true,
    minDistance: px(4),
    onDeactivate: (event) => {
      const up = event.translationY < -SWIPE_DISTANCE || event.velocityY < -SWIPE_SPEED;
      const down = event.translationY > SWIPE_DISTANCE || event.velocityY > SWIPE_SPEED;
      if (up && !expanded) onExpandedChange(true);
      else if (down && expanded) onExpandedChange(false);
      else if (down && onClose) onClose();
    },
  });

  return (
    <View style={styles.anchor} pointerEvents="box-none">
      <PixelFrame skin="navy" style={styles.sheet} contentStyle={styles.frame}>
        <GestureDetector gesture={swipe}>
          <View onLayout={(e) => setHeaderHeight(e.nativeEvent.layout.height)}>
            {/* The handle is a visual tap/swipe area; screen readers use the title button below. */}
            <Pressable
              onPress={() => onExpandedChange(!expanded)}
              accessible={false}
              aria-hidden
              importantForAccessibility="no"
              tabIndex={-1}
              style={styles.handleRow}>
              <View style={styles.handle} />
            </Pressable>
            <View style={styles.titleRow}>
              {/* Siblings, not nested: VoiceOver merges a button's children into one element. */}
              <Pressable
                ref={titleButton}
                onPress={() => onExpandedChange(!expanded)}
                accessibilityRole="button"
                accessibilityLabel={title}
                accessibilityHint={[subtitle, expanded ? 'Collapses the details' : 'Shows the details'].filter(Boolean).join('. ')}
                aria-expanded={expanded}
                style={styles.toggle}>
                {icon && <PixelIcon name={icon} />}
                <View style={styles.titleText}>
                  <PixelText variant="title" tone="light" numberOfLines={1}>
                    {title}
                  </PixelText>
                  {subtitle && (
                    <PixelText variant="caption" tone="lightSoft" numberOfLines={1}>
                      {subtitle}
                    </PixelText>
                  )}
                </View>
              </Pressable>
              {onClose && <IconButton icon="close" accessibilityLabel={`Close ${title}`} onPress={onClose} />}
            </View>
          </View>
        </GestureDetector>
        {expanded && (
          <ScrollView style={{ maxHeight: bodyMax }} contentContainerStyle={[styles.body, !!artwork && styles.illustratedBody]}>
            {!!artwork && (
              <PixelFrame skin="navy" contentStyle={styles.artworkFrame}>
                <Image source={artwork} style={styles.artwork} resizeMode="cover" accessible={false} />
              </PixelFrame>
            )}
            {children}
          </ScrollView>
        )}
        {action && (
          <View style={styles.action} onLayout={(e) => setActionHeight(e.nativeEvent.layout.height)}>
            {action}
          </View>
        )}
      </PixelFrame>
    </View>
  );
}

const styles = StyleSheet.create({
  anchor: { flex: 1, justifyContent: 'flex-end', alignItems: 'center', paddingHorizontal: Space.sm },
  sheet: { width: '100%', maxWidth: Size.maxContentWidth },
  frame: { paddingHorizontal: Space.lg, paddingTop: 0, paddingBottom: Space.lg },
  handleRow: { alignItems: 'center', justifyContent: 'center', height: Space.lg },
  handle: { width: px(20), height: px(2), backgroundColor: Frames.navy.highlight },
  titleRow: { flexDirection: 'row', alignItems: 'center', gap: Space.md, paddingBottom: Space.md },
  toggle: { flex: 1, flexDirection: 'row', alignItems: 'center', gap: Space.md, minHeight: Size.touch },
  titleText: { flex: 1 },
  action: { paddingTop: Space.md },
  artworkFrame: { overflow: 'hidden' },
  artwork: { width: '100%', height: px(36), ...Platform.select({ web: { imageRendering: 'pixelated' } }) },
  illustratedBody: { gap: Space.sm, paddingVertical: Space.sm },
  body: {
    gap: Space.md,
    paddingVertical: Space.md,
    borderTopWidth: px(1),
    borderTopColor: Palette.navyRaised,
  },
});
