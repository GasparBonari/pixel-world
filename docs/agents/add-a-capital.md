# Prompt: add the next country and its capital

Paste everything below the line into Codex, and fill in the two placeholders first.

---

Add **{COUNTRY}** and its capital **{CAPITAL}** to Earthia, at the same level of detail as Portugal/Lisbon, Spain/Madrid and France/Paris. Work in this repository. Expo and code rules are in `AGENTS.md`; follow them. Art rules are in `docs/art/ART_CONTRACT.md` (§1–§3a); read it first. Read `DEVELOPMENT_PLAN.md` (Phase 4) for how the existing capitals were built.

## What the player sees (do not change this structure)

1. **Continent zoom (about 6×):** the night-sea board with flora, fauna and mountain icons. It already exists, so don't touch it.
2. **Country zoom (zoom 4.4–6.4, only over a covered country):** a few buildings at the country's real cities, plus a few trees, boats, and at most one or two famous country landmarks at their real sites.
   - One sprite per place, in the country's building family. The capital is a `capital` marker (a walled town with a gold star).
   - The next two cities are a `church` each (a `mosque` in Turkey and Albania; Bosnia and Kosovo alternate).
   - Other cities, at least 75 km apart, alternate between a `church` and a `house`.
   - **Add the country to `FAMILY` in `build_map_icons.py`** (central, mediterranean, atlantic, nordic, orthodox or ottoman; see `docs/art/ART_CONTRACT.md` §3a). The build fails without it.
   - Examples of landmarks: Spain's La Mancha windmills, France's Mont-Saint-Michel and Saint-Émilion vineyards.
   - **Placement is automatic; don't hand-place offsets.** The builder reveals icons in zoom steps so they never overlap once fully visible, draws a landmark that sits on its capital a few pixels aside, and leaves out towns or trees that only fit beyond zoom 6.2 (listed under `omitted`). The rules are in `docs/art/ART_CONTRACT.md` §3a.
3. **Capital zoom (zoom 6.3–7.0, only within 1.5° of the capital):** one detailed isometric city scene, 720×520 art pixels.
   - It grows out of the capital's location and can be panned.
   - It is an **illustration**: the capital's real landmarks in their real relative positions (north at the top, west on the left), with distances compressed to fit. It is not a street-accurate map.

## Files you will touch

