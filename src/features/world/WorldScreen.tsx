import { useLocalSearchParams } from 'expo-router';
import { useState } from 'react';

import { cameraFromParams } from './globe-camera';
import WorldView from './WorldView';

export function WorldScreen() {
  const params = useLocalSearchParams<{ lon?: string; lat?: string; zoom?: string }>();
  // Keep the entry camera as Home's reset target through tab navigation.
  const [initialCamera] = useState(() => cameraFromParams(params));
  return <WorldView initialCamera={initialCamera} />;
}
