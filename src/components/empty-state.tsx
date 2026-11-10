import { Link, type Href } from 'expo-router';
import { Pressable, StyleSheet, View } from 'react-native';

import { ThemedText } from '@/components/themed-text';
import { Spacing } from '@/constants/theme';
import { useTheme } from '@/hooks/use-theme';

type EmptyStateProps = {
  label: string;
  title: string;
  description: string;
  actionLabel: string;
  href: Href;
};

export function EmptyState({ label, title, description, actionLabel, href }: EmptyStateProps) {
  const theme = useTheme();

  return (
    <View style={[styles.card, { backgroundColor: theme.backgroundElement, borderColor: theme.border }]}>
      <ThemedText type="code" themeColor="accent" style={styles.label}>
        {label}
      </ThemedText>
      <View style={[styles.symbol, { backgroundColor: theme.backgroundSelected }]} aria-hidden>
        <ThemedText type="subtitle" themeColor="accent">
          +
        </ThemedText>
      </View>
      <View style={styles.message}>
        <ThemedText type="subtitle" style={styles.title}>
          {title}
        </ThemedText>
        <ThemedText themeColor="textSecondary" style={styles.description}>
          {description}
        </ThemedText>
      </View>
      <Link href={href} asChild>
        <Pressable
          android_ripple={{ color: theme.backgroundSelected }}
          style={StyleSheet.flatten([styles.action, { backgroundColor: theme.accent }])}>
          <ThemedText type="smallBold" themeColor="textOnAccent">
            {actionLabel}
          </ThemedText>
        </Pressable>
      </Link>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    alignItems: 'center',
    borderWidth: 2,
    paddingHorizontal: Spacing.four,
    paddingVertical: Spacing.five,
    gap: Spacing.four,
  },
  label: {
    letterSpacing: 2,
    textAlign: 'center',
  },
  symbol: {
    width: Spacing.six,
    height: Spacing.six,
    alignItems: 'center',
    justifyContent: 'center',
  },
  message: {
    alignItems: 'center',
    gap: Spacing.two,
  },
  title: {
    fontSize: 24,
    lineHeight: 32,
    textAlign: 'center',
  },
  description: {
    textAlign: 'center',
    maxWidth: 400,
  },
  action: {
    minHeight: 48,
    minWidth: 160,
    paddingHorizontal: Spacing.four,
    paddingVertical: Spacing.three,
    alignItems: 'center',
    justifyContent: 'center',
  },
});
