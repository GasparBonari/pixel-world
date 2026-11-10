# Pixel World — Development Plan

**Priority: build the world’s visuals and zoom journey first.** The app should open directly on a beautiful pixel Earth, then reveal a continent, a country, and a detailed capital as the player zooms. The latest GlobeQuest concept image supplied on 10 November 2026 is the visual reference.

The previous Phase 3 navigation/visit implementation has been removed: parchment panels, location pickers, settings, visit markers, saved visits, the global capital catalog, and its storage dependency. Those features return after the map experience is convincing. The globe and earlier foundation remain.

**Current work: Phase 3 — the continent game board is running in the app** (P3-V02/P3-V04 in progress), following [art contract draft 2.1](./docs/art/ART_CONTRACT.md). Zooming in darkens the daytime ocean into the night sea and turns the land into the raised, puzzle-piece board with mountain and tree icons. **Next: Malta's country pack (OSM detail) and a higher zoom limit, then the pin/name chip, header and card.**

## The experience we are building

| Scale | What the player should see | How it should feel |
| --- | --- | --- |
| Earth | Recognizable continents, blue oceans, green/arid/icy land, readable coasts, clouds, stepped lighting, a pixel atmosphere, and stars | Open the app into the full-screen universe; drag to spin and pinch toward a place |
| Continent | The continent fills the view; countries, islands, coasts, rivers, terrain, and major settlements become readable | Follow the same geographic focus as the globe fills the screen and curvature becomes less visible |
| Country | A recognizable country map with richer terrain, roads/settlements where data supports them, and a clear capital | Continue zooming into that geography; finer information arrives in the same palette and pixel treatment |
| Capital | A geographically grounded scene with streets, building footprints, water, parks, recognizable landmarks, and appropriate city scenery | Arrive in a place worth exploring, with a useful maximum zoom and a smooth return to the country |

The reference illustrates **Earth → Europe → Portugal → Lisbon**. Keep the existing detailed-pack pilot **Europe → Malta → Valletta**, then **Europe → Italy → Rome**. The reference’s Lisbon scene guides visual richness; full Lisbon coverage can follow through the same pipeline.

The reference’s quest lists, avatar, XP, badges, statistics, and parchment cards describe the eventual game. They are later layers over the map. Stop geographic drill-down at capital cities for this iteration.

## Visual rules

1. **World first.** The map and universe fill the screen. Keep the opening free of large panels, pickers, travel forms, and game dashboards while building the scenery.
2. **One art direction.** Keep hard pixel edges, a coordinated ocean/land palette, coherent outlines, stepped lighting, and a consistent scale for decorative elements. The city must belong to the same world as the planet.
3. **Zoom reveals actual detail.** Increasing the size of the current globe texture does not create rivers, streets, buildings, or landmarks. Add the geographic layers each scale needs.
4. **Follow the place.** Preserve the point under the gesture, geographic alignment, orientation, and camera continuity. Use a gradual change of scale/detail; avoid a jump to a disconnected city picture or a differently styled atlas.
5. **Keep coarse coverage while loading.** Reveal finer detail when ready, retain the current view during loading, and bound memory. Do not blank or remount the map between scales.
6. **Separate scenery and source geometry.** Real geography anchors shorelines, roads, and landmarks. Decorative clouds/trees/color variation are illustrative; do not invent named places from noise.
7. **Keep coverage honest.** A capital overview is not a detailed city scene. Define coverage and useful zoom limits until a pack exists.
8. **Build only what is used.** Keep assets small, record sources/licenses, and measure compressed and decoded costs. Removed atlas/demo/sprite images stay removed.

## Phases and order

| Phase | Focus | Result | Status |
| --- | --- | --- | --- |
| 1 | App foundation | Expo app, routing, shared styling, and checks | Complete |
| 2 | Earth and universe | An attractive, responsive opening planet | Core implemented; visual refinement and platform validation active |
| 3 | Continent/country visuals and continuous zoom | Richer geography appears while zooming into the same world | Next |
| 4 | Detailed capital visuals | The journey reaches recognizable Valletta scenery | Planned |
| 5 | Exploration controls and saved visits | Lightweight contextual navigation and explicit local records support the finished map | Deferred until the visual journey works |
| 6 | Game interface and progression | Quests, avatar/XP, badges, statistics, and collections reflect real records | Deferred |
| 7 | Second capital and release validation | Rome reuses the visual pipeline; the two-capital experience is verified | Planned |

