import { StyleSheet, Text, View } from 'react-native';
import Animated, { useAnimatedStyle, type SharedValue } from 'react-native-reanimated';

import { Palette, PixelFonts, WorldColors } from '@/constants/theme';
import labels from '@/data/country-labels.json';
import { globePoint, type GlobeCamera, type GlobeViewport } from './globe-camera';
import { BOARD_ZOOM_START } from './globe-shader';

type Props = {
  viewport: GlobeViewport;
  camera: SharedValue<GlobeCamera>;
  snapshot: GlobeCamera;
};

export function CountryLabels(props: Props) {
  const { snapshot, viewport } = props;
  const occupied: { x: number; y: number }[] = [];
  const visible =
    // Names show on the zoomed globe, then hand over to the board, which has no name labels.
    snapshot.zoom < 1.3 || snapshot.zoom >= BOARD_ZOOM_START + 0.4
      ? []
      : labels.filter((label) => {
          const p = globePoint(label.longitude, label.latitude, snapshot, viewport);
          if (
            p.depth < 0.25 ||
            p.x < 60 ||
            p.x > viewport.width - 60 ||
            p.y < 20 ||
            p.y > viewport.height - 20 ||
            occupied.length >= 16 ||
            occupied.some((other) => Math.abs(other.x - p.x) < 115 && Math.abs(other.y - p.y) < 34)
          )
            return false;
          occupied.push(p);
          return true;
        });
  return (
    <View pointerEvents="none" style={StyleSheet.absoluteFill}>
      {visible.map((label) => (
        <CountryLabel key={label.id} {...props} label={label} />
      ))}
    </View>
  );
}

function CountryLabel({ camera, viewport, label }: Props & { label: (typeof labels)[number] }) {
  const style = useAnimatedStyle(() => {
    const p = globePoint(label.longitude, label.latitude, camera.get(), viewport);
    return {
      transform: [{ translateX: p.x - 75 }, { translateY: p.y - 10 }],
      opacity: p.depth > 0.2 ? 1 : 0,
    };
  });
  return (
    <Animated.View style={[styles.label, style]}>
      <Text numberOfLines={1} style={styles.text}>
        {label.name}
      </Text>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  label: { position: 'absolute', width: 150, alignItems: 'center' },
  text: {
    fontFamily: PixelFonts.bold,
    fontSize: 13,
    lineHeight: 18,
    color: Palette.snow,
    // A hard, unblurred drop shadow reads as a pixel outline over land and sea.
    textShadowColor: WorldColors.space,
    textShadowRadius: 0,
    textShadowOffset: { width: 1, height: 1 },
  },
});
