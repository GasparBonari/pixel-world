import { useEffect, useState } from 'react';
import { useReducedMotion } from 'react-native-reanimated';

import { Motion } from '@/constants/theme';

/**
 * Stepped animation: returns the current frame (0 … count - 1), advancing one frame every
 * `Motion.frameMs` and stopping on the last. It replays from frame 0 whenever `trigger` changes.
 * With the OS reduce-motion setting on, it returns the last frame straight away.
 *
 *   const frame = useSteps(POP.length, visible);
 *   <View style={{ transform: [{ scale: POP[frame] }] }} />
 */
export function useSteps(count: number, trigger: unknown): number {
  const reduceMotion = useReducedMotion();
  const last = Math.max(0, count - 1);
  const [played, setPlayed] = useState({ trigger, frame: 0 });

  useEffect(() => {
    if (reduceMotion) return;
    let frame = 0;
    const id = setInterval(() => {
      frame += 1;
      setPlayed({ trigger, frame });
      if (frame >= last) clearInterval(id);
    }, Motion.frameMs);
    return () => clearInterval(id);
  }, [trigger, last, reduceMotion]);

  if (reduceMotion) return last;
  // A new trigger restarts at frame 0 on this render, before the interval's first tick.
  return played.trigger === trigger ? Math.min(played.frame, last) : 0;
}
