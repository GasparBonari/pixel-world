import { useLocalSearchParams } from 'expo-router';
import { useMemo } from 'react';

import { cameraFromParams } from '@/features/world/globe-camera';
import WorldView from '@/features/world/WorldView';

export default function WorldScreen() {
  // Optional deep link to a view, e.g. /?lon=14.5&lat=35.9&zoom=2.6 (handy for design review).
  const params = useLocalSearchParams<{ lon?: string; lat?: string; zoom?: string }>();
  const initialCamera = useMemo(() => cameraFromParams(params), [params]);
  return <WorldView initialCamera={initialCamera} />;
}
