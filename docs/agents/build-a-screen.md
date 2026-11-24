# Recipe: build a screen or sheet

For any interface task (country sheet, challenge card, Quests tab, Passport...). Read [UI_KIT.md](../ui/UI_KIT.md) first; this is the step-by-step version.

## 1. Pin down the task

- Find the task ID in [DEVELOPMENT_PLAN.md](../../DEVELOPMENT_PLAN.md) (e.g. P5-03). Read that task and its phase's dependencies only.
- Check the "Product guardrails" in [AGENTS.md](../../AGENTS.md) (from [PROJECT_VISION.md](../../PROJECT_VISION.md)): if the screen needs XP, currencies, an avatar, or multiple-choice trivia, stop and ask.
- Find the closest reference in `docs/ui/reference/` for the look, and the matching "Screen recipe" in UI_KIT.md for the structure.

## 2. Put files in the right place

```
src/app/<route>.tsx                 # 3–6 lines: import and render the view. No styles.
src/features/<feature>/<Name>View.tsx  # the screen: layout from @/ui components
src/features/<feature>/<logic>.ts   # pure logic (selectors, derivations) — testable with node --test
```

Sheets over the map are components in `src/features/<feature>/`, rendered by the world screen, not routes; the map must stay mounted.

## 3. Compose from the kit

Every screen is a `Screen`; details over the map are a `BottomSheet` in its `overlay`:

```tsx
import { useState } from 'react';

import { BottomSheet, PixelButton, ProgressBar, Screen, SectionHeader, TabBar, TopBar } from '@/ui';

export function WorldTab({ country, found, total, onExplore }: Props) {
  const [expanded, setExpanded] = useState(false);
  return (
    <Screen
      background="none"
      scroll={false}
      header={<TopBar><ProgressBar title="Europe discovered" value={...} total={...} tone="light" /></TopBar>}
      footer={<TabBar … />}
      overlay={
        country && (
          <BottomSheet
            title={country.name}
            subtitle={`${country.continent} · Capital: ${country.capital}`}
            icon="pin"
            expanded={expanded}
            onExpandedChange={setExpanded}
            onClose={…}
            action={<PixelButton variant="primary" label={`Explore ${country.capital}`} onPress={onExplore} block />}>
            <ProgressBar title="Country progress" value={found} total={total} tone="light" />
            <SectionHeader title="Landmarks" icon="landmark" count={`${found} / ${total} found`} tone="light" />
            {/* CollectibleTile row */}
          </BottomSheet>
        )
      }>
      {/* the map */}
    </Screen>
  );
}
```

Finding something opens `<PixelModal><CollectibleCard justFound … /></PixelModal>`. Reversible actions show `useNotice()` with an Undo action; only irreversible ones use `ConfirmDialog`.

Allowed in a screen's `StyleSheet`: layout (`flex*`, `gap`, `padding`/`margin` from `Space`/`px`, `width`/`height` from `Size`/`px`, `position`, `alignItems`...) and `backgroundColor: Palette.*`. Everything visual beyond that belongs in a kit component.

## 4. Data and honesty

- Counts come from the content catalog and saved records (P5-02, P5-07). Until they exist, take them as props; never hard-code numbers in a real screen.
- A country with no content shows "Coming soon" (`ProgressBar` does this for `total = 0`), never "complete".
- Facts shown on cards come from the catalog with their source, never written inline in a component.

## 5. Accessibility

- Every pressable is at least 48 pt (`Size.touch`) and has a role and label (kit components do this).
- Icon-only buttons: `IconButton` with `accessibilityLabel`.
- Status = icon or number + colour, never colour alone.
- Animations: stepped, and skipped when `useReducedMotion()` is true.

## 6. Verify

```bash
npm run lint && npm run typecheck && npm test
npm run web    # open the route at 390×844 (Chrome device toolbar, iPhone 12/13/14 size)
```

Look for: text overflowing frames, a second gold button, panels covering more than half the map, tap targets under 48 pt, and light text on parchment or ink text on navy.

## 7. Report

Update the task's checkbox and note in DEVELOPMENT_PLAN.md: what you built, what you verified, and what you did not (physical phones, Safari, screen readers). If you added a kit component, add it to UI_KIT.md's table and `/ui-kit`.
