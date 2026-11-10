import { ActivityIndicator, Pressable, StyleSheet, View } from 'react-native';

import { ThemedText } from '@/components/themed-text';
import { Colors, PixelFonts, Spacing, WorldColors } from '@/constants/theme';

export function MapStatus({
  error = false,
  onRetry,
}: {
  error?: boolean;
  onRetry?: () => void;
}) {
  const theme = Colors.dark;
  return (
    <View style={styles.container}>
      {!error && <ActivityIndicator color={theme.accent} accessibilityLabel="Loading map" />}
      <ThemedText type="small" style={styles.message}>
        {error ? 'The map couldn’t load. Please try again.' : 'Preparing your world…'}
      </ThemedText>
      {error && onRetry && (
        <Pressable
          accessibilityRole="button"
          onPress={onRetry}
          style={[styles.retry, { backgroundColor: theme.accent }]}>
          <ThemedText type="smallBold" style={[styles.pixelBold, { color: theme.textOnAccent }]}>
            Reload map
          </ThemedText>
        </Pressable>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: WorldColors.space,
    justifyContent: 'center',
    alignItems: 'center',
    gap: Spacing.three,
  },
  message: {
    textAlign: 'center',
    paddingHorizontal: Spacing.three,
    color: Colors.dark.text,
    fontFamily: PixelFonts.regular,
    fontWeight: 'normal',
    fontSize: 16,
  },
  // Custom font files carry their own weight; a synthetic fontWeight would blur the pixels.
  pixelBold: { fontFamily: PixelFonts.bold, fontWeight: 'normal' },
  retry: { minHeight: 48, justifyContent: 'center', paddingHorizontal: Spacing.four },
});