**Visual milestone before Phase 5:** demonstrate Earth → Europe → Malta → Valletta and back, with actual detail increasing at each scale. Minimal focus/back controls needed to demonstrate this belong to the visual work; visits, searchable global pickers, progress panels, and rewards do not.

## Current implementation

- Expo SDK 58, Expo Router, Skia 2.14.0, Gesture Handler, and Reanimated.
- Full-screen Earth and universe with drag, pinch, wheel, keyboard, and Home reset. The opening camera faces the Atlantic/Europe/Africa rather than an arbitrary destination screen.
- The Earth detail pass adds a brighter atmosphere and stepped outer glow, coastal shallows/sandy edges, forest-like green variation, arid colors, icy polar texture, restrained ocean highlights, and layered clouds with shadows. These surface treatments are illustrative; the geographic masks still anchor the real coastlines.
- Space contains a cratered moon, a satellite with solar-panel grids/body/dish/antenna, varied blue/white/gold stars, and faint background color. Objects move to suitable positions for portrait/landscape and sit behind the growing planet. The scenery uses shader code, with no new image files, dependencies, or decoded textures.
- One 4096×2048 Natural Earth land/border/lake texture: **222,387 PNG bytes**, approximately **32 MiB decoded**, excluding GPU/transient overhead. Country names are display labels only.
- The same sphere renderer stays active through zoom 0–5 (1×–32×). From zoom 1.5 to 2.5, one shader blends the daytime globe into the continent board.
  - Terrain pixels are 3 points on phones at every zoom (`CELLS_ACROSS`).
  - Sea bands come from a coast-distance field and are converted to screen pixels at each zoom.
  - Country tones and borders come from the board texture's country index.
  - Raised coasts come from the neighbouring screen pixels.
  - 1,093 icons (295 mountains, tree clumps) draw in one Skia `Atlas`, projected every frame and fading in from zoom 2.0.
  - Coverage is global but continent-scale only. Beyond about zoom 4, coasts and borders turn blocky until country packs exist.
- The generator rebuilds the globe, display labels, manifest, and public-domain attribution from three pinned Natural Earth inputs. Outputs replace completed files atomically so Metro can remain running during regeneration.
- No visit tracking, local progress store, capital catalog, modal location picker, or contextual game HUD is currently installed.

[README.md](./README.md) contains run/regeneration/check commands. [TECHNICAL_PLAN.md](./TECHNICAL_PLAN.md) remains an architecture reference; this document controls implementation order.

## Phase 1 — Foundation

- [x] **P1-01 — Configure project checks.** SDK-compatible lint and typecheck commands.
- [x] **P1-02 — Resolve starter typing issues.** Expo declarations and web typing fixes.
- [x] **P1-03 — Establish routing.** Expo Router screens in src/app/; world rendering outside routes.
- [x] **P1-04 — Establish theme foundations.** Shared colors, type, and spacing.
- [x] **P1-05 — Verify the foundation.** Lint/typecheck, available browser checks, and platform bundle exports.

## Phase 2 — Earth presentation and visual foundation

**Result:** opening the app immediately shows an appealing, interactive pixel planet in a full-screen universe.

