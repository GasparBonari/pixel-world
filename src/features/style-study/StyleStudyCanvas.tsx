import {
  Atlas,
  Canvas,
  FilterMode,
  MipmapMode,
  Picture,
  Skia,
  createPicture,
  useImage,
  type SkImage,
} from '@shopify/react-native-skia';
import { useFonts } from 'expo-font';
import { Link } from 'expo-router';
import { useMemo, useState, type PropsWithChildren } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, View, useWindowDimensions } from 'react-native';

import { PixelFonts, WorldColors } from '@/constants/theme';
import { MapStatus } from '@/features/world/MapStatus';
import {
  PALETTES,
  SCENE_HEIGHT,
  SCENE_WIDTH,
  buildScene,
  drawBatches,
  sceneScale,
  type Sheet,
} from './scene';

const SAMPLING = { filter: FilterMode.Nearest, mipmap: MipmapMode.None } as const;
const INK = '#3A2318';
const PIXEL = PixelFonts.regular;
const PIXEL_BOLD = PixelFonts.bold;
const NINJA = 'NinjaNormal';

export default function StyleStudyCanvas() {
  const { width, height } = useWindowDimensions();
  // Pixelify Sans is loaded by the root layout; only the pack's own font is loaded here.
  const [fontsLoaded] = useFonts({
    [NINJA]: require('@/assets/style-study/ninja-adventure/normal-font.ttf'),
  });
  const [palette, setPalette] = useState<'globe' | 'pack'>('globe');
  const recolored = {
    floor: useImage(require('@/assets/style-study/globe-palette/floor.png')),
    water: useImage(require('@/assets/style-study/globe-palette/water.png')),
    nature: useImage(require('@/assets/style-study/globe-palette/nature.png')),
  };
  const original: Record<Sheet, SkImage | null> = {
    floor: useImage(require('@/assets/style-study/ninja-adventure/floor.png')),
    water: useImage(require('@/assets/style-study/ninja-adventure/water.png')),
    house: useImage(require('@/assets/style-study/ninja-adventure/house.png')),
    nature: useImage(require('@/assets/style-study/ninja-adventure/nature.png')),
    inspector: useImage(require('@/assets/style-study/ninja-adventure/inspector.png')),
    villager: useImage(require('@/assets/style-study/ninja-adventure/villager.png')),
    boat: useImage(require('@/assets/style-study/ninja-adventure/boat.png')),
  };
  const panel = useImage(require('@/assets/style-study/ninja-adventure/panel.png'));

  const images = palette === 'globe' ? { ...original, ...recolored } : original;
  if (
    !fontsLoaded ||
    !panel ||
    [...Object.values(original), ...Object.values(recolored)].some((image) => !image)
  )
    return <MapStatus />;

  const scale = sceneScale(width, height * 0.6);
  const sceneWidth = SCENE_WIDTH * scale;
  const ui = scale >= 3 ? 3 : 2;

  return (
    <ScrollView style={styles.page} contentContainerStyle={styles.content}>
      <View style={[styles.column, { maxWidth: sceneWidth }]}>
        <View style={styles.header}>
          <Link href="/" style={styles.back}>
            ‹ Globe
          </Link>
          <Text style={styles.title} accessibilityRole="header">
            Style study
          </Text>
        </View>
        <Text style={styles.caption}>
          Ninja Adventure tiles (CC0) at {scale}× · Pixelify Sans · candidate for P2-06
        </Text>
        <View style={styles.toggle} accessibilityRole="radiogroup">
          {(
            [
              ['globe', 'Globe palette'],
              ['pack', 'Pack colours'],
            ] as const
          ).map(([value, label]) => (
            <Pressable
              key={value}
              accessibilityRole="radio"
              accessibilityState={{ checked: palette === value }}
              onPress={() => setPalette(value)}
              style={[styles.toggleButton, palette === value && styles.toggleSelected]}>
              <Text style={[styles.toggleText, palette === value && styles.toggleTextSelected]}>
                {label}
              </Text>
            </Pressable>
          ))}
        </View>
      </View>

      <View style={[styles.sceneFrame, { width: Math.min(sceneWidth, width) }]}>
        <Scene images={images as Record<Sheet, SkImage>} scale={scale} />
      </View>

      <View style={[styles.column, { maxWidth: sceneWidth }]}>
        <PixelPanel image={panel} scale={ui}>
          <Text style={styles.cardTitle}>City Challenges</Text>
          <Text style={styles.cardNote}>Sample text for the style study</Text>
          {['Try a local pastry', 'Visit a viewpoint', 'Ride a historic tram'].map((label, i) => (
            <View key={label} style={styles.row}>
              <View style={[styles.check, i === 0 && styles.checkDone]} />
              <Text style={styles.rowText}>{label}</Text>
            </View>
          ))}
        </PixelPanel>

        <PixelPanel image={panel} scale={ui}>
          <Text style={styles.cardTitle}>Type</Text>
          <FontSample family={PIXEL} label="Pixelify Sans (OFL)" />
          <FontSample family={NINJA} label="Ninja Adventure font" />
        </PixelPanel>

        <View style={styles.palettes}>
          <Swatches title="Globe shader" colors={PALETTES.globe} />
          <Swatches title="Ninja Adventure" colors={PALETTES.pack} />
        </View>
      </View>
    </ScrollView>
  );
}

