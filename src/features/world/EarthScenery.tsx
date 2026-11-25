import { Atlas, FilterMode, Group, MipmapMode, useRSXformBuffer, type SkImage } from '@shopify/react-native-skia';
import { useDerivedValue, type SharedValue } from 'react-native-reanimated';

import iconData from '@/data/map-icons.json';

import { EARTH_OVERVIEW_END, globePoint, type GlobeCamera, type GlobeViewport } from './globe-camera';
import { iconOpacity } from './map-icons';
import { sunDirection } from './motion';

const mountains = iconData.frames.filter((_, index) => iconData.names[index] === 'mountain');
const dune = iconData.frames[iconData.names.indexOf('dune')];

// Anchors selected from the sourced continent artwork, kept stable as denser board placements
// change. The shared still frames draw from north to south.
const placements = [
  [mountains[2], 23.625, 69.625],
  [mountains[0], 8.625, 46.375],
  [mountains[2], -114.875, 45.375],
  [mountains[0], -80.875, 38.125],
  [mountains[0], -0.625, 32.875],
  [mountains[2], 86.125, 27.375],
  [dune, 12.125, 25.375],
  [mountains[0], 39.125, 14.375],
  [mountains[0], -74.625, -10.625],
  [mountains[2], -65.625, -28.625],
  [mountains[1], 27.875, -29.125],
  [mountains[2], 148.875, -37.125],
] as const;
const scenery = placements.map(([[x, y, width, height], longitude, latitude]) => ({
  longitude, latitude, rect: { x, y, width, height },
}));
const sprites = scenery.map(({ rect }) => rect);
const sampling = { filter: FilterMode.Nearest, mipmap: MipmapMode.None } as const;

export function EarthScenery({ image, camera, viewport, time }: {
  image: SkImage;
  camera: SharedValue<GlobeCamera>;
  viewport: GlobeViewport;
  time: SharedValue<number>;
}) {
  const scale = Math.max(1, Math.round(Math.min(viewport.width, viewport.height) / 390));
  const transforms = useRSXformBuffer(scenery.length, (value, index) => {
    'worklet';
    const current = camera.get();
    const { longitude, latitude, rect } = scenery[index];
    const point = globePoint(longitude, latitude, current, viewport);
    if (current.zoom >= EARTH_OVERVIEW_END || point.depth < 0.36 || sunDirection(longitude, latitude, time.get())[2] < 0.08) {
      value.set(0, 0, -9999, -9999);
      return;
    }
    value.set(scale, 0, Math.round(point.x - rect.width * scale / 2), Math.round(point.y - (rect.height - 1) * scale));
  });
  const opacity = useDerivedValue(() => 1 - iconOpacity(camera.get().zoom, 0, EARTH_OVERVIEW_END));

  return (
    <Group opacity={opacity}>
      <Atlas image={image} sprites={sprites} transforms={transforms} sampling={sampling} />
    </Group>
  );
}
