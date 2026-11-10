import { spaceShader } from './space-shader';

/** Zoom range over which the daytime globe becomes the night-sea game board (ART_CONTRACT.md). */
export const BOARD_ZOOM_START = 1.5;
export const BOARD_ZOOM_END = 2.5;
/** Terrain pixel size in points: 3 on a 390-point-wide phone. */
export const CELLS_ACROSS = 130;

// Geographic masks preserve the real coastlines. Surface colors, relief, cloud
// systems, and space scenery are illustrative, deterministic pixel artwork.
export const globeShader = `
uniform shader geography;
uniform shader board;
uniform shader boardSmooth;
uniform float2 viewport;
uniform float2 angles;
uniform float radius;
uniform float zoom;
uniform float2 textureSize;
uniform float2 boardSize;

const float3 EDGE_LIGHT = float3(0.659,0.867,0.922);
const float3 COAST_BAND = float3(0.180,0.427,0.686);
const float3 SEA_BAND = float3(0.145,0.341,0.604);
const float3 NIGHT_BAND = float3(0.114,0.259,0.447);
const float3 NIGHT = float3(0.086,0.196,0.353);
const float3 SPARKLE = float3(0.624,0.765,0.910);
const float3 LAND_HI = float3(0.725,0.867,0.388);
const float3 CLIFF_TOP = float3(0.373,0.541,0.173);
const float3 CLIFF = float3(0.255,0.400,0.165);
const float3 GRASS = float3(0.541,0.761,0.251);
const float3 GRASS_DARK = float3(0.455,0.675,0.239);
const float3 GRASS_LIGHT = float3(0.639,0.812,0.306);
const float3 FOREST = float3(0.373,0.659,0.235);
const float3 BOREAL = float3(0.435,0.659,0.271);
const float3 TUNDRA = float3(0.663,0.761,0.494);
const float3 DRY = float3(0.706,0.765,0.353);
const float3 SAND = float3(0.820,0.702,0.388);
const float3 DUNE = float3(0.749,0.604,0.314);
const float3 SNOW = float3(0.957,0.965,0.933);
const float3 BORDER = float3(0.933,0.961,0.784);
const float3 RELIEF = float3(0.651,0.659,0.384);

float hash(float2 p) { return fract(sin(dot(p,float2(127.1,311.7)))*43758.5453); }
float noise(float2 p) {
  float2 cell = floor(p), f = fract(p);
  f = f*f*(3.0-2.0*f);
  return mix(mix(hash(cell),hash(cell+float2(1,0)),f.x),mix(hash(cell+float2(0,1)),hash(cell+float2(1,1)),f.x),f.y);
}

${spaceShader}

float surfaceNoise(float2 coordinate, float2 scale, float2 offset) {
  float2 wrapped = float2(fract(coordinate.x),coordinate.y);
  float2 point = wrapped*scale+offset;
  float value = noise(point);
  // Blend the longitude seam so rotating across the date line stays continuous.
  if (wrapped.x > 0.90)
    value = mix(value,noise(point-float2(scale.x,0)),smoothstep(0.90,1.0,wrapped.x));
  return value;
}

float cloudField(float2 uv) {
  float2 wind = float2(uv.x+sin(uv.y*28.0)*0.018,uv.y);
  return surfaceNoise(wind,float2(18,28),float2(6,3))*0.80 + surfaceNoise(wind,float2(55,70),float2(0))*0.20;
}

// Screen point -> (u, v, z) on the sphere; z < 0 means off the planet.
float3 surface(float2 q) {
  float2 p = (q-viewport*0.5)/radius;
  p.y = -p.y;
  float d = dot(p,p);
  if (d > 1.0) return float3(0.0,0.0,-1.0);
  float z = sqrt(1.0-d);
  float latitude = asin(clamp(p.y*cos(angles.y)+z*sin(angles.y),-1.0,1.0));
  float longitude = angles.x+atan(p.x,z*cos(angles.y)-p.y*sin(angles.y));
  return float3(fract(longitude/6.28318530718+0.5),clamp(0.5-latitude/3.14159265359,0.0,0.99999),z);
}

// Lakes count as water, so they get the same pale edge and raised banks as the sea.
float landAt(float3 s) {
  if (s.z < 0.0) return 0.0;
  float3 g = geography.eval(s.xy*textureSize).rgb;
  return step(0.5,g.r)*(1.0-step(0.5,g.b));
}

float countryAt(float3 s) {
  if (s.z < 0.0) return 0.0;
  return floor(board.eval(s.xy*boardSize).r*255.0+0.5);
}

float3 tone(float3 c, float amount) {
  return amount > 0.0 ? mix(c,float3(1.0),amount) : mix(c,float3(0.0),-amount);
}

// Continent-scale "game board" colour for one terrain pixel (ART_CONTRACT.md, sections 2 and 4).
float3 boardColor(float2 point, float cell, float3 here, float lon, float lat, float terrain, float desertWeight) {
  float kmPerCell = 6371.0*cell/radius;
  // World-anchored hash cells, quantised per zoom octave so specks and sparkles stay put while panning.
  float perDegree = exp2(floor(log2(111.2/kmPerCell)));
  float2 worldCell = floor(float2(lon,lat)*perDegree);
  float3 up = surface(point-float2(0.0,cell));
  float3 up2 = surface(point-float2(0.0,2.0*cell));
  float3 left = surface(point-float2(cell,0.0));
  float3 right = surface(point+float2(cell,0.0));
  float3 down = surface(point+float2(0.0,cell));
  float isLand = landAt(here);
  float landUp = landAt(up), landLeft = landAt(left), landRight = landAt(right), landDown = landAt(down);

  if (isLand < 0.5) {
    if (landUp > 0.5) return CLIFF_TOP;
    if (landAt(up2) > 0.5) return CLIFF;
    if (landLeft + landRight + landDown > 0.5) return EDGE_LIGHT;
    float cells = boardSmooth.eval(here.xy*boardSize).g*255.0*3.0/kmPerCell;
    if (cells >= 6.0 && hash(worldCell) < 0.004) return SPARKLE;
    if (cells <= 3.0) return COAST_BAND;
    if (cells <= 6.0) return SEA_BAND;
    if (cells <= 11.0) return NIGHT_BAND;
    return NIGHT;
  }

  float id = countryAt(here);
  // Finer noise (~0.25 degrees) roughens climate edges, so they never read as straight lines.
  float detail = surfaceNoise(here.xy,float2(1400,900),float2(3.0));
  float band = abs(lat)+(terrain-0.5)*5.0+(detail-0.5)*2.0;
  float3 c = GRASS;
  if (band > 57.0) c = BOREAL;
  if (band > 67.0) c = TUNDRA;
  if (band > 76.0) c = SNOW;
  float wobble = (detail-0.5)*3.0;
  if (lon > -10.0+wobble && lon < 42.0+wobble && lat > 33.0 && lat < 40.5+(terrain-0.5)*4.0+wobble*0.6) c = DRY;
  bool sandy = desertWeight+(terrain-0.5)*0.25+(detail-0.5)*0.35 > 0.5;
  if (sandy) c = fract(lon*0.8+lat*1.7+terrain*2.0) < 0.12 ? DUNE : SAND;
  // Puzzle-map tone: each country slightly lighter or darker.
  c = tone(c,(hash(float2(id,7.0))-0.5)*0.16);
  bool green = band <= 67.0 && !sandy;
  float speck = hash(worldCell+17.0);
  if (green && terrain > 0.62) c = FOREST;
  else if (green && speck < 0.0125) c = GRASS_LIGHT;
  else if (green && speck < 0.025) c = GRASS_DARK;
  float ranges = board.eval(here.xy*boardSize).b;
  if (ranges > 0.1) c = mix(c,RELIEF,ranges > 0.8 ? 0.4 : 0.25);
  // Pale 1-pixel borders between countries, never on a coast.
  if (id > 0.5 && landRight > 0.5 && countryAt(right) > 0.5 && countryAt(right) != id) c = BORDER;
  if (id > 0.5 && landDown > 0.5 && countryAt(down) > 0.5 && countryAt(down) != id) c = BORDER;
  // Lit top and left coasts.
  if (landUp < 0.5 || landLeft < 0.5) c = LAND_HI;
  return c;
}

half4 main(float2 position) {
  float cell = max(1.25,min(viewport.x,viewport.y)/${CELLS_ACROSS.toFixed(1)});
  float2 point = (floor(position/cell)+0.5)*cell;
  float2 p = (point-viewport*0.5)/radius;
  p.y = -p.y;
  float d = dot(p,p);
  if (d > 1.0) {
    float3 space = universe(position,viewport);
    float glow = floor(pow(1.0-smoothstep(1.0,1.20,d),2.0)*6.0)/6.0;
    space = mix(space,float3(0.09,0.32,0.66),glow*0.48);
    float rim = 1.0-smoothstep(1.0,1.035,d);
    return half4(mix(space,float3(0.38,0.77,0.97),rim*0.85),1);
  }

  float3 here = surface(point);
  float2 uv = here.xy;
  float z = here.z;
  float3 data = geography.eval(uv*textureSize).rgb;
  float degrees = 90.0-uv.y*180.0;
  float lonDegrees = (uv.x-0.5)*360.0;

  float terrain = surfaceNoise(uv,float2(140,90),float2(0));
  float grain = surfaceNoise(uv,float2(460,280),float2(0));
  float forest = smoothstep(0.42,0.76,terrain);
  float3 land = mix(float3(0.54,0.76,0.25),float3(0.20,0.48,0.25),floor(forest*4.0)/4.0);
  land *= 0.94+floor(grain*4.0)*0.025;
  // Broad illustrative climate zones, not measured vegetation or elevation.
  float sahara = 1.0-smoothstep(0.55,1.0,length(float2((lonDegrees-15.0)/36.0,(degrees-24.0)/11.0)));
  float arabia = 1.0-smoothstep(0.45,1.0,length(float2((lonDegrees-46.0)/14.0,(degrees-24.0)/14.0)));
  float australia = 1.0-smoothstep(0.40,1.0,length(float2((lonDegrees-133.0)/23.0,(degrees+25.0)/13.0)));
  float desert = floor(max(max(sahara,arabia),australia)*4.0)/4.0;
  float3 sand = mix(float3(0.82,0.70,0.39),float3(0.92,0.81,0.52),floor(terrain*3.0)/3.0);
  land = mix(land,sand,desert);
  if (abs(degrees) > 69.0+terrain*6.0)
    land = mix(float3(0.74,0.87,0.79),float3(0.94,0.98,0.88),floor(grain*3.0)/3.0);

  float oceanTone = floor((terrain*0.7+grain*0.3)*5.0)/5.0;
  float3 ocean = mix(float3(0.09,0.27,0.60),float3(0.16,0.45,0.75),oceanTone);
  float wave = step(0.85,surfaceNoise(uv,float2(85,420),float2(0)));
  ocean = mix(ocean,float3(0.32,0.63,0.84),wave*0.32);

  float isLand = step(0.5,data.r);
  float coastTexels = max(1.0,9.0/exp2(zoom));
  float2 texel = uv*textureSize;
  float east = geography.eval(texel+float2(coastTexels,0)).r;
  float west = geography.eval(texel-float2(coastTexels,0)).r;
  float north = geography.eval(texel+float2(0,coastTexels)).r;
  float south = geography.eval(texel-float2(0,coastTexels)).r;
  float shoreWater = (1.0-isLand)*max(max(east,west),max(north,south));
  float shoreLand = isLand*(1.0-min(min(east,west),min(north,south)));
  ocean = mix(ocean,float3(0.25,0.66,0.77),shoreWater*0.80);
  land = mix(land,float3(0.79,0.84,0.43),shoreLand*0.55);
  float3 color = mix(ocean,land,isLand);
  color = mix(color,ocean,step(0.5,data.b));
  float border = data.g*smoothstep(0.5,1.4,zoom);
  color = mix(color,float3(0.25,0.39,0.26),border*0.65);

  float cloudFade = 1.0-smoothstep(0.5,1.8,zoom);
  float clouds = cloudField(uv);
  float shadow = step(0.68,cloudField(uv+float2(0.003,0.004)))*cloudFade;
  color = mix(color,color*float3(0.61,0.69,0.78),shadow*0.55);
  float cover = step(0.68,clouds)*cloudFade;
  float3 cloudColor = clouds > 0.76 ? float3(0.98,1.0,0.96) : float3(0.79,0.89,0.93);
  color = mix(color,cloudColor,cover);

  // Zooming in: the daytime sea darkens into the night sea and the land becomes the game board.
  float boardMix = smoothstep(${BOARD_ZOOM_START.toFixed(2)},${BOARD_ZOOM_END.toFixed(2)},zoom);
  if (boardMix > 0.001)
    color = mix(color,boardColor(point,cell,here,lonDegrees,degrees,terrain,desert),boardMix);

  float light = dot(float3(p,z),normalize(float3(-0.35,0.55,1.0)));
  float shade = clamp(floor((0.45+light*0.55)*8.0)/8.0,0.35,1.0);
  color = mix(float3(0.08,0.13,0.26),color,mix(shade,1.0,boardMix));
  if (z < 0.16) color = mix(color,float3(0.38,0.74,0.94),0.58*(1.0-boardMix));
  return half4(color,1);
}
`;
