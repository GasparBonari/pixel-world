import { COUNTRY_ZOOM } from './globe-camera';
import { spaceShader } from './space-shader';

/** Zoom range over which the globe becomes the night-sea game board (ART_CONTRACT.md). */
export const BOARD_ZOOM_START = 1.5;
export const BOARD_ZOOM_END = 2.5;
export const CONTINENT_ZOOM_START = 2;
/** Terrain pixel size in points: 3 on a 390-point-wide phone. */
export const CELLS_ACROSS = 130;

// Geographic masks preserve the real coastlines. Surface colors, relief, cloud
// systems, and space scenery are illustrative, deterministic pixel artwork.
export const globeShader = `
uniform shader geography;
uniform shader board;
uniform shader boardSmooth;
// Ocean depth (assets/world/depth.png), filtered: 0 shelf, then deeper than 200/1000/2000/4000 m.
uniform shader seabed;
uniform shader cityLights;
uniform float2 viewport;
uniform float2 angles;
uniform float radius;
uniform float zoom;
uniform float selectedCountry;
// Seconds in whole animation frames (motion.ts); 0 keeps the scene still (reduce motion).
uniform float time;
uniform float3 sun;
uniform float2 textureSize;
uniform float2 boardSize;
uniform float2 seabedSize;

const float3 EDGE_LIGHT = float3(0.659,0.867,0.922);
const float3 COAST_BAND = float3(0.180,0.427,0.686);
const float3 SEA_BAND = float3(0.145,0.341,0.604);
const float3 NIGHT_BAND = float3(0.114,0.259,0.447);
const float3 NIGHT = float3(0.086,0.196,0.353);
const float3 NIGHT_DEEP = float3(0.067,0.161,0.302);
const float3 WAVE = float3(0.157,0.376,0.651);
// Shallow coasts by climate (ART_CONTRACT.md section 2): teal in temperate seas, turquoise in the
// tropics, for the coastal ring's inner (coast) and outer (sea) band and for open shelf water.
const float3 COAST_TEAL = float3(0.165,0.525,0.659);
const float3 COAST_TROPIC = float3(0.184,0.690,0.722);
const float3 SEA_TEAL = float3(0.137,0.431,0.600);
const float3 SEA_TROPIC = float3(0.137,0.569,0.624);
const float3 SHELF = float3(0.133,0.314,0.541);
const float3 SHELF_TROPIC = float3(0.118,0.416,0.561);
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
const float3 SELECTION_EDGE = float3(1.0,0.81,0.32);

// Arithmetic hash ("hash without sine", after Dave Hoskins). A sin-based hash loses precision on
// large inputs, by a different amount on each GPU: at country zoom, world cells number in the
// thousands and it turned sea glints and grass specks into dense vertical streaks on real GPUs,
// while software rendering looked fine. This one gives the same values everywhere.
float hash(float2 p) {
  float3 q = fract(float3(p.xyx)*0.1031);
  q += dot(q,q.yzx+33.33);
  return fract((q.x+q.y)*q.z);
}
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
  float2 wind = float2(uv.x+sin(uv.y*42.0)*0.012,uv.y);
  return surfaceNoise(wind,float2(21,30),float2(6,3))*0.72 + surfaceNoise(wind,float2(63,85),float2(0))*0.28;
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
    // Glints twinkle, each lit for 40% of its own 3-second cycle; the same number shows at once as
    // the fixed set a still scene keeps.
    float glint = hash(worldCell);
    if (cells >= 6.0 && (time > 0.0 ? glint < 0.005 && fract(time*0.33+hash(worldCell+3.0)) < 0.4 : glint < 0.002))
      return SPARKLE;
    // Surf: broken lines of foam roll in from 3.5 cells out to the shore every 3 seconds, out of
    // step along the coast.
    if (time > 0.0 && cells <= 3.5) {
      float swell = 3.5*(1.0-fract(time/3.0+surfaceNoise(here.xy,float2(90,60),float2(5.0))*2.0));
      if (abs(cells-swell) < 0.5 && hash(worldCell+9.0) < 0.6) return mix(COAST_BAND,EDGE_LIGHT,0.7);
    }
    // The coastal ring follows the shore loosely: each edge wanders up to about a pixel either way
    // along the coast, and a world-anchored checkerboard dithers it so neighbouring tones blend.
    float checker = mod(worldCell.x+worldCell.y,2.0)-0.5;
    float ring = cells+(surfaceNoise(here.xy,float2(260,170),float2(11.0))-0.5)*2.4+checker*0.7;
    // Real depth: 0 on the continental shelf up to 4 beyond 4000 m, contours wandering and
    // dithered the same way. Shallow water is tinted by climate: turquoise in the tropics, teal in
    // temperate seas, the plain blues towards the poles.
    float sea = seabed.eval(here.xy*seabedSize).r*4.0+(surfaceNoise(here.xy,float2(520,340),float2(7.0))-0.5)*0.5+checker*0.3;
    bool shelf = sea < 0.5;
    float warmth = 1.0-smoothstep(23.0,47.0,abs(lat))+checker*0.12;
    bool tropic = shelf && warmth > 0.62;
    bool temperate = shelf && !tropic && warmth > 0.25;
    if (ring <= 3.0) return tropic ? COAST_TROPIC : temperate ? COAST_TEAL : COAST_BAND;
    if (ring <= 6.0) return tropic ? SEA_TROPIC : temperate ? SEA_TEAL : SEA_BAND;
    // Wave crests over open water: in a fifth of the blocks of 9x6 wave cells, a small crest (two
    // pixels on top, one either side below) that rolls a pixel east and back; now and then its top
    // glints. Wave cells scale longitude by latitude, so a cell is never narrower than a screen pixel.
    float2 waveCell = floor(float2(lon*cos(radians(lat)),lat)*perDegree);
    float2 block = floor(waveCell/float2(9.0,6.0));
    if (ring > 11.0 && hash(block+31.0) < 0.2) {
      float roll = time > 0.0 ? mod(floor(time*1.2+hash(block+5.0)*2.0),2.0) : 0.0;
      float2 crest = waveCell-block*float2(9.0,6.0)-float2(1.0+floor(hash(block+13.0)*4.0)+roll,1.0+floor(hash(block+17.0)*3.0));
      bool top = crest.y == 1.0 && (crest.x == 1.0 || crest.x == 2.0);
      if (top || (crest.y == 0.0 && (crest.x == 0.0 || crest.x == 3.0)))
        return top && time > 0.0 && fract(time*0.5+hash(block+7.0)) < 0.12 ? SPARKLE : shelf ? SEA_BAND : WAVE;
    }
    // Beyond the ring: shelf water stays light, the continental slope (200-1000 m) and a step out
    // from steep coasts are mid-blue, the deep sea is night blue, and beyond 4000 m darker still.
    if (shelf) return tropic ? SHELF_TROPIC : SHELF;
    if (ring <= 9.0 || sea < 1.5) return NIGHT_BAND;
    return sea < 3.5 ? NIGHT : NIGHT_DEEP;
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
  bool green = band <= 67.0 && !sandy;
  float speck = hash(worldCell+17.0);
  if (green && terrain > 0.56) c = mix(c,FOREST,terrain > 0.68 ? 0.82 : 0.48);
  else if (green && speck < 0.0125) c = GRASS_LIGHT;
  else if (green && speck < 0.025) c = GRASS_DARK;
  // Step the ground tones before applying the shared tint, so forests also belong to their country.
  c = tone(c,(floor(detail*4.0)/3.0-0.5)*0.10+(hash(float2(id,7.0))-0.5)*0.22);
  float ranges = board.eval(here.xy*boardSize).b;
  if (ranges > 0.1) c = mix(c,RELIEF,(ranges > 0.8 ? 0.45 : 0.25)+step(0.56,detail)*0.15);

  // Close-up fields are decorative. Grid variation stays in world coordinates as the camera pans.
  float countryDetail = smoothstep(${COUNTRY_ZOOM.in},${COUNTRY_ZOOM.full},zoom);
  if (countryDetail > 0.0 && green) {
    float2 field = float2(lon*cos(radians(lat)),lat)*7.0;
    float2 plot = floor(field+(detail-0.5)*0.45);
    float crop = hash(plot+53.0);
    float hedge = step(0.86,fract(field.x))*step(0.55,crop);
    float shade = crop < 0.34 ? -0.13 : crop > 0.70 ? 0.12 : 0.0;
    c = tone(c,(shade-hedge*0.07)*countryDetail*(1.0-ranges*0.7));
  }

  bool selected = selectedCountry > 0.0 && id == selectedCountry && zoom < ${COUNTRY_ZOOM.max};
  float rightId = landRight > 0.5 ? countryAt(right) : 0.0;
  float downId = landDown > 0.5 ? countryAt(down) : 0.0;
  if (selected) {
    // Use the same board index as tap hit testing. Keep the accent on land, including islands.
    if (min(min(landUp,landDown),min(landLeft,landRight)) < 0.5 ||
        countryAt(up) != id || countryAt(left) != id || rightId != id || downId != id)
      return SELECTION_EDGE;
    c = mix(c,SELECTION_EDGE,0.13);
  }
  // Pale 1-pixel borders between countries, never on a coast.
  if (id > 0.5 && ((rightId > 0.5 && rightId != id) || (downId > 0.5 && downId != id))) c = BORDER;
  // Lit top and left coasts.
  if (landUp < 0.5 || landLeft < 0.5) c = LAND_HI;
  return c;
}

// Brief curtains in both polar regions. Integer longitude harmonics meet at the date line.
float3 polarAurora(float3 color, float longitude, float latitude, float night, float planet) {
  if (time <= 0.0 || abs(latitude) < 58.0 || abs(latitude) > 80.0 || night == 0.0) return color;
  float age = mod(time+(latitude < 0.0 ? 13.0 : 0.0),28.0);
  if (age < 1.0 || age > 9.0) return color;
  float envelope = smoothstep(1.0,3.0,age)*(1.0-smoothstep(6.0,9.0,age));
  float angle = radians(longitude);
  float folds = sin(angle*9.0-age*1.4);
  float base = 64.0+3.2*sin(angle*4.0+age*0.55)+1.5*folds;
  float height = abs(latitude)-base;
  float curtain = step(0.0,height)*(1.0-smoothstep(1.0,6.5+folds*2.0,height));
  float streaks = 0.65+0.35*sin(angle*29.0+folds*2.0);
  float brightness = floor(curtain*streaks*envelope*night*5.0+0.5)/5.0;
  float3 glow = height < 2.0 ? float3(0.35,0.94,0.65) : float3(0.21,0.63,0.69);
  return mix(color,glow,brightness*planet*0.78);
}

half4 main(float2 position) {
  float cell = max(1.25,min(viewport.x,viewport.y)/${CELLS_ACROSS.toFixed(1)});
  float2 point = (floor(position/cell)+0.5)*cell;
  float2 p = (point-viewport*0.5)/radius;
  p.y = -p.y;
  float d = dot(p,p);
  float planet = 1.0-smoothstep(0.6,${BOARD_ZOOM_START.toFixed(2)},zoom);
  if (d > 1.0) {
    float3 space = universe(position,viewport);
    float glow = floor((1.0-smoothstep(1.025,1.24,d))*4.0)/4.0;
    float atmosphere = 1.0;
    if (planet > 0.0 && d < 1.24) {
      float limbLight = smoothstep(-0.30,0.10,dot(p/sqrt(d),sun.xy));
      atmosphere = mix(1.0,0.35+limbLight*0.65,planet);
    }
    space = mix(space,float3(0.07,0.37,0.82),glow*0.64*atmosphere);
    float rim = 1.0-smoothstep(1.0,1.035,d);
    space = mix(space,float3(0.43,0.89,1.0),rim*0.96*atmosphere);
    return half4(space,1);
  }

  float3 here = surface(point);
  float2 uv = here.xy;
  float z = here.z;
  float3 data = geography.eval(uv*textureSize).rgb;
  float degrees = 90.0-uv.y*180.0;
  float lonDegrees = (uv.x-0.5)*360.0;

  float terrain = surfaceNoise(uv,float2(140,90),float2(0));
  float grain = surfaceNoise(uv,float2(460,280),float2(0));
  float forest = smoothstep(0.32,0.74,terrain);
  float3 land = mix(float3(0.65,0.84,0.26),float3(0.14,0.52,0.25),floor(forest*5.0)/5.0);
  land *= 0.96+floor(grain*4.0)*0.024;
  // Broad illustrative climate zones, not measured vegetation or elevation.
  float sahara = 1.0-smoothstep(0.55,1.0,length(float2((lonDegrees-15.0)/36.0,(degrees-24.0)/11.0)));
  float arabia = 1.0-smoothstep(0.45,1.0,length(float2((lonDegrees-46.0)/14.0,(degrees-24.0)/14.0)));
  float australia = 1.0-smoothstep(0.40,1.0,length(float2((lonDegrees-133.0)/23.0,(degrees+25.0)/13.0)));
  float desert = floor(max(max(sahara,arabia),australia)*4.0)/4.0;
  float3 sand = mix(float3(0.82,0.55,0.26),float3(1.0,0.87,0.56),floor(terrain*4.0)/4.0);
  land = mix(land,sand,desert);
  if (abs(degrees) > 69.0+terrain*6.0)
    land = mix(float3(0.61,0.80,0.94),float3(0.99,1.0,0.97),floor(grain*4.0)/4.0);

  float oceanTone = floor((terrain*0.7+grain*0.3)*5.0)/5.0;
  float3 ocean = mix(float3(0.035,0.19,0.47),float3(0.07,0.47,0.80),oceanTone);
  // Real depth from space: shelves a step lighter (turquoise over tropical banks), the abyss a
  // step darker.
  float seaDepth = seabed.eval(uv*seabedSize).r*4.0;
  float warmSea = 1.0-smoothstep(23.0,40.0,abs(degrees));
  if (seaDepth < 0.5) ocean = mix(ocean,mix(float3(0.16,0.58,0.84),float3(0.20,0.78,0.78),floor(warmSea*2.0)/2.0),0.58);
  else if (seaDepth > 3.5) ocean *= 0.86;
  // Wave highlights drift slowly east (one noise cell, about 4 degrees, every 30 s).
  float wave = step(0.78,surfaceNoise(uv-float2(time/2700.0,0),float2(65,240),float2(0)));
  ocean = mix(ocean,float3(0.21,0.64,0.88),wave*0.42);

  float isLand = step(0.5,data.r);
  float coastTexels = max(1.0,9.0/exp2(zoom));
  float2 texel = uv*textureSize;
  float east = geography.eval(texel+float2(coastTexels,0)).r;
  float west = geography.eval(texel-float2(coastTexels,0)).r;
  float north = geography.eval(texel+float2(0,coastTexels)).r;
  float south = geography.eval(texel-float2(0,coastTexels)).r;
  float shoreWater = (1.0-isLand)*max(max(east,west),max(north,south));
  float shoreLand = isLand*(1.0-min(min(east,west),min(north,south)));
  ocean = mix(ocean,float3(0.36,0.79,0.84),shoreWater*0.92);
  land = mix(land,float3(0.86,0.94,0.41),shoreLand*0.64);
  float3 color = mix(ocean,land,isLand);
  color = mix(color,ocean,step(0.5,data.b));
  float border = data.g*smoothstep(0.5,1.4,zoom);
  color = mix(color,float3(0.25,0.39,0.26),border*0.65);

  float cloudFade = 1.0-smoothstep(0.5,1.8,zoom);
  // Weather drifts east over the surface: once round the planet in 15 minutes.
  float cover = 0.0;
  if (cloudFade > 0.0) {
    float2 weather = uv-float2(time/900.0,0);
    float clouds = cloudField(weather);
    float upper = cloudField(weather+float2(0.003,0.005));
    float shadow = step(0.71,upper)*cloudFade;
    color = mix(color,color*float3(0.50,0.65,0.82),shadow*0.6);
    cover = step(0.71,clouds)*cloudFade;
    float3 cloudColor = float3(0.54,0.73,0.93);
    if (upper < 0.71 || clouds > 0.78) cloudColor = float3(0.81,0.91,0.99);
    if (upper < 0.68 || clouds > 0.83) cloudColor = float3(1.0,0.99,0.95);
    color = mix(color,cloudColor,cover);
  }

  // Zooming in: the sea darkens into the night sea and the land becomes the game board.
  float boardMix = smoothstep(${BOARD_ZOOM_START.toFixed(2)},${BOARD_ZOOM_END.toFixed(2)},zoom);
  boardMix *= 2.0-boardMix;
  if (boardMix > 0.001)
    color = mix(color,boardColor(point,cell,here,lonDegrees,degrees,terrain,desert),boardMix);

  float light = dot(float3(p,z),normalize(float3(-0.35,0.55,1.0)));
  float shade = clamp(floor((0.50+light*0.57)*8.0)/8.0,0.35,1.0);
  color = mix(float3(0.08,0.13,0.26),color,mix(shade,1.0,boardMix));
  if (z < 0.16) color = mix(color,float3(0.38,0.74,0.94),0.58*(1.0-boardMix));

  if (planet > 0.0) {
    float sunlight = dot(float3(p,z),sun);
    float night = 1.0-smoothstep(-0.32,0.10,sunlight);
    night = floor(night*5.0+0.5)/5.0;
    float dusk = step(-0.16,sunlight)*(1.0-step(0.08,sunlight));
    color = mix(color,color*float3(1.0,0.76,0.69),dusk*planet*0.48);
    float3 nightColor = color*float3(0.27,0.39,0.59)+float3(0.018,0.024,0.046);
    color = mix(color,nightColor,night*planet);
    if (night > 0.0 && isLand > 0.0 && data.b < 0.5) {
      float lights = cityLights.eval(uv*float2(512,256)).r;
      float glow = floor(lights*5.0+0.5)/5.0;
      color = mix(color,float3(1.0,0.77,0.40),glow*night*planet*(1.0-cover*0.86));
    }
    color = polarAurora(color,lonDegrees,degrees,night,planet);
  }
  return half4(color,1);
}
`;
