import { useCallback, useRef, useState } from 'react';
import { useAnimatedReaction, type SharedValue } from 'react-native-reanimated';
import { scheduleOnRN } from 'react-native-worklets';

import {
  getSelectableCountry,
  getWorldTier,
  selectCountryAtTap,
  type SelectableCountry,
} from '../country-sheet/country-selection';
import { boardContinentAt, boardCountryAt } from './board-country-lookup';
import labels from '../../data/country-labels.json';
import {
  activeCapital,
  CAPITAL_ZOOM,
  COUNTRY_ZOOM,
  globeLocation,
  type GlobeCamera,
  type GlobeViewport,
} from './globe-camera';
import { BOARD_ZOOM_END, CONTINENT_ZOOM_START } from './globe-shader';
import capitals from '../../data/capitals.json';

const labelsById = new Map(labels.map((label) => [label.id, label]));

export function useWorldNavigation(
  camera: SharedValue<GlobeCamera>,
  openingCamera: GlobeCamera,
  viewport: GlobeViewport,
  touch: () => void
) {
  const [snapshot, setSnapshot] = useState(openingCamera);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const countryCamera = useRef<GlobeCamera | undefined>(undefined);
  const clearSelection = useCallback(() => setSelectedId(null), []);

  const updateSnapshot = useCallback((next: GlobeCamera, leftCapital: boolean) => {
    setSnapshot(next);
    if (next.zoom < COUNTRY_ZOOM.in) clearSelection();
    if (leftCapital) countryCamera.current = undefined;
  }, [clearSelection]);

  useAnimatedReaction(
    () => {
      const current = camera.get();
      const capitalId = activeCapital(current)?.id;
      // A country-scale viewport can be narrower than five degrees. Sample it more closely so
      // panning across a border also updates the title.
      const regional = !capitalId && current.zoom >= CONTINENT_ZOOM_START;
      const degrees = regional ? (current.zoom >= COUNTRY_ZOOM.in ? 0.25 : 1) : 5;
      const key = `${Math.floor(current.longitude / degrees)}:${Math.floor(current.latitude / degrees)}:${Math.floor(current.zoom * 10)}:${capitalId ?? ''}`;
      return { key, capitalId };
    },
    (next, previous) => {
      if (next.key !== previous?.key) {
        scheduleOnRN(updateSnapshot, camera.get(), !!previous?.capitalId && !next.capitalId);
      }
    }
  );

  const selectAt = useCallback((x: number, y: number, current: GlobeCamera) => {
    if (getWorldTier(current) !== 'country') return;
    const point = globeLocation(x, y, current, viewport);
    const hitId = point ? boardCountryAt(point.longitude, point.latitude) : null;
    setSelectedId((id) => selectCountryAtTap(id, current, hitId));
  }, [viewport]);

  function reset() {
    touch();
    clearSelection();
    countryCamera.current = undefined;
    camera.set(openingCamera);
  }

  const tier = getWorldTier(snapshot);
  const selection = tier === 'country' && selectedId ? getSelectableCountry(selectedId) : undefined;
  const active = activeCapital(snapshot);
  const capitalName = active && capitals.find((scene) => scene.id === active.id)?.name;
  const regional = !active && snapshot.zoom >= CONTINENT_ZOOM_START;
  const centerId = regional ? boardCountryAt(snapshot.longitude, snapshot.latitude) : null;
  const center = centerId ? labelsById.get(centerId) : undefined;
  const preferredCapitalId = selection?.capital.id ?? (tier === 'country' && centerId
    ? getSelectableCountry(centerId)?.capital.id : undefined);
  let regionalTitle: string | undefined;
  if (regional && tier === 'country') regionalTitle = center?.name ?? 'Country map';
  else if (regional) {
    const continent = boardContinentAt(snapshot.longitude, snapshot.latitude) ?? center?.continent;
    regionalTitle = continent === 'Australia' ? 'Oceania' : continent ?? 'Continent map';
  }

  function focusCapital({ id, longitude, latitude }: Pick<SelectableCountry['capital'], 'id' | 'longitude' | 'latitude'>) {
    const current = camera.get();
    if (getWorldTier(current) !== 'country') return;
    touch();
    countryCamera.current = current;
    camera.set({ longitude, latitude, zoom: CAPITAL_ZOOM.full, capitalId: id });
  }

  function explore() {
    if (selection) focusCapital(selection.capital);
  }

  function back() {
    const current = camera.get();
    const capital = activeCapital(current);
    touch();
    if (capital) {
      camera.set(countryCamera.current ?? {
        longitude: capital.longitude,
        latitude: capital.latitude,
        zoom: COUNTRY_ZOOM.full,
      });
      countryCamera.current = undefined;
    } else if (getWorldTier(current) === 'country') {
      clearSelection();
      camera.set({ longitude: current.longitude, latitude: current.latitude, zoom: BOARD_ZOOM_END });
    } else if (current.zoom >= CONTINENT_ZOOM_START) {
      camera.set({ longitude: current.longitude, latitude: current.latitude, zoom: 0 });
    }
  }

  return {
    snapshot, selection, capitalName, regionalTitle, preferredCapitalId, clearSelection, selectAt, reset, explore, focusCapital,
    back: tier !== 'overview' || regional ? back : undefined,
    backLabel: active ? 'Back to country' : tier === 'country' ? 'Back to continent' : 'Back to Earth',
  };
}
