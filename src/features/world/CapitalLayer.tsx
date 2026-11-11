import { FilterMode, Group, Image, MipmapMode, type SkImage } from '@shopify/react-native-skia';
import { useDerivedValue, type SharedValue } from 'react-native-reanimated';

import { CAPITAL_REACH, type GlobeCamera, type GlobeViewport } from './globe-camera';
import { capitalOpacity, capitalRect, type CapitalScene } from './capitals';

const NEAREST = { filter: FilterMode.Nearest, mipmap: MipmapMode.None } as const;

/**
 * A capital's isometric scene (scripts/art/build_capitals.py). It grows out of the capital's
 * location as the camera zooms in, and is drawn at whole icon pixels once fully arrived.
 */
export function CapitalLayer({
  image,
  scene,
  camera,
  viewport,
  iconScale,
}: {
  image: SkImage;
  scene: CapitalScene;
  camera: SharedValue<GlobeCamera>;
  viewport: GlobeViewport;
  iconScale: number;
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
    const near =
      Math.abs(c.longitude - scene.longitude) <= CAPITAL_REACH &&
      Math.abs(c.latitude - scene.latitude) <= CAPITAL_REACH;
    return near ? capitalOpacity(c.zoom) : 0;
  });
  return (
    <Group opacity={opacity}>
      <Image image={image} x={x} y={y} width={width} height={height} fit="fill" sampling={NEAREST} />
    </Group>
  );
}
