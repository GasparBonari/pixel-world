import {
  Atlas,
  FilterMode,
  Group,
  MipmapMode,
  Skia,
  useRSXformBuffer,
  type SkImage,
} from '@shopify/react-native-skia';
import { useMemo } from 'react';
import { useDerivedValue, type SharedValue } from 'react-native-reanimated';

import iconData from '@/data/map-icons.json';
import { globePoint, type GlobeCamera, type GlobeViewport } from './globe-camera';
import { BOARD_ZOOM_END, BOARD_ZOOM_START, CELLS_ACROSS } from './globe-shader';
import { iconOpacity } from './map-icons';

type Frame = [number, number, number, number];
type Icon = [number, number, number, number, number];
const frames = iconData.frames as Frame[];
const icons = iconData.icons as Icon[];
const SAMPLING = { filter: FilterMode.Nearest, mipmap: MipmapMode.None } as const;

/**
 * Continent-scale mountains and trees (ART_CONTRACT.md), one batched draw. Icon pixels are
 * two-thirds of a terrain pixel. Each frame projects every icon onto the sphere; icons on the
 * far side are parked off-screen. The list is sorted north to south, so it draws back to front.
 */
export function MapIcons({
  image,
  camera,
  viewport,
}: {
  image: SkImage;
  camera: SharedValue<GlobeCamera>;
  viewport: GlobeViewport;
}) {
  const sprites = useMemo(
    () => icons.map(([frame]) => Skia.XYWHRect(...(frames[frame] as Frame))),
    []
  );
  const scale = (Math.max(1.25, Math.min(viewport.width, viewport.height) / CELLS_ACROSS) * 2) / 3;
  const transforms = useRSXformBuffer(icons.length, (value, index) => {
    'worklet';
    const current = camera.get();
    const [frame, longitude, latitude, dx, dy] = icons[index];
    const [, , width, height] = frames[frame];
    const point = globePoint(longitude, latitude, current, viewport);
    if (current.zoom < BOARD_ZOOM_START || point.depth < 0.15) {
      value.set(0, 0, -9999, -9999);
      return;
    }
    value.set(
      scale,
      0,
      Math.round(point.x + (dx - width / 2) * scale),
      Math.round(point.y + (dy - height + 1) * scale)
    );
  });
  const opacity = useDerivedValue(() =>
    iconOpacity(camera.get().zoom, BOARD_ZOOM_START, BOARD_ZOOM_END)
  );
  return (
    <Group opacity={opacity}>
      <Atlas image={image} sprites={sprites} transforms={transforms} sampling={SAMPLING} />
    </Group>
  );
}
