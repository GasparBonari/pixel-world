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
import { COUNTRY_ZOOM, globePoint, type GlobeCamera, type GlobeViewport } from './globe-camera';
import { BOARD_ZOOM_END, BOARD_ZOOM_START } from './globe-shader';
import { iconOpacity } from './map-icons';
import { bobAt, phaseAt, poseAt, type Motion } from './motion';

type Frame = [number, number, number, number];
/**
 * [frame, longitude, latitude, dx, dy, tier, extra] from scripts/art/build_map_icons.py. Tier 0 is
 * the continent board, tier 1 a country's buildings. For a country icon, extra is the zoom from
 * which it is fully visible and clear of its neighbours. A continent icon with extra 1 makes way for
 * a capital or landmark: it fades out as the country tier fades in.
 */
type Icon = [number, number, number, number, number, number, number?];
type Fade = { start: number; end: number };
/**
 * Icons drawn together. Per icon: its frame for each pose (one entry when still), the motion that
 * picks the pose (motion.ts), a phase so neighbours don't move in step, and whether it bobs (boats).
 */
type Band = {
  icons: Icon[];
  fadeIn: Fade;
  fadeOut?: Fade;
  poses: number[][];
  motions: (Motion | '')[];
  phases: number[];
  bobs: boolean[];
};

const frames = iconData.frames as Frame[];
const allIcons = iconData.icons as Icon[];
/** Still frame -> [motion, frame for each pose] (build_map_icons.py: ANIMATED). */
const animations = iconData.animations as unknown as Record<string, [Motion, number[]]>;
const BOAT = iconData.names.indexOf('boat');
const SAMPLING = { filter: FilterMode.Nearest, mipmap: MipmapMode.None } as const;

/** Zoom steps between country-icon appearances (APPEAR_STEP in build_map_icons.py). */
const APPEAR_STEP = 0.2;
/**
 * iconOpacity fades over the second half of its range. The first country icons fade in with the
 * tier (zoom 4.4–5.0); later ones only over the step before they are fully visible, so at a
 * resting zoom at most one step is faint.
 */
const countryFade = (full: number): Fade => {
  const span = full > COUNTRY_ZOOM.full ? APPEAR_STEP : COUNTRY_ZOOM.full - COUNTRY_ZOOM.in;
  return { start: full - 2 * span, end: full };
};

function band(icons: Icon[], fadeIn: Fade, fadeOut?: Fade): Band {
  return {
    icons,
    fadeIn,
    fadeOut,
    poses: icons.map(([frame]) => animations[frame]?.[1] ?? [frame]),
    motions: icons.map(([frame]) => animations[frame]?.[0] ?? ''),
    phases: icons.map(([, longitude, latitude]) => phaseAt(longitude, latitude)),
    bobs: icons.map(([frame]) => frame === BOAT),
  };
}

/** Icons drawn together because they fade in (and out) at the same zooms. */
function bandsOf(tier: 0 | 1): Band[] {
  const icons = allIcons.filter((icon) => icon[5] === tier);
  if (tier === 0) {
    const board = { start: BOARD_ZOOM_START, end: BOARD_ZOOM_END };
    return [
      band(icons.filter((icon) => icon[6] !== 1), board),
      band(icons.filter((icon) => icon[6] === 1), board, countryFade(COUNTRY_ZOOM.full)),
    ].filter((b) => b.icons.length > 0);
  }
  const byZoom = new Map<number, Icon[]>();
  for (const icon of icons) {
    const full = icon[6] ?? COUNTRY_ZOOM.full;
    byZoom.set(full, [...(byZoom.get(full) ?? []), icon]);
  }
  return [...byZoom.entries()]
    .sort(([a], [b]) => a - b)
    .map(([full, group]) => band(group, countryFade(full)));
}
const BANDS = [bandsOf(0), bandsOf(1)] as const;

/**
 * One tier of map icons (ART_CONTRACT.md): continent flora, fauna and mountains, or the countries'
 * buildings. Country icons appear in zoom steps, so neighbours never overlap once fully visible.
 * Each step is one batched draw.
 */
export function MapIcons({
  image,
  camera,
  viewport,
  scale,
  tier,
  time,
}: {
  image: SkImage;
  camera: SharedValue<GlobeCamera>;
  viewport: GlobeViewport;
  scale: number;
  tier: 0 | 1;
  time: SharedValue<number>;
}) {
  return (
    <>
      {BANDS[tier].map((b) => (
        <IconBand
          key={`${b.fadeIn.end}-${b.fadeOut ? 'out' : 'in'}`}
          image={image}
          camera={camera}
          viewport={viewport}
          scale={scale}
          band={b}
          time={time}
        />
      ))}
    </>
  );
}

/**
 * Icon pixels are two-thirds of a terrain pixel. Each frame projects every icon onto the sphere;
 * icons on the far side or fully faded are parked off-screen. Icons are sorted north to south, so
 * each band draws back to front. Animated icons switch atlas frames as the clock ticks; a band with
 * none never reads the clock, so it redraws only when the camera moves.
 */
function IconBand({
  image,
  camera,
  viewport,
  scale,
  band,
  time,
}: {
  image: SkImage;
  camera: SharedValue<GlobeCamera>;
  viewport: GlobeViewport;
  scale: number;
  band: Band;
  time: SharedValue<number>;
}) {
  const { icons, poses, motions, phases, bobs } = band;
  const { start, end } = band.fadeIn;
  const fadesOut = band.fadeOut !== undefined;
  const outStart = band.fadeOut?.start ?? 0;
  const hiddenFrom = band.fadeOut?.end ?? Infinity;
  // Only bands that move capture the clock (a worklet subscribes to the shared values it captures).
  const poseClock = motions.some((motion) => motion !== '') ? time : null;
  const bobClock = bobs.some(Boolean) ? time : null;
  const sprites = useRectBuffer(icons.length, (rect, index) => {
    'worklet';
    const options = poses[index];
    const pose =
      poseClock && options.length > 1
        ? poseAt(motions[index] as Motion, poseClock.get(), phases[index], icons[index][1])
        : 0;
    const [x, y, width, height] = frames[options[pose] ?? options[0]];
    rect.setXYWH(x, y, width, height);
  });
  const transforms = useRSXformBuffer(icons.length, (value, index) => {
    'worklet';
    const current = camera.get();
    const [frame, longitude, latitude, dx, dy] = icons[index];
    const [, , width, height] = frames[frame];
    const point = globePoint(longitude, latitude, current, viewport);
    if (current.zoom < start || current.zoom >= hiddenFrom || point.depth < 0.15) {
      value.set(0, 0, -9999, -9999);
      return;
    }
    const bob = bobClock && bobs[index] ? bobAt(bobClock.get(), phases[index]) : 0;
    value.set(
      scale,
      0,
      Math.round(point.x + (dx - width / 2) * scale),
      Math.round(point.y + (dy + bob - height + 1) * scale)
    );
  });
  const opacity = useDerivedValue(() => {
    const zoom = camera.get().zoom;
    const shown = iconOpacity(zoom, start, end);
    return fadesOut ? shown * (1 - iconOpacity(zoom, outStart, hiddenFrom)) : shown;
  });
  return (
    <Group opacity={opacity}>
      <Atlas image={image} sprites={sprites} transforms={transforms} sampling={SAMPLING} />
    </Group>
  );
}
