This is an Expo/React Native mobile application. Prioritize mobile-first patterns, performance, and cross-platform compatibility.

**WorldQuest** (working title; repo `pixel-world`) turns the real planet into a pixel-art adventure: spin a pixel Earth, zoom through continents and countries into illustrated capital scenes, and collect landmarks, wildlife, and landscapes. These instructions apply to every coding agent (Codex, Claude) and to humans.

## Start here

Read in this order before your first task. Do not read the large documents end to end.

1. [PROJECT_VISION.md](./PROJECT_VISION.md): what we build and what we deliberately do not build. It is short; read it all.
2. [DEVELOPMENT_PLAN.md](./DEVELOPMENT_PLAN.md): read "Phases and order", then only the phase and task ID you are working on. Phase 4 is about 1,200 lines of capital fact sheets; skip it unless your task is a capital.
3. [docs/ui/UI_KIT.md](./docs/ui/UI_KIT.md): **required before any interface work.**
4. [docs/art/ART_CONTRACT.md](./docs/art/ART_CONTRACT.md): required before map, sprite, or scene art work.
5. [docs/agents/](./docs/agents/): step-by-step recipes for common tasks: [build-a-screen.md](./docs/agents/build-a-screen.md), [add-a-capital.md](./docs/agents/add-a-capital.md).

## Project map

| Path | What lives there |
| --- | --- |
| `src/app/` | Expo Router routes only. Thin files that render a view from `src/features/` |
| `src/features/world/` | The map: Skia globe, continent board, country tier, capital scenes, motion. Art code, follows ART_CONTRACT |
| `src/features/<feature>/` | One folder per feature (country sheet, quests, passport...): its views, hooks, and logic |
| `src/ui/` | **The pixel UI kit.** Every interface element is built from these |
| `src/constants/theme.ts` | **The only place** colours, spacing, sizes, and type are defined |
| `src/data/` | Generated data (capitals, map icons, labels). Do not hand-edit files marked "Generated" |
| `assets/world/`, `assets/ui/` | Generated images. Rebuild with their scripts, never edit by hand |
| `scripts/geography/`, `scripts/art/` | Python build scripts for geography, sprites, capitals, UI icons (use `.venv/bin/python`) |
| `tests/*.test.mjs` | `node --test` suites, including `ui-kit.test.mjs`, which enforces the UI rules |

## Product guardrails

From PROJECT_VISION.md. If a task, mockup, or request conflicts with these, stop and ask the owner. Do not build it quietly.

- **The map is the main attraction.** The interface appears in context (sheets, chips, markers) and gets out of the way. No dashboards over the world.
- **Real geography.** Never invent named places, facts, or coordinates. Every landmark, animal, and fact needs a source.
- **Honest progress.** Counts always show a real denominator and come from saved records. Discovering is never confused with visiting. No placeholder statistics in real screens.
- **Not in the first release:** currencies, coins, gems, shops, energy, XP and levels (deferred to the playtest), avatars, accounts, backend, social features, leaderboards, runtime AI-generated facts, and multiple-choice trivia (challenges are "find it" and map taps).
- **€0 to run:** offline, local persistence, no paid APIs, no server.
- **Gameplay before more capitals:** new capitals stay paused until the Phase 5 playtest gate (P5-08) passes.

## Interface rules (summary of docs/ui/UI_KIT.md)

- Every screen is a `Screen`; details over the map are a `BottomSheet` in its `overlay`, so the map stays mounted. Reversible actions show an Undo notice (`useNotice`); only irreversible ones ask with `ConfirmDialog`.
- Build screens only from `@/ui` components and `@/constants/theme` tokens. Missing a component? Add it to `src/ui/` and `/ui-kit`; never style a one-off in a screen.
- No hex/rgb colours, `fontSize`, `fontFamily`, or `fontWeight` outside `theme.ts`. No `borderRadius`, blur, gradients, glass, soft shadows, or `elevation`.
- One UI pixel = 2 pt: sizes are `px(n)`, spacing is `Space.*`.
- Exactly one gold `primary` button per screen. Green only for success or progress. Never colour alone: pair every state with an icon or number.
- Pixel icons from `PixelIcon` only (no `expo-symbols`, vector icons, or emoji).
- Check UI_KIT.md's Roadmap before a task: if a part you need is listed as missing, build it in the kit first.
- Motion is stepped and honours reduce motion.
- `npm test` fails if these are broken. Fix the code, not the test.

