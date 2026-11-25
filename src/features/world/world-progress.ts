import { catalogEntries, getCheckedCountryCollectibles, hasContent } from '../catalog/catalog';

const countryPacks = catalogEntries
  .filter((entry) => entry.kind === 'country' && hasContent(entry.id))
  .map(({ id }) => getCheckedCountryCollectibles(id));

export function getWorldProgress(found: { has(id: string): boolean }) {
  return {
    value: countryPacks.filter((pack) => pack.every(({ id }) => found.has(id))).length,
    total: countryPacks.length,
  };
}
