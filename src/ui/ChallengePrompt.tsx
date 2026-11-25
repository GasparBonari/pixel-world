import { StyleSheet, View } from 'react-native';

import { Space, px } from '@/constants/theme';

import { PixelFrame } from './PixelFrame';
import { PixelIcon } from './PixelIcon';
import { PixelText } from './PixelText';
import { useSteps } from './use-steps';

const SHAKE = [0, -2, 2, -1, 1, 0] as const;

type ChallengePromptProps = {
  title: string;
  feedback?: string;
  /** Increment on each miss to replay the shake. */
  misses?: number;
  complete?: boolean;
};

export function ChallengePrompt({ title, feedback, misses = 0, complete = false }: ChallengePromptProps) {
  const frame = useSteps(SHAKE.length, misses);
  return (
    <View style={misses > 0 && { transform: [{ translateX: px(SHAKE[frame]) }] }}>
      <PixelFrame skin={complete ? 'green' : 'parchment'} contentStyle={styles.row}>
        <PixelIcon name={complete ? 'check' : 'landmark'} />
        <View style={styles.copy} accessibilityLiveRegion="polite" aria-live="polite">
          <PixelText variant="label">{title}</PixelText>
          {feedback && <PixelText variant="caption">{feedback}</PixelText>}
        </View>
      </PixelFrame>
    </View>
  );
}

const styles = StyleSheet.create({
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Space.sm,
    paddingHorizontal: Space.sm,
  },
  copy: { flex: 1 },
});
