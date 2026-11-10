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
import { COUNTRY_ZOOM, globePoint, type GlobeCamera, type GlobeViewport } from './globe-camera';
import { BOARD_ZOOM_END, BOARD_ZOOM_START } from './globe-shader';
import { iconOpacity } from './map-icons';

type Frame = [number, number, number, number];
/** [frame, longitude, latitude, dx, dy, tier]: tier 0 continent, 1 country. */
type Icon = [number, number, number, number, number, number];
const frames = iconData.frames as Frame[];
const allIcons = iconData.icons as Icon[];
/** Zoom range over which each tier fades in. */
export const ICON_TIERS = [
  { start: BOARD_ZOOM_START, end: BOARD_ZOOM_END },
  { start: COUNTRY_ZOOM.in * 2 - COUNTRY_ZOOM.full, end: COUNTRY_ZOOM.full },
] as const;
const SAMPLING = { filter: FilterMode.Nearest, mipmap: MipmapMode.None } as const;

/**
 * One tier of map icons (ART_CONTRACT.md) in one batched draw: continent flora, fauna and
 * mountains, or a country's buildings. Icon pixels are two-thirds of a terrain pixel. Each frame
 * projects every icon onto the sphere; icons on the far side are parked off-screen. The list is
 * sorted north to south, so it draws back to front.
 */
export function MapIcons({
  image,
  camera,
  viewport,
  scale,
  tier,
}: {
  image: SkImage;
  camera: SharedValue<GlobeCamera>;
  viewport: GlobeViewport;
  scale: number;
  tier: 0 | 1;
}) {
  const icons = useMemo(() => allIcons.filter((icon) => (icon[5] ?? 0) === tier), [tier]);
  const sprites = useMemo(
    () => icons.map(([frame]) => Skia.XYWHRect(...(frames[frame] as Frame))),
    [icons]
  );
  const { start, end } = ICON_TIERS[tier];
  const transforms = useRSXformBuffer(icons.length, (value, index) => {
    'worklet';
    const current = camera.get();
    const [frame, longitude, latitude, dx, dy] = icons[index];
    const [, , width, height] = frames[frame];
    const point = globePoint(longitude, latitude, current, viewport);
    if (current.zoom < start || point.depth < 0.15) {
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
  const opacity = useDerivedValue(() => iconOpacity(camera.get().zoom, start, end));
  return (
    <Group opacity={opacity}>
      <Atlas image={image} sprites={sprites} transforms={transforms} sampling={SAMPLING} />
    </Group>
  );
}
