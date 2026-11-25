import { StyleSheet } from 'react-native';
import Animated, { useAnimatedStyle, type SharedValue } from 'react-native-reanimated';

import { Size, Space, U, px } from '@/constants/theme';
import capitals from '@/data/capitals.json';
import { Chip, type ChipProps } from '@/ui';

import { activeCapital, COUNTRY_ZOOM, globePoint, type GlobeCamera, type GlobeViewport } from './globe-camera';

type Capital = (typeof capitals)[number];

const LABEL_WIDTH = px(84);
const HEADER_SPACE = Size.touch + 2 * Space.md;

function labelPoint(capital: Capital, camera: GlobeCamera, viewport: GlobeViewport, bottomInset: number) {
  'worklet';
  const point = globePoint(capital.longitude, capital.latitude, camera, viewport);
  const y = Math.round(point.y / U) * U - Space.sm;
  const visible = point.depth > 0.25 && point.x >= 0 && point.x <= viewport.width &&
    y >= HEADER_SPACE && y + Size.touch <= viewport.height - bottomInset;
  return { ...point, y, visible };
}

export function CapitalLabel({ camera, snapshot, viewport, preferredId, selected, mapTap, onExplore }: {
  camera: SharedValue<GlobeCamera>;
  snapshot: GlobeCamera;
  viewport: GlobeViewport;
  preferredId?: string;
  selected: boolean;
  mapTap: NonNullable<ChipProps['mapTap']>;
  onExplore: (capital: Capital) => void;
}) {
  // Leave room for the collapsed country sheet. An expanded sheet also takes priority over the map.
  const bottomInset = selected ? px(78) : Space.xs;
  let capital: Capital | undefined;
  let closest = Infinity;
  if (snapshot.zoom >= COUNTRY_ZOOM.in && !activeCapital(snapshot)) {
    for (const candidate of capitals) {
      const point = labelPoint(candidate, snapshot, viewport, bottomInset);
      if (!point.visible) continue;
      if (candidate.id === preferredId) {
        capital = candidate;
        break;
      }
      const distance = Math.hypot(point.x - viewport.width / 2, point.y - viewport.height / 2);
      if (distance < closest) {
        capital = candidate;
        closest = distance;
      }
    }
  }
  return capital && <CapitalChip key={capital.id} {...{ capital, camera, viewport, bottomInset, mapTap, onExplore }} />;
}

function CapitalChip({ capital, camera, viewport, bottomInset, mapTap, onExplore }: {
  capital: Capital;
  camera: SharedValue<GlobeCamera>;
  viewport: GlobeViewport;
  bottomInset: number;
  mapTap: NonNullable<ChipProps['mapTap']>;
  onExplore: (capital: Capital) => void;
}) {
  const width = Math.min(LABEL_WIDTH, viewport.width);
  const position = useAnimatedStyle(() => {
    const current = camera.get();
    const point = labelPoint(capital, current, viewport, bottomInset);
    const visible = point.visible && current.zoom >= COUNTRY_ZOOM.in && !activeCapital(current);
    const x = Math.round(point.x / U) * U - width / 2;
    return {
      transform: [
        { translateX: Math.max(0, Math.min(viewport.width - width, x)) },
        { translateY: visible ? point.y - viewport.height / 2 : -viewport.height },
      ],
    };
  });

  return (
    <Animated.View pointerEvents="box-none" style={[styles.label, { width }, position]}>
      <Chip
        label={capital.name}
        icon="pin"
        compact
        accessibilityLabel={`Open ${capital.name}`}
        mapTap={mapTap}
        onPress={() => onExplore(capital)}
      />
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  label: { position: 'absolute', top: '50%', left: 0, alignItems: 'center' },
});
