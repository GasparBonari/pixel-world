import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
  type PropsWithChildren,
} from 'react';
import { AccessibilityInfo, StyleSheet, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { Motion, Size, Space, px } from '@/constants/theme';

import { PixelButton } from './PixelButton';
import { PixelFrame } from './PixelFrame';
import { PixelIcon, type IconName } from './PixelIcon';
import { PixelText } from './PixelText';
import { useSteps } from './use-steps';

export type NoticeOptions = {
  /** One short sentence: "Visit to Portugal removed." */
  message: string;
  icon?: IconName;
  /** One action, usually Undo. Its handler runs once and closes the notice. */
  action?: { label: string; onPress: () => void };
  /** Milliseconds; defaults to Motion.noticeMs, or Motion.noticeWithActionMs with an action. */
  duration?: number;
};

type Shown = NoticeOptions & { id: number };

const NoticeContext = createContext<((notice: NoticeOptions) => void) | null>(null);

/** Slide in from above: three stepped frames, in UI pixels. */
const SLIDE = [-px(8), -px(2), 0] as const;

/**
 * Hosts the app's notices. Mounted once in the root layout; screens call `useNotice()`.
 * One notice at a time: a new one replaces the current one. Notices sit at the top of the
 * screen, clear of bottom sheets and the tab bar, and are announced to screen readers.
 */
export function NoticeProvider({ children }: PropsWithChildren) {
  const [notice, setNotice] = useState<Shown | null>(null);
  const nextId = useRef(0);

  const show = useCallback((options: NoticeOptions) => {
    nextId.current += 1;
    setNotice({ ...options, id: nextId.current });
  }, []);

  useEffect(() => {
    if (!notice) return;
    AccessibilityInfo.announceForAccessibility(notice.message);
    const duration = notice.duration ?? (notice.action ? Motion.noticeWithActionMs : Motion.noticeMs);
    const timer = setTimeout(() => setNotice(null), duration);
    return () => clearTimeout(timer);
  }, [notice]);

  return (
    <NoticeContext.Provider value={show}>
      {children}
      {notice && <NoticeView notice={notice} onDismiss={() => setNotice(null)} />}
    </NoticeContext.Provider>
  );
}

/**
 * Show a short notice. Use it to confirm a change and offer Undo, or to report a failed save:
 *
 *   const notify = useNotice();
 *   notify({ message: 'Visit removed.', icon: 'undo', action: { label: 'Undo', onPress: restore } });
 */
export function useNotice() {
  const show = useContext(NoticeContext);
  if (!show) throw new Error('useNotice needs <NoticeProvider> (mounted in src/app/_layout.tsx)');
  return show;
}

function NoticeView({ notice, onDismiss }: { notice: Shown; onDismiss: () => void }) {
  const insets = useSafeAreaInsets();
  const frame = useSteps(SLIDE.length, notice.id);
  const { action } = notice;
  return (
    <View
      style={[styles.layer, { top: insets.top + Space.sm }]}
      pointerEvents="box-none"
      accessibilityLiveRegion="polite">
      <PixelFrame
        skin="navy"
        depth={1}
        style={[styles.notice, { transform: [{ translateY: SLIDE[frame] }] }]}
        contentStyle={styles.content}>
        {notice.icon && <PixelIcon name={notice.icon} />}
        <PixelText tone="light" style={styles.message}>
          {notice.message}
        </PixelText>
        {action && (
          <PixelButton
            label={action.label}
            onPress={() => {
              // Dismiss first, so a notice the action shows ("Visit restored.") isn't cleared.
              onDismiss();
              action.onPress();
            }}
          />
        )}
      </PixelFrame>
    </View>
  );
}

const styles = StyleSheet.create({
  layer: { position: 'absolute', left: Space.sm, right: Space.sm, alignItems: 'center' },
  notice: { width: '100%', maxWidth: Size.maxContentWidth },
  content: { flexDirection: 'row', alignItems: 'center', gap: Space.md, padding: Space.sm, paddingLeft: Space.md },
  message: { flex: 1 },
});
