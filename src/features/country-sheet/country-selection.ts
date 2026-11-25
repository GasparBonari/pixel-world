import scenes from '../../data/capitals.json';
import { getCatalogChildren, getCatalogEntry, getCheckedLandmarks } from '../catalog/catalog';
import { activeCapital, COUNTRY_ZOOM, type GlobeCamera } from '../world/globe-camera';

const sceneIds = new Set(scenes.map((scene) => scene.id));

export function getSelectableCountry(id: string) {
  const country = getCatalogEntry(id);
  if (country?.kind !== 'country') return;
  const continent = getCatalogEntry(country.parentId);
  const capital = getCatalogChildren(id).find((entry) => entry.kind === 'capital' && sceneIds.has(entry.id));
  if (continent?.kind === 'continent' && capital?.kind === 'capital') {
    return { country, continent, capital };
  }
}

export type SelectableCountry = NonNullable<ReturnType<typeof getSelectableCountry>>;

export function getCountryProgress(capitalId: string, found: { has(id: string): boolean }) {
  const landmarks = getCheckedLandmarks(capitalId);
  return { landmarks, value: landmarks.filter(({ id }) => found.has(id)).length, total: landmarks.length };
}

export function getWorldTier(camera: GlobeCamera) {
  if (activeCapital(camera)) return 'capital';
  return camera.zoom >= COUNTRY_ZOOM.in ? 'country' : 'overview';
}

export function selectCountryAtTap(currentId: string | null, camera: GlobeCamera, hitId: string | null) {
  if (getWorldTier(camera) !== 'country') return currentId;
  if (hitId === null) return null;
  return getSelectableCountry(hitId) ? hitId : currentId;
}
