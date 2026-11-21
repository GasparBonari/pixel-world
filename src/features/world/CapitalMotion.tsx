import {
  Atlas,
  FilterMode,
  Group,
  MipmapMode,
  rect,
  useRectBuffer,
  useRSXformBuffer,
  type SkImage,
} from '@shopify/react-native-skia';
import { useDerivedValue, type SharedValue } from 'react-native-reanimated';

import capitalMotion from '@/data/capital-motion.json';
import iconData from '@/data/map-icons.json';
import {
  CLOUD_SHADOWS,
  GULLS,
  GULL_ALTITUDE,
  GULL_SHADOW_SHIFT,
  cloudShadowAt,
  glintAt,
  gullAt,
} from './capital-motion';
import type { CapitalScene } from './capitals';
import { phaseAt, poseAt } from './motion';

type Frame = [number, number, number, number];
const frames = iconData.frames as Frame[];
const animations = iconData.animations as unknown as Record<string, [string, number[]]>;
const frameOf = (name: string) => iconData.names.indexOf(name);
const GLINT = animations[frameOf('glint')][1];
const WINGS = animations[frameOf('bird')][1];
const GULL_SHADOW = frameOf('bird-shadow');
const CLOUD = frameOf('cloud-shadow');
const SPOTS = capitalMotion as unknown as Record<string, { glints: [number, number][] }>;
const SAMPLING = { filter: FilterMode.Nearest, mipmap: MipmapMode.None } as const;

/**
 * The moving parts of the capital being visited, drawn in scene pixels over its image and clipped
 * to it: cloud shadows, then water glints, then gulls with their shadows, in one batched draw.
 * Nothing shows while the clock is still (reduce motion).
 */
export function CapitalMotion({
  icons,
  scene,
  sceneRect,
  time,
}: {
  icons: SkImage;
  scene: CapitalScene;
  sceneRect: SharedValue<{ x: number; y: number; width: number; height: number }>;
  time: SharedValue<number>;
}) {
  const glints = SPOTS[scene.id]?.glints ?? [];
  const phases = glints.map(([x, y]) => phaseAt(x, y));
  const firstGlint = CLOUD_SHADOWS;
  const firstGull = firstGlint + glints.length;
  const count = firstGull + GULLS * 2;
  const { width, height } = scene;
  const cloudSize: [number, number] = [frames[CLOUD][2], frames[CLOUD][3]];

  // Which atlas frame each entry shows, and where its top-left corner sits in the scene.
  const sprites = useRectBuffer(count, (r, index) => {
    'worklet';
    const t = time.get();
    let frame = CLOUD;
    if (index >= firstGull) {
      const gull = index - firstGull;
      frame = gull < GULLS ? GULL_SHADOW : WINGS[poseAt('flap', t, gull * 0.37, 0)];
    } else if (index >= firstGlint) {
      frame = GLINT[glintAt(t, phases[index - firstGlint]).pose];
    }
    const [x, y, w, h] = frames[frame];
    r.setXYWH(x, y, w, h);
  });
  const transforms = useRSXformBuffer(count, (value, index) => {
    'worklet';
    const t = time.get();
    const area = sceneRect.get();
    const scale = area.width / width;
    let place: [number, number] | null = null;
    if (t > 0 && index < firstGlint) {
      const shadow = cloudShadowAt(index, t, width, height, cloudSize);
      place = [shadow.x, shadow.y];
    } else if (t > 0 && index < firstGull) {
      const glint = glintAt(t, phases[index - firstGlint]);
      const [x, y] = glints[index - firstGlint];
      if (glint.visible) place = [x - 1 + glint.dx, y];
    } else if (t > 0) {
      const gull = index - firstGull;
      const isShadow = gull < GULLS;
      const at = gullAt(isShadow ? gull : gull - GULLS, t, width, height);
      const [, , w, h] = frames[isShadow ? GULL_SHADOW : WINGS[0]];
      place = isShadow
        ? [at.x - w / 2 + GULL_SHADOW_SHIFT, at.y + GULL_ALTITUDE - h]
        : [at.x - w / 2, at.y - h];
    }
    if (!place) {
      value.set(0, 0, -9999, -9999);
      return;
    }
    value.set(scale, 0, Math.round(area.x + place[0] * scale), Math.round(area.y + place[1] * scale));
  });
  const clip = useDerivedValue(() => {
    const area = sceneRect.get();
    return rect(area.x, area.y, area.width, area.height);
  });
  return (
    <Group clip={clip}>
      <Atlas image={icons} sprites={sprites} transforms={transforms} sampling={SAMPLING} />
    </Group>
  );
}
