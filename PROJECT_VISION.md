# Pixel World — Project Vision

Status: proposal for review. Research date: 9 November 2026.

Development phases and actionable tasks: [DEVELOPMENT_PLAN.md](./DEVELOPMENT_PLAN.md).

## The idea

Pixel World turns real-world travel into a pixel-art adventure. Players explore Earth, discover countries and cities, and collect memories of places they have visited through small, locally relevant challenges.

The central experience is **Earth → continents → countries → cities → challenges**. Moving across those scales should feel like exploring a retro adventure game. The geography comes from the real world; its visual language comes from classic top-down games.

Start by proving that this interaction is attractive and pleasant on a phone. The progression system can evolve after the visual and technical foundations work.

## Product principles

- **A recognizable Earth.** Coastlines, country locations, cities, and challenge coordinates should be geographically grounded. Decorative trees and buildings can be symbolic.
- **One coherent art direction.** Terrain, markers, panels, and landmarks share a palette, pixel scale, outline weight, and lighting convention.
- **Exploration without friction.** Pinch, drag, tap, and clear zoom controls make the world easy to navigate with one hand or two.
- **A rewarding record of travel.** Visiting a place changes its appearance and creates a visible sense of progress.
- **Small content, global structure.** Cover the planet at overview scale, then add detailed destinations through a repeatable data pipeline.
- **A sustainable solo project.** Prefer free data, reusable art, local persistence, and a bounded prototype over services with recurring costs.

## What exploration looks like

| Scale | Player experience | Visual direction |
| --- | --- | --- |
| Planet | Recognize Earth, spin it, zoom toward a region | Required pixel-art globe inspired by the supplied reference: stepped pixels, green terrain, blue oceans, white clouds, shaded rim, and a dark star field |
| Continent | Pan across recognizable landmasses | Broad land and water shapes, restrained terrain patterns |
| Country | Select a place and see its exploration state | Borders, names, state colors, and an accessible selection highlight |
| City or region | Find destinations and available activities | More detailed geography, reusable trees and buildings, city labels |
| Point of interest | Open a challenge and record an experience | Pixel markers and a readable challenge panel |

The globe is a presentation mode rather than a promise of a physically continuous 3D planet. A brief animated transition to a flat map is acceptable if it preserves the chosen location and feels deliberate. Seamless 3D globe-to-street rendering is outside the first MVP.

Browsing remains available before visiting a country. Unlocking changes progression and presentation; it should not prevent someone from learning about a future trip.

## Pixel-art direction

Use **16×16 sprites** as the initial unit. Use 32×32 or larger multiples only for landmarks that need more detail. Establish a small shared palette, consistent silhouettes, and a fixed top-down/three-quarter sprite convention before expanding the art collection.

Generate the geographic base from data, using stepped coastlines, limited colors, simple water patterns, and reusable terrain motifs. Avoid treating a blurred or downsampled conventional street map as the final aesthetic. At close zoom, preserve recognizable road and coast relationships while simplifying decorative detail.

Pan and zoom should move smoothly. Texture sampling should preserve hard pixel edges; an absolutely uniform pixel grid during every fractional zoom is not required. Prioritize readable geography and comfortable movement over rigid integer-only camera steps.

Use a pixel font selectively for short labels if a suitable licensed font is chosen later. Challenge descriptions and accessibility settings need comfortable reading sizes. Status must also appear as text or symbols, so color is never the only signal.

