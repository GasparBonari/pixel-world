import type { PropsWithChildren } from 'react';
import { Modal, Pressable, StyleSheet, View, useWindowDimensions } from 'react-native';

import { Palette, Size, Space } from '@/constants/theme';

import { Panel } from './Panel';
import { PixelButton } from './PixelButton';
import { PixelText } from './PixelText';
import { useSteps } from './use-steps';

/** Card pop: three frames at 12 fps (a quarter second). Reduce motion shows the last. */
const POP = [0.85, 1.05, 1] as const;

export type PixelModalProps = PropsWithChildren<{
  visible: boolean;
  /** Called by the backdrop, the Android back button, and the dialog's own buttons. */
  onClose: () => void;
  /** Screen-reader name for the dialog. */
  label: string;
}>;

/**
 * A centred parchment dialog over a dimmed world. It pops in with a stepped scale. The map
 * under it stays mounted. Content: `CollectibleCard`, `ConfirmDialog`, or a custom column.
 */
export function PixelModal({ visible, onClose, label, children }: PixelModalProps) {
  const frame = useSteps(POP.length, visible);
  const { height } = useWindowDimensions();
  return (
    <Modal visible={visible} transparent animationType="none" onRequestClose={onClose}>
      <View style={styles.backdrop}>
        <Pressable
          style={StyleSheet.absoluteFill}
          onPress={onClose}
          accessibilityRole="button"
          accessibilityLabel="Close"
        />
        <View
          style={[styles.dialog, { maxHeight: height * 0.85, transform: [{ scale: POP[frame] }] }]}
          accessibilityViewIsModal
          accessibilityLabel={label}>
          <Panel>{children}</Panel>
        </View>
      </View>
    </Modal>
  );
}

export type ConfirmDialogProps = {
  visible: boolean;
  title: string;
  /** What will happen, in one or two sentences, including whether it can be undone. */
  message: string;
  confirmLabel: string;
  cancelLabel?: string;
  /** Red confirm button for actions that delete records ("Reset progress"). */
  destructive?: boolean;
  onConfirm: () => void;
  onCancel: () => void;
};

/**
 * Ask before an action that loses something. Name the action on the button ("Reset progress"),
 * never "OK". Prefer an Undo notice instead when the action can be reversed.
 */
export function ConfirmDialog({
  visible,
  title,
  message,
  confirmLabel,
  cancelLabel = 'Cancel',
  destructive = false,
  onConfirm,
  onCancel,
}: ConfirmDialogProps) {
  return (
    <PixelModal visible={visible} onClose={onCancel} label={title}>
      <PixelText variant="heading" accessibilityRole="header">
        {title}
      </PixelText>
      <PixelText variant="body" tone="inkSoft">
        {message}
      </PixelText>
      <View style={styles.buttons}>
        <PixelButton label={cancelLabel} onPress={onCancel} style={styles.button} />
        <PixelButton
          label={confirmLabel}
          variant={destructive ? 'danger' : 'primary'}
          onPress={onConfirm}
          style={styles.button}
        />
      </View>
    </PixelModal>
  );
}

const styles = StyleSheet.create({
  backdrop: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: Space.lg,
    backgroundColor: Palette.scrim,
  },
  dialog: { width: '100%', maxWidth: Size.maxContentWidth },
  buttons: { flexDirection: 'row', flexWrap: 'wrap', gap: Space.sm, paddingTop: Space.sm },
  button: { flexGrow: 1, flexBasis: '40%' },
});
