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
import { useIsFocused } from 'expo-router';
import { use, useCallback, useEffect, useState } from 'react';
import { StyleSheet, View } from 'react-native';
import {
  usePanGesture,
  usePinchGesture,
  useSimultaneousGestures,
  useTapGesture,
} from 'react-native-gesture-handler';
import { useDerivedValue, useSharedValue } from 'react-native-reanimated';
import { scheduleOnRN } from 'react-native-worklets';

import { CAPITAL_IMAGES } from '@/data/capital-images';
import capitals from '@/data/capitals.json';
import { WorldMapScreen } from '@/features/country-sheet/WorldMapScreen';
import { FoundLandmarkDialog } from '@/features/find-it/FoundLandmarkDialog';
import { useFindIt } from '@/features/find-it/use-find-it';
import { WorldReadyContext } from '@/features/navigation/GameTabs';
import { ChallengePrompt } from '@/ui';
import { boardCountryIndex } from './board-country-lookup';
import { Birds } from './Birds';
import { ContinentLabels } from './ContinentLabels';
import { CountryFerry } from './CountryFerry';
import { CountryLabels } from './CountryLabels';
import {
  activeCapital,
  EARTH_OVERVIEW_END,
  globeRadius,
  OPENING_CAMERA,
  rotateGlobe,
  zoomGlobe,
  type GlobeCamera,
  type GlobeViewport,
} from './globe-camera';
import { CELLS_ACROSS, globeShader } from './globe-shader';
import { CapitalLayer } from './CapitalLayer';
import { clampToCapitals } from './capitals';
import { MapIcons } from './MapIcons';
import { MapStatus } from './MapStatus';
import { MapSurface } from './MapSurface';
import { sunDirection } from './motion';
import { useWorldClock } from './use-world-clock';
import { useWorldNavigation } from './use-world-navigation';

