# Pixel World

A mobile-first pixel-art travel exploration game built with Expo, React Native, TypeScript, and Expo Router.

The app opens on a full-screen pixel Earth and star field. Drag to spin; pinch or scroll to zoom. Earth now has coastal shallows and sandy edges, varied green/arid/icy surface color, ocean highlights, cloud layers/shadows, and a brighter pixel atmosphere. Space includes a cratered moon, a satellite with solar panels, varied stars, and faint background color. The opening view faces the Atlantic. The original land shapes and pixel rendering remain. Web also supports arrow keys, +/−, and Home reset.

Zooming in (1×–32×) turns the globe into the continent **game board** from the [art contract](./docs/art/ART_CONTRACT.md):

- The daytime ocean darkens into a night sea with stepped coast bands and sparkles.
- The land becomes raised, with lit coasts and green cliff edges.
- Countries take slightly different greens, with pale borders.
- Each continent's own plants, landforms and animals fade in as icons: oaks, bears, boars, deer and foxes in Europe; acacias, baobabs, lions, giraffes, rhinos, elephants and zebras in Africa; bamboo, pandas, tigers, camels, orangutans and snow leopards in Asia; and so on, with 29 species in all. Snow-capped mountains sit on real ranges.

It is the same sphere throughout, with no switch to a flat map.

Zooming further into **Portugal** brings in a few buildings at its real cities (a castle at Lisbon, church towns, houses), plus trees and boats. Zooming into **Lisbon** grows an isometric city scene out of its location: the castle on its hill, the Sé, the Rua Augusta arch over Praça do Comércio, pastel houses, a tram street, Belém Tower in the Tagus. You can pan around it. Try `/?lon=-8.3&lat=39.6&zoom=5.6` (Portugal) or `/?lon=-9.1365&lat=38.71&zoom=7` (Lisbon). Deep zoom is only allowed where such detail exists. Rebuild the city scenes with `.venv/bin/python scripts/art/build_capitals.py`. On web, a view can be opened directly, e.g. `/?lon=10&lat=47&zoom=2.6`.

Development still prioritizes **Earth → continent → country → capital visuals** before game controls and saved progress. Country detail (Malta), capital streets and buildings, the pin/name chip, the title header and the bottom card are upcoming work.

## Project documents

- [Development plan](./DEVELOPMENT_PLAN.md) — implementation tasks, phase status, and verification results.
- [Project vision](./PROJECT_VISION.md) — product concept and MVP scope.
- [Technical plan](./TECHNICAL_PLAN.md) — architecture, geographic data, asset licenses, and validation targets.
- [Art contract](./docs/art/ART_CONTRACT.md) — shared palette and pixel rules per scale, with Europe/Malta mockups (draft for review).

## Run locally

Install the locked dependencies:

```bash
npm ci
```

The postinstall step copies the installed Skia browser engine to `public/canvaskit.wasm`. This generated file is ignored by Git; run `npm run postinstall` if it is missing. Web loads this local file rather than a CDN.

Start Expo and use the terminal's QR code or platform shortcuts:

```bash
npm start
```

To start directly in a browser:

```bash
npm run web
```

For an Android emulator or iOS simulator, use `npm run android` or `npm run ios` with the appropriate platform tools installed. SDK 58 lists Skia as bundled in Expo Go; use a matching client for an initial phone check. Native rendering has not yet been exercised on a device here.

## Globe assets

The active game artwork is:

- `assets/world/globe.png`: a 4096×2048 equirectangular texture of land, country-border and lake masks.
- `assets/world/board.png`: 2048×1024. It holds each country's index, the distance from water to land in 3 km steps, and mountain-range areas, for the board's puzzle tones, borders, night-sea bands and relief tint.
- `assets/world/map-icons.png`: a sheet of original icons, placed by `src/data/map-icons.json`.

Clouds, terrain/forest-like colors, lighting, stars, moon, and satellite are decorative and render in Skia shaders. Source URLs/checksums and license terms are retained in [the pack manifest](./assets/world/manifest.json) and [license](./assets/world/LICENSE.txt).

The unused atlas tiles, Tiny Town/Tiny City sprites, and Expo demo images have been removed. The configured app icons and favicon remain. Candidate city/nature art sources are listed in the technical plan; import them when a feature uses them.

