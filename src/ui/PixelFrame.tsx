import type { PropsWithChildren } from 'react';
import { StyleSheet, View, type StyleProp, type ViewStyle } from 'react-native';

import { Frames, px, type FrameSkin } from '@/constants/theme';

export type PixelFrameProps = PropsWithChildren<{
  skin: FrameSkin;
  /** Thickness under the frame in UI pixels (0 = flat). Buttons use Size.buttonDepth. */
  depth?: number;
  /** Pressed frames sink by `depth`, covering their lip. */
  pressed?: boolean;
  /** Outer box: width, flex, margins. */
  style?: StyleProp<ViewStyle>;
  /** Inner box: padding, layout of the children. */
  contentStyle?: StyleProp<ViewStyle>;
}>;

/** Two rectangles that together make a box with 1 UI pixel notched corners. */
function Silhouette({ color, inset = 0 }: { color: string; inset?: number }) {
  const i = px(inset);
  return (
    <>
      <View style={[styles.abs, { top: i + px(1), bottom: i + px(1), left: i, right: i, backgroundColor: color }]} />
      <View style={[styles.abs, { top: i, bottom: i, left: i + px(1), right: i + px(1), backgroundColor: color }]} />
    </>
  );
}

/**
 * The pixel box every panel, button, chip, and bar is drawn with. Pure Views, whole UI pixels,
 * no radius, blur, or gradient: outline with notched corners, fill, top highlight, bottom shade,
 * and a lip underneath for raised frames.
 */
export function PixelFrame({ skin, depth = 0, pressed = false, style, contentStyle, children }: PixelFrameProps) {
  const f = Frames[skin];
  const lip = px(depth);
  return (
    <View style={[{ paddingBottom: lip }, style]}>
      {depth > 0 && (
        <View style={[styles.abs, { top: lip, bottom: 0, left: 0, right: 0 }]}>
          <Silhouette color={f.lip} />
        </View>
      )}
      <View style={pressed ? { transform: [{ translateY: lip }] } : undefined}>
        <Silhouette color={f.outline} />
        <View style={[styles.abs, { top: px(1), bottom: px(1), left: px(1), right: px(1), backgroundColor: f.fill }]} />
        <View style={[styles.abs, { top: px(1), height: px(1), left: px(2), right: px(2), backgroundColor: f.highlight }]} />
        <View style={[styles.abs, { bottom: px(1), height: px(1), left: px(2), right: px(2), backgroundColor: f.shade }]} />
        <View style={[styles.content, contentStyle]}>{children}</View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  abs: { position: 'absolute' },
  // Outline + highlight/shade rows take 2 UI pixels on each side; content starts inside them.
  // Keep the frame sized to its content. Native Yoga can stretch an auto-height frame with flexGrow.
  content: { padding: px(2) },
});
