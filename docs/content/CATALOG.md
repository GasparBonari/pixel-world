# Content catalog

The hand-authored files in [`src/data/catalog/`](../../src/data/catalog/) supply display names, parent links, and collectible facts for gameplay. The pure TypeScript [catalog loader](../../src/features/catalog/catalog.ts) exports `catalogEntries`, `getCatalogEntry(id)`, `getCatalogChildren(parentId)`, and `hasContent(countryId)`. Children are direct. To list a country's capital landmarks, look up the country's capital child and then the capital's children.

## Schema

Each JSON file contains an array of entries. Each entry has a globally unique, stable `id`, a display `name`, and a `kind`. Child entries also have a `parentId` that points to an existing entry.

| Kind | Parent | Additional fields |
| --- | --- | --- |
| `continent` | Root | Stored with continent-wide collectibles, currently in `europe.json` |
| `country` | Continent | Uses the existing country label's Natural Earth `ADM0_A3` ID |
| `capital` | Country | Scene ID, `longitude` and `latitude` from the scene registry |
| `landmark` | Capital | P5-01 landmark ID, real `longitude` and `latitude`, `coordinateSource`, optional `fact` |
| `wildlife` | Continent or country | `sources` for the species or habitat, optional `fact` |
| `landscape` | Continent or country | `longitude`, `latitude`, `sources`, optional `fact` |

Coordinates are decimal degrees. `coordinateSource` records a repo-relative `path` and the `key` in its `SITES` table. In `capital_sites.py`, the key is written as `capital-id.builder_name`. The coordinate tables and the Phase 4 research they refer to establish placement provenance. Fact sources are recorded alongside the player-facing text.

Europe's wildlife entries use each species' `kind` from [`scenery.json`](../../scripts/geography/scenery.json) and its existing source URL. Each species appears once, under Europe, even when the board has several placements. The Phase 5 slice has landmark facts for Lisbon, Paris and Athens. Landscapes currently have a type only.

## Add a country

1. Find the country ID and name in [`country-labels.json`](../../src/data/country-labels.json) and its scene in [`capitals.json`](../../src/data/capitals.json). Use the country ID as the filename, for example `PRT.json`. Use the continent's catalog ID for the country parent and the country ID for the capital parent.
2. Copy every landmark ID and name from the scene's [P5-01 export](../../src/data/capital-landmarks/). Give each landmark the capital ID as its parent. Use [`capital_sites.py`](../../scripts/art/capital_sites.py) or the capital's landmark module `SITES` table for coordinates and record the specific row in `coordinateSource`. Keep existing IDs when display names change so saved discoveries still resolve.
3. Add fact text and evidence when there is a reviewed content pack. Import the new JSON file in [`catalog.ts`](../../src/features/catalog/catalog.ts) and include it in `catalogEntries`. Run `node --test tests/catalog.test.mjs`. Update the slice coverage check when a new fact pack ships.

## Fact review and progress

- Write one or two plain sentences that total at most 220 characters. Write for curious players and favour details they can connect to what they see.
- A `fact` has `text`, a `status` of `checked` or `unchecked`, and one or two `sources` with a readable `label` and an HTTPS `url`. Prefer an official or heritage-body page and, where available, a second independent source.
- Open the cited pages and check every claim before marking the fact `checked`. Dates, counts, attributions, anecdotes, legends and superlatives all require explicit support. Keep drafts with evidence awaiting review as `unchecked` and omit `fact` when there is no draft.
- `hasContent` requires at least one checked collectible in the country or its capital. A country with `hasContent` false is ineligible for completion. Count the checked collectibles in its released pack for the denominator and use saved discoveries for the numerator. Continent-wide wildlife contributes to the continent's collection. Travel records are separate.

## Continent and territory policy

Initial coverage mirrors the 44 existing scenes in the Europe release. Their current `europe` links reflect that release grouping pending the owner decisions below. Natural Earth uses de facto boundaries for its default map data, and the app's IDs come from its admin-0 layer. The catalog's scene inventory and the eventual country totals serve different purposes. [Natural Earth Admin 0 countries](https://www.naturalearthdata.com/downloads/50m-cultural-vectors/50m-admin-0-countries-2/)

| Decision | Proposed rule and reasoning | Status |
| --- | --- | --- |
| Which Natural Earth entities count as countries? | Use Natural Earth IDs for map lookup. For the global country denominator, start with UN member and observer states and allow explicit owner-approved exceptions. Dependent territories can have their own map and content entries outside that total. This keeps the progress count independent of which polygons Natural Earth draws. | proposed, needs owner decision |
| Kosovo | Retain `KOS` and the Pristina scene as separately browsable content. Count `KOS` once as an explicit gameplay exception, reflecting its distinct map ID and capital scene. | proposed, needs owner decision |
| Northern Cyprus | Keep `CYN` as a separate map label where the existing data provides it. Propose one Cyprus country count under `CYP` and keep the existing Nicosia pack there. This keeps one pack for the current single scene. | proposed, needs owner decision |
| Turkey | Assign `TUR` to Asia for global progress, following the UN M49 Western Asia grouping. Keep Ankara accessible from its existing map location. A single progress parent prevents double counting. | proposed, needs owner decision |
| Russia | Assign `RUS` to Europe for global progress, following the UN M49 Eastern Europe grouping. A single progress parent keeps one country total across both parts of the map. | proposed, needs owner decision |

The proposed statistical groupings follow [UN M49](https://unstats.un.org/unsd/methodology/m49/#geo-regions).
