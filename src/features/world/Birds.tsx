import {
  Atlas,
  FilterMode,
  Group,
  MipmapMode,
  useRectBuffer,
  useRSXformBuffer,
  type SkImage,
} from '@shopify/react-native-skia';
import { useDerivedValue, type SharedValue } from 'react-native-reanimated';

import iconData from '@/data/map-icons.json';
import { ALTITUDE, FLOCKS, FORMATION, SHADOW_SHIFT, flockAt } from './flocks';
import { globePoint, type GlobeCamera, type GlobeViewport } from './globe-camera';
import { BOARD_ZOOM_END, BOARD_ZOOM_START } from './globe-shader';
import { iconOpacity } from './map-icons';
import { poseAt } from './motion';

type Frame = [number, number, number, number];
const frames = iconData.frames as Frame[];
const BIRD = iconData.names.indexOf('bird');
const SHADOW = iconData.names.indexOf('bird-shadow');
const WINGS = (iconData.animations as unknown as Record<string, [string, number[]]>)[BIRD][1];
const BIRDS = FLOCKS.length * FORMATION.length;
const SAMPLING = { filter: FilterMode.Nearest, mipmap: MipmapMode.None } as const;

/**
 * Flocks crossing the board (flocks.ts), in one batched draw: every shadow first, then every bird.
 * They fade in with the board's other icons and keep flapping as the clock ticks. With reduce motion
 * (time 0) there are none, so the still scene is the one before animation existed.
 */
export function Birds({
  image,
  camera,
  viewport,
  scale,
  time,
}: {
  image: SkImage;
  camera: SharedValue<GlobeCamera>;
  viewport: GlobeViewport;
  scale: number;
  time: SharedValue<number>;
}) {
  const sprites = useRectBuffer(BIRDS * 2, (rect, index) => {
    'worklet';
    const bird = index - BIRDS;
    const frame =
      bird < 0 ? SHADOW : WINGS[poseAt('flap', time.get(), (bird % FORMATION.length) * 0.37, bird)];
    const [x, y, width, height] = frames[frame];
    rect.setXYWH(x, y, width, height);
  });
  const transforms = useRSXformBuffer(BIRDS * 2, (value, index) => {
    'worklet';
    const current = camera.get();
    const shadow = index < BIRDS;
    const bird = shadow ? index : index - BIRDS;
    const flock = FLOCKS[Math.floor(bird / FORMATION.length)];
    const place = flockAt(flock, time.get());
    const point = globePoint(place.longitude, place.latitude, current, viewport);
    if (current.zoom < BOARD_ZOOM_START || point.depth < 0.15) {
      value.set(0, 0, -9999, -9999);
      return;
    }
    const [dx, dy] = FORMATION[bird % FORMATION.length];
    const [, , width, height] = frames[shadow ? SHADOW : BIRD];
    const x = (place.east ? dx : -dx) + (shadow ? SHADOW_SHIFT : 0);
    const y = dy - (shadow ? 0 : ALTITUDE);
    value.set(
      scale,
      0,
      Math.round(point.x + (x - width / 2) * scale),
      Math.round(point.y + (y - height + 1) * scale)
    );
  });
  const opacity = useDerivedValue(() =>
    time.get() > 0 ? iconOpacity(camera.get().zoom, BOARD_ZOOM_START, BOARD_ZOOM_END) : 0
  );
  return (
    <Group opacity={opacity}>
      <Atlas image={image} sprites={sprites} transforms={transforms} sampling={SAMPLING} />
    </Group>
  );
}
