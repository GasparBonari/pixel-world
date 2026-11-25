import lookup from '../../data/board-country-lookup.json';

const BASE64 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
let rows: DataView | undefined;

function decodeRows(encoded: string) {
  // Decode once, on the first country tap. This also works on native JS runtimes without atob.
  const padding = encoded.endsWith('==') ? 2 : encoded.endsWith('=') ? 1 : 0;
  const bytes = new Uint8Array((encoded.length / 4) * 3 - padding);
  let accumulator = 0;
  let bits = 0;
  let index = 0;
  for (let i = 0; i < encoded.length - padding; i++) {
    accumulator = (accumulator << 6) | BASE64.indexOf(encoded[i]);
    bits += 6;
    if (bits >= 8) {
      bits -= 8;
      bytes[index++] = accumulator >>> bits;
    }
  }
  return new DataView(bytes.buffer);
}

/** Read the Natural Earth ID from the same geographic grid as board.png. */
export function boardCountryAt(longitude: number, latitude: number) {
  const { width, height, countryIds } = lookup;
  const longitudeFraction = ((((longitude + 180) % 360) + 360) % 360) / 360;
  const x = Math.floor(longitudeFraction * width);
  const y = Math.min(height - 1, Math.max(0, Math.floor(((90 - latitude) / 180) * height)));

  const data = (rows ??= decodeRows(lookup.rows));
  // The header stores each row's first run, with one extra offset for the final row's end.
  // Every run stores its starting column (uint16) and the board's red channel value (uint8).
  const runBytes = (height + 1) * 2;
  let start = data.getUint16(y * 2, true);
  let end = data.getUint16((y + 1) * 2, true);
  while (end - start > 1) {
    const mid = Math.floor((start + end) / 2);
    if (data.getUint16(runBytes + mid * 3, true) <= x) start = mid;
    else end = mid;
  }
  return countryIds[data.getUint8(runBytes + start * 3 + 2)];
}
