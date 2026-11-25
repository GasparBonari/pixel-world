# Earthia — Technical Plan

Status: architecture reference. Phase 1 and the Phase 2 globe foundation are implemented; the Phase 3 hierarchy/manual-visit prototype has been removed and development now prioritizes the visual zoom journey; unused prototype images have been removed. Phase 2 validation remains open for native-device benchmarks and detailed coastal/urban styling.

Research date: 9 November 2026. Performance budgets and estimates below are proposals, not benchmark results.

Current rendering refinement: the globe remains active through country zoom, using the original texture, palette, pixel grid, and lighting. The earlier separately styled atlas handoff is removed. Atlas/cache experiments below remain architectural history; unused atlas images, sprite packs, their loader/index, and unused cached sources have been deleted. Future destination detail must extend the globe's art direction.

## Recommendation

Keep Expo, React Native, TypeScript, and Expo Router. Prototype **React Native Skia with pre-generated pixel-art raster tiles**, a small geographic selection layer, and local progress storage. Share the geographic model and most drawing logic across platforms; isolate browser initialization and input differences.

This is a deliberately bounded renderer: a global overview, two detailed destination packs, pan/zoom, selection, and markers. It is not a new general-purpose GIS engine. It is the preferred experiment because visual control is central to the product, Skia is listed in Expo SDK 58, and the first demonstration can avoid a live map service. Compatibility and performance still need testing. [Expo SDK 58 Skia reference](https://docs.expo.dev/versions/v58.0.0/sdk/skia/)

**Decision gate:** time-box the initial camera, tile, and pixel-style experiments to approximately 3–5 working days. If they cannot meet the interaction budgets, evaluate MapLibre Native plus MapLibre GL JS against the same generated tiles. Do not build both production renderers in advance.

The supplied visual reference makes the spinning pixel-art globe a core requirement. Use the existing Skia stack for the sphere and preserve its pixel-art style through country zoom; keep high-detail city coverage bounded to destination packs.

The [development plan](./DEVELOPMENT_PLAN.md) contains the implementation backlog and [current Phase 2 evidence](./DEVELOPMENT_PLAN.md#phase-2-verification). Skia 2.14.0 is installed; the active renderer uses local browser CanvasKit and one 4096×2048 globe texture. Unused atlas tiles and sprite imports have been removed. Device measurements remain pending.

## Repository assessment

This assessment describes the Expo starter at commit `c80e104`, before Phase 1 implementation. Current results are recorded in the [development plan](./DEVELOPMENT_PLAN.md#phase-1-verification).

| Area | Observed state | Implication |
| --- | --- | --- |
| Core versions | `expo ~58.0.23`, React `19.3.0`, React Native `0.88.1`, TypeScript `~6.0.3` | Use SDK 58 documentation and verify third-party compatibility against these versions |
| Package manager | `package-lock.json`; no `bun.lock` | Use npm/npx for this repository |
| Routing | `src/app/_layout.tsx`, `index.tsx`, `explore.tsx` | Existing routes are starter screens; keep all new non-route logic outside `src/app/` |
| Navigation | `AppTabs` has native and `.web.tsx` implementations | A useful precedent for isolating platform differences |
| Animation/input | Gesture Handler `~3.3.0`, Reanimated `4.7.1`, Worklets `0.13.0` already declared | Reuse these before adding another input or animation system |
| Styling | Shared theme constants, themed components, web CSS | Extend existing conventions with a game palette and accessible UI |
| Map/game/data | No renderer, geographic dataset, challenge catalog, or progress store | There is no existing game implementation to preserve |
| Assets | Expo/template artwork only | Candidate third-party art has not been downloaded or adopted |
| Native configuration | No root `ios/` or `android/`; configuration in `app.json` | Retain Continuous Native Generation and config plugins |
| Web | `web.output` is `server`; React Native Web installed | Canvas/WASM must initialize on the client; rendering support does not imply server-side canvas support |
| Tests/tooling | No project test suite or ESLint configuration/dependencies | Establish a clean baseline before implementation |

Read the [SDK 58 reference](https://docs.expo.dev/versions/v58.0.0/) and [Expo's documentation index and corrections](https://docs.expo.dev/llms.txt) during this review. Follow versioned pages for later implementation rather than copying remembered API examples.

### Baseline checks

Historical results, before Phase 1 implementation:

- `npx --no-install expo lint`: exited 1 because ESLint is not configured. Declined its dependency/configuration bootstrap to keep this task limited to documentation.
- `npx --no-install tsc --noEmit`: exited 2 with three existing diagnostics: missing CSS-module declarations in `src/components/animated-icon.web.tsx:5`, incompatible forwarded `ref` typing in `src/components/app-tabs.web.tsx:38`, and a missing side-effect CSS import declaration in `src/constants/theme.ts:6`.

Phase 1 resolved these issues through Expo's global type declarations, corrected web ref typing, and the Expo lint configuration. It also fixed the web theme hook's hydration-related lint error. Lint/typecheck now pass; see the [current verification record](./DEVELOPMENT_PLAN.md#phase-1-verification) for runtime and export coverage.

## Rendering architecture comparison

The comparison below records the original engineering expectations. Skia now has browser prototype measurements in the development plan; native performance and the MapLibre alternative have not been benchmarked here.

| Concern | A — MapLibre Native + GL JS | B — Skia + generated tiles (recommended experiment) |
| --- | --- | --- |
| Mobile renderer | `@maplibre/maplibre-react-native` wraps MapLibre Native for iOS/Android | React Native Skia draws the game map on a canvas |
| Web renderer | Separate `maplibre-gl` integration; do not assume the native wrapper supplies a web map | CanvasKit/WASM browser backend; requires explicit loading |
| Camera and large maps | Established map camera, tile scheduling, geographic picking, label placement | We implement a small camera, tile selection, hit testing, and bounded label placement |
| Pixel-art fidelity | Vector colors, patterns, and icons are easy; ordinary vector rendering does not guarantee stepped pixel geometry. Pre-rendered pixel rasters give stronger control | Direct control over sampling, composition, state overlays, and low-resolution effects; fractional scale still needs visual testing |
| Globe | GL JS supports globe; Native globe is an open feature request. A shared globe would need another presentation layer | A custom 2D globe can use the same drawing stack; projection, picking, and transition are our responsibility |
| Performance | Native tile handling is a strong default for large geographic scenes; extra native dependency and separate web behavior | Small cached raster scenes should be tractable; image decode, GPU memory, and custom scheduling are the main risks |
| Dynamic exploration | Country features can be styled dynamically | Keep country geometry/masks separate from static terrain; no raster rebuild per visit |
| Offline | Platform-specific source/cache behavior must be validated; native offline support does not imply identical browser storage | Bundled packs support a native offline MVP; browser offline reload and downloadable packs require additional work |
| Solo development cost | Less map-engine work, more style/platform integration; requires native builds | Less integration surface for a bounded game map, more camera/data-pipeline ownership |
| Best use | Many detailed regions, conventional map behavior, or a failed custom-camera experiment | A visually distinctive, limited destination prototype with a strict data budget |

MapLibre's [getting started guide](https://maplibre.org/maplibre-react-native/docs/setup/getting-started/) identifies the wrapper's native platforms and New Architecture requirement from v11. Its [Expo setup](https://maplibre.org/maplibre-react-native/docs/setup/expo/) requires a config plugin and rebuilt native app; it does not run in Expo Go. The [globe roadmap](https://maplibre.org/roadmap/maplibre-gl-js/globe-view/) and [Native globe issue](https://github.com/maplibre/maplibre-native/issues/3161) establish the platform gap. Recheck these before implementation.

Skia's [v2 installation guide](https://wcandillon.github.io/react-native-skia/v2/docs/getting-started/installation/) describes its React/RN and animation dependencies; the repository meets the documented minimums, which is not proof of compatibility with every current package combination. The [web guide](https://wcandillon.github.io/react-native-skia/v2/docs/getting-started/web/) documents asynchronous CanvasKit loading and Router integration. The [SDK 58 reference](https://docs.expo.dev/versions/v58.0.0/sdk/skia/) currently recommends Skia 2.14.0. Use documentation for the Expo-resolved major, not an arbitrary latest release.

### Other approaches considered

- **Phaser in a web surface:** strong sprite, camera, and tilemap tooling, with TypeScript support. Phaser targets browsers and WebGL/Canvas; it is not a native React Native renderer. Native delivery needs an embedded browser/DOM surface or another wrapper. That introduces another lifecycle/input boundary and does not supply GIS or a globe. Prefer it if the product pivots to a browser-first game. [Phaser platform description](https://docs.phaser.io/phaser/getting-started/what-is-phaser)
- **React Native SVG:** suitable for a small world-map visual experiment, country polygons, or icons; not the preferred engine for a dense tiled world. A large animated element tree and art sampling need separate measurement. Expo lists Android/iOS/web support, but does not promise game-scene performance. [SDK 58 SVG reference](https://docs.expo.dev/versions/v58.0.0/sdk/svg/)

### Platform commitments and limits

| Capability | iOS/Android | Web |
| --- | --- | --- |
| Proposed Skia map | Documented platform support; verify on actual phones | Documented through CanvasKit; test Safari and Chromium separately |
| Expo Go trial | SDK 58 lists Skia as bundled; match the Expo-resolved version and client | Not applicable; browser build |
| Native build | Needed for non-bundled native modules, native configuration changes, and standalone validation | No native build; still requires browser asset/WASM setup |
| Gesture execution | Skia integrates with Reanimated on the native UI thread | Do not assume the native UI-thread model; test browser main-thread responsiveness |
| Globe | Custom experiment, not a built-in geographic capability | Same experiment; shaders and sampling require cross-browser validation |
| Accessible controls | React Native controls around the canvas | React Native Web controls and keyboard/pointer alternatives |

Skia documents [Reanimated integration](https://wcandillon.github.io/react-native-skia/v2/docs/animations/animations/) and [image sampling](https://wcandillon.github.io/react-native-skia/v2/docs/images/). Put challenge panels, buttons, and a visible-place list in normal accessible UI; a canvas alone does not provide an accessible interface.

## Globe-to-city design

Use one authoritative geographic position in WGS84 longitude/latitude, independent of projection and drawing coordinates. Distinguish continuous camera scale from discrete data/detail levels.

| View | Proposed data/detail | Behavior |
| --- | --- | --- |
| Planet | A low-resolution equirectangular Earth texture generated from Natural Earth | Required 2D sphere projection; drag to spin, zoom toward country borders/names and the atlas |
| Atlas, currently z0–5 | Global pixel terrain, borders, simplified country geometry, ranked place labels | Pan/zoom globally; show state and select countries |
| Region, roughly z5–9 | More detailed Natural Earth geometry and ranked city points | Stream the chosen regional subset; do not imply street-level accuracy |
| City, roughly z10–15 | OSM-derived data for bundled destination bounds | Roads, water, land-use patterns, symbolic buildings, and curated POIs |
| Challenge, roughly z14–16 | Curated markers and text | Select a place or use an overlapping-marker list; open a normal UI panel |

These are initial thresholds to tune, not source coverage guarantees. Natural Earth's `1:10m`, `1:50m`, and `1:110m` mean map scales of 1:10 million, 1:50 million, and 1:110 million, not metre-level detail. Its [populated places](https://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-populated-places/) support ranked overview labels, not every settlement.

### Globe presentation

Implemented: sample a 4096×2048 equirectangular land/border/lake mask through an orthographic Skia shader. Screen-space quantization creates stepped pixels, with decorative terrain colors, clouds, a shaded rim, and stars based on the reference. The scene fills the viewport without surrounding app chrome. Drag rotates longitude/latitude; pinch, wheel, and keyboard zoom toward the atlas. Clouds fade before borders and country labels appear. The geographic model is shared with the atlas.

**Continent board (Phase 3, implemented).** The same shader blends into the continent "game board" between zoom 1.5 and 2.5, as set out in `docs/art/ART_CONTRACT.md`. It has no separate atlas renderer and no projection switch.

- A second texture, `board.png` (2048×1024, 8 MiB decoded), holds three things:
  - each country's index, for puzzle tones and borders;
  - a latitude-corrected distance from water to land, for the night-sea bands, converted to screen pixels at each zoom;
  - mountain-range areas.
- The shader samples that texture twice: nearest-neighbour for the indices, filtered for the distance.
- Raised coasts and borders compare a pixel with its neighbouring screen pixels, after projecting them back onto the sphere.
- Icons are one Skia `Atlas`. Their RSXform buffer is recomputed on the UI thread whenever the camera changes, and icons on the far side are parked off-screen.
- Country-scale detail (Malta) will add a small regional texture sampled the same way.

The globe uses Skia [runtime shaders](https://wcandillon.github.io/react-native-skia/v2/docs/shaders/overview/). Browser rendering and repeated transitions are verified; native shader precision, performance, and Safari still need checks. Terrain colors and cloud patterns are artwork, not satellite weather, vegetation, or elevation data.

The current camera stays on the sphere at zoom 0–4 (1×–16×). Zoom changes its radius and geographic focal point without replacing the texture or shader. Country borders/names appear within the same artwork; clouds fade gradually. Home resets the view. Tests cover inverse projection, focal-point zoom beyond the old handoff threshold, and zoom limits. The removed Phase 3 prototype no longer supplies selection, capital markers, panels, or visits. The active zoom remains an overview. Richer continent/country geography and a continuous transition to detailed capital scenery must be built before exploration UI and saved records.

The globe can show the poles. The flat map clamps latitude to Web Mercator's approximately ±85.0511° limit; polar close-ups are deferred. Wrap longitude at the antimeridian. Verify Fiji, Alaska, and a near-polar target as well as the initial destinations.

### Camera and detail changes

- Pinch keeps the geographic point under the gesture focal point stable; drag pans. The full-screen view uses gestures without visible buttons; web adds wheel/pointer and keyboard zoom/reset input.
- Drive camera transforms with shared animation values; avoid updating a large React tree every frame. Notify application state only when selection, coverage, or detail bands change.
- Load visible tiles and a small buffer. Keep a coarser parent tile while a child decodes; do not show a blank canvas during a detail change.
- Keep label/marker sizes usable in screen coordinates. Use a simple ranked screen-grid collision rule for the bounded MVP.
- Outside a city pack, retain the lower-detail overview and cap useful zoom with a coverage message. Higher zoom must not fabricate streets or quests.

## Free data and art

### Geographic data

| Source | Proposed use | License and implementation consequence |
| --- | --- | --- |
| [Natural Earth terms](https://www.naturalearthdata.com/about/terms-of-use/) | Global land, coastline, country boundaries, broad geographic features | Public domain; attribution optional, but retain source/version provenance |
| [Natural Earth countries](https://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-admin-0-countries/) | Country selection and display | Generalized boundaries; de facto boundaries by default, with disputed/POV considerations. Curate identifiers and preserve boundary provenance |
| [Natural Earth populated places](https://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-populated-places/) | Ranked country/region/city labels | Same public-domain dataset family; generalized point locations, not a complete local search service |
| [OpenStreetMap](https://www.openstreetmap.org/copyright) via [Geofabrik extracts](https://www.geofabrik.de/data/download.html) | City roads, water, parks, building/land-use footprints, candidate POIs | ODbL 1.0 data; attribution and applicable database-sharing obligations. Process snapshots offline rather than relying on a runtime API |
| [Geofabrik Malta extract](https://download.geofabrik.de/europe/malta.html) | Small initial source for Valletta and Malta | Free OSM extract under the underlying OSM license; source input size is not the final map-pack size |

Natural Earth omits or simplifies small features at broad scales. Add explicit small-country selection anchors and retain a finer geographic subset where appropriate. Do not equate its polygon count with a universally agreed number of countries. Use an explicit product policy for territories and disputed borders.

### Pixel-art shortlist

| Pack | License/source evidence | Fit and decision |
| --- | --- | --- |
| [Kenney Tiny Town](https://kenney.nl/assets/tiny-town) | Creator lists 16×16 tiles and CC0 | Preferred terrain/settlement starting family; use symbolic buildings without claiming exact architecture |
| [Kenney Tiny City](https://kenney.nl/assets/tiny-city) | Creator archive includes CC0 terms and 16×16 tiles | Candidate urban roads, buildings, vehicles, and props; import only when used |
| [Kenney Pixel UI Pack](https://kenney.nl/assets/pixel-ui-pack) | Creator lists CC0; also [published by Kenney on OpenGameArt](https://opengameart.org/content/pixel-ui-pack-750-assets) | Candidate panels, buttons, and cursors; adapt palette and scale after a style check |
| [Kenney Tiny Battle](https://kenney.nl/assets/tiny-battle) | Creator lists CC0; [Kenney's OpenGameArt listing](https://opengameart.org/content/tiny-battle) also identifies CC0 | Optional reference/props; combat assets are unnecessary for this MVP |
| [Ninja Adventure on itch.io](https://pixel-boy.itch.io/ninja-adventure-asset-pack) | Pack page lists "Creative Commons Zero v1.0 Universal"; the archive includes the CC0 1.0 legal text | Style-study candidate (P2-06): warm 16×16 terrain, water, Mediterranean-looking roofs, 90+ characters, and UI frames. Buildings are one-storey and Japanese-themed in places; needs palette remapping to the globe. Its bundled font is not used for text. Study subset and hashes in `assets/style-study/ninja-adventure/manifest.json` |
| [0x72 DungeonTileset II on itch.io](https://0x72.itch.io/dungeontileset-ii) | Creator lists 16×16 and CC0, with optional payment | Free alternative art direction. Do not mix its darker dungeon style into the selected overworld without deliberate reworking |

Adopt one terrain family initially. The shortlist is not a commitment to combine all packs. CC0 removes attribution requirements for these assets; voluntary creator credits remain useful. Tiny Town and Tiny City were evaluated and then removed because the app did not use their artwork. The shortlist remains a source reference. The only third-party sprites currently imported are the Ninja Adventure subset used by the `/style-study` route, which is not yet adopted art. Record source hashes, versions, and licenses when future destination features actually adopt a pack.

Landmarks should use a handful of original sprites or carefully reviewed compatible additions. Neither generic town tiles nor OSM building outlines automatically produce recognizable real-world landmark art. Pixelify Sans (SIL Open Font License 1.1, installed as `@expo-google-fonts/pixelify-sans`) is the candidate pixel font. The root layout loads it before hiding the splash screen; it sets the globe's country labels, the map loading/error text, and the style study. Check its readability on a phone.

### Attribution and service boundaries

OSM data licensing, generated artwork licensing, and hosted service usage are separate concerns:

- Show a legible `© OpenStreetMap contributors` link to the copyright/license page when displaying OSM-derived detail; include source details in credits and pack metadata. This is a conservative presentation choice consistent with the [OSMF attribution guidelines](https://osmfoundation.org/wiki/Licence/Attribution_Guidelines).
- A rendered map image and an OSM-derived database are different artifacts. ODbL sections 4.3–4.6 cover attribution, share-alike, and access to derivative databases, including public produced works made from them. Retain the derived geographic data or reproducible alteration material needed for distribution. Original app code and quest writing are not automatically placed under ODbL. Keep their provenance separate; separation alone does not eliminate obligations for a combined derivative database. [ODbL legal text](https://opendatacommons.org/licenses/odbl/1-0/)
- Do not build the prototype by downloading or recoloring the public OSM tile service. Its [tile policy](https://operations.osmfoundation.org/policies/tiles/) prohibits bulk/offline prefetch and provides no service guarantee. Obtain raw extracts and generate our own tiles.
- Do not assume a public geocoder, Overpass endpoint, or MapLibre demo server is a free production backend. The MVP needs none of them at runtime.

## Generate the geography instead of drawing it

Use a repeatable **offline build pipeline**. The current Python/Pillow generator builds the globe and display labels from pinned Natural Earth sources. Keep raw downloads out of the app bundle. The following broader tooling remains proposed for capital detail:

1. **Acquire pinned inputs.** Download selected Natural Earth layers and regional OSM extracts. Record URL, snapshot date, checksum, license, and feature selection rules.
2. **Normalize and simplify.** Produce WGS84 metadata and a stable country/territory registry. Use topology-aware tools such as [Mapshaper](https://github.com/mbloch/mapshaper) for broad boundaries. Preserve shared edges, polygon holes, islands, and antimeridian splits.
3. **Select detail by scale.** Dissolve land for the planet; retain countries for the atlas; extract water, major roads, land use, and a limited building layer for cities. A low-detail overview is not a substitute for city inputs.
4. **Project onto a fixed grid.** Use Web Mercator XYZ tiles for flat maps, and a separate equirectangular texture for the globe. Rasterize at exact geographic extents with [GDAL](https://gdal.org/en/stable/programs/gdal_rasterize.html), then apply a small deterministic palette/sprite-composition step. Work on a coarse semantic grid, not a full-resolution conventional basemap.
5. **Apply art rules.** Map water, land, vegetation, urban areas, and road classes to a shared palette and tile patterns. Seed decorative variations from world coordinates so regeneration and panning do not move them. At city scale, simplified footprints or terrain patterns convey density; a few POIs receive deliberate landmark sprites.
6. **Separate appearance from interaction.** Export static terrain, country shapes or index masks, city/POI coordinates, and labels as separate layers. Progress changes a state overlay; it never requires rebuilding the terrain pyramid.
7. **Package and validate.** Emit bounded tile packs and a manifest with coverage, zoom limits, source/license metadata, and hashes. Generate a static asset index for Metro's literal asset references instead of constructing dynamic `require()` paths at runtime.

Keep pixels aligned to the world grid, not the current viewport. Generate with a border buffer and crop tiles consistently so coastlines, roads, and patterns join at tile edges. Preserve a logical selection layer when visual snapping removes a tiny island. Art transformations simplify appearance, not the authoritative challenge coordinates.

Use small reproducible CLI steps, with a short raster-composition script if necessary; do not create a procedural-world framework. Manually review difficult coastlines, narrow roads, and a few landmark placements. The second destination should reveal reusable rules and necessary exceptions.

### Coverage and storage bounds

Proposed starting limits:

- Removed atlas experiment: a z0–5 pyramid used 1,365 terrain tiles (2,002,062 PNG bytes) plus an earlier 222,387-byte globe. It is no longer generated or loaded. The restored active 222,387-byte globe uses 1:10m land/lakes and 1:50m borders, with display-label metadata. The Phase 3 selection/capital catalog has been removed.
- Regional z5–9 detail generated only for the two destination regions. Generate city z10–15 detail only inside small city bounding boxes; do not build a whole country's high-zoom pyramid by default.
- Initial geographic/art pack target: **under 20 MiB compressed**, excluding app runtime libraries. Measure before adopting this as a release limit; reduce bounds/detail if exceeded.
- Retain a single **32 MiB** decoded globe texture and a **16 MiB** byte-budgeted atlas LRU, approximately **48 MiB** combined retained capacity plus renderer/transient overhead. This revises the original 32 MiB total-image proposal to support the requested globe detail. Include GPU copies, parent tiles, and temporary decodes in device measurements; reduce texture dimensions if physical-device results require it.
- Bound queued decoding and release obsolete images after fast camera moves. Do not decode the entire world pyramid at launch.

The suggested 256-pixel tile encoding and coarser source art grid are experiment parameters. Nearest sampling preserves hard edges but can shimmer during fractional zoom; compare a few source grids on devices before freezing the format.

Initially bundle the two detail packs and low-detail Earth assets. Additional countries reuse generation rules and a geographic manifest; worldwide high-detail tiles are not precomputed or shipped. Future remote packs need explicit bandwidth, caching, and update budgets.

On native, installed bundled assets can support the sample route without a network connection. On web, serve the app, CanvasKit, and map assets from the same deployment and make no external map requests. Ordinary browser caching does not guarantee offline reload; a service worker/cache strategy and offline-update tests would be a separate enhancement. Do not claim browser offline support from bundling alone.

PMTiles is a possible later archive/distribution format, not an MVP dependency. Its documented MapLibre integration is browser-based using `addProtocol`; that is not evidence of identical React Native support. Use ordinary bundled files first. [PMTiles concepts](https://docs.protomaps.com/) and [MapLibre GL integration](https://docs.protomaps.com/pmtiles/maplibre)

## Application boundaries

Proposed modules, created only after review and the initial experiments:

```text
src/app/                         Expo Router screens/layouts only
  _layout.tsx                    Navigation, theme, app initialization
  index.tsx                      World screen composition
  explore.tsx                    Destination/progress list, repurposed if useful
src/features/world/
  WorldView.tsx                  Canvas composition and accessible controls
  WorldView.web.tsx              Only if browser initialization requires it
  camera.ts                     Geographic camera and detail thresholds
  projection.ts                 Forward/inverse projection and wrapping
  tiles.ts                      Visibility calculation and bounded image cache
  selection.ts                  Country/marker picking
src/features/exploration/
  model.ts                      Visits and derived country state
  storage.ts                    Versioned local progress persistence
src/features/challenges/
  model.ts                      Challenge definitions and completion rules
  ChallengePanel.tsx            Accessible normal React Native UI
src/data/                        Generated metadata and authored content catalogs
src/constants/                  Existing theme plus shared game palette
assets/world/                   Generated geographic/art packs and licenses
scripts/geography/              Build-time transformations and validation
```

Start with functions and small components; add folders only when useful. Do not build a general renderer interface, entity-component system, backend repository layer, or global state framework for the first slice. If MapLibre wins the experiment, replace the rendering boundary while retaining geographic data, challenge definitions, and progress rules.

The data flow is:

```text
Pinned geographic data + art rules -> generated map packs -> canvas
Authored challenges + POI coordinates --------------------> markers/panels
Player actions -> exploration model -> local storage -----> state overlays
```

Keep the map mounted while opening a country or challenge panel. Selecting a country need not navigate to a new screen and lose camera state. Any actual screen navigation remains in [Expo Router](https://docs.expo.dev/router/introduction/).

### Minimal data contracts

| Record | Essential fields |
| --- | --- |
| Country | Internal stable ID, display name, optional ISO codes, source IDs, bounds, selection geometry/anchor, content availability |
| Place | Stable ID, country ID, longitude/latitude, kind, display name, source reference |
| Challenge | Stable ID, country ID, optional place ID/coordinates, title, description, content version |
| Player progress | Schema version, manually visited country IDs with dates, completed challenge IDs with dates |
| Pack manifest | Pack ID/version, geographic bounds, min/max zoom, tile index, source snapshots/hashes, license/attribution, content version |

Treat IDs as opaque strings. ISO codes are useful metadata but not universally populated or sufficient for territories; maintain explicit mappings and migrations. Never key progress by display name, feature array position, or tile ID.

Derive `unvisited`, `visited`, `partial`, and `completed` from canonical visit/completion records. For the MVP, require a recorded visit before completing its challenges. Derive partial/completed only when the available challenge count is greater than zero. Undoing a visit with completed challenges should explicitly offer to clear that country's completion records, preserving the invariant.

Calculate `completed active challenges / available active challenges` for the displayed pack version. Label it as activity progress. New content can reduce that percentage without erasing earlier completions; retain stable IDs and explain that more activities became available.

### Current visual-first scope

The app currently opens directly on the Earth/universe scene. WorldCanvas measures the full viewport; GlobeCanvas owns the camera, gestures, one cached globe image, and read-only country labels. The Earth detail pass adds richer land/ocean/ice shading, layered clouds with shadows, coastal color, an atmosphere rim/glow, a cratered moon, a solar-panel satellite, and varied stars. The background shader places distant objects for portrait/landscape; the sphere naturally covers them during zoom. World surface noise blends across the longitude seam. All added scenery is illustrative shader artwork, with no additional decoded images. The land/border/lake texture is restored to 222,387 bytes and remains approximately 32 MiB decoded before GPU/transient costs.

Phase 3’s capital catalog, country-code selection mask, modal location picker, contextual panels, visit models/store, and AsyncStorage dependency have been removed. The [development plan](./DEVELOPMENT_PLAN.md) now puts richer continent/country rendering and geographically anchored capital scenery before these application features. The 16× globe overview does not establish city-level coverage. Build a continuous visual route before claiming the four-scale experience.

### Persistence — deferred until after the visual journey

Use Expo's documented [AsyncStorage integration](https://docs.expo.dev/versions/v58.0.0/sdk/async-storage/) for a small versioned progress document on native and web. It is unencrypted persistent key-value storage, appropriate for this prototype's visit/completion records, not large map images.

Hydrate before accepting progress edits; keep transient camera/input state separate. Serialize writes to prevent an older save overwriting newer progress, validate/migrate the schema, and report save/load failure without silently discarding records. A corrupt record should offer an explicit reset rather than automatically wiping progress. Browser storage can be unavailable or cleared; local-only persistence is not a backup or cross-device sync.

There is no active progress store or storage dependency. Reintroduce versioned country/capital/POI records, linked undo rules, ordered writes, recovery, and migrations when Phase 5 adds discovery records (P5-07); Phase 7 adds visits (P7-04). Recent visits should derive from explicit dated records, not camera navigation.

No backend, authentication, GPS, background tracking, geocoder, or state-management dependency is needed for this slice. A future location provider can add verification evidence to the visit model without changing map geometry.

## Development and €0 boundaries

Skia is installed for rendering. AsyncStorage is deferred until saved records are implemented. Install SDK-compatible packages with `npx expo install`, then run lint and typecheck. Keep Gesture Handler/Reanimated already present; do not install Phaser or MapLibre speculatively.

The [SDK 58 Skia reference](https://docs.expo.dev/versions/v58.0.0/sdk/skia/) lists it in Expo Go, allowing an early compatible-client visual trial. Custom non-bundled native code requires a development build. Use EAS cloud builds through `npx eas-cli@latest build --profile development` when needed, with generated native configuration expressed through app config/plugins. Never hand-create native projects. [Development builds](https://docs.expo.dev/develop/development-builds/introduction/)

| Cost area | Prototype strategy | Limit |
| --- | --- | --- |
| Data/art/software | Public-domain/CC0 art plus licensed OSM data and open-source tools | Processing time, disk, and license obligations still exist |
| Runtime mapping | Bundled maps, no external map requests | Coverage is intentionally small |
| Builds | Expo Go trial, then cloud builds within a free allowance | [Expo pricing](https://expo.dev/pricing) has bounded free build quotas/queues; do not promise unlimited builds |
| Native iOS testing | Expo Go first if a compatible phone/client is available | Physical-device development distribution may require paid Apple membership; simulator validation is not equivalent to a physical phone |
| Distribution | Local web and development previews first | [Apple](https://developer.apple.com/programs/) lists US$99 annual membership; [Google Play](https://support.google.com/googleplay/android-developer/answer/6112435) lists a US$25 registration fee, subject to eligibility/local terms |
| Future hosting | Consider static regional packs only after measuring usage | Storage, requests, bandwidth, and provider terms prevent a permanent global €0 guarantee |

The project can target a €0 prototype using existing hardware and free tooling. Public store release and global hosting are separate budgets. If access to an iPhone is unavailable, record iOS as unvalidated instead of claiming cross-platform parity.

## Validation experiments and decision gates

Run these after the architecture review, before building the broader application. Keep recordings, timings, device/browser versions, pack sizes, and a short pass/fail note. Time estimates assume existing access to suitable hardware and datasets.

| Experiment | Time box | Evidence and proposed acceptance | Response to failure |
| --- | --- | --- | --- |
| SDK/rendering compatibility | 0.5–1 day | Minimal Skia scene with a texture, gesture, and shader in SDK 58 on Android/iOS; web loads local CanvasKit with loading/error UI and no server import failure | Resolve compatible versions within the box; track unavailable platforms explicitly; evaluate the alternative if blocked |
| Pixel terrain generation | 1 day | Generate the same coastal/urban sample from Malta and Rome; inspect 1×/2×/3× density and fractional zoom. Coastlines/roads remain recognizable; no visible tile seams; second area uses the same rules | Simplify layers, adjust the grid/palette; reject mixed art styles before expanding coverage |
| Camera and cache stress | 1–2 days | Repeated pan/pinch across tile boundaries on a mid-range Android and an available iPhone. Aim for p95 frame time ≤20 ms, no map-work stall >100 ms after warm-up, atlas cache within 16 MiB plus one 32 MiB globe texture, and no growing memory trend over 5 minutes | Fix scheduling/culling once; if custom camera/tile work still fails, compare MapLibre with the same tiles |
| Globe and projection handoff | Core Phase 2 validation | Sphere texture and inverse picking agree; selected center differs by ≤8 screen points across transition; reverse/interrupt behavior is stable; test equator, antimeridian, and polar limit | Correct projection/transition behavior in the existing Skia implementation; do not add a second 3D engine |
| State and offline walkthrough | 0.5–1 day | Earth → country → city → challenge; manual record/undo; relaunch retains progress. An installed native build's bundled route works in airplane mode. Web makes no external map requests. Simulated save failure is visible | Fix progress/asset lifecycle before adding content; browser offline reload remains deferred until an explicit cache strategy is validated |
| Selection and geographic edge cases | 0.5 day | Malta reachable by an accessible anchor; Fiji/Alaska wrapping, polygon holes, disputed IDs, overlapping POIs, and absent detail handled. Challenge coordinates remain independent of decorative art | Improve selection metadata and coverage messages; no false visits/completion from missing data |

Use release/development builds and browser performance tools where available; Expo Go timings are early signals, not final performance evidence. Test a cold web load on a throttled mobile connection, measure the CanvasKit/asset payload, and aim for an interactive atlas within 5 seconds; keep a loading state and retry path if not achieved. This is an initial target to calibrate against actual devices.

For the MapLibre fallback test, use pixel raster tiles with nearest magnification and a small selection layer. The [style specification](https://maplibre.org/maplibre-style-spec/layers/#raster-resampling) documents `raster-resampling: nearest` across GL JS/Native; newer generic resampling controls have different support, so check the pinned engines. Verify asset loading and native/web APIs rather than copying GL JS examples into the native wrapper. Preserve the required globe and shared geographic model when evaluating any atlas fallback.

## Development phases

[DEVELOPMENT_PLAN.md](./DEVELOPMENT_PLAN.md) is the source of truth for project phases, actionable task IDs, dependencies, and completion criteria.

| Phase | Project milestone |
| --- | --- |
| 1 | Project foundation and app shell |
| 2 | Pixel-art Earth and map interaction |
| 3 | Continent/country scenery and continuous zoom |
| 4 | Detailed Valletta scenery and the complete visual journey |
| 5 | Exploration controls and saved visits |
| 6 | Game interface, quests, and progression |
| 7 | Rome, platform validation, and preview |

Phase 1 and the Phase 2 globe foundation remain implemented. The previous Phase 3 navigation/visit prototype is removed. Continue with Earth presentation and the P2-06 art contract, then the new P3-V continent/country rendering tasks and Phase 4’s detailed capital. Application UI, visits, and progression follow the visual milestone. Phone/Safari validation and performance measurements remain open.

The required globe is part of Phase 2 and final MVP verification. Post-MVP features remain outside this backlog until separately scoped.

Allow roughly **3–5 focused weeks** for the core MVP, with additional time for integration issues, unfamiliar GIS/shader work, or unavailable hardware. This is a planning estimate, not a delivery commitment. Use actual phase results to refine subsequent estimates.

## Largest risks

| Risk | Why it matters | Containment |
| --- | --- | --- |
| A custom renderer grows into a GIS project | Camera, culling, selection, and caching consume solo development time | Bounded capabilities, early time box, MapLibre comparison using the same raster output |
| Pixel style loses geographic readability | Attractive noise can hide islands, merge roads, or create false landmarks | World-anchored grid, logical selection metadata, two contrasting samples, human review |
| Globe consumes the project | Projection transitions and mobile shaders can dominate effort | A bounded 2D Skia sphere using the same geographic model and a simple atlas handoff |
| Data/decode growth | Compressed files hide GPU/RAM cost; a whole-planet city pyramid is infeasible for this MVP | Coverage manifests, byte budgets, local processing, regional packs, no all-world high detail |
| Cross-platform gaps | Native thread behavior, browser WASM, build access, and API support differ | Explicit platform matrix and measured evidence; mark untested targets honestly |
| Content/progress ambiguity | Updated activities, territories, and manual visits can produce misleading completion | Stable IDs, pack versions, explicit denominator, no zero-challenge completion |
| License/service assumptions | Open data does not imply free hosted tiles or no distribution obligations | Source manifests, retained license material, raw-extract workflow, visible credits |

The approach is feasible for a small exploration prototype if visual generation and camera experiments pass. Global expansion should reuse the same coordinate/content contracts and generation rules, while treating detailed coverage, curation effort, and distribution cost as explicit incremental work.
