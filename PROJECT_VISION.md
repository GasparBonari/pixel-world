# WorldQuest — Project Vision

Status: agreed direction, 20 November 2026. Replaces the 9 November proposal. "WorldQuest" is a working title; check app-store and trademark availability before building branding around it.

Development phases and tasks: [DEVELOPMENT_PLAN.md](./DEVELOPMENT_PLAN.md). Map art rules: [docs/art/ART_CONTRACT.md](./docs/art/ART_CONTRACT.md). Architecture: [TECHNICAL_PLAN.md](./TECHNICAL_PLAN.md).

**Explore. Discover. Learn. Collect.**

## The idea

WorldQuest turns the real planet into a pixel-art adventure. Players spin a pixel Earth, zoom through continents and countries into illustrated capital scenes, and collect what they find there: landmarks, wildlife, landscapes. The geography is real; the visual language comes from classic 2D adventure games.

People should open the app because they are curious about what they will find next, not because they need to look something up. A session can be five minutes with today's featured place, or an hour wandering a continent.

## Who it is for

Anyone curious about the world: geography fans, gamers, and travellers. **Nobody needs to travel to enjoy the app.** Virtual discovery is the core experience. Recording real trips is an optional personal layer on top of it.

## Product principles

- **The map is the main attraction.** It fills the screen. Interface appears in context — a sheet, a chip, a marker — and gets out of the way again. No dashboards over the world.
- **Zooming is rewarding in itself.** Every scale reveals detail the previous one didn't have.
- **A recognizable Earth.** Coastlines, countries, capitals, landmarks, and animal habitats are geographically grounded and sourced. Decorative trees, clouds, and houses can be illustrative, but never invent named places.
- **One coherent art direction.** World, scenes, icons, panels, and buttons share one palette, one pixel treatment, and one lighting convention.
- **Learn by noticing, not by reading.** Facts arrive attached to something on screen, in a sentence or two, not as articles.
- **Honest progress.** Counts always show a real denominator ("3 of 7 landmarks"). Discovering a place is never confused with visiting it.
- **A sustainable solo project.** Free data, generated art, local persistence, offline use, no backend, no recurring costs.

## The journey

| Scale | What the player sees | What they can do |
| --- | --- | --- |
| Planet | Pixel Earth in a starry universe | Spin, pinch toward a region, see progress per continent |
| Continent | A game-board map: night sea, puzzle-piece countries, flora, wildlife, mountains | Spot animals and landforms, pick a country |
| Country | Richer terrain, real cities with small buildings, the capital | Open the country sheet, see what is left to discover |
| Capital | An isometric diorama of the capital's real landmarks in their real relative positions | Find landmarks and hidden details, collect them |

The journey should feel continuous: the camera follows the chosen place and detail grows with zoom. Arriving at a capital may use a deliberate transition into its scene; a seamless planet-to-street 3D world is not a goal. Drill-down stops at capitals. Other cities appear only as small country-scale buildings.

## Two tracks: Discovery and Travel

Progress has two independent tracks. A country can be fully discovered and never visited, or visited and barely discovered. The interface shows them differently so they are never confused.

**Discovery** (everyone, in the app):

| State | Meaning | Treatment |
| --- | --- | --- |
| Undiscovered | The player has never opened this country | Muted colours, no count |
| Discovered | The player has opened the country | Colour restored, "0 of N" count appears |
| In progress | Some of its collectibles are found | Segmented progress bar, "n of N" |
| Completed | Every collectible in a non-empty content pack is found | Completion badge or border |

Opening a country discovers it. Collectibles are earned by finding them (completing their challenge), not by scrolling past them. A country with no content is never shown as completed.

**Travel** (optional, real life):

| State | Meaning | Treatment |
| --- | --- | --- |
| No record | — | Nothing |
| Want to go | On the player's wishlist | Wishlist marker |
| Visited | The player recorded a real visit | Passport stamp, visited pin on the map |

Visits are recorded manually and on trust: a dated check-in that can be undone. There is no GPS verification. Browsing or discovering never records travel.

## What players discover

**At launch**, collectibles come from content the project already researches and sources:

- **Landmarks** — the real buildings and monuments in each capital scene, each with sourced coordinates.
- **Wildlife** — native animals placed in sourced habitats on the continent board.
- **Landscapes** — characteristic flora and landforms (volcanoes, glaciers, dunes, forests).

Each collectible gets a pixel card with a name and one or two checked sentences.

**Later**, and only as curated, fact-checked packs: foods, traditions, and historical facts. Writing and verifying cultural content for every country is the most expensive and riskiest content in the project, so it waits until the core loop is proven.

## Challenges

Challenges ask the player to look at the world, not to recall general trivia. In priority order:

1. **Find it.** Locate a landmark or hidden detail inside a capital scene ("Find the bridge with the dragons"). This is the signature challenge type: it suits pixel art and uses scenes that already exist.
2. **Spot the animal.** Find or identify wildlife in its habitat on the continent board.
3. **Map questions.** Questions answered by tapping the map ("Tap the country whose capital is Lisbon"), not multiple-choice quizzes about things the player can't see.
4. **Country sets.** Find all of a country's collectibles to complete it.

