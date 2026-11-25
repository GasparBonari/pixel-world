import { getCheckedLandmarks, type CheckedLandmark } from '../catalog/catalog';

import athens from '../../data/capital-landmarks/athens.json';
import lisbon from '../../data/capital-landmarks/lisbon.json';
import paris from '../../data/capital-landmarks/paris.json';

type Point = { x: number; y: number };
type Dimensions = { width: number; height: number };
export type LandmarkBounds = readonly [x: number, y: number, width: number, height: number];
type LandmarkShape = { id: string; bbox: LandmarkBounds; mask: string };

export type LandmarkPrompt = { landmark: CheckedLandmark; shape: LandmarkShape };

const ASSIST_AFTER = 3;
const PACKS = new Map(Object.entries({ athens, lisbon, paris }).map(([id, { landmarks }]) => {
  // P5-01 validates the tuple length and exports masks in stable ID order.
  const shapes: LandmarkShape[] = landmarks.map(({ id, bbox: [x, y, width, height], mask }) => ({
    id, bbox: [x, y, width, height], mask,
  }));
  const checked = new Map(getCheckedLandmarks(id).map((landmark) => [landmark.id, landmark]));
  const prompts = shapes.flatMap((shape) => {
    const landmark = checked.get(shape.id);
    return landmark ? [{ landmark, shape }] : [];
  });
  if (id === 'lisbon') {
    const first = prompts.findIndex(({ landmark }) => landmark.id === 'belem-tower');
    if (first > 0) prompts.unshift(...prompts.splice(first, 1));
  }
  return [id, { shapes, prompts }] as const;
}));

export function getChallenge(capitalId: string) {
  return PACKS.get(capitalId);
}

export function nextPrompt(prompts: readonly LandmarkPrompt[], found: { has(id: string): boolean }) {
  return prompts.find(({ landmark }) => !found.has(landmark.id));
}

/** Convert a map-local screen position through the actual, snapped render rectangle. */
export function screenToScenePixel(point: Point, rect: Point & Dimensions, scene: Dimensions): Point | undefined {
  if (point.x < rect.x || point.x >= rect.x + rect.width || point.y < rect.y || point.y >= rect.y + rect.height) return;
  const x = Math.floor(((point.x - rect.x) / rect.width) * scene.width);
  const y = Math.floor(((point.y - rect.y) / rect.height) * scene.height);
  if (x >= 0 && x < scene.width && y >= 0 && y < scene.height) return { x, y };
}

const BASE64 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';

export function maskContains({ bbox: [left, top, width, height], mask }: LandmarkShape, point: Point): boolean {
  const x = point.x - left;
  const y = point.y - top;
  if (!(x >= 0 && x < width && y >= 0 && y < height)) return false;

  const bit = y * width + x;
  // A packed byte starts at bit 0, 2 or 4 of a Base64 character and spans two characters.
  const byteStart = (bit >> 3) * 8;
  const character = Math.floor(byteStart / 6);
  const pair = (BASE64.indexOf(mask[character]) << 6) | BASE64.indexOf(mask[character + 1]);
  const byte = pair >> (4 - byteStart % 6);
  return Boolean(byte & (1 << (bit & 7)));
}

export function classifyTap(point: Point, target: LandmarkShape, shapes: readonly LandmarkShape[]) {
  if (maskContains(target, point)) return 'hit';
  if (shapes.some((shape) => shape.id !== target.id && maskContains(shape, point))) return 'other';
  return 'miss';
}

export function recordMiss(misses: ReadonlyMap<string, number>, id: string): ReadonlyMap<string, number> {
  return new Map(misses).set(id, (misses.get(id) ?? 0) + 1);
}

export function showAssist(misses: number) {
  return misses >= ASSIST_AFTER;
}

export function assistHint({ id, bbox: [x, y, width, height] }: LandmarkShape, scene: Dimensions) {
  if (id === 'belem-tower') return 'Look near the river.';
  const col = (x + width / 2) / scene.width;
  const row = (y + height / 2) / scene.height;
  const horizontal = col < 1 / 3 ? 'left' : col > 2 / 3 ? 'right' : '';
  const vertical = row < 1 / 3 ? 'top' : row > 2 / 3 ? 'bottom' : '';
  const direction = [vertical, horizontal].filter(Boolean).join(' ') || 'middle';
  return `Look toward the ${direction} of the scene.`;
}
