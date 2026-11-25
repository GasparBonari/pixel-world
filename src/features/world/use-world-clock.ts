import { useCallback, useEffect } from 'react';
import {
  useFrameCallback,
  useReducedMotion,
  useSharedValue,
  type SharedValue,
} from 'react-native-reanimated';
import { scheduleOnUI } from 'react-native-worklets';

import { constrainGlobe, OPENING_CAMERA, type GlobeCamera } from './globe-camera';
import { OPENING_INPUT, animationStep, animationTime, spinSpeed } from './motion';

const OPENING_EASE_SECONDS = 2 / 3;

/**
 * The living world's clock (motion.ts). `time` advances in whole animation frames, so shaders and
 * sprites that read it redraw only when it ticks. While the player leaves the planet alone, the
 * clock also turns it, starting as soon as the scene is `visible`. `touch` marks player input, which
 * stops the spin until they are idle again. With the system's reduce-motion setting on, the clock
 * never starts: time stays 0 and the scene is still.
 */
export function useWorldClock(camera: SharedValue<GlobeCamera>, visible: boolean) {
  const reduceMotion = useReducedMotion();
  const time = useSharedValue(0);
  const lastInput = useSharedValue(OPENING_INPUT);
  const openingEase = useSharedValue<{ start: number; longitudeOffset: number } | null>(null);
  // The frame callback re-registers whenever the scene re-renders (the spin itself refreshes the
  // country labels), which restarts its own timeSinceFirstFrame. Keep our own origin instead.
  const origin = useSharedValue(-1);
  const clock = useFrameCallback((frame) => {
    'worklet';
    if (origin.get() < 0) origin.set(frame.timestamp);
    const now = animationTime(frame.timestamp - origin.get());
    const previous = time.get();
    if (now === previous) return;
    time.set(now);
    const ease = openingEase.get();
    if (ease) {
      const progress = Math.min(1, (now - ease.start) / OPENING_EASE_SECONDS);
      const remaining = 1 - progress * progress * (3 - 2 * progress);
      camera.set(constrainGlobe({
        ...OPENING_CAMERA,
        longitude: OPENING_CAMERA.longitude + ease.longitudeOffset * remaining,
      }));
      if (progress === 1) openingEase.set(null);
      return;
    }
    const current = camera.get();
    const speed = spinSpeed(current.zoom, now - lastInput.get());
    if (speed > 0) {
      camera.set(
        constrainGlobe({ ...current, longitude: current.longitude - speed * animationStep(previous, now) })
      );
    }
  }, false);
  // Start once the planet is on screen, so a slow load doesn't turn it away from its opening view.
  useEffect(() => {
    clock.setActive(visible && !reduceMotion);
  }, [clock, visible, reduceMotion]);
  const touch = useCallback(() => {
    'worklet';
    lastInput.set(time.get());
    openingEase.set(null);
  }, [lastInput, openingEase, time]);

  const returnToOpening = useCallback(() => {
    scheduleOnUI(() => {
      'worklet';
      touch();
      if (reduceMotion) {
        camera.set(OPENING_CAMERA);
        return;
      }
      // Idle spin only changes longitude. Take the shortest path even after crossing the date line.
      const longitudeOffset = ((camera.get().longitude - OPENING_CAMERA.longitude + 540) % 360) - 180;
      openingEase.set({ start: time.get(), longitudeOffset });
    });
  }, [camera, openingEase, reduceMotion, time, touch]);

  return { time, touch, returnToOpening };
}
