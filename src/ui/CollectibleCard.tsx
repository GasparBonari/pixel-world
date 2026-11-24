import { Image, Linking, Pressable, StyleSheet, View, type ImageSourcePropType } from 'react-native';

import { Palette, Space, px } from '@/constants/theme';

import { Chip } from './Chip';
import { PixelButton } from './PixelButton';
import { PixelIcon, type IconName } from './PixelIcon';
import { PixelText } from './PixelText';
import { Ribbon } from './Ribbon';

export type CollectibleKind = 'landmark' | 'wildlife' | 'landscape';

const Kinds: Record<CollectibleKind, { label: string; icon: IconName }> = {
  landmark: { label: 'Landmark', icon: 'landmark' },
  wildlife: { label: 'Wildlife', icon: 'paw' },
  landscape: { label: 'Landscape', icon: 'mountain' },
};

export type CollectibleCardProps = {
  name: string;
  kind: CollectibleKind;
  /** Crop of the capital scene or the landmark's 4× study. */
  image?: ImageSourcePropType;
  /** One or two checked sentences from the content catalog. Never written in the component. */
  description: string;
  /** Where the facts come from; always shown. */
  source: { label: string; url: string };
  /** When the player found it. Omit while it is still missing. */
  foundOn?: Date;
  /** Shows the gold "Found!" ribbon: the moment the player finds it. */
  justFound?: boolean;
  /** The card's single button. */
  onClose: () => void;
  closeLabel?: string;
};

/**
 * The collectible detail card, shown inside a `PixelModal`:
 *
 *   <PixelModal visible={open} onClose={close} label={item.name}>
 *     <CollectibleCard {...item} justFound onClose={close} />
 *   </PixelModal>
 */
export function CollectibleCard({
  name,
  kind,
  image,
  description,
  source,
  foundOn,
  justFound = false,
  onClose,
  closeLabel = 'Keep exploring',
}: CollectibleCardProps) {
  const k = Kinds[kind];
  return (
    <>
      {justFound && <Ribbon label="Found!" icon="star" skin="gold" />}
      <View style={styles.picture}>
        {image ? (
          <Image source={image} style={styles.image} resizeMode="cover" accessibilityIgnoresInvertColors />
        ) : (
          <PixelIcon name={k.icon} />
        )}
      </View>
      <Chip label={k.label} icon={k.icon} />
      <PixelText variant="title" accessibilityRole="header">
        {name}
      </PixelText>
      <PixelText variant="body">{description}</PixelText>
      <Pressable
        onPress={() => Linking.openURL(source.url)}
        accessibilityRole="link"
        accessibilityLabel={`Source: ${source.label}`}
        style={styles.source}>
        <PixelIcon name="info" />
        <PixelText variant="caption" tone="inkSoft" style={styles.sourceText} numberOfLines={2}>
          Source: {source.label}
        </PixelText>
        <PixelIcon name="chevron" />
      </Pressable>
      {foundOn && (
        <PixelText variant="caption" tone="success">
          Found {foundOn.toLocaleDateString(undefined, { day: 'numeric', month: 'short', year: 'numeric' })}
        </PixelText>
      )}
      <PixelButton variant="primary" label={closeLabel} onPress={onClose} block />
    </>
  );
}

const styles = StyleSheet.create({
  picture: {
    height: px(64),
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: Palette.navyDeep,
    borderWidth: px(1),
    borderColor: Palette.parchmentEdge,
    overflow: 'hidden',
  },
  image: { width: '100%', height: '100%' },
  source: { flexDirection: 'row', alignItems: 'center', gap: Space.sm, minHeight: px(24) },
  sourceText: { flex: 1 },
});
