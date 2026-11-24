import { ActivityIndicator, StyleSheet, View } from 'react-native';

import { Palette, Space } from '@/constants/theme';
import { PixelButton, PixelText } from '@/ui';

export function MapStatus({
  error = false,
  onRetry,
}: {
  error?: boolean;
  onRetry?: () => void;
}) {
  return (
    <View style={styles.container}>
      {!error && <ActivityIndicator color={Palette.gold} accessibilityLabel="Loading map" />}
      <PixelText tone="light" align="center" style={styles.message}>
        {error ? 'The map couldn’t load. Please try again.' : 'Preparing your world…'}
      </PixelText>
      {error && onRetry && <PixelButton variant="primary" label="Reload map" onPress={onRetry} />}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Palette.space,
    justifyContent: 'center',
    alignItems: 'center',
    gap: Space.lg,
  },
  message: { paddingHorizontal: Space.lg },
});
