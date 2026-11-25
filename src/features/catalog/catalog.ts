import albania from '../../data/catalog/ALB.json';
import andorra from '../../data/catalog/AND.json';
import austria from '../../data/catalog/AUT.json';
import belgium from '../../data/catalog/BEL.json';
import bulgaria from '../../data/catalog/BGR.json';
import bosniaAndHerzegovina from '../../data/catalog/BIH.json';
import belarus from '../../data/catalog/BLR.json';
import switzerland from '../../data/catalog/CHE.json';
import cyprus from '../../data/catalog/CYP.json';
import czechia from '../../data/catalog/CZE.json';
import germany from '../../data/catalog/DEU.json';
import denmark from '../../data/catalog/DNK.json';
import spain from '../../data/catalog/ESP.json';
import estonia from '../../data/catalog/EST.json';
import finland from '../../data/catalog/FIN.json';
import france from '../../data/catalog/FRA.json';
import unitedKingdom from '../../data/catalog/GBR.json';
import greece from '../../data/catalog/GRC.json';
import croatia from '../../data/catalog/HRV.json';
import hungary from '../../data/catalog/HUN.json';
import ireland from '../../data/catalog/IRL.json';
import iceland from '../../data/catalog/ISL.json';
import italy from '../../data/catalog/ITA.json';
import kosovo from '../../data/catalog/KOS.json';
import liechtenstein from '../../data/catalog/LIE.json';
import lithuania from '../../data/catalog/LTU.json';
import luxembourg from '../../data/catalog/LUX.json';
import latvia from '../../data/catalog/LVA.json';
import moldova from '../../data/catalog/MDA.json';
import northMacedonia from '../../data/catalog/MKD.json';
import malta from '../../data/catalog/MLT.json';
import montenegro from '../../data/catalog/MNE.json';
import netherlands from '../../data/catalog/NLD.json';
import norway from '../../data/catalog/NOR.json';
import poland from '../../data/catalog/POL.json';
import portugal from '../../data/catalog/PRT.json';
import romania from '../../data/catalog/ROU.json';
import russia from '../../data/catalog/RUS.json';
import serbia from '../../data/catalog/SRB.json';
import slovakia from '../../data/catalog/SVK.json';
import slovenia from '../../data/catalog/SVN.json';
import sweden from '../../data/catalog/SWE.json';
import turkey from '../../data/catalog/TUR.json';
import ukraine from '../../data/catalog/UKR.json';
import europe from '../../data/catalog/europe.json';

export type CatalogSource = Readonly<{ label: string; url: string }>;

export type CatalogFact = Readonly<{
  text: string;
  status: 'checked' | 'unchecked';
  sources: readonly [CatalogSource] | readonly [CatalogSource, CatalogSource];
}>;

type NamedEntry = Readonly<{ id: string; name: string }>;
type ChildEntry = NamedEntry & Readonly<{ parentId: string }>;
type Coordinates = Readonly<{ longitude: number; latitude: number }>;

export type ContinentEntry = NamedEntry & Readonly<{ kind: 'continent' }>;
export type CountryEntry = ChildEntry & Readonly<{ kind: 'country' }>;
export type CapitalEntry = ChildEntry & Coordinates & Readonly<{ kind: 'capital' }>;

export type LandmarkEntry = ChildEntry & Coordinates & Readonly<{
  kind: 'landmark';
  coordinateSource: Readonly<{ path: string; key: string }>;
  fact?: CatalogFact;
}>;
export type CheckedLandmark = LandmarkEntry & { readonly fact: CatalogFact & { readonly status: 'checked' } };

export type WildlifeEntry = ChildEntry & Readonly<{
  kind: 'wildlife';
  sources: readonly CatalogSource[];
  fact?: CatalogFact;
}>;

export type LandscapeEntry = ChildEntry & Coordinates & Readonly<{
  kind: 'landscape';
  sources: readonly CatalogSource[];
  fact?: CatalogFact;
}>;

export type CollectibleEntry = LandmarkEntry | WildlifeEntry | LandscapeEntry;
export type CatalogEntry = ContinentEntry | CountryEntry | CapitalEntry | CollectibleEntry;

// JSON imports widen literal strings to string. The catalog tests check the data at this boundary.
export const catalogEntries = [
  europe, albania, andorra, austria, belgium, bulgaria, bosniaAndHerzegovina, belarus, switzerland,
  cyprus, czechia, germany, denmark, spain, estonia, finland, france, unitedKingdom, greece, croatia,
  hungary, ireland, iceland, italy, kosovo, liechtenstein, lithuania, luxembourg, latvia, moldova,
  northMacedonia, malta, montenegro, netherlands, norway, poland, portugal, romania, russia, serbia,
  slovakia, slovenia, sweden, turkey, ukraine,
].flat() as readonly CatalogEntry[];

const entryById = new Map(catalogEntries.map((entry) => [entry.id, entry]));
const childrenByParent = new Map<string, CatalogEntry[]>();

for (const entry of catalogEntries) {
  if (entry.kind === 'continent') continue;
  const children = childrenByParent.get(entry.parentId);
  if (children) children.push(entry);
  else childrenByParent.set(entry.parentId, [entry]);
}

export function getCatalogEntry(id: string): CatalogEntry | undefined {
  return entryById.get(id);
}

export function getCatalogChildren(parentId: string): readonly CatalogEntry[] {
  return childrenByParent.get(parentId) ?? [];
}

export function getCheckedLandmarks(capitalId: string): readonly CheckedLandmark[] {
  return getCatalogChildren(capitalId).filter(
    (entry): entry is CheckedLandmark => entry.kind === 'landmark' && entry.fact?.status === 'checked'
  );
}

function hasCheckedFact(entry: CatalogEntry): boolean {
  return 'fact' in entry && entry.fact?.status === 'checked';
}

export function hasContent(countryId: string): boolean {
  return getCatalogEntry(countryId)?.kind === 'country'
    && getCatalogChildren(countryId).some((entry) =>
      entry.kind === 'capital'
        ? getCatalogChildren(entry.id).some(hasCheckedFact)
        : hasCheckedFact(entry)
    );
}