function Scene({ images, scale }: { images: Record<Sheet, SkImage>; scale: number }) {
  const batches = useMemo(
    () =>
      drawBatches(buildScene()).map((batch) => ({
        key: `${batch.layer}:${batch.sheet}`,
        sheet: batch.sheet,
        sprites: batch.items.map(({ source: [x, y, w, h] }) => Skia.XYWHRect(x, y, w, h)),
        transforms: batch.items.map((item) =>
          Skia.RSXform(scale, 0, item.x * scale, item.y * scale)
        ),
      })),
    [scale]
  );
  return (
    <Canvas
      style={{ width: SCENE_WIDTH * scale, height: SCENE_HEIGHT * scale }}
      accessibilityLabel="Pixel-art seaside street with houses, trees, two people and a boat">
      {batches.map((batch) => (
        <Atlas
          key={batch.key}
          image={images[batch.sheet]}
          sprites={batch.sprites}
          transforms={batch.transforms}
          sampling={SAMPLING}
        />
      ))}
    </Canvas>
  );
}

/** Text in normal React Native views over a pixel nine-slice frame drawn by Skia. */
function PixelPanel({ image, scale, children }: PropsWithChildren<{ image: SkImage; scale: number }>) {
  const [size, setSize] = useState({ width: 0, height: 0 });
  const picture = useMemo(() => {
    if (!size.width || !size.height) return null;
    return createPicture(
      (canvas) => {
        canvas.scale(scale, scale);
        canvas.drawImageNine(
          image,
          Skia.XYWHRect(6, 6, 5, 5),
          Skia.XYWHRect(0, 0, Math.floor(size.width / scale), Math.floor(size.height / scale)),
          FilterMode.Nearest
        );
      },
      { width: size.width, height: size.height }
    );
  }, [image, scale, size]);
  return (
    <View
      style={styles.panel}
      onLayout={({ nativeEvent: { layout } }) => {
        const next = { width: Math.round(layout.width), height: Math.round(layout.height) };
        setSize((value) =>
          value.width === next.width && value.height === next.height ? value : next
        );
      }}>
      {picture && (
        <Canvas style={StyleSheet.absoluteFill} pointerEvents="none">
          <Picture picture={picture} />
        </Canvas>
      )}
      <View style={{ paddingHorizontal: 9 * scale, paddingVertical: 8 * scale }}>{children}</View>
    </View>
  );
}

function FontSample({ family, label }: { family: string; label: string }) {
  return (
    <View style={styles.fontSample}>
      <Text style={[styles.fontLabel]}>{label}</Text>
      <Text style={{ fontFamily: family, fontSize: 22, color: INK }}>Lisbon · Explore</Text>
      <Text style={{ fontFamily: family, fontSize: 15, color: INK }}>
        Walk the waterfront and find the viewpoint. 2 of 4 complete.
      </Text>
    </View>
  );
}

function Swatches({
  title,
  colors,
}: {
  title: string;
  colors: readonly (readonly [string, string])[];
}) {
  return (
    <View style={styles.swatchGroup}>
      <Text style={styles.swatchTitle}>{title}</Text>
      <View style={styles.swatchRow}>
        {colors.map(([name, color]) => (
          <View key={name} style={styles.swatch}>
            <View style={[styles.swatchColor, { backgroundColor: color }]} />
            <Text style={styles.swatchLabel}>{name}</Text>
            <Text style={styles.swatchLabel}>{color}</Text>
          </View>
        ))}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  page: { flex: 1, backgroundColor: WorldColors.space },
  content: { alignItems: 'center', paddingVertical: 16, gap: 14 },
  column: { width: '100%', paddingHorizontal: 12, gap: 14 },
  header: { flexDirection: 'row', alignItems: 'center', gap: 14 },
  back: { fontFamily: PIXEL, fontSize: 16, color: '#FFAD5D', padding: 6 },
  title: { fontFamily: PIXEL_BOLD, fontSize: 26, color: '#F5F0DC' },
  caption: { fontFamily: PIXEL, fontSize: 13, color: '#B9C2CF', marginTop: -8 },
  toggle: { flexDirection: 'row', gap: 8 },
  toggleButton: {
    minHeight: 40,
    justifyContent: 'center',
    paddingHorizontal: 12,
    borderWidth: 2,
    borderColor: '#FFAD5D',
  },
  toggleSelected: { backgroundColor: '#FFAD5D' },
  toggleText: { fontFamily: PIXEL, fontSize: 14, color: '#FFAD5D' },
  toggleTextSelected: { color: '#141B1B' },
  sceneFrame: { alignItems: 'center', overflow: 'hidden' },
  panel: { width: '100%' },
  cardTitle: { fontFamily: PIXEL_BOLD, fontSize: 20, color: INK },
  cardNote: { fontFamily: PIXEL, fontSize: 12, color: '#8A6A55', marginBottom: 8 },
  row: { flexDirection: 'row', alignItems: 'center', gap: 10, paddingVertical: 4 },
  check: { width: 14, height: 14, borderWidth: 2, borderColor: INK, backgroundColor: '#FFF' },
  checkDone: { backgroundColor: '#5FA84B' },
  rowText: { fontFamily: PIXEL, fontSize: 16, color: INK },
  fontSample: { marginTop: 8, gap: 2 },
  fontLabel: { fontFamily: PIXEL, fontSize: 12, color: '#8A6A55' },
  palettes: { gap: 10 },
  swatchGroup: { gap: 4 },
  swatchTitle: { fontFamily: PIXEL_BOLD, fontSize: 14, color: '#F5F0DC' },
  swatchRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 6 },
  swatch: { width: 58, alignItems: 'flex-start' },
  swatchColor: { width: 58, height: 26, borderWidth: 2, borderColor: '#141B1B' },
  swatchLabel: { fontFamily: PIXEL, fontSize: 10, color: '#B9C2CF' },
});
