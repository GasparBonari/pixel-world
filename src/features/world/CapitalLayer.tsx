import { FilterMode, Group, Image, MipmapMode, type SkImage } from '@shopify/react-native-skia';
import { useDerivedValue, type SharedValue } from 'react-native-reanimated';

import { CapitalMotion } from './CapitalMotion';
import { activeCapital, type GlobeCamera, type GlobeViewport } from './globe-camera';
import { capitalOpacity, capitalRect, type CapitalScene } from './capitals';

const NEAREST = { filter: FilterMode.Nearest, mipmap: MipmapMode.None } as const;

/**
 * A capital's isometric scene (scripts/art/build_capitals.py). It grows out of the capital's
 * location as the camera zooms in, and is drawn at whole icon pixels once fully arrived. While it is
 * the capital being visited (`animated`), its water glints, gulls and cloud shadows move over it.
 */
export function CapitalLayer({
  image,
  scene,
  camera,
  viewport,
  iconScale,
  icons,
  time,
  animated,
}: {
  image: SkImage;
  scene: CapitalScene;
  camera: SharedValue<GlobeCamera>;
  viewport: GlobeViewport;
  iconScale: number;
  icons: SkImage;
  time: SharedValue<number>;
  animated: boolean;
}) {
  const rect = useDerivedValue(() => {
    const r = capitalRect(scene, camera.get(), viewport, iconScale);
    return { x: Math.round(r.x), y: Math.round(r.y), width: r.width, height: r.height };
  });
  const x = useDerivedValue(() => rect.get().x);
  const y = useDerivedValue(() => rect.get().y);
  const width = useDerivedValue(() => rect.get().width);
  const height = useDerivedValue(() => rect.get().height);
  // Only the capital being visited appears, never a neighbour's scene at the screen edge.
  const opacity = useDerivedValue(() => {
    const c = camera.get();
    return activeCapital(c)?.id === scene.id ? capitalOpacity(c.zoom) : 0;
  });
  return (
    <Group opacity={opacity}>
      <Image image={image} x={x} y={y} width={width} height={height} fit="fill" sampling={NEAREST} />
      {animated && <CapitalMotion icons={icons} scene={scene} sceneRect={rect} time={time} />}
    </Group>
  );
}
