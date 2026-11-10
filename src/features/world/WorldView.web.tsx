import { WithSkiaWeb } from '@shopify/react-native-skia/lib/module/web';
import { Component, useSyncExternalStore, type PropsWithChildren } from 'react';

import type { GlobeCamera } from './globe-camera';
import { MapStatus } from './MapStatus';

const subscribe = () => () => {};
const loadCanvas = () => import('./WorldCanvas');
const options = { locateFile: (file: string) => `/${file}` };

class MapErrorBoundary extends Component<PropsWithChildren, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() {
    return { failed: true };
  }
  render() {
    return this.state.failed ? (
      <MapStatus error onRetry={() => window.location.reload()} />
    ) : (
      this.props.children
    );
  }
}

export default function WorldView({ initialCamera }: { initialCamera?: GlobeCamera }) {
  const ready = useSyncExternalStore(
    subscribe,
    () => true,
    () => false
  );
  if (!ready) return <MapStatus />;
  return (
    <MapErrorBoundary>
      <WithSkiaWeb
        getComponent={loadCanvas}
        opts={options}
        fallback={<MapStatus />}
        componentProps={{ initialCamera }}
      />
    </MapErrorBoundary>
  );
}