## Expo has changed — do not trust your training data

Expo ships breaking changes every SDK release. APIs you remember are likely renamed, moved, or removed. Before writing any code that touches an Expo, EAS, or React Native API:

1. Read the major version of the `expo` package in `package.json` (currently **SDK 58**).
2. Fetch the matching versioned docs: `https://docs.expo.dev/versions/v<major>.0.0/`
3. For anything else, fetch https://docs.expo.dev/llms.txt — an index of all Expo docs with corrections to common LLM misconceptions. Follow its links to the specific page you need; never answer from memory.

## Commands

This project uses **npm** (`package-lock.json`).

```bash
npx expo install <package>  # ALWAYS use instead of npm/yarn/pnpm/bun add — resolves SDK-compatible versions
npm start                   # dev server (npm run web for the browser)
npm run lint                # lint
npm run typecheck           # typecheck
npm test                    # logic tests + UI rule guards
npx expo-doctor             # diagnose dependency and config issues
npx expo install --fix      # fix incompatible package versions
.venv/bin/python scripts/art/build_ui_icons.py   # rebuild UI icons
```

Useful URLs on web: `/ui-kit` (every UI component), `/?lon=-9.14&lat=38.72&zoom=7` (deep link to a camera view, here Lisbon).

## Definition of done

A task is done only when all of these hold:

1. `npm run lint`, `npm run typecheck`, and `npm test` pass. Paste the summary lines in your report.
2. UI changes are looked at on web at 390×844 (phone portrait), and new components appear in `/ui-kit`.
3. The task's checkbox in DEVELOPMENT_PLAN.md is updated with a short, factual note: what changed, what was verified, and what was *not* verified (for example "not yet checked on a physical phone"). Say plainly what you did not check.
4. Docs that describe the changed behaviour are updated (UI_KIT.md, ART_CONTRACT.md, README.md).
5. One task per commit, with a short lowercase message in the repo's style (e.g. `country sheet added`). Commit only when the owner asks.

## Navigation & Routing

- Use **Expo Router** for all navigation. Routes live in `src/app/` — every file there is a screen, `_layout.tsx` files define navigators. Keep non-route code (components, hooks, utils) outside `src/app/`.
- Import `Link`, `router`, and `useLocalSearchParams` from `expo-router`.
- The map stays mounted across navigation; details open as sheets over it so the camera never resets.
- Tabs (P7-01): custom tab bar via `expo-router/ui`; see UI_KIT.md "Navigation".
- Docs: https://docs.expo.dev/router/introduction.md

## Building with EAS

Use EAS to build, sign, and submit the app in the cloud (`eas build`, `eas submit`) and to ship over-the-air updates (`eas update`) — no local Xcode or Android Studio required. Run EAS CLI as `npx eas-cli@latest <command>`; substitute that for bare `eas` in docs examples.
Docs: https://docs.expo.dev/eas/index.md

## Rules

- If `ios/` and `android/` directories do not exist, they are generated (Continuous Native Generation). Never create or edit them by hand — configure native behavior in `app.json` and config plugins.
- Expo Go only includes its bundled native modules. After adding a library with native code, the app needs a development build: `npx expo run:ios|android` locally, or `eas build --profile development`.
- Prefer recommended Expo modules over third-party libraries, and check your available skills before adding dependencies. Install a dependency only when a feature uses it. Docs: https://docs.expo.dev/versions/latest/index.md
- Generated files (headers say "Generated by ...") are rebuilt by their script, never edited by hand.
- Record the source and license of every new asset, dataset, or font (see `assets/world/manifest.json`).
