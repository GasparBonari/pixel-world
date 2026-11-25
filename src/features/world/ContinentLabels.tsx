import { StyleSheet, View } from 'react-native';
import Animated, { useAnimatedStyle, type SharedValue } from 'react-native-reanimated';

import { U, px } from '@/constants/theme';
import { Chip } from '@/ui';

import { EARTH_OVERVIEW_END, globePoint, type GlobeCamera, type GlobeViewport } from './globe-camera';

// Cartographic label positions chosen on the Natural Earth land mask. They mark continental
// interiors for readability and do not represent measured centers or political boundaries.
const CONTINENTS = [
  { name: 'Europe', longitude: 17, latitude: 53 },
  { name: 'Africa', longitude: 19, latitude: 1 },
  { name: 'Asia', longitude: 72, latitude: 43 },
  { name: 'North America', longitude: -87, latitude: 43 },
  { name: 'South America', longitude: -58, latitude: -16 },
  { name: 'Oceania', longitude: 135, latitude: -24 },
  { name: 'Antarctica', longitude: 0, latitude: -86 },
] as const;

type Props = {
  viewport: GlobeViewport;
  camera: SharedValue<GlobeCamera>;
  snapshot: GlobeCamera;
};
type Continent = (typeof CONTINENTS)[number];

const HALF_WIDTH = px(25);
const HALF_HEIGHT = px(6);
const RIM_DEPTH = 0.24;

export function ContinentLabels({ camera, snapshot, viewport }: Props) {
  const occupied: { x: number; y: number; width: number }[] = [];
  const visible = CONTINENTS.filter(({ name, longitude, latitude }) => {
    const point = globePoint(longitude, latitude, snapshot, viewport);
    const halfWidth = Math.min(HALF_WIDTH, px(4) + name.length * px(2));
    if (
      point.depth < RIM_DEPTH ||
      point.x < halfWidth || point.x > viewport.width - halfWidth ||
      point.y < HALF_HEIGHT || point.y > viewport.height - HALF_HEIGHT ||
      occupied.some(({ x, y, width }) =>
        Math.abs(point.x - x) < halfWidth + width && Math.abs(point.y - y) < 3 * HALF_HEIGHT)
    ) return false;
    occupied.push({ ...point, width: halfWidth });
    return true;
  });

  return (
    <View style={StyleSheet.absoluteFill} pointerEvents="none">
      {visible.map((continent) => (
        <ContinentLabel key={continent.name} continent={continent} camera={camera} viewport={viewport} />
      ))}
    </View>
  );
}

function ContinentLabel({ continent, camera, viewport }: Omit<Props, 'snapshot'> & { continent: Continent }) {
  const { name, longitude, latitude } = continent;
  const position = useAnimatedStyle(() => {
    const current = camera.get();
    const point = globePoint(longitude, latitude, current, viewport);
    return {
      opacity: point.depth >= RIM_DEPTH && current.zoom < EARTH_OVERVIEW_END ? 1 : 0,
      transform: [
        { translateX: Math.round(point.x / U) * U - HALF_WIDTH },
        { translateY: Math.round(point.y / U) * U - HALF_HEIGHT },
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
