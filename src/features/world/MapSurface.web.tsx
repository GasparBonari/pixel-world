import { useEffect, useRef } from 'react';
import { StyleSheet, View } from 'react-native';
import { GestureDetector } from 'react-native-gesture-handler';

import type { MapSurfaceProps } from './MapSurface';

export function MapSurface({
  gesture,
  enabled,
  onZoom,
  onPan,
  onReset,
  onSelectCenter,
  children,
}: MapSurfaceProps) {
  const element = useRef<HTMLDivElement>(null);
  const wasEnabled = useRef(enabled);
  useEffect(() => {
    if (enabled && !wasEnabled.current) element.current?.focus();
    wasEnabled.current = enabled;
  }, [enabled]);

  useEffect(() => {
    const node = element.current;
    if (!node || !enabled) return;
    // RNGH handles the pointer gesture. Suppress the follow-up click so it cannot hit
    // a modal control that mounted on pointer-up, outside this map surface.
    function preventTouchClick(event: TouchEvent) {
      if (event.cancelable) event.preventDefault();
    }
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
    node.addEventListener('touchend', preventTouchClick, { passive: false });
    return () => {
      node.removeEventListener('wheel', wheel);
      node.removeEventListener('touchend', preventTouchClick);
    };
  }, [enabled, onZoom]);

  return (
    <div
      ref={element}
      tabIndex={enabled ? 0 : undefined}
      aria-hidden={!enabled}
      role="region"
      aria-label="Interactive Earth map. Use arrow keys to pan, plus or minus to zoom, Enter to try the point at the center, and Home to reset."
      // Keep browser pinch zoom off the map surface even while its gestures are disabled.
      style={{ display: 'flex', flexDirection: 'column', height: '100%', outlineOffset: 4, touchAction: 'none' }}
      onKeyDown={(event) => {
        if (!enabled) return;
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
        else if (event.key === 'Enter') onSelectCenter();
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
