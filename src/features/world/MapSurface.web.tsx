import { useEffect, useRef } from 'react';
import { StyleSheet, View } from 'react-native';
import { GestureDetector } from 'react-native-gesture-handler';

import type { MapSurfaceProps } from './MapSurface';

export function MapSurface({
  gesture,
  onZoom,
  onPan,
  onReset,
  children,
  label,
}: MapSurfaceProps) {
  const element = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const node = element.current;
    if (!node) return;
    function wheel(event: WheelEvent) {
      event.preventDefault();
      const bounds = node!.getBoundingClientRect();
      const pixels =
        event.deltaY * (event.deltaMode === 1 ? 16 : event.deltaMode === 2 ? bounds.height : 1);
      onZoom(
        Math.max(-0.5, Math.min(0.5, -pixels / 400)),
        event.clientX - bounds.left,
        event.clientY - bounds.top
      );
    }
    node.addEventListener('wheel', wheel, { passive: false });
    return () => node.removeEventListener('wheel', wheel);
  }, [onZoom]);

  return (
    <div
      ref={element}
      tabIndex={0}
      role="region"
      aria-label={
        label ??
        'Interactive Earth map. Use arrow keys to pan, plus or minus to zoom, and Home to reset.'
      }
      style={{ display: 'flex', flexDirection: 'column', height: '100%', outlineOffset: 4 }}
      onKeyDown={(event) => {
        const bounds = event.currentTarget.getBoundingClientRect();
        if (['+', '=', '-', '_'].includes(event.key))
          onZoom(
            ['+', '='].includes(event.key) ? 0.5 : -0.5,
            bounds.width / 2,
            bounds.height / 2
          );
        else if (event.key === 'ArrowLeft') onPan(48, 0);
        else if (event.key === 'ArrowRight') onPan(-48, 0);
        else if (event.key === 'ArrowUp') onPan(0, 48);
        else if (event.key === 'ArrowDown') onPan(0, -48);
        else if (event.key === 'Home') onReset();
        else return;
        event.preventDefault();
      }}>
      <GestureDetector gesture={gesture} touchAction="none">
        <View style={styles.fill}>{children}</View>
      </GestureDetector>
    </div>
  );
}

const styles = StyleSheet.create({ fill: { flex: 1 } });