## Sessions and the daily loop

- **Five minutes:** each day features one country or capital with 3–5 discoveries. This gives a short session a clear goal and a reason to come back.
- **Longer sessions:** free exploration, with any country's remaining collectibles always available.
- No penalties for missing days in the first version. Streaks, if added, reward without punishing.

## Progression and rewards

**First version:** collection counts, completion badges, and passport stamps — all derived from real records, all undoable without leaving rewards behind.

**Deferred:** XP and levels. Add them only if playtesting shows progress feels flat without them.

**Excluded:** in-app currencies, coins, gems, energy systems, and shops. Monetization is undecided, and nothing in the design should depend on it.

## Visual identity and UI

The interface is part of the same world as the map. Map art follows [ART_CONTRACT.md](./docs/art/ART_CONTRACT.md); the interface follows these rules:

- **Two surfaces.** Night-navy for the frame (top bar, tab bar, sheets over the map) and cream parchment for content (cards, challenges, the passport).
- **One gold button** for the main action on a screen. Cream bevelled buttons for everything else; green only for success and progress.
- **One UI pixel = 2 points**, the same as map icons. Borders, bevels, notches, and shadows are whole UI pixels. Frames are nine-slice pixel art generated in the shared palette and drawn with nearest-neighbour sampling.
- **Type.** Pixelify Sans for titles, labels, chips, and numbers, at fixed sizes. Longer text (collectible descriptions, challenge instructions) must stay comfortable to read; whether that is Pixelify Sans or a plainer companion font is decided by testing on a phone.
- **Pixel icons** in the palette, not system symbols. No frosted glass, gradients, or soft glows on game UI.
- **Stepped motion.** Short, frame-like animations (button press, card pop, stamp slam) instead of smooth fades. Respect reduced-motion settings.
- **Never colour alone.** Every status also has a symbol or a number.

**Navigation:** the map is home. A thin top bar shows overall progress. A three-tab bar: **World** (the map), **Quests** (today's featured place and open challenges), **Passport** (stamps, visited places, wishlist, collection). Country and collectible details open as sheets over the map so the camera never resets.

## First playable release

Covers the regions whose capital scenes exist — currently Europe.

Includes:

1. Globe → continent → country → capital journey with continuous camera.
2. The discovery track: country states, landmark and wildlife collectibles, "find it" challenges in capital scenes, and clouds over undiscovered countries that clear as players explore.
3. A daily featured place.
4. The travel track: manual dated visits with undo, wishlist, home country, generated passport stamps, and a My World view of visited countries.
5. Local, versioned persistence and full offline use on native.
6. The pixel UI kit applied to the map overlay, country sheet, challenge, and passport.
7. Game feel: animated scenes (water, smoke, flags, boats, birds, people), chiptune music and sound effects, haptics, and real day/night on the globe and in capitals.

Excludes: accounts, backend, payments and currencies, social features and leaderboards, GPS verification, live online data, AI-generated facts, AR, avatars and characters, cities beyond capitals, food/tradition/history packs, and street-accurate city maps.

**Build order:** prove the gameplay loop on three capitals and playtest it on phones before adding more capitals. Phases and tasks are in [DEVELOPMENT_PLAN.md](./DEVELOPMENT_PLAN.md).

## Long term

Every country and its capital, with increasingly detailed scenes. More challenge types on the same world (spot the animal, map questions), a wildlife field guide, shareable postcards, landmark close-ups, seasonal events, and curated cultural packs. Each addition reuses the same data pipeline and art rules rather than hand-drawing new maps.

## How we avoid drawing the world

[Natural Earth](https://www.naturalearthdata.com/about/terms-of-use/) (public domain) supplies the global base; [OpenStreetMap](https://www.openstreetmap.org/copyright) data is used where finer geography is needed, with attribution. Build-time scripts turn geography into pixel terrain at each scale. Icons, buildings, and capital scenes are generated by the project's own art scripts under the art contract. Every landmark and animal placement records its sources. Human effort goes into art rules, landmark accuracy, and good challenges — not into drawing coastlines.

## What success means

- Someone goes from the globe to a capital and finds their first collectible without explanation.
- A five-minute session with the daily place feels complete; a longer one never runs out of things to find.
- Players who never travel enjoy the app as much as those who do.
- Recording a visit or finding a collectible visibly changes the world, and survives closing the app.
- Pan, pinch, and scene transitions stay smooth on a mid-range phone.
- Everything works offline with no paid API or running server.

## Open decisions

- **Name:** WorldQuest availability.
- **XP and levels:** add or not, after playtesting the first version.
- **Body font:** Pixelify Sans or a companion font for longer text.
- **Daily place selection:** curated schedule or rotation through available content.
- **Monetization:** undecided; must not shape the core design.
