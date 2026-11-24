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
import { capitalOpacity } from './capitals';
import { FERRY_ROUTES, ferryAt, ferryFacesEast, ferryRoutePoint, type FerryRoute } from './country-ferry';
import { globePoint, type GlobeCamera, type GlobeViewport } from './globe-camera';
import { iconOpacity } from './map-icons';

const FERRY_WEST = iconData.names.indexOf('ferry');
const HULL_FRAMES = iconData.frames.slice(FERRY_WEST, FERRY_WEST + 2);
const WAKE_FRAME = iconData.frames[iconData.names.indexOf('ferry-wake')];
const SAMPLING = { filter: FilterMode.Nearest, mipmap: MipmapMode.None } as const;
const WAKE_PATCHES = 2;
const SPRITES_PER_FERRY = WAKE_PATCHES + 1;
const FERRY_BANDS = [...new Set(FERRY_ROUTES.map((route) => route.fullZoom))].map((zoom) => ({
  zoom,
  routes: FERRY_ROUTES.filter((route) => route.fullZoom === zoom),
}));

type FerryProps = {
  image: SkImage;
  camera: SharedValue<GlobeCamera>;
  viewport: GlobeViewport;
  scale: number;
  time: SharedValue<number>;
};

export function CountryFerry(props: FerryProps) {
  return (
    <>
      {FERRY_BANDS.map(({ zoom, routes }) => (
        <FerryBand key={zoom} {...props} fullZoom={zoom} routes={routes} />
      ))}
    </>
  );
}

/** One batched draw per visibility band, with foam following each ferry's earlier positions. */
function FerryBand({
  image,
  camera,
  viewport,
  scale,
  time,
  fullZoom,
  routes,
}: FerryProps & { fullZoom: number; routes: FerryRoute[] }) {
  const opacity = useDerivedValue(() => {
    const { zoom } = camera.get();
    return iconOpacity(zoom, fullZoom - 0.4, fullZoom) * (1 - capitalOpacity(zoom));
  });
  const ferryTime = useDerivedValue(() => (opacity.get() > 0 ? time.get() : 0));
  const count = routes.length * SPRITES_PER_FERRY;
  const sprites = useRectBuffer(count, (rect, index) => {
    'worklet';
    const route = routes[Math.floor(index / SPRITES_PER_FERRY)];
    const isWake = index % SPRITES_PER_FERRY < WAKE_PATCHES;
    let frame = WAKE_FRAME;
    if (!isWake) {
      const { returning } = ferryAt(ferryTime.get(), route.crossingSeconds);
      frame = HULL_FRAMES[Number(ferryFacesEast(route.points, returning))];
    }
    const [x, y, width, height] = frame;
    rect.setXYWH(x, y, width, height);
  });
  const transforms = useRSXformBuffer(count, (transform, index) => {
    'worklet';
    if (opacity.get() === 0) {
      transform.set(0, 0, -9999, -9999);
      return;
    }
    const current = camera.get();
    const route = routes[Math.floor(index / SPRITES_PER_FERRY)];
    const sprite = index % SPRITES_PER_FERRY;
    const isWake = sprite < WAKE_PATCHES;
    const { progress, returning, underway } = ferryAt(ferryTime.get(), route.crossingSeconds);
    const lag = isWake ? (WAKE_PATCHES - sprite) * 0.105 : 0;
    const position = progress + (returning ? lag : -lag);
    if (isWake && (!underway || position < 0 || position > 1)) {
      transform.set(0, 0, -9999, -9999);
      return;
    }
    const { longitude, latitude } = ferryRoutePoint(route.points, position);
    const point = globePoint(longitude, latitude, current, viewport);
    if (point.depth < 0.15 || point.x < -64 || point.x > viewport.width + 64
      || point.y < -64 || point.y > viewport.height + 64) {
      transform.set(0, 0, -9999, -9999);
      return;
    }
    const [, , width, height] = isWake ? WAKE_FRAME : HULL_FRAMES[0];
    const size = scale * (route.spriteScale ?? 1) * (sprite === 0 ? 0.7 : 1);
    transform.set(
      size,
      0,
      Math.round(point.x - width * size / 2),
      Math.round(point.y - (height - 1) * size)
    );
  });
  return (
    <Group opacity={opacity}>
      <Atlas image={image} sprites={sprites} transforms={transforms} sampling={SAMPLING} />
    </Group>
  );
}
