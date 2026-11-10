import { useSyncExternalStore } from 'react';
import { useColorScheme as useRNColorScheme } from 'react-native';

const subscribe = () => () => {};

export function useColorScheme() {
  const colorScheme = useRNColorScheme();
  // Match the server's light theme on the first hydration render.
  const hasHydrated = useSyncExternalStore(subscribe, () => true, () => false);

  if (hasHydrated) {
    return colorScheme;
  }

  return 'light';
}
