// Guards for the pixel UI kit rules in docs/ui/UI_KIT.md. If one fails, fix the code, not the test.
import assert from 'node:assert/strict';
import { readFileSync, readdirSync, statSync } from 'node:fs';
import test from 'node:test';
import ts from 'typescript';

const root = new URL('../', import.meta.url);
const read = (path) => readFileSync(new URL(path, root), 'utf8');

const { outputText } = ts.transpileModule(read('src/constants/theme.ts'), {
  compilerOptions: { module: ts.ModuleKind.ES2022, target: ts.ScriptTarget.ES2022 },
});
const theme = await import(`data:text/javascript;base64,${Buffer.from(outputText).toString('base64')}`);

function filesUnder(dir) {
  return readdirSync(new URL(dir, root)).flatMap((name) => {
    const path = `${dir}/${name}`;
    if (statSync(new URL(path, root)).isDirectory()) return filesUnder(path);
    return /\.tsx?$/.test(name) && !name.endsWith('.generated.ts') ? [path] : [];
  });
}

// Interface code: routes, the kit, and every feature folder, including new ones. Only the map
// renderer and the art style study are art code (they follow ART_CONTRACT.md instead); interface
// files inside them are listed explicitly.
const ART_FEATURES = new Set(['world', 'style-study']);
const UI_FILES = [
  ...filesUnder('src/app'),
  ...filesUnder('src/ui'),
  ...readdirSync(new URL('src/features', root))
    .filter((name) => !ART_FEATURES.has(name))
    .flatMap((name) => filesUnder(`src/features/${name}`)),
  'src/features/world/MapStatus.tsx',
];

test('every token size is a whole number of UI pixels', () => {
  const sizes = { ...theme.Space, ...theme.Size };
  delete sizes.buttonDepth; // counted in UI pixels already
  delete sizes.panelDepth;
  for (const [name, value] of Object.entries(sizes)) {
    assert.equal(value % theme.U, 0, `${name} = ${value} is not a multiple of U (${theme.U})`);
  }
});

test('the type scale uses only Pixelify Sans', () => {
  const fonts = new Set(Object.values(theme.PixelFonts));
  for (const [name, style] of Object.entries(theme.Type)) {
    assert.ok(fonts.has(style.fontFamily), `${name} uses ${style.fontFamily}`);
  }
});

test('interface code takes colours, fonts, and sizes from the tokens', () => {
  const rules = [
    [/['"]#[0-9a-fA-F]{3,8}['"]/, 'a hex colour (use Palette)'],
    [/\brgba?\(/, 'an rgb() colour (use Palette)'],
    [/\bfontFamily\s*:/, 'fontFamily (use PixelText)'],
    [/\bfontSize\s*:/, 'fontSize (use the Type scale via PixelText)'],
    [/\bfontWeight\s*:(?!\s*['"]normal['"])/, 'a synthetic fontWeight (use the bold font file)'],
    [/\bborderRadius\b/, 'borderRadius (pixel corners are notched by PixelFrame)'],
    [/\b(shadowRadius|elevation)\s*:/, 'a soft shadow (use a PixelFrame lip)'],
    [/LinearGradient|expo-blur|expo-glass-effect|BlurView/, 'a gradient or blur (not in the pixel style)'],
    [/from ['"]expo-symbols['"]|@expo\/vector-icons/, 'system icons (use PixelIcon)'],
  ];
  const problems = [];
  for (const file of UI_FILES) {
    const lines = read(file).split('\n');
    lines.forEach((line, i) => {
      if (/^\s*(\/\/|\*)/.test(line)) return;
      for (const [pattern, what] of rules) {
        if (pattern.test(line)) problems.push(`${file}:${i + 1} uses ${what}`);
      }
    });
  }
  assert.deepEqual(problems, []);
});

test('route files stay thin and outside the kit', () => {
  for (const file of filesUnder('src/app')) {
    assert.ok(!/StyleSheet\.create/.test(read(file)) || file.endsWith('_layout.tsx'), `${file} defines styles; move the screen into src/features/`);
  }
});

function pngSize(path) {
  const bytes = readFileSync(new URL(path, root));
  return [bytes.readUInt32BE(16), bytes.readUInt32BE(20)];
}

test('every UI icon has sharp files for each screen density', () => {
  const names = [...read('src/ui/icons.generated.ts').matchAll(/^ {2}(\w+): require/gm)].map((m) => m[1]);
  assert.ok(names.length >= 10, 'icon map is empty');
  for (const name of names) {
    for (const [suffix, scale] of [['', 2], ['@2x', 4], ['@3x', 6]]) {
      const [w, h] = pngSize(`assets/ui/icons/${name}${suffix}.png`);
      assert.deepEqual([w, h], [12 * scale, 12 * scale], `${name}${suffix}.png`);
    }
  }
});

test('every kit export is documented in UI_KIT.md, so agents know it exists', () => {
  const index = read('src/ui/index.ts');
  const doc = read('docs/ui/UI_KIT.md');
  const names = [...index.matchAll(/export \{([^}]*)\}/g)]
    .flatMap((m) => m[1].split(','))
    .map((name) => name.trim())
    .filter((name) => name && !name.startsWith('type '));
  const missing = names.filter((name) => !doc.includes(`\`${name}\``));
  assert.deepEqual(missing, [], 'add these to the Components table in docs/ui/UI_KIT.md');
});
