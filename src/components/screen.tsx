import type { PropsWithChildren } from 'react';
import { ScrollView, StyleSheet, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { ThemedText } from '@/components/themed-text';
import { MaxContentWidth, Spacing } from '@/constants/theme';
import { useTheme } from '@/hooks/use-theme';

type ScreenProps = PropsWithChildren<{
  title: string;
  description: string;
}>;

export function Screen({ title, description, children }: ScreenProps) {
  const theme = useTheme();

  return (
    <SafeAreaView
      edges={['top', 'left', 'right']}
      style={[styles.container, { backgroundColor: theme.background }]}>
      <ScrollView contentInsetAdjustmentBehavior="automatic" contentContainerStyle={styles.scroll}>
        <View style={styles.content}>
          <View style={styles.header}>
            <ThemedText type="code" themeColor="accent" style={styles.wordmark}>
              PIXEL WORLD
            </ThemedText>
            <ThemedText type="title" accessibilityRole="header">
              {title}
            </ThemedText>
            <ThemedText themeColor="textSecondary">{description}</ThemedText>
          </View>
          {children}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  scroll: {
    flexGrow: 1,
    alignItems: 'center',
  },
  content: {
    width: '100%',
    maxWidth: MaxContentWidth,
    padding: Spacing.four,
    paddingBottom: Spacing.five,
    gap: Spacing.five,
  },
  header: {
    gap: Spacing.three,
  },
  wordmark: {
    letterSpacing: 3,
    paddingVertical: Spacing.two,
  },
});
