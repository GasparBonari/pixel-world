/** Session progress. P5-07 can hydrate and save these records behind the same interface. */
export function createLandmarkProgress() {
  let records: ReadonlyMap<string, Date> = new Map();
  const listeners = new Set<() => void>();

  return {
    getSnapshot: () => records,
    subscribe(listener: () => void) {
      listeners.add(listener);
      return () => { listeners.delete(listener); };
    },
    markFound(id: string, date: Date) {
      if (records.has(id)) return;
      records = new Map(records).set(id, date);
      for (const listener of listeners) listener();
    },
  };
}

export const landmarkProgress = createLandmarkProgress();