A development-only style study at `/style-study` (open `http://localhost:8081/style-study` on web) draws a small seaside street from a 188 KB subset of the CC0 [Ninja Adventure](https://pixel-boy.itch.io/ninja-adventure-asset-pack) pack, alongside Pixelify Sans text and a globe/pack palette comparison. Its files, source paths and SHA-256 hashes are in `assets/style-study/ninja-adventure/manifest.json`. It is input for the P2-06 art contract, not adopted art. The page defaults to a globe-palette version of the grass, foliage, and water tiles; regenerate it with `python3 scripts/art/recolor_style_study.py` (Pillow 12.1.1, as pinned for the geography script). Its colour table and output hashes are in `assets/style-study/globe-palette/manifest.json`.

App text on the globe (country labels, loading and error messages) uses Pixelify Sans from `@expo-google-fonts/pixelify-sans` (SIL Open Font License 1.1).

The globe and country display labels are already in the repository. Regeneration requires Python 3 and the pinned Pillow version:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r scripts/geography/requirements.txt
PATH="$PWD/.venv/bin:$PATH" npm run assets:prepare
```

The script verifies four pinned Natural Earth source hashes and rebuilds the globe and board textures, display labels, manifest, and license. Then rebuild the map icons (sheet and placements) with `.venv/bin/python scripts/art/build_map_icons.py`. Downloads stay in the ignored `.cache/geography/` directory and are excluded from the app. Completed outputs replace files atomically so Metro can remain running. Removed catalog/atlas/sprite images are not downloaded or recreated.

| Disk content | Current size |
| --- | --- |
| Globe texture | 222,387 bytes (about 217 KiB) |
| Board texture | 316,659 bytes (about 309 KiB) |
| Map icon sheet and placements | 1,594 bytes + about 26 KiB JSON |
| Generated browser engine | About 7.8 MiB |
| Skia development packages in `node_modules` | About 740 MiB, including prebuilt binaries for several platforms |

The development dependency footprint is separate from the artwork. A platform build uses its own binaries; these figures are not an installed-app size measurement. The renderer retains the decoded 32 MiB globe texture and 8 MiB board texture and reuses them at every zoom level, plus renderer/transient overhead. Phone measurements remain pending.

## Phase 3 design mockups

`scripts/art/phase3_mockups.py` renders the continent (Europe) and country (Malta) design targets in `docs/art/phase3/` from real data, following the [art contract](./docs/art/ART_CONTRACT.md). The app does not load them. The Malta view reads an OpenStreetMap extract, which needs pyosmium, so use the project virtual environment:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r scripts/art/requirements.txt
.venv/bin/python scripts/art/phase3_mockups.py
```

Map icons (landmarks and buildings, each continent's flora and landforms, and its animals) are generated by `scripts/art/sprites.py`; run it on its own to refresh the enlarged icon sheet at `docs/art/phase3/sprites.png`.

The script downloads pinned Natural Earth layers into `.cache/geography/` and the Geofabrik `malta-261108.osm.pbf` snapshot into `.cache/osm/`. Both folders are ignored by Git. It verifies checksums against `scripts/art/phase3-sources.lock.json` and the pinned OSM hash. Images derived from OSM show `© OpenStreetMap contributors`.

## Visual development order

1. Refine Earth’s silhouette, coast/ocean colors, clouds, lighting, atmosphere, and opening composition.
2. Add richer continent/country geography with continuous camera/detail transitions in the same art style.
3. Build recognizable, geographically anchored Valletta scenery; use Rome to prove the capital pipeline.
4. Add lightweight exploration UI, saved visits, quests, and the game HUD after the visual journey works.

The latest concept image guides the artwork and zoom experience. Its example statistics, quests, and rewards are not initial app data. See [the development plan](./DEVELOPMENT_PLAN.md) for visual acceptance criteria and deferred features.

## Project checks

```bash
npm run lint
npm run typecheck
npm test
npx expo-doctor
```

Typecheck loads Expo's built-in global declarations directly through `tsconfig.json`, so it also works before the first dev-server run generates the ignored `expo-env.d.ts` file.

To verify JavaScript and asset exports for all three platforms:

```bash
npx expo export --platform all --output-dir dist --max-workers 2
```

Exports validate bundling; they do not build or launch native app binaries. Web output currently uses Expo's server rendering configuration.

## Platform verification

Seven focused logic tests cover projection, camera limits, cache utilities, inverse globe coordinates, and focal zoom. Browser verification checks the clean full-screen scene, gestures, responsive layouts, shader compilation, and reuse of the same texture. The removed Phase 3 prototype’s visit/navigation checks are no longer part of the active app.

Native device/emulator launches and Safari have not been verified in this workspace. Native navigation, safe areas, status bar appearance, and splash behavior still need a device check. App config changes apply to newly built native apps; a browser check does not validate native splash appearance.

## Development conventions

Keep route files in `src/app/` and shared UI outside that directory. Use the shared theme tokens for colors and spacing. Read the installed SDK's documentation before changing Expo or React Native APIs, install project dependencies with `npx expo install`, and run lint/typecheck before completing a task. See [AGENTS.md](./AGENTS.md) for the full repository instructions.
