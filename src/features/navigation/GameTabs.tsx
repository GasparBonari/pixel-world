import { usePathname } from 'expo-router';
import { TabList, TabSlot, TabTrigger, Tabs } from 'expo-router/ui';
import { createContext, useCallback, useState, type ComponentProps } from 'react';
import { Platform, StyleSheet, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { Palette } from '@/constants/theme';
import { TabBar } from '@/ui';

const TABS = [
  { key: 'world', href: '/', label: 'World', icon: 'globe' },
  { key: 'quests', href: '/quests', label: 'Quests', icon: 'scroll' },
  { key: 'passport', href: '/passport', label: 'Passport', icon: 'passport' },
] as const;

export const WorldReadyContext = createContext<(() => void) | null>(null);

// Keep each visited tab mounted. SDK 58's web Screen drops the styles when detaching is disabled.
const renderTab: NonNullable<ComponentProps<typeof TabSlot>['renderFn']> = (descriptor, { loaded, isFocused }) =>
  (loaded || isFocused) ? (
    <View
      style={[StyleSheet.absoluteFill, !isFocused && styles.inactiveScreen]}
      aria-hidden={!isFocused}>
      {descriptor.render()}
    </View>
  ) : null;

export function GameTabs() {
  const pathname = usePathname();
  const [worldReady, setWorldReady] = useState(false);
  const revealTabs = useCallback(() => setWorldReady(true), []);

  return (
    <WorldReadyContext value={revealTabs}>
      <Tabs options={{ backBehavior: 'firstRoute' }}>
        <TabSlot detachInactiveScreens={false} renderFn={renderTab} style={styles.slot} />
        <TabList style={styles.hidden}>
          {TABS.map(({ key, href }) => <TabTrigger key={key} name={key} href={href} />)}
        </TabList>
        {(worldReady || pathname !== '/') && (
          <SafeAreaView edges={['bottom', 'left', 'right']} style={styles.footer}>
            <TabBar items={TABS} />
          </SafeAreaView>
        )}
      </Tabs>
    </WorldReadyContext>
  );
}

const styles = StyleSheet.create({
  slot: { flex: 1 },
  hidden: { display: 'none' },
  // Keep Skia's drawing surface at full size while World is offscreen.
  inactiveScreen: {
    opacity: 0,
    pointerEvents: 'none',
    ...Platform.select({ web: { visibility: 'hidden' } }),
  },
  footer: { backgroundColor: Palette.navyDeep },
});
