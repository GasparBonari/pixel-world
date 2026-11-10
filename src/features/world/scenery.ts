// Pure layout rules; the renderer projects geographic anchors before calling this.
export type SceneryFeature = {
  id: string;
  kind: string;
  continent: string;
  longitude: number;
  latitude: number;
  animal: boolean;
};
export type ProjectedScenery = {
  feature: SceneryFeature;
  x: number;
  y: number;
  depth: number;
};
export const MAX_SCENERY = 56;

export function sceneryOpacity(zoom: number) {
  'worklet';
  const value = Math.max(0, Math.min(1, (zoom - 0.9) / 0.5));
  return value * value * (3 - 2 * value);
}

export function sceneryScale(zoom: number, viewport: { width: number; height: number }) {
  'worklet';
  const unit = Math.max(1.1, Math.min(2.2, Math.min(viewport.width, viewport.height) / 270));
  return unit * Math.min(1.6, 2 ** (Math.max(0, zoom - 1.2) * 0.2));
}

export function selectScenery(
  items: ProjectedScenery[],
  viewport: { width: number; height: number },
  zoom: number
) {
  if (zoom <= 0.9) return [];
  const scale = sceneryScale(zoom, viewport);
  const candidates = items.filter(
    (p) =>
      p.depth > 0.3 &&
      p.x > -80 &&
      p.x < viewport.width + 80 &&
      p.y > -80 &&
      p.y < viewport.height + 80
  );
  // Wildlife first, then mountain silhouettes, then vegetation. Stable IDs settle ties.
  const priority = (p: ProjectedScenery) =>
    p.feature.animal
      ? 0
      : ['mountain', 'glacier', 'iceberg', 'volcano', 'red-rock', 'dune'].includes(p.feature.kind)
        ? 1
        : 2;
  candidates.sort(
    (a, b) =>
      priority(a) - priority(b) ||
      Math.hypot(a.x - viewport.width / 2, a.y - viewport.height / 2) -
        Math.hypot(b.x - viewport.width / 2, b.y - viewport.height / 2) ||
      a.feature.id.localeCompare(b.feature.id)
  );
  const selected: ProjectedScenery[] = [];
  for (const item of candidates) {
    const spacing = (item.feature.animal ? 22 : 13) * scale;
    if (
      selected.some(
        (other) =>
          Math.abs(item.x - other.x) <
            Math.max(spacing, other.feature.animal ? 24 * scale : spacing) &&
          Math.abs(item.y - other.y) <
            (item.feature.animal || other.feature.animal ? 21 : 13) * scale
      )
    )
      continue;
    selected.push(item);
    if (selected.length === MAX_SCENERY) break;
  }
  // Northern/back features draw before southern/front ones, like the reference scenery.
  return selected.sort((a, b) => a.y - b.y);
}
