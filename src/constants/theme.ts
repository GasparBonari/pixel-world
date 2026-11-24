/**
 * Game UI tokens: the only place the interface defines colours, sizes, and type.
 * Rules and usage: docs/ui/UI_KIT.md. Pure data (no React Native imports) so tests can read it.
 *
 * One UI pixel (U) = 2 points, the same as a map-icon pixel. Every size, border, gap, and
 * offset in the interface is a whole number of UI pixels: write `px(3)`, never `6`.
 */

/** Points per UI pixel. */
export const U = 2;

/** A length of `n` whole UI pixels, in points. */
export const px = (n: number) => n * U;

/**
 * The palette. Hues match the map art (scripts/art/phase3_mockups.py `P`, scripts/art/sprites.py),
 * so panels, buttons, and the world belong to one picture.
 */
export const Palette = {
  // Night-navy frame: top bar, tab bar, sheets over the map. Continuous with the night sea.
  space: '#090D16',
  /** The night sea (ART_CONTRACT §2): screen background behind panels. */
  night: '#16325A',
  navyDeep: '#0D1830',
  navy: '#142443',
  navyRaised: '#1D3360',
  navyEdge: '#3A5A94',
  navyInk: '#05080F',

  // Cream parchment: content (cards, challenges, the passport).
  parchment: '#F3DFB4',
  parchmentLight: '#FFF3D6',
  parchmentShadow: '#C9A36B',
  parchmentEdge: '#6B4426',
  cream: '#FFF6E2',
  creamShade: '#E2CB9F',

  // Gold: the one main action on a screen, and highlights.
  goldLight: '#FFE58A',
  gold: '#F6C443',
  goldShade: '#C98A1E',
  goldDeep: '#8A5A12',

  // Green: success and progress only.
  greenLight: '#9BD04A',
  green: '#62AC3C',
  greenShade: '#3E7F34',
  greenInk: '#22472A',

  // Red: map pins and alerts.
  redLight: '#FF8E8E',
  red: '#E8404A',
  redShade: '#A82634',
  redInk: '#4A1A20',

  // Text.
  ink: '#3A2318',
  inkSoft: '#7A5A3E',
  snow: '#F4F6EE',
  mist: '#A9B8D6',
  muted: '#6B7488',

  chip: '#FFFDF5',
  /** Hard drop shadow under frames: an offset silhouette, never a blur. */
  shadow: 'rgba(5, 8, 15, 0.45)',
  /** Dims the world behind dialogs. */
  scrim: 'rgba(5, 8, 15, 0.6)',
} as const;

export type PaletteColor = keyof typeof Palette;

/**
 * Frame skins for PixelFrame. Each is drawn as: outline (1 U, notched corners), fill,
 * a 1 U highlight along the inside top edge, a 1 U shade along the inside bottom edge,
 * and an optional lip (the button's thickness) under it.
 */
export const Frames = {
  parchment: {
    outline: Palette.parchmentEdge,
    fill: Palette.parchment,
    highlight: Palette.parchmentLight,
    shade: Palette.parchmentShadow,
    lip: Palette.shadow,
  },
  navy: {
    outline: Palette.navyInk,
    fill: Palette.navy,
    highlight: Palette.navyEdge,
    shade: Palette.navyDeep,
    lip: Palette.shadow,
  },
  gold: {
    outline: Palette.ink,
    fill: Palette.gold,
    highlight: Palette.goldLight,
    shade: Palette.goldShade,
    lip: Palette.goldDeep,
  },
  cream: {
    outline: Palette.parchmentEdge,
    fill: Palette.cream,
    highlight: '#FFFFFF',
    shade: Palette.creamShade,
    lip: Palette.parchmentShadow,
  },
  green: {
    outline: Palette.greenInk,
    fill: Palette.green,
    highlight: Palette.greenLight,
    shade: Palette.greenShade,
    lip: Palette.greenInk,
  },
  chip: {
    outline: Palette.ink,
    fill: Palette.chip,
    highlight: Palette.chip,
    shade: Palette.creamShade,
    lip: Palette.shadow,
  },
  /** Destructive confirmations only ("Reset progress"). */
  red: {
    outline: Palette.redInk,
    fill: Palette.red,
    highlight: Palette.redLight,
    shade: Palette.redShade,
    lip: Palette.redInk,
  },
  track: {
    outline: Palette.navyInk,
    fill: Palette.navyDeep,
    highlight: Palette.navyDeep,
    shade: Palette.navyDeep,
    lip: Palette.shadow,
  },
} as const;

export type FrameSkin = keyof typeof Frames;

/** Gaps and padding, in whole UI pixels. */
export const Space = {
  xs: px(2),
  sm: px(4),
  md: px(6),
  lg: px(8),
  xl: px(12),
  xxl: px(16),
} as const;

/** Layout sizes. */
export const Size = {
  /** Smallest tappable height or width (24 U = 48 pt). */
  touch: px(24),
  icon: px(12),
  /** Lip under raised buttons, in UI pixels. Pressing removes it. */
  buttonDepth: 2,
  panelDepth: 1,
  maxContentWidth: px(240),
} as const;

/** Stepped motion: animations advance in whole frames on the world clock's rate, never eased. */
export const Motion = {
  /** One animation frame at 12 frames per second. */
  frameMs: 83,
  /** How long a notice stays: plain, and with an action such as Undo. */
  noticeMs: 4000,
  noticeWithActionMs: 6000,
  /** Sheets and dialogs never cover more than this share of the screen height. */
  sheetMaxShare: 0.5,
} as const;

/** Pixelify Sans (OFL 1.1), loaded once by the root layout. Font names, not CSS stacks. */
export const PixelFonts = {
  regular: 'PixelifySans_400Regular',
  bold: 'PixelifySans_700Bold',
} as const;

/** The fixed type scale. Never set fontSize anywhere else. */
export const Type = {
  display: { fontFamily: PixelFonts.bold, fontSize: 32, lineHeight: 36 },
  title: { fontFamily: PixelFonts.bold, fontSize: 24, lineHeight: 28 },
  heading: { fontFamily: PixelFonts.bold, fontSize: 20, lineHeight: 24 },
  label: { fontFamily: PixelFonts.bold, fontSize: 16, lineHeight: 20 },
  body: { fontFamily: PixelFonts.regular, fontSize: 16, lineHeight: 22 },
  caption: { fontFamily: PixelFonts.regular, fontSize: 12, lineHeight: 16 },
} as const;

export type TypeVariant = keyof typeof Type;

/** The world scene behind everything. */
export const WorldColors = {
  space: Palette.space,
} as const;