const effect = Skia.RuntimeEffect.Make(globeShader);
// Globe (32 MiB decoded), board (8 MiB), depth (2 MiB) and icon sheet, each decoded once per app session.
const TEXTURES = {
  globe: require('@/assets/world/globe.png'),
  board: require('@/assets/world/board.png'),
  depth: require('@/assets/world/depth.png'),
  lights: require('@/assets/world/city-lights.png'),
  icons: require('@/assets/world/map-icons.png'),
  ...CAPITAL_IMAGES,
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
  const focused = useIsFocused();
  const revealTabs = use(WorldReadyContext);
  // A camera parsed from the launch URL goes directly to the map.
  const [showTitle, setShowTitle] = useState(initialCamera === undefined);
  const [error, setError] = useState(false);
  const [images, setImages] = useState<Textures | null>(null);
  useEffect(() => {
    if (!showTitle && images && effect) revealTabs?.();
  }, [showTitle, images, revealTabs]);
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
  const { time, touch, returnToOpening } = useWorldClock(camera, focused && images !== null);
  const navigation = useWorldNavigation(camera, openingCamera, viewport, touch);
  const { snapshot, selectAt } = navigation;
  const earthOverview = snapshot.zoom < EARTH_OVERVIEW_END;
  // Icon pixels are two-thirds of a terrain pixel (3 points on a phone -> 2 points).
  const iconScale = (Math.max(1.25, Math.min(viewport.width, viewport.height) / CELLS_ACROSS) * 2) / 3;
  const { tapAt, banner, assist, capitalId, recentFind, closeCard } = useFindIt(snapshot, viewport, iconScale);
  const selectMapPoint = useCallback((x: number, y: number, current: GlobeCamera) => {
    selectAt(x, y, current);
    tapAt(x, y, current);
  }, [selectAt, tapAt]);

  function selectCenter() {
    touch();
    selectMapPoint(viewport.width / 2, viewport.height / 2, camera.get());
  }

  const enterWorld = useCallback(() => {
    returnToOpening();
    setShowTitle(false);
  }, [returnToOpening]);

  const zoom = useCallback(
    (delta: number, x: number, y: number) => {
      touch();
      const next = zoomGlobe(camera.get(), camera.get().zoom + delta, x, y, viewport);
      camera.set(clampToCapitals(next, capitals, viewport, iconScale));
    },
    [camera, viewport, iconScale, touch]
  );
  const rotate = useCallback(
    (dx: number, dy: number) => {
      touch();
      const next = rotateGlobe(camera.get(), dx, dy, viewport);
      camera.set(clampToCapitals(next, capitals, viewport, iconScale));
    },
    [camera, viewport, iconScale, touch]
  );

  const suppressTap = useSharedValue(false);
  // Any touch stops the idle spin, even one that doesn't move far enough to start a drag.
  const pan = usePanGesture({
    enabled: !showTitle,
    maxPointers: 1,
    minDistance: 6,
    onTouchesDown: () => touch(),
    onActivate: () => suppressTap.set(true),
    onUpdate: (event) => {
      touch();
      camera.set(
        clampToCapitals(
          rotateGlobe(camera.get(), event.changeX, event.changeY, viewport),
          capitals,
          viewport,
          iconScale
        )
      );
    },
  });
  const pinch = usePinchGesture({
    enabled: !showTitle,
    // Pinch tracks additional fingers on web even when there is too little motion to activate it.
    onTouchesDown: (event) => suppressTap.set(event.numberOfTouches > 1),
    onActivate: () => suppressTap.set(true),
    onUpdate: (event) => {
      touch();
      camera.set(
        clampToCapitals(
          zoomGlobe(
            camera.get(),
            camera.get().zoom + Math.log2(event.scaleChange),
            event.focalX,
            event.focalY,
            viewport
          ),
          capitals,
          viewport,
          iconScale
        )
      );
    },
  });
  const tap = useTapGesture({
    enabled: !showTitle,
    maxDistance: 5,
    onDeactivate: (event) => {
      if (!event.canceled && !suppressTap.get()) {
        scheduleOnRN(selectMapPoint, event.x, event.y, camera.get());
      }
    },
  });
  const gesture = useSimultaneousGestures(pan, pinch, tap);
  // Only the capital being visited runs its scene animation (snapshot follows the camera in steps).
  const visiting = activeCapital(snapshot)?.id;
  const selectedCountry = navigation.selection ? boardCountryIndex(navigation.selection.country.id) : 0;
  const uniforms = useDerivedValue(() => {
    const c = camera.get();
    const sceneTime = time.get();
    return {
      viewport: [viewport.width, viewport.height],
      angles: [(c.longitude * Math.PI) / 180, (c.latitude * Math.PI) / 180],
      radius: globeRadius(viewport, c.zoom),
      zoom: c.zoom,
      selectedCountry,
      time: sceneTime,
      sun: sunDirection(c.longitude, c.latitude, sceneTime),
      textureSize: [4096, 2048],
      boardSize: [2048, 1024],
      seabedSize: [1024, 512],
    };
  });

  if (error || !effect) return <MapStatus error onRetry={onRetry} />;
  if (!images) return <MapStatus />;
  return (
    <WorldMapScreen
      earthOverview={earthOverview}
      selection={navigation.selection}
      selectedScene={navigation.selection && images[navigation.selection.capital.id as keyof typeof CAPITAL_IMAGES]}
      regionalTitle={navigation.regionalTitle}
      capitalName={navigation.capitalName}
      prompt={banner && <ChallengePrompt {...banner} />}
      onEnterWorld={showTitle ? enterWorld : undefined}
      onBack={navigation.back}
      backLabel={navigation.backLabel}
      onClose={navigation.clearSelection}
      onExplore={navigation.explore}>
      <View
        style={styles.scene}
        accessibilityElementsHidden={showTitle}
        importantForAccessibility={showTitle ? 'no-hide-descendants' : 'auto'}>
        <MapSurface
          gesture={gesture}
          enabled={!showTitle}
          onZoom={zoom}
          onPan={rotate}
          onReset={navigation.reset}
          onSelectCenter={selectCenter}>
          <Canvas style={styles.fill} testID="world-globe">
            <Fill>
              <Shader source={effect} uniforms={uniforms}>
                <ImageShader image={images.globe} tx="repeat" ty="clamp" fit="none" sampling={NEAREST} />
                <ImageShader image={images.board} tx="repeat" ty="clamp" fit="none" sampling={NEAREST} />
                {/* The same board image, filtered: smooth distance-to-coast for the sea bands. */}
                <ImageShader image={images.board} tx="repeat" ty="clamp" fit="none" sampling={LINEAR} />
                {/* Ocean depth, filtered so depth contours blend. */}
                <ImageShader image={images.depth} tx="repeat" ty="clamp" fit="none" sampling={LINEAR} />
                <ImageShader image={images.lights} tx="repeat" ty="clamp" fit="none" sampling={LINEAR} />
              </Shader>
            </Fill>
            <MapIcons image={images.icons} camera={camera} viewport={viewport} scale={iconScale} tier={0} time={time} />
            <CountryFerry image={images.icons} camera={camera} viewport={viewport} scale={iconScale} time={time} />
            <MapIcons image={images.icons} camera={camera} viewport={viewport} scale={iconScale} tier={1} time={time} />
            <Birds image={images.icons} camera={camera} viewport={viewport} scale={iconScale} time={time} />
            {capitals.map((scene) => (
              <CapitalLayer
                key={scene.id}
                image={images[scene.id as keyof typeof CAPITAL_IMAGES]}
                scene={scene}
                camera={camera}
                viewport={viewport}
                iconScale={iconScale}
                icons={images.icons}
                time={time}
                animated={visiting === scene.id}
                assist={capitalId === scene.id ? assist?.bbox : undefined}
              />
            ))}
          </Canvas>
        </MapSurface>
        {!showTitle && earthOverview && <ContinentLabels viewport={viewport} camera={camera} snapshot={snapshot} />}
        <CountryLabels viewport={viewport} camera={camera} snapshot={snapshot} selection={navigation.selection} />
      </View>
      {focused && recentFind && (
        <FoundLandmarkDialog
          found={recentFind}
          sceneImage={images[recentFind.prompt.landmark.parentId as keyof typeof CAPITAL_IMAGES]}
          onClose={closeCard}
        />
      )}
    </WorldMapScreen>
  );
}

const styles = StyleSheet.create({
  fill: { flex: 1 },
  scene: { flex: 1, overflow: 'hidden' },
});
