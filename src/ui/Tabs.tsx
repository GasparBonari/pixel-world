import { TabTrigger, type TabTriggerSlotProps } from 'expo-router/ui';
import type { ComponentProps } from 'react';
import { Pressable, StyleSheet, View } from 'react-native';

import { Frames, Palette, Size, Space, px } from '@/constants/theme';

import { PixelFrame } from './PixelFrame';
import { PixelIcon, type IconName } from './PixelIcon';
import { PixelText } from './PixelText';

export type TabItem<K extends string> = { key: K; label: string; icon?: IconName };

type TabsProps<K extends string> = {
  items: readonly TabItem<K>[];
  value: K;
  onChange: (key: K) => void;
};

/** In-screen section switcher (Discover / Challenges / Info). The selected tab is gold. */
export function SegmentedTabs<K extends string>({ items, value, onChange }: TabsProps<K>) {
  return (
    <View style={styles.segmented} accessibilityRole="tablist">
      {items.map((item) => {
        const selected = item.key === value;
        return (
          <Pressable
            key={item.key}
            style={styles.grow}
            onPress={() => onChange(item.key)}
            accessibilityRole="tab"
            accessibilityState={{ selected }}
            accessibilityLabel={item.label}>
            <PixelFrame skin={selected ? 'gold' : 'navy'} depth={1} pressed={selected} contentStyle={styles.segment}>
              {item.icon && <PixelIcon name={item.icon} />}
              <PixelText variant="label" tone={selected ? 'ink' : 'light'} numberOfLines={1}>
                {item.label}
              </PixelText>
            </PixelFrame>
          </Pressable>
        );
      })}
    </View>
  );
}

type TabBarProps<K extends string> = TabsProps<K> | { items: readonly TabItem<K>[] };

/** The app's bottom tabs. Register their names and routes in the navigator's TabList. */
export function TabBar<K extends string>(props: TabBarProps<K>) {
  return (
    <View style={styles.bar} accessibilityRole="tablist">
      {props.items.map((item) => 'onChange' in props ? (
        <TabBarButton
          key={item.key}
          label={item.label}
          icon={item.icon}
          style={styles.grow}
          isFocused={item.key === props.value}
          onPress={() => props.onChange(item.key)}
        />
      ) : (
        <TabTrigger key={item.key} name={item.key} style={styles.grow} asChild>
          <TabBarButton label={item.label} icon={item.icon} />
        </TabTrigger>
      ))}
    </View>
  );
}

function TabBarButton({
  label, icon, isFocused = false, ...props
}: ComponentProps<typeof Pressable> & Pick<TabTriggerSlotProps, 'href' | 'isFocused'> & {
  label: string;
  icon?: IconName;
}) {
  return (
    <Pressable
      {...props}
      accessibilityRole="tab"
      aria-selected={isFocused}
      accessibilityLabel={label}>
      <PixelFrame skin={isFocused ? 'gold' : 'navy'} depth={1} pressed={isFocused} contentStyle={styles.tab}>
        {icon && <PixelIcon name={icon} />}
        <PixelText variant="caption" tone={isFocused ? 'ink' : 'light'} numberOfLines={1}>
          {label}
        </PixelText>
      </PixelFrame>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  grow: { flex: 1 },
  segmented: { flexDirection: 'row', gap: Space.xs },
  segment: {
    minHeight: Size.touch - px(1),
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: Space.xs,
    paddingHorizontal: Space.xs,
  },
  bar: {
    flexDirection: 'row',
    gap: Space.xs,
    padding: Space.xs,
    backgroundColor: Palette.navyDeep,
    borderTopWidth: px(1),
    borderTopColor: Frames.navy.highlight,
  },
  tab: { minHeight: Size.touch + px(4), alignItems: 'center', justifyContent: 'center', gap: px(1) },
});
