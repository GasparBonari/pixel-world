/** A byte-budgeted LRU. Visible images stay protected until their canvas commit completes. */
export class ImageCache<T> {
  private entries = new Map<string, { value: T; bytes: number }>();
  private bytes = 0;
  readonly budget: number;
  private release: (value: T) => void;

  constructor(budget: number, release: (value: T) => void) {
    this.budget = budget;
    this.release = release;
  }

  get byteLength() {
    return this.bytes;
  }
  get size() {
    return this.entries.size;
  }

  get(key: string): T | undefined {
    const entry = this.entries.get(key);
    if (!entry) return undefined;
    this.entries.delete(key);
    this.entries.set(key, entry);
    return entry.value;
  }

  set(key: string, value: T, bytes: number) {
    const previous = this.entries.get(key);
    if (previous) {
      this.bytes -= previous.bytes;
      if (previous.value !== value) this.release(previous.value);
      this.entries.delete(key);
    }
    this.entries.set(key, { value, bytes });
    this.bytes += bytes;
  }

  trim(protectedKeys: Set<string>) {
    for (const [key, entry] of this.entries) {
      if (this.bytes <= this.budget) break;
      if (protectedKeys.has(key)) continue;
      this.entries.delete(key);
      this.bytes -= entry.bytes;
      this.release(entry.value);
    }
  }

  clear() {
    for (const entry of this.entries.values()) this.release(entry.value);
    this.entries.clear();
    this.bytes = 0;
  }
}