**Initial art source:** [Kenney Tiny Town](https://kenney.nl/assets/tiny-town) provides 16×16 CC0 tiles. [Kenney Pixel UI Pack](https://kenney.nl/assets/pixel-ui-pack) provides CC0 interface art. These are starting candidates, subject to a visual compatibility check. Only a few distinctive landmark sprites should need original drawing. The full asset and license shortlist is in [TECHNICAL_PLAN.md](./TECHNICAL_PLAN.md#free-data-and-art).

## Exploration and progression

Countries and locations have four displayed states:

| State | Meaning in the prototype | Suggested treatment |
| --- | --- | --- |
| Unvisited | No visit recorded | Muted terrain, outlined marker |
| Visited | A visit is recorded; no available challenge is complete | Color restored, visit badge |
| Partially explored | Some, but not all, available challenges are complete | Colored terrain, progress indicator |
| Completed | Every challenge in a non-empty available content pack is complete | Distinct badge or border |

Completion means completion of the app's available activities, not complete knowledge of a country. Display a concrete denominator, such as **2 of 5 available challenges**, rather than suggesting that five activities represent an entire nation.

For the prototype, use an explicitly labeled **manual visit record**. Players can record a past visit, undo it, and mark a challenge complete. This demonstrates state and persistence without pretending to verify travel. GPS verification, anti-cheating, and the handling of historical visits remain product decisions.

Future rewards could include XP, a travel journal, country stamps, collectibles, achievements, and cosmetic unlocks. None is required to validate the map experience.

## Challenges

Challenges should give players a reason to notice a place: a landmark, local food, a park, a cultural detail, or a short exploration route. The first content pack should favor public places and simple experiences that can be described accurately.

Possible example prompts for Malta include discovering Valletta's waterfront, visiting a public garden, or trying pastizzi. These are content concepts, not verified venue recommendations; opening hours, access, precise coordinates, and descriptions must be checked when authoring the pack.

Keep challenge text separate from map art and player state. A destination can receive more activities without regenerating its terrain or resetting completed activities. Location-based activities need coordinates; a food experience can belong to a city or country without implying a particular restaurant.

## Proposed first MVP

The proposed slice covers a global overview, **Malta with a Valletta detail area**, and a second contrasting city area, provisionally **Rome, Italy**. Malta tests small-island visibility; Rome tests denser urban geometry and whether generation rules transfer to another destination. These are planning choices, not inferred player locations.

Include:

1. A global Earth view with pan/zoom, country names, and selection.
2. A spinning pixel-art globe with increasingly detailed country geography that keeps the original planet's palette, shading, and pixel treatment throughout zoom.
3. All four country states, demonstrated through manual progress and clearly labeled sample data where needed.
4. Generated city detail for two bounded areas, with about five challenges per destination.
5. Country and challenge panels, manual completion, undo, and local persistence.
6. A coherent pixel-art presentation on iOS, Android, and web, with platform verification tracked explicitly.
7. An offline native walkthrough using bundled map and content packs; the web preview serves its own assets without external map APIs.

Outside detailed areas, the app should retain a useful overview and say **Detailed map not available yet**. Unsupported destinations can still be selected and recorded as visited. A country with no challenges must not be marked completed merely because its challenge count is zero.

Exclude authentication, payments, social features, background location, navigation directions, a full quest engine, worldwide street-level coverage, and a system for downloading arbitrary offline countries.

## How we avoid drawing the world

Use [Natural Earth](https://www.naturalearthdata.com/about/terms-of-use/), whose map data is public domain, for the broad geographic foundation. Use [OpenStreetMap](https://www.openstreetmap.org/copyright) data for selected detailed areas, respecting attribution and ODbL obligations.

A build-time process converts geography into pixel-art terrain at several scales. Reusable art supplies forests, settlements, markers, and panels. Human effort goes into art rules, a small number of landmarks, and compelling challenges. Expanding coverage adds data packs through those same rules; it does not require drawing a new country map from scratch.

This makes global coverage structurally possible. It does not make global detailed data processing, distribution, or content curation free. Start with bundled areas and measure the real costs before adding hosting.

## What success means

- Someone can move from the Earth view to a country, city, and challenge without explanation.
- A short session feels like exploring a game world, and the selected real places remain recognizable.
- Pan and pinch remain responsive on a representative mid-range phone.
- Recording a visit visibly changes the country; progress survives closing and reopening the app.
- Generating the second destination reuses the first destination's rules and reveals where they need improvement.
- The entire demonstration works without a paid map API or a running backend.

Performance, package-size, and compatibility targets are proposed in [TECHNICAL_PLAN.md](./TECHNICAL_PLAN.md#validation-experiments-and-decision-gates). They are acceptance criteria to test, not measured results.

## Decisions to review

The technical recommendation is a small Skia-based renderer using generated maps, with MapLibre as the alternative if custom camera or tile management becomes too expensive to maintain. Review the experiments before treating that choice as final.

The globe is required for the first release. Remaining product choices include whether Malta and Rome are the right initial destinations and how travel should eventually be verified. The proposed MVP can test the experience with manual records while those longer-term decisions remain open.
