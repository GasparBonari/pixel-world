import { Path, Skia, type SkRect } from '@shopify/react-native-skia';
import { useDerivedValue, type SharedValue } from 'react-native-reanimated';

import { Palette, px } from '@/constants/theme';
import type { LandmarkBounds } from '../find-it/challenge';
import type { CapitalScene } from './capitals';
import { CAPITAL_ZOOM, type GlobeCamera } from './globe-camera';

/** Four corner brackets pulse in whole map pixels around the target's bounds. */
export function CapitalAssist({ bounds, scene, sceneRect, time, camera }: {
  bounds: LandmarkBounds;
  scene: CapitalScene;
  sceneRect: SharedValue<SkRect>;
  time: SharedValue<number>;
  camera: SharedValue<GlobeCamera>;
}) {
  const opacity = useDerivedValue(() => Number(camera.get().zoom >= CAPITAL_ZOOM.full));
  const inset = useDerivedValue(() => 4 + (Math.floor(time.get() * 2) % 2) * 2);
  const path = useDerivedValue(() => {
    const [x, y, width, height] = bounds;
    const area = sceneRect.get();
    const scale = area.width / scene.width;
    const pad = inset.get();
    const left = Math.round(area.x + (x - pad) * scale);
    const top = Math.round(area.y + (y - pad) * scale);
    const right = Math.round(area.x + (x + width + pad) * scale);
    const bottom = Math.round(area.y + (y + height + pad) * scale);
    const arm = Math.round(Math.min(8 * scale, (right - left) / 3, (bottom - top) / 3));
    const corners = Skia.PathBuilder.Make();
    corners.moveTo(left + arm, top).lineTo(left, top).lineTo(left, top + arm);
    corners.moveTo(right - arm, top).lineTo(right, top).lineTo(right, top + arm);
    corners.moveTo(left + arm, bottom).lineTo(left, bottom).lineTo(left, bottom - arm);
    corners.moveTo(right - arm, bottom).lineTo(right, bottom).lineTo(right, bottom - arm);
    return corners.detach();
  });

  return (
    <>
      <Path path={path} color={Palette.navyInk} style="stroke" strokeWidth={px(3)} antiAlias={false} opacity={opacity} />
      <Path path={path} color={Palette.goldLight} style="stroke" strokeWidth={px(1)} antiAlias={false} opacity={opacity} />
    </>
  );
}
