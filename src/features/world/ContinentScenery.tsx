import { Group, Path, Skia, type SkPath } from '@shopify/react-native-skia';
import { memo } from 'react';
import { useDerivedValue, type SharedValue } from 'react-native-reanimated';

import features from '@/data/scenery.json';
import { globePoint, type GlobeCamera, type GlobeViewport } from './globe-camera';
import { sceneryOpacity, sceneryScale, selectScenery, type SceneryFeature } from './scenery';
import { spriteArt, type SpriteKind } from './sprite-art';

type Props = {
  viewport: GlobeViewport;
  camera: SharedValue<GlobeCamera>;
  snapshot: GlobeCamera;
};
const cache = new Map<SpriteKind, { color: string; path: SkPath }[]>();

function drawing(kind: SpriteKind) {
  const cached = cache.get(kind);
  if (cached) return cached;
  const art = spriteArt[kind];
  const paths = new Map<string, SkPath>();
  art.rows.forEach((row, y) => {
    [...row].forEach((pixel, x) => {
      if (pixel === '.') return;
      const path = paths.get(pixel) ?? Skia.Path.Make();
      path.addRect(Skia.XYWHRect(x, y, 1, 1));
      paths.set(pixel, path);
    });
  });
  const result = [...paths].map(([pixel, path]) => ({ color: art.colors[pixel], path }));
  cache.set(kind, result);
  return result;
}

export function ContinentScenery({ camera, snapshot, viewport }: Props) {
  if (snapshot.zoom <= 0.9) return null;
  const selected = selectScenery(
    features.map((feature) => ({
      feature,
      ...globePoint(feature.longitude, feature.latitude, snapshot, viewport),
    })),
    viewport,
    snapshot.zoom
  );
  return (
    <>
      {selected.map(({ feature }) => (
        <ScenerySprite key={feature.id} feature={feature} viewport={viewport} camera={camera} />
      ))}
    </>
  );
}

const ScenerySprite = memo(function ScenerySprite({
  feature,
  camera,
  viewport,
}: {
  feature: SceneryFeature;
  camera: SharedValue<GlobeCamera>;
  viewport: GlobeViewport;
}) {
  const art = spriteArt[feature.kind as SpriteKind];
  const paths = drawing(feature.kind as SpriteKind);
  const transform = useDerivedValue(() => {
    const current = camera.get();
    const point = globePoint(feature.longitude, feature.latitude, current, viewport);
    const scale = sceneryScale(current.zoom, viewport);
    return [
      { translateX: Math.round(point.x) },
      { translateY: Math.round(point.y) },
      { scale },
      { translateX: -art.width / 2 },
      { translateY: -art.height },
    ];
  });
  const opacity = useDerivedValue(() => {
    const current = camera.get();
    const point = globePoint(feature.longitude, feature.latitude, current, viewport);
    return sceneryOpacity(current.zoom) * Math.max(0, Math.min(1, (point.depth - 0.35) / 0.2));
  });
  return (
    <Group transform={transform} opacity={opacity} antiAlias={false}>
      {paths.map(({ color, path }) => (
        <Path key={color} path={path} color={color} />
      ))}
    </Group>
  );
});
