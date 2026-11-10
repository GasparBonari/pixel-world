import { WithSkiaWeb } from '@shopify/react-native-skia/lib/module/web';
import { useSyncExternalStore } from 'react';

import { MapStatus } from '@/features/world/MapStatus';

const subscribe = () => () => {};
const loadCanvas = () => import('./StyleStudyCanvas');
const options = { locateFile: (file: string) => `/${file}` };

export default function StyleStudyView() {
  // CanvasKit loads in the browser only; server rendering shows the loading state.
  const ready = useSyncExternalStore(
    subscribe,
    () => true,
    () => false
  );
  if (!ready) return <MapStatus />;
  return <WithSkiaWeb getComponent={loadCanvas} opts={options} fallback={<MapStatus />} />;
}
