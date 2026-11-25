import type { PropsWithChildren } from 'react';
import { StyleSheet, View } from 'react-native';
import { GestureDetector, type ComposedGesture } from 'react-native-gesture-handler';

export type MapSurfaceProps = PropsWithChildren<{
  gesture: ComposedGesture;
  enabled: boolean;
  onZoom: (delta: number, x: number, y: number) => void;
  onPan: (dx: number, dy: number) => void;
  onReset: () => void;
  onSelectCenter: () => void;
}>;

export function MapSurface({ gesture, children }: MapSurfaceProps) {
  return (
    <GestureDetector gesture={gesture} touchAction="none">
      <View style={styles.fill}>{children}</View>
    </GestureDetector>
  );
}

const styles = StyleSheet.create({ fill: { flex: 1 } });
