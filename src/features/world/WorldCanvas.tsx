import { useState } from 'react';
import { StyleSheet, View } from 'react-native';

import { WorldColors } from '@/constants/theme';
import { GlobeCanvas } from './GlobeCanvas';
import type { GlobeCamera, GlobeViewport } from './globe-camera';
import { MapStatus } from './MapStatus';

export default function WorldCanvas({ initialCamera }: { initialCamera?: GlobeCamera }) {
  const [viewport, setViewport] = useState<GlobeViewport>({ width: 0, height: 0 });
  return (
    <View
      style={styles.scene}
      onLayout={({ nativeEvent: { layout } }) => {
        const width = Math.round(layout.width),
          height = Math.round(layout.height);
        setViewport((value) =>
          value.width === width && value.height === height ? value : { width, height }
        );
      }}>
      {viewport.width > 0 && viewport.height > 0 ? (
        <GlobeCanvas viewport={viewport} initialCamera={initialCamera} />
      ) : (
        <MapStatus />
      )}
    </View>
  );
}
const styles = StyleSheet.create({
  scene: { flex: 1, overflow: 'hidden', backgroundColor: WorldColors.space },
});
