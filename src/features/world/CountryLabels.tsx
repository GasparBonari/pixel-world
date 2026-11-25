import { StyleSheet, View } from 'react-native';
import Animated, { useAnimatedStyle, type SharedValue } from 'react-native-reanimated';

import { Size, Space, U, px } from '@/constants/theme';
import labels from '@/data/country-labels.json';
import { Chip } from '@/ui';

import { COUNTRY_ZOOM, globePoint, type GlobeCamera, type GlobeViewport } from './globe-camera';
import { CONTINENT_ZOOM_START } from './globe-shader';

type Props = {
  viewport: GlobeViewport;
  camera: SharedValue<GlobeCamera>;
  snapshot: GlobeCamera;
};
type PlaceLabel = { name: string; longitude: number; latitude: number };

const HALF_WIDTH = px(34);
const HALF_HEIGHT = px(6);
const HEADER_SPACE = Size.touch + 2 * Space.md;
const LABEL_LIMIT = 8;
const RIM_DEPTH = 0.25;

export function CountryLabels({ snapshot, camera, viewport }: Props) {
  if (snapshot.zoom < CONTINENT_ZOOM_START || snapshot.zoom >= COUNTRY_ZOOM.in) return null;

  const visible: (typeof labels)[number][] = [];
  const occupied: { x: number; y: number; halfWidth: number }[] = [];
  for (const label of labels) {
    const { x, y, depth } = globePoint(label.longitude, label.latitude, snapshot, viewport);
    const halfWidth = Math.min(HALF_WIDTH, Space.sm + label.name.length * px(2));
    if (depth < RIM_DEPTH || x < halfWidth || x > viewport.width - halfWidth ||
        y < HEADER_SPACE + HALF_HEIGHT || y > viewport.height - 2 * HALF_HEIGHT ||
        occupied.some((other) => Math.abs(other.x - x) < other.halfWidth + halfWidth &&
          Math.abs(other.y - y) < 3 * HALF_HEIGHT)) continue;

    visible.push(label);
    occupied.push({ x, y, halfWidth });
    if (visible.length === LABEL_LIMIT) break;
  }

  return (
    <View style={StyleSheet.absoluteFill} pointerEvents="none">
      {visible.map((place) => <CountryLabel key={place.id} place={place} camera={camera} viewport={viewport} />)}
    </View>
  );
}

function CountryLabel({ camera, viewport, place }: {
  camera: SharedValue<GlobeCamera>;
  viewport: GlobeViewport;
  place: PlaceLabel;
}) {
  const { longitude, latitude, name } = place;
  const position = useAnimatedStyle(() => {
    const current = camera.get();
    const { x, y, depth } = globePoint(longitude, latitude, current, viewport);
    const atTier = current.zoom >= CONTINENT_ZOOM_START && current.zoom < COUNTRY_ZOOM.in;
    const visible = atTier && depth >= RIM_DEPTH && y >= HEADER_SPACE &&
      y < viewport.height - HALF_HEIGHT && x >= 0 && x <= viewport.width;
    return {
      opacity: visible ? 1 : 0,
      transform: [
        { translateX: Math.min(viewport.width - 2 * HALF_WIDTH, Math.max(0, Math.round(x / U) * U - HALF_WIDTH)) },
        { translateY: Math.round(y / U) * U - HALF_HEIGHT },
      ],
    };
  });
  return (
    <Animated.View style={[styles.label, position]}>
      <Chip skin="navy" label={name} compact />
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  label: { position: 'absolute', left: 0, top: 0, width: 2 * HALF_WIDTH, alignItems: 'center' },
});
