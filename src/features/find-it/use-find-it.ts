import { useCallback, useRef, useState, useSyncExternalStore } from 'react';

import scenes from '../../data/capitals.json';
import { capitalScreenRect } from '../world/capitals';
import { activeCapital, CAPITAL_ZOOM, type GlobeCamera, type GlobeViewport } from '../world/globe-camera';
import {
  assistHint,
  classifyTap,
  getChallenge,
  nextPrompt,
  recordMiss,
  screenToScenePixel,
  showAssist,
  type LandmarkPrompt,
} from './challenge';
import { landmarkProgress } from './landmark-progress';

export type FoundLandmark = { prompt: LandmarkPrompt; date: Date };

function challengeCapitalId(camera: GlobeCamera) {
  return camera.zoom >= CAPITAL_ZOOM.full ? activeCapital(camera)?.id : undefined;
}

export function useFindIt(snapshot: GlobeCamera, viewport: GlobeViewport, iconScale: number) {
  const records = useSyncExternalStore(landmarkProgress.subscribe, landmarkProgress.getSnapshot);
  const [misses, setMisses] = useState<ReadonlyMap<string, number>>(() => new Map());
  const [recentFind, setRecentFind] = useState<FoundLandmark>();
  const cardOpen = useRef(false);
  const capitalId = challengeCapitalId(snapshot);
  const scene = scenes.find(({ id }) => id === capitalId);
  const challenge = capitalId && getChallenge(capitalId);
  const prompt = challenge ? nextPrompt(challenge.prompts, records) : undefined;

  const tapAt = useCallback((x: number, y: number, camera: GlobeCamera) => {
    if (!scene || !challenge || !prompt || cardOpen.current || challengeCapitalId(camera) !== scene.id) return;
    if (landmarkProgress.getSnapshot().has(prompt.landmark.id)) return;
    const pixel = screenToScenePixel({ x, y }, capitalScreenRect(scene, camera, viewport, iconScale), scene);
    if (!pixel) return;
    const result = classifyTap(pixel, prompt.shape, challenge.shapes);
    if (result === 'miss') setMisses((previous) => recordMiss(previous, prompt.landmark.id));
    if (result === 'hit') {
      const date = new Date();
      cardOpen.current = true;
      setRecentFind({ prompt, date });
      landmarkProgress.markFound(prompt.landmark.id, date);
    }
  }, [scene, challenge, prompt, viewport, iconScale]);

  function closeCard() {
    cardOpen.current = false;
    setRecentFind(undefined);
  }

  const visiblePrompt = recentFind?.prompt ?? prompt;
  const missCount = prompt && !recentFind ? misses.get(prompt.landmark.id) ?? 0 : 0;
  const assist = prompt && showAssist(missCount) ? prompt.shape : undefined;
  const banner = scene && challenge && challenge.prompts.length > 0 ? {
    title: visiblePrompt
      ? `Find ${visiblePrompt.landmark.name}`
      : `All ${challenge.prompts.length} landmarks found in ${scene.name}`,
    feedback: assist ? assistHint(assist, scene) : missCount > 0 ? 'Keep looking!' : undefined,
    misses: missCount,
    complete: !visiblePrompt,
  } : undefined;

  return { tapAt, banner, assist, capitalId, recentFind, closeCard };
}