| What | Where |
| --- | --- |
| Landmark builders (true isometric 3D) | a new `scripts/art/landmarks_<region>.py`, reusing helpers from `scripts/art/landmarks_paris.py` (`P`, `seg`, `poly`, `corners`, `facade`, `mansard`, `egg_dome`, `stone_bridge`, `preview`) and `scripts/art/landmarks_iberia.py` (`hip_roof`, `crenellate`, `stone_courses`, `arch_opening`, `palette_of`, `tones`). It **must** end with a `SITES` table, one row per landmark: `(name, builder, footprint, (real_longitude, real_latitude), (x, y) scene anchor[, elevation])`, as in `landmarks_croatia.py`. The scene places landmarks from this table, and `check_capital.py` checks placement against it |
| Capital scene + registry | `scripts/art/build_capitals.py`: a `<capital>()` function and a `CAPITALS` entry `{id, name, country, longitude, latitude, render}`. It writes `assets/world/capitals/<id>.png`, `src/data/capitals.json` and the generated `src/data/capital-images.ts` (never edit that file by hand) |
| Country tier | `scripts/art/build_map_icons.py`: a `COUNTRY_TIER` entry `{adm0, bounds, capital, cities, landmarks}`. Use the Natural Earth `ADM0_A3` code; the capital name must match Natural Earth's populated places |
| New country-landmark icons, if any | `scripts/art/sprites.py`: add the function to `FLORA` or `ICONS`, and to `VARIANTS` in `build_map_icons.py` |
| Camera coverage | `COVERAGE` in `src/features/world/globe-camera.ts`: the same id, the capital's lon/lat, and the same bounds as `COUNTRY_TIER` |
| Tests | `tests/capital.test.mjs`: add a test that the country tier marks the capital and any landmark, like the France and Spain tests. **Note:** the "no detail yet" example (currently Rome) must stay an uncovered city; change it if you cover Italy |
| Docs | `DEVELOPMENT_PLAN.md` (a Phase 4 paragraph for the new capital), `docs/art/ART_CONTRACT.md` (the capital's palette in §3a, any new country landmark), `README.md` (example URLs) |

## Art rules (summary; the contract is authoritative)

- **Isometric geometry:** 16×8 tiles. A tile `(i, j)` maps to screen `x = (i - j)·8`, `y = (i + j)·4 − z`. Light comes from the upper left: the **+j face is lit** and the **+i face is shaded**. Each face has 3–4 tones. Outlines are 1 pixel, in a dark shade of each material's own hue.
- **Build in true 3D:** every landmark is built from (i, j, height) points, faces filled per material, and edges and lattice as projected lines. Do not draw flat front-on cut-outs.
- **Pixel size:** scene pixels are drawn at 2 screen points (icon pixels); terrain pixels are 3 points. Never scale art by a non-integer.
- **Each capital gets its own palette and house type,** so cities don't look alike:
  - Lisbon: pastel or azulejo walls, terracotta hip roofs;
  - Madrid: brick, ochre or cream walls, a balcony on every floor, slate mansards;
  - Paris: cream Haussmann blocks, zinc mansards with dormers, continuous balconies.
- **Proportion landmarks against the houses.** Monuments that dominate the real skyline must dominate the scene.
- **Keep every landmark in view.** Tall houses must never stand just in front of a landmark (on its screen-lower side). Reserve squares or streets there (`reserve(...)` in the scene functions).
- **Rivers run along an isometric axis,** so bridges (`stone_bridge`) cross them squarely. Keep the bank in front of a river open (promenades and trees), or tall blocks will hide the water.
- **Visible tile range:** with `CENTER_TILE = 40` and 720×520, a tile is visible when `i − j ∈ [−45, 45]` and `i + j ∈ [15, 145]`. Don't put landmarks against the edges.
- **Facts only:** use real landmarks and real coordinates. No invented places, progress numbers, XP or badges. Country-tier landmarks must be real, well-known places at their true lon/lat.

## Detail standard (the bar every building must reach)

The current art is the minimum quality, not a rough draft to approximate. Before you start, open the benchmarks and match their level of detail:
- the landmark previews in `docs/art/capitals/`: `paris-eiffel.png`, `paris-louvre.png`, `paris-notre-dame-arc.png`, `paris-sacre-coeur-houses.png`, `lisbon-castle-se.png`, `lisbon-se.png`, `lisbon-belem-arch-houses.png`, `madrid-palace.png`, `madrid-almudena.png`, `madrid-plaza-sol-metropolis.png`, `madrid-alcala-retiro-houses.png`;
- the finished scenes in `assets/world/capitals/` (`lisbon.png`, `madrid.png`, `paris.png`).

**Every landmark must have:**
- **Silhouette:** recognisable from its outline alone (towers, domes, spires, arches in the right number and proportion).
- **Signature details:** the features people know it by, each drawn, not implied. Examples: the Eiffel Tower's open lattice legs, base arches and platforms; Notre-Dame's twin towers, rose window, portals and flying buttresses; Belém Tower's loggia, domed watchtowers and cross-carved battlements; the Metrópolis' gilded dome and winged Victory.
- **Material and structure:** stone courses or rustication, cornices and string courses, columns or pilasters, window and door openings with frames, roofs with tile or slate texture and a ridge.
- **Shading:** a lit face, a shaded face and highlights, with 3–4 tones per material. Outlines in each material's own dark hue.

**Every house must have:**
- framed windows (two-pane glass and sills);
- doors or shopfronts on the ground floor;
- balconies or ironwork where the city has them;
- a plinth and a cornice;
- a textured roof (tiles, slate or zinc, with dormers on mansards) and chimneys;
- variety across the city (colours, heights, a few special houses), in that city's own style.

**The scene must have:**
- streets, squares and quays with distinct paving;
- trees and gardens;
- water with highlights and boats where there is water;
- no landmark hidden or cut off;
- a recognisable composition of the real city.

**Not finished if any of these remain:**
- plain boxes or blank walls;
- single-tone faces;
- stick or antenna-like statues;
- landmarks no bigger than the houses around them;
- patterns repeated so evenly they read as noise (fences, cages, stripes);
- details leaking onto the wrong face;
- anything noticeably simpler than the benchmarks.

If a landmark still looks crude next to the benchmarks, keep refining it. Don't move on.

**Before finishing,** compare your new previews side by side with the benchmarks. In your report, name each landmark and the signature details you drew. Say plainly which ones still fall short.

## Accuracy: build it right the first time

A review of all 27 existing capitals found that most buildings were fine but several cities were wrong in ways nobody had checked:
- Paris was drawn mirrored east–west, and Madrid rotated by 90°.
- Rivers put landmarks on the wrong bank (Berlin), canal rings put churches in the wrong district (Amsterdam), and gorges and hills were missing (Luxembourg, Tallinn, Vilnius).
- A waterfront City Hall stood inland (Stockholm).
- Buildings lost their defining feature: Nordiska museet had no central tower, the Belvedere was drawn compact instead of long and low, and Matthias Church's two towers were swapped.
- A Slovak flag without its coat of arms read as Russia's, and a coordinate in the docs was 1.2 km off.

Fixing them afterwards meant re-laying out whole scenes. **Treat everything below as part of the work, not an optional review:** a capital is not finished until every point is checked and stated in your report.

### Before drawing: a fact sheet per landmark

Write this down for each landmark and keep it in your report. Don't rely on memory alone; look the building up.
- **Real coordinates** of the building itself (not its square or the nearest street), from two independent sources, e.g. Wikipedia/Wikidata and OpenStreetMap. They should agree within about 100 m; if not, find out why. These go into `SITES` and into `DEVELOPMENT_PLAN.md`, so a wrong value spreads.
- **Setting:** which bank of the river, on which hill or plateau, on the water's edge or inland, inside which ring or district.
- **Silhouette facts:**
  - how many towers, domes and spires, and of what shape;
  - which tower stands at which end or corner (by compass direction);
  - the overall proportions (long and low? tall and narrow?);
  - roof form and colour, wall materials and colours.
- **The defining feature,** the one thing that makes it recognisable (Nordiska museet's central tower, Tyn Church's twin spires, the Belvedere's stepped copper roofline). If the model lacks it, the model is wrong, however detailed the rest is.
- **Which way its famous front faces** (by compass).

### Getting directions right in isometric

North is up, west is left: screen `x` grows eastward and `y` grows southward. Tile axes are diagonal:
- `+i` runs to the **south-east** (down-right).
- `+j` runs to the **south-west** (down-left).
- The two visible walls are the lit `+j` face, facing south-west, and the shaded `+i` face, facing south-east. North- and east-facing sides are hidden.

Use this every time you place something "at one end":
- **On the lit `+j` face,** the `-i` end is the north-west end and the `+i` end the south-east end. Example: Matthias Church's tall tower is at the *south*-west corner, so on a front drawn as the `+j` face it belongs at the `+i` end. It was drawn at the `-i` end, which swapped the towers.
- **On the shaded `+i` face,** the `-j` end is the north-east end and the `+j` end the south-west end.
- **A front that really faces north or east** sits on a hidden side. Either accept that and say so in your report, or turn the building and note the turn. Never let it happen by accident.

### Lay out geography before buildings

1. Draw the water and the terrain first.
   - **Rivers:** take the real course (where it enters the scene, where it bends, where it leaves) and approximate it with isometric-axis segments.
   - **Hills, plateaus and gorges:** raise them with the `elev` / `iso.ground_tile(..., elevation, wall)` pattern, like Gradec in `zagreb()`, Castle Hill in `ljubljana()` or the plateaus in `luxembourg()`. Draw landmarks on raised ground at that height (a `z` parameter on the builder plus an elevation column in `SITES`).
   - **Coasts and harbours:** put them on the correct side of the scene.
2. Then place landmarks from `SITES` anchors and check each one against its fact sheet. Is it on the right bank, on its hill, at the water's edge if it really is?
3. Every pair of landmarks more than about 120 m apart must keep its real east–west and north–south order. Compress distances freely, but never swap an order and never mirror or rotate the city.

### Model checks that are easy to miss

- **Count and handedness:** count towers, domes, spires and arches against the fact sheet, and check which end each one is on (see the direction rules above).
- **Keep the real proportions.**
  - A long, low palace must stay long and low. If its wings disappear, make the front longer; don't make it a compact block.
  - In this projection, a deep, tall block's shaded face hides lower parts to its `+i` side, so keep projecting pavilions shallow.
- **Monuments that dominate the real skyline must dominate the scene;** check against the houses next to them.
- **Flags and emblems:** many flags share stripes (Slovakia, Slovenia and Russia; Croatia and others). Draw the national arms where the real flag has them, so the flag can't be read as another country's.
- **Don't invent things:** no bridges, towers or flags you can't confirm. If a detail is a guess, leave it out or say in the report that it's unconfirmed.

## Required workflow (quality comes from iteration)

1. **List the capital's 6–9 defining landmarks,** write the fact sheet for each (see above), and decide the scene layout (river course, hills, squares, main streets) from real geography before writing code.
2. **Build each landmark alone** and render it on a test plot at 4× with `preview(...)` into `docs/art/capitals/<capital>-*.png`.
   - **Look at every preview image** and go through its fact sheet point by point:
     - silhouette, and the count and position of towers and domes;
     - proportions and colours;
     - the defining feature;
     - which way the front faces.
   - Fix what's wrong and re-render. Expect several passes per landmark.
   - If you cannot view images, stop and ask the user to review the previews before you integrate.
3. **Write the scene function** from `SITES` and render `.venv/bin/python scripts/art/build_capitals.py`. Then run the placement and visibility check:
   ```bash
   .venv/bin/python scripts/art/check_capital.py <id>
   ```
   It must print `OK`: no `REVERSED` pairs, rank correlation 1.00 on both axes, `hidden=0` and `clipped=0` for every landmark, and no overlaps. Then look at `assets/world/capitals/<id>.png` against your fact sheets, especially water, hills, banks and districts. The checker can't see those. Iterate until both pass.
4. **Find the scene's water** for its animation: run `.venv/bin/python scripts/art/capital_motion.py --preview /tmp/water` and open `/tmp/water/<id>.png`. Water is marked magenta and glint spots yellow. If the magenta covers roofs or glass, or misses the river, add a point on the real water to `WATER_AT` in that script and run it again. A scene without water gets no glints.
5. **Add the country tier,** then run `.venv/bin/python scripts/art/build_map_icons.py`. Check that every country-tier icon lies inside the country's bounds; the tests enforce this. The build prints how many country icons appear at each zoom step and which were left out. Your landmark must not be among them, and `tests/board.test.mjs` checks that nothing overlaps.
6. **Add `COVERAGE`,** then check in the browser:
   - start `npm run web`;
   - open `http://localhost:8081/?lon=<lon>&lat=<lat>&zoom=5` for the country and `...&zoom=7` for the capital;
   - also zoom in with the scroll wheel from the country view into the capital, and drag to pan. Panning must stop at the scene's edges.

## Checks before you finish

```bash
.venv/bin/python scripts/art/check_capital.py <id>   # must print OK
npm test                 # all tests must pass
npx tsc --noEmit
npx expo lint
npx expo export --platform android --platform ios --output-dir /tmp/pw-export --max-workers 2
```

Report what you ran and what passed. Include the fact sheet for each landmark, with your two coordinate sources and the setting, the defining feature, the tower/front orientation, and whether the model matches each point. Say what you could not verify (for example, real devices, or an unconfirmed detail). Do not commit unless asked.

## Setup on a fresh machine

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r scripts/art/requirements.txt -r scripts/geography/requirements.txt
PATH="$PWD/.venv/bin:$PATH" npm run assets:prepare      # globe and board textures
.venv/bin/python scripts/art/phase3_mockups.py          # fetches the pinned Natural Earth layers the icon builder needs
```

## Pitfalls already hit (avoid them)

- **Never silence a render script's errors** (`>/dev/null 2>&1`). A failure leaves stale preview images that look like "no change".
- **Don't reuse a name inside a draw closure.** A local variable that shadows a pattern function, such as `glass`, raises `UnboundLocalError` only at paint time.
- **Pattern functions apply to both walls.** If a front pattern (rose window, portal) is meant for the lit face only, give the shaded face its own pattern.
- **Things seen through openings** (courtyards, arches) must be clipped to the opening. Otherwise they spill over the façade below.
- **Draw order is `scene.add(depth, ...)` with depth ≈ `i + j + wi + wj`.** Parts that must rise through a roofline, like pavilions, need a larger depth than the wings they overlap.
- **Country bounding boxes overlap** (Portugal's box covers part of Spain). Trees and boats are filtered by the board texture's country index; keep it that way.
- **Adding coverage can break tests** that use an example city as "uncovered". Update the example; don't weaken the test.
- **Mirrored or rotated layouts look plausible.** Paris and Madrid passed visual review when they were built, while being wrong. Only checking real orderings (`check_capital.py`) catches this.
- **"Which end?" mistakes:** a tower on the wrong end of a front looks just as good as one on the right end. Always derive the end from the compass rules above, never by eye.
- **Doc coordinates are not automatically right.** A table entry was off by 1.2 km. Verify every coordinate against a second source before writing it down.
- **A study image can be stale.** If you change a model, re-run its module's `main()` so its study matches the code.
