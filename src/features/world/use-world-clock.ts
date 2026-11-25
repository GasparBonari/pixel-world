import { useCallback, useEffect } from 'react';
import {
  useFrameCallback,
  useReducedMotion,
  useSharedValue,
  type FrameInfo,
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
  const elapsed = useSharedValue(0);
  const tick = useCallback((frame: FrameInfo) => {
    'worklet';
    // The first frame after tab focus has no delta, so the camera never catches up on hidden time.
    const delta = frame.timeSincePreviousFrame ?? 0;
    elapsed.set(elapsed.get() + delta);
    const now = animationTime(elapsed.get());
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
  }, [camera, elapsed, lastInput, openingEase, time]);
  const clock = useFrameCallback(tick, false);
  const touch = useCallback(() => {
    'worklet';
    lastInput.set(time.get());
    openingEase.set(null);
  }, [lastInput, openingEase, time]);
  useEffect(() => {
    // Leaving World counts as input. Give the player the usual idle delay on return.
    if (!visible && clock.isActive) touch();
    clock.setActive(visible && !reduceMotion);
  }, [clock, visible, reduceMotion, touch]);

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
