import {
  Canvas,
  Fill,
  FilterMode,
  ImageShader,
  MipmapMode,
  Shader,
  Skia,
  loadData,
  type SkImage,
} from '@shopify/react-native-skia';
import { useCallback, useEffect, useState } from 'react';
import { StyleSheet, View } from 'react-native';
import {
  usePanGesture,
  usePinchGesture,
  useSimultaneousGestures,
} from 'react-native-gesture-handler';
import { useAnimatedReaction, useDerivedValue, useSharedValue } from 'react-native-reanimated';
import { scheduleOnRN } from 'react-native-worklets';

import { CountryLabels } from './CountryLabels';
import {
  globeRadius,
  OPENING_CAMERA,
  rotateGlobe,
  zoomGlobe,
  type GlobeCamera,
  type GlobeViewport,
} from './globe-camera';
import { globeShader } from './globe-shader';
import { MapIcons } from './MapIcons';
import { MapStatus } from './MapStatus';
import { MapSurface } from './MapSurface';

const effect = Skia.RuntimeEffect.Make(globeShader);
// Globe (32 MiB decoded), board (8 MiB) and icon sheet, each decoded once per app session.
const TEXTURES = {
  globe: require('@/assets/world/globe.png'),
  board: require('@/assets/world/board.png'),
  icons: require('@/assets/world/map-icons.png'),
};
type Textures = Record<keyof typeof TEXTURES, SkImage>;
let textures: Promise<Textures> | undefined;

function loadTextures() {
  textures ??= Promise.all(
    Object.entries(TEXTURES).map(([name, source]) =>
      loadData(source, (data) => Skia.Image.MakeImageFromEncoded(data)).then((image) => {
        if (!image) throw new Error(`${name} texture could not decode`);
        return [name, image] as const;
      })
    )
  )
    .then((entries) => Object.fromEntries(entries) as Textures)
    .catch((error: unknown) => {
      textures = undefined;
      throw error;
    });
  return textures;
}

const NEAREST = { filter: FilterMode.Nearest, mipmap: MipmapMode.None } as const;
const LINEAR = { filter: FilterMode.Linear, mipmap: MipmapMode.None } as const;
type SceneProps = { viewport: GlobeViewport; initialCamera?: GlobeCamera };

export function GlobeCanvas(props: SceneProps) {
  const [attempt, setAttempt] = useState(0);
  return <GlobeScene key={attempt} {...props} onRetry={() => setAttempt((value) => value + 1)} />;
}

function GlobeScene({
  viewport,
  initialCamera,
  onRetry,
}: SceneProps & { onRetry: () => void }) {
  const openingCamera = initialCamera ?? OPENING_CAMERA;
  const [error, setError] = useState(false);
  const [images, setImages] = useState<Textures | null>(null);
  useEffect(() => {
    let active = true;
    loadTextures()
      .then((value) => {
        if (active) setImages(value);
      })
      .catch(() => {
        if (active) setError(true);
      });
    return () => {
      active = false;
    };
  }, []);
  const camera = useSharedValue(openingCamera);
  const [snapshot, setSnapshot] = useState(openingCamera);
  const reset = useCallback(() => camera.set(openingCamera), [camera, openingCamera]);
  const zoom = useCallback(
    (delta: number, x: number, y: number) => {
      const next = zoomGlobe(camera.get(), camera.get().zoom + delta, x, y, viewport);
      camera.set(next);
    },
    [camera, viewport]
  );
  const rotate = useCallback(
    (dx: number, dy: number) => {
      const next = rotateGlobe(camera.get(), dx, dy, viewport);
      camera.set(next);
    },
    [camera, viewport]
  );

  useAnimatedReaction(
    () => {
      const c = camera.get();
      return `${Math.floor(c.longitude / 5)}:${Math.floor(c.latitude / 5)}:${Math.floor(c.zoom * 10)}`;
    },
    (next, previous) => {
      if (next !== previous) scheduleOnRN(setSnapshot, camera.get());
    }
  );
  const pan = usePanGesture({
    maxPointers: 1,
    minDistance: 6,
    onUpdate: (event) => {
      camera.set(rotateGlobe(camera.get(), event.changeX, event.changeY, viewport));
    },
  });
  const pinch = usePinchGesture({
    onUpdate: (event) => {
      camera.set(
        zoomGlobe(
          camera.get(),
          camera.get().zoom + Math.log2(event.scaleChange),
          event.focalX,
          event.focalY,
          viewport
        )
      );
    },
  });
  const gesture = useSimultaneousGestures(pan, pinch);
  const uniforms = useDerivedValue(() => {
    const c = camera.get();
    return {
      viewport: [viewport.width, viewport.height],
      angles: [(c.longitude * Math.PI) / 180, (c.latitude * Math.PI) / 180],
      radius: globeRadius(viewport) * 2 ** c.zoom,
      zoom: c.zoom,
      textureSize: [4096, 2048],
      boardSize: [2048, 1024],
    };
  });

  if (error || !effect) return <MapStatus error onRetry={onRetry} />;
  if (!images) return <MapStatus />;
  return (
    <View style={styles.scene}>
      <MapSurface
        label="Interactive Earth globe. Use arrow keys to spin, plus or minus to zoom, and Home to reset."
        gesture={gesture}
        onZoom={zoom}
        onPan={rotate}
        onReset={reset}>
        <Canvas style={styles.fill} testID="world-globe">
          <Fill>
            <Shader source={effect} uniforms={uniforms}>
              <ImageShader image={images.globe} tx="repeat" ty="clamp" fit="none" sampling={NEAREST} />
              <ImageShader image={images.board} tx="repeat" ty="clamp" fit="none" sampling={NEAREST} />
              {/* The same board image, filtered: smooth distance-to-coast for the sea bands. */}
              <ImageShader image={images.board} tx="repeat" ty="clamp" fit="none" sampling={LINEAR} />
            </Shader>
          </Fill>
          <MapIcons image={images.icons} camera={camera} viewport={viewport} />
        </Canvas>
      </MapSurface>
      <CountryLabels viewport={viewport} camera={camera} snapshot={snapshot} />
    </View>
  );
}

const styles = StyleSheet.create({
  fill: { flex: 1 },
  scene: { flex: 1, overflow: 'hidden' },
});
