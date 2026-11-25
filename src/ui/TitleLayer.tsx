import { useEffect, useRef, useState, type ComponentRef } from 'react';
import {
  AccessibilityInfo,
  Image,
  Platform,
  StyleSheet,
  View,
  useWindowDimensions,
  type ImageSourcePropType,
} from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { Space, U, px } from '@/constants/theme';

import { PixelButton } from './PixelButton';
import { PixelText } from './PixelText';
import { Ribbon } from './Ribbon';
import { useSteps } from './use-steps';

export type TitleLayerProps = {
  /** Dimensions are in artwork pixels. Source densities are generated at 2, 4 and 6 times that size. */
  logo: { source: ImageSourcePropType; name: string; width: number; height: number };
  tagline: string;
  onExplore: () => void;
};

const EXIT = [
  { offset: 0, opacity: 1 },
  { offset: px(2), opacity: 1 },
  { offset: px(6), opacity: 0.75 },
  { offset: px(12), opacity: 0.4 },
] as const;
const webSampling = Platform.select({ web: { imageRendering: 'pixelated' } });
const headingStyle = Platform.select({ web: { outlineStyle: 'solid' as const, outlineWidth: 0 } });

/** A launch overlay that leaves the scene visible between the title and the action. */
export function TitleLayer({ logo, tagline, onExplore }: TitleLayerProps) {
  const insets = useSafeAreaInsets();
  const { width, height } = useWindowDimensions();
  const heading = useRef<ComponentRef<typeof View>>(null);
  const [exiting, setExiting] = useState(false);
  const frame = useSteps(exiting ? EXIT.length + 1 : 1, exiting);
  const finished = exiting && frame === EXIT.length;
  const reported = useRef(false);

  useEffect(() => {
    const id = requestAnimationFrame(() => {
      if (!heading.current) return;
      if (Platform.OS === 'web') heading.current.focus();
      else AccessibilityInfo.sendAccessibilityEvent(heading.current, 'focus');
    });
    return () => cancelAnimationFrame(id);
  }, []);

  useEffect(() => {
    if (finished && !reported.current) {
      reported.current = true;
      onExplore();
    }
  }, [finished, onExplore]);

  if (finished) return null;
  const { offset, opacity } = EXIT[frame];
  const fits = px(logo.width) <= width - insets.left - insets.right - 2 * Space.lg;
  const top = px(Math.min(48, Math.floor(height * 0.11 / U)));
  const bottom = px(Math.min(36, Math.floor(height * 0.09 / U)));

  return (
    <View style={[styles.layer, { paddingTop: insets.top + top, paddingBottom: bottom }]} pointerEvents="box-none">
      <View style={[styles.title, { opacity, transform: [{ translateY: -offset }] }]} pointerEvents="none">
        <View
          ref={heading}
          accessible
          accessibilityRole="image"
          accessibilityLabel={logo.name}
          style={headingStyle}
          tabIndex={Platform.OS === 'web' ? -1 : undefined}>
          {fits ? (
            <Image
              source={logo.source}
              accessible={false}
              aria-hidden
              resizeMode="stretch"
              style={{ width: px(logo.width), height: px(logo.height), ...webSampling }}
            />
          ) : (
            <PixelText variant="display" tone="gold" align="center" outlined aria-hidden>
              {logo.name}
            </PixelText>
          )}
        </View>
        <Ribbon label={tagline} variant="label" />
      </View>
      <View style={[styles.action, { opacity, transform: [{ translateY: offset }] }]}>
        <PixelButton
          label="Explore"
          icon="globe"
          variant="primary"
          block
          disabled={exiting}
          onPress={() => setExiting(true)}
        />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  layer: { flex: 1, justifyContent: 'space-between', alignItems: 'center', paddingHorizontal: Space.lg },
  title: { alignItems: 'center', gap: Space.sm, maxWidth: '100%' },
  action: { width: px(104), maxWidth: '100%' },
});
