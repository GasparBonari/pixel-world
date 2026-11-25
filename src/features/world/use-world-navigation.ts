import { useCallback, useRef, useState } from 'react';
import { useAnimatedReaction, type SharedValue } from 'react-native-reanimated';
import { scheduleOnRN } from 'react-native-worklets';

import {
  getSelectableCountry,
  getWorldTier,
  selectCountryAtTap,
} from '../country-sheet/country-selection';
import { boardCountryAt } from './board-country-lookup';
import {
  activeCapital,
  CAPITAL_ZOOM,
  COUNTRY_ZOOM,
  globeLocation,
  type GlobeCamera,
  type GlobeViewport,
} from './globe-camera';
import { BOARD_ZOOM_END } from './globe-shader';
import capitals from '../../data/capitals.json';

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
      const key = `${Math.floor(current.longitude / 5)}:${Math.floor(current.latitude / 5)}:${Math.floor(current.zoom * 10)}:${capitalId ?? ''}`;
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

  function explore() {
    if (!selection) return;
    const current = camera.get();
    if (getWorldTier(current) !== 'country') return;
    const { id, longitude, latitude } = selection.capital;
    touch();
    countryCamera.current = current;
    camera.set({ longitude, latitude, zoom: CAPITAL_ZOOM.full, capitalId: id });
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
    }
  }

  return {
    snapshot, selection, capitalName, clearSelection, selectAt, reset, explore,
    back: tier !== 'overview' ? back : undefined,
  };
}