- [x] **P2-01 — Connect the renderer.** Skia native entry and browser CanvasKit with loading/failure/retry states.
- [x] **P2-02 — Generate the Earth overview.** Pinned Natural Earth masks, display labels, provenance, and license.
- [x] **P2-03 — Implement the globe camera.** Rotation, focal zoom, wrap/tilt bounds, and web input alternatives.
- [x] **P2-04 — Keep the original art through zoom.** Reuse the globe texture; remove obsolete atlas and unused images.
- [ ] **P2-05 — Validate the renderer.** Physical Android/iPhone, Safari, frame behavior, GPU/transient memory, five-minute memory trends, and throttled cold loading. Record unavailable targets.
- [ ] **P2-06 — Define the four-scale art contract.** Capture Earth/continent/country/capital style studies. Specify palette, pixel density, water/coast treatment, terrain, outline weight, lighting, and city-building perspective. Plan the gradual globe-to-regional presentation before generating detail packs.
  - **Continent/country contract, [draft 2](./docs/art/ART_CONTRACT.md) (10 November 2026).** Draft 1, using globe-blue water, dark borders and 2-point pixels, was judged too far from the concept image. Draft 2 adopts the concept's look:
    - a night sea with sparkles and clouds;
    - raised land with lit coasts and green cliff faces;
    - puzzle-piece country tones with pale borders;
    - a few large upright icons (snowy mountains, tree clumps, houses, castles, sailboats), with no rivers, roads or country-name labels;
    - an orange selection glow with a pin and white chip;
    - 3-point art pixels;
    - a parchment header and bottom card, with factual content only.

    Draft 2.1 adds detailed, shaded icons from `scripts/art/sprites.py`: a multi-peak snowy mountain, grassy hill, broadleaf and pine trees, castle, parish church, house, sailboat and pin. They are drawn with 2-point icon pixels over the 3-point terrain. Water bands are still measured in art pixels. Real-data mockups are in `docs/art/phase3/` (Europe from Natural Earth; Malta from OSM). Five open questions await review, including how the daytime globe ocean transitions to the night sea. The capital-scale rules are deferred to Phase 4.
  - **Capital/UI style study (10 November 2026), route `/style-study`.** A 12×11-tile seaside street from [Ninja Adventure](https://pixel-boy.itch.io/ninja-adventure-asset-pack) (CC0), drawn with Skia `Atlas` (8 batched draws, nearest sampling, whole-number scale; 2× on phones), plus a nine-slice panel and Pixelify Sans text. Findings: the warm 16×16 style and terracotta/red-tiled roofs suit the reference; its buildings are one-storey cottages, so multi-storey townhouses and landmarks still need original sprites. Pack grass `#ADBC3A` is yellower than globe grass `#8AC240`, and pack water `#71DDEE` is much lighter than globe shallows `#40A8C4`. **Decision: remap the pack to the globe.** `scripts/art/recolor_style_study.py` swaps 9 grass/foliage and 5 water colours for the globe's land and water ramps (exact-colour table; roofs, paths, flowers, and characters unchanged) and writes `assets/style-study/globe-palette/`. The study page shows the globe palette by default, with a toggle back to the pack colours. Pixelify Sans reads well at 12–22 px and now sets the globe's country labels and loading/error text, loaded by the root layout behind the splash screen; the pack's own font has broken letter spacing in the browser and is rejected for text. The pack's orange nine-slice frame works at 2–3×; the reference's cream parchment would need a recolour. Imported files total 188,319 bytes. The study does not yet define the continent/country scales, and it has not been checked on native devices.
- [x] **P2-07 — Make the first Earth visual pass.** Clear the opening UI; refine opening framing, ocean/coastal colors, atmosphere, stars, clouds, and silhouette while preserving real land shapes and the original pixel treatment. Continue visual iteration as needed.

- [x] **P2-08 — Add reference-inspired Earth and space detail.** Brighter land/ocean/ice texture, readable coasts, cloud bodies/highlights/shadows, atmosphere/glow, varied stars, a cratered moon, and a detailed satellite. Keep the scene interactive, use responsive object placement, hide distant objects naturally behind the zooming sphere, preserve the geography mask, and avoid new image downloads.

**Exit criteria:** Earth reads clearly at phone/tablet/desktop sizes; drag/pinch remain responsive; the shared art rules are concrete enough to guide the next scales. Device evidence remains tracked rather than inferred from a bundle export.

## Phase 3 — Continent/country scenery and visual zoom

**Dependencies:** the globe and P2-06 art rules. This replaces the removed navigation/visit prototype. Previous task IDs P3-01 through P3-06 are retired; the new visual tasks use P3-V IDs.

- [ ] **P3-V01 — Prepare geographic detail for the pilot route.** Bound Europe/Malta inputs; retain source IDs, coastlines/islands, country shapes, and real terrain/water data needed for rendering. Add only the metadata the visual journey uses.
  - *Started (10 November 2026):* inputs are pinned for the design mockups. They are Natural Earth rivers, mountain ranges and populated places (`scripts/art/phase3-sources.lock.json`) and the Geofabrik Malta OSM snapshot `malta-261108`. In it, Malta has 7,711 coastline points versus 38 in Natural Earth 1:10m, so the country scale must use OSM. No app data pack is generated yet.
- [ ] **P3-V02 — Render the continent view.** Show recognizable European geography with readable countries, islands, rivers, and terrain in the established pixel style. Use actual geographic detail and restrained labels; keep the scene full-screen.
  - *In progress (10 November 2026):* the board renders in the globe shader from `assets/world/board.png`, generated by `npm run assets:prepare`, with icons from `scripts/art/build_map_icons.py`. Country-name labels hand over to the board at zoom 1.9. Still to do: selection (pin, glow, chip), the header and card, and checks on native devices.
- [ ] **P3-V03 — Render the country view.** Add Malta’s finer coast/water, land-use/terrain, settlement/major-road structure, and Valletta’s geographic position. Scale decorative scenery deliberately; do not scatter arbitrary named landmarks.
- [ ] **P3-V04 — Connect the zoom visually.** Define camera/detail ranges from geographic bounds rather than the example image’s 10×/5× labels. Preserve the gesture’s focus through a gradual presentation/projection change, reveal detail progressively, and reverse cleanly. Keep one camera coordinate model.
- [ ] **P3-V05 — Verify visual continuity.** Capture the same route at all zoom thresholds and fractional zooms; check coastline alignment, pixel/palette continuity, tiny islands, loading, interrupted gestures, rotation/orientation, portrait/landscape, and bounded asset loading.

**Exit criteria:** zooming toward Europe and Malta reveals visibly richer geography, with no art-style switch, abrupt replacement image, or screen-sized UI blocking the map. A read-only globe enlarged to 16× does not meet this milestone.

## Phase 4 — Capital scenery: Valletta

**Dependencies:** connected continent/country rendering and the shared art contract.

- [ ] **P4-01 — Prepare the bounded capital pack.** Pin Malta/Valletta OSM inputs; extract coast/water, streets, parks, and building footprints with source/license records and reproducible generation.
- [ ] **P4-02 — Render recognizable capital scenery.** Compose streets, buildings, greenery, waterfront, and curated landmarks using the world’s palette, pixel grid, outlines, and lighting. Preserve geographic position even when sprites use a three-quarter perspective.
- [ ] **P4-03 — Connect country to capital.** Reveal the capital’s real detail around its coordinates, retain coarse coverage while loading, and cap useful zoom. Returning restores the same country context. Other capitals stay coverage-limited until packs exist.
- [ ] **P4-04 — Verify the complete visual journey.** Walk Earth → Europe → Malta → Valletta and back. Check landmarks/roads against sources, visual continuity, input interruption, asset/disk/decoded costs, and available platforms. Record unavailable native checks.

**Exit criteria:** the capital is recognizable scenery with real geographic anchors, not an overview marker or standalone city illustration. Complete the visual milestone before adding the game UI.

## Phase 5 — Exploration controls and saved visits

**Dependencies:** the four-scale visual journey.

- [ ] **P5-01 — Add minimal contextual navigation.** Lightweight title/back/focus controls and accessible alternatives support map gestures. Any sheets remain optional/collapsible; preserve the mounted scene and parent camera.
- [ ] **P5-02 — Add the approved location/POI catalog.** Stable IDs, parent relationships, multiple/no-capital cases, source provenance, and explicit detailed-coverage bounds. Document continent/territory policy.
- [ ] **P5-03 — Add explicit visit/discovery actions.** Viewing a place never records travel. Define dated country/capital/POI visits and linked undo behavior before wiring UI.
- [ ] **P5-04 — Add versioned local persistence.** Hydration, schema validation/migrations, ordered saves, failure/retry, and explicit reset. Keep transient camera/input state separate; install storage only when used.
- [ ] **P5-05 — Verify exploration records.** Visit/undo, relaunch, corrupt/unavailable storage, content updates, and no progress changes from browsing.

## Phase 6 — Game interface, quests, and progression

**Dependencies:** finished scenery and canonical exploration records.

- [ ] **P6-01 — Author real capital activities.** Stable IDs, source-grounded places, original content, categories, and defined rewards.
- [ ] **P6-02 — Add quest interactions.** Select a place, inspect/complete/undo an activity, and persist its record.
- [ ] **P6-03 — Derive progress and rewards.** Activity denominators, XP/levels, badges/stamps, and undo rules use actual records; repeat completion cannot farm rewards.
- [ ] **P6-04 — Add the reference-inspired HUD.** Avatar/XP, parchment cards, travel stats, recent visits, country summaries, and capital checklists complement the map. No placeholder rewards or fabricated percentages.
- [ ] **P6-05 — Add working game destinations/settings.** Expo Router views for Quests, Collection, Progress, and Profile arrive with content; retain map/camera state.

## Phase 7 — Rome, platform validation, and preview

- [ ] **P7-01 — Add Rome through the same pipeline.** Reuse capital preparation/style rules, then author places/activities without creating a new exploration flow.
- [ ] **P7-02 — Validate platforms and accessibility.** Available Android/iPhone and Chromium/Safari; safe areas, targets, labels, reduced motion, sheet/gesture separation, tiny countries, date-line and polar behavior.
- [ ] **P7-03 — Measure the real scenes.** Frame behavior, decoded/GPU/transient memory, cold loading, pack/app disk cost, and five-minute memory trends.
- [ ] **P7-04 — Verify saved/offline behavior.** Installed native packs in airplane mode, relaunch, write failure/reset, reward undo, and content versions. Browser offline reload needs a separately tested cache strategy.
- [ ] **P7-05 — Prepare the preview.** Retain attribution, regeneration instructions, coverage limits, a recorded four-scale walkthrough, and passing project checks.

## Verification record

The foundation previously passed lint/typecheck, seven projection/camera/cache tests, Expo Doctor (20/20), all-platform bundle exports, and Chrome full-screen/rotation/zoom/loading-retry checks. The removed Phase 3 prototype’s navigation/storage tests no longer describe shipped functionality.

**Visual reset verification (10 November 2026):** lint, typecheck, all seven retained logic tests, Expo Doctor (20/20), and iOS/Android/web exports passed. Chrome 157 checks passed for the clean opening, shader compilation, drag, real two-finger pinch, wheel zoom, country display labels, Home reset, retained canvas, and a single globe image request. Full-screen bounds passed at 320×568, 390×844, 844×390, 768×1024, and 1440×900, with no runtime errors. Regeneration is deterministic and restores the original globe mask byte for byte. Physical devices, Safari, and performance/memory profiling remain open.


**Continent board verification (10 November 2026):**
- Lint passes. Typecheck passes except for the existing error in the unused `ContinentScenery.tsx`.
- 18 of 19 tests pass, including new tests for the URL camera, icon fade, icon data and board texture size. The existing scenery-scale test still fails.
- Regenerating assets keeps `globe.png` and the country labels byte-identical.
- Chrome (via the DevTools protocol, with real waits) renders the opening globe, zoom 2.0 (transition), 2.6 (Europe board) and 4.0 (Italy and Malta). Mouse-wheel zoom from the opening view reaches the board with no console errors.
- Android and iOS exports pass. Native device performance is unmeasured: the board adds about 6 inverse projections and 9 texture samples per pixel, and Safari is unchecked.

**Earth/space detail pass verification (10 November 2026):** lint/typecheck and the seven retained logic tests pass. Chrome 157 compiles the combined Earth/space shader and verifies drag, real pinch, wheel zoom, Home reset, retained canvas, clean full-screen layouts at five viewport sizes, and one globe image request. Fresh phone opening and portrait/landscape screenshots show the moon, satellite, stars, atmosphere, and cloud/surface detail. iOS/Android/web exports pass; native runtime performance and Safari remain unverified. The existing 222,387-byte geography PNG and its decoded-image budget are unchanged; all added art is shader code.
