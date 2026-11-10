// Decorative pixel scenery. Coordinates use the unzoomed Earth radius so the
// planet covers distant objects naturally as it fills the screen.
export const spaceShader = `
bool box(float2 p, float2 halfSize) {
  return abs(p.x) <= halfSize.x && abs(p.y) <= halfSize.y;
}

float3 universe(float2 screenPoint, float2 screenSize) {
  float unit = max(1.0,min(screenSize.x,screenSize.y)/230.0);
  float2 point = (floor(screenPoint/unit)+0.5)*unit;
  float2 uv = point/screenSize;
  float3 color = mix(float3(0.015,0.024,0.065),float3(0.025,0.038,0.095),uv.y);
  float nebula = noise(uv*float2(7,5)+9.0);
  color += float3(0.018,0.035,0.075)*smoothstep(0.45,0.85,nebula);

  float2 cell = floor(point/(unit*23.0));
  float2 pixel = floor(mod(point/unit,23.0));
  float seed = hash(cell);
  float2 center = floor(float2(hash(cell+19.0),hash(cell+47.0))*17.0)+3.0;
  float2 distance = abs(pixel-center);
  if (seed > 0.73 && max(distance.x,distance.y) < 0.5) {
    color = mix(float3(0.21,0.35,0.53),float3(0.81,0.91,1.0),hash(cell+71.0));
  }
  if (seed > 0.975) {
    float arms = max(distance.x,distance.y);
    if ((distance.x < 0.5 || distance.y < 0.5) && arms < 3.0)
      color = arms < 1.0 ? float3(1.0,0.96,0.74) : float3(0.91,0.66,0.32);
    else if (distance.x <= 1.0 && distance.y <= 1.0)
      color = float3(0.19,0.25,0.38);
  }

  float base = min(screenSize.x,screenSize.y)*0.41;
  float portrait = step(screenSize.x*1.15,screenSize.y);
  float2 moonCenter = screenSize*0.5 + base*mix(float2(1.55,-0.60),float2(0.88,-1.32),portrait);
  float2 moon = (point-moonCenter)/(base*0.12);
  float moonDistance = dot(moon,moon);
  if (moonDistance < 1.10) {
    color = float3(0.12,0.13,0.24);
    if (moonDistance <= 1.0) {
      float depth = sqrt(max(0.0,1.0-moonDistance));
      float light = clamp(dot(float3(moon.x,-moon.y,depth),normalize(float3(-0.5,0.6,1))),0.0,1.0);
      light = floor(light*5.0)/5.0;
      color = mix(float3(0.34,0.34,0.49),float3(0.91,0.88,0.94),light);
      float crater = min(min(length(moon-float2(-0.32,-0.30))/0.25,
                            length(moon-float2(0.39,0.12))/0.31),
                        min(length(moon-float2(-0.15,0.48))/0.20,
                            length(moon-float2(0.42,-0.57))/0.16));
      if (crater < 1.0) color *= 0.73;
      if (crater > 0.72 && crater < 1.0 && moon.y < 0.35) color += float3(0.12,0.11,0.14);
      if (noise(moon*12.0) > 0.73) color *= 0.88;
    }
  }

  float2 satelliteCenter = screenSize*0.5 + base*mix(float2(-1.55,-0.42),float2(-0.88,-1.20),portrait);
  float2 offset = (point-satelliteCenter)/unit;
  // Rotated, hand-sized pixel silhouette: solar arrays, bus, dish, and antenna.
  float2 satellite = floor(float2(offset.x*0.83-offset.y*0.56,offset.x*0.56+offset.y*0.83));
  float2 panel = float2(abs(satellite.x)-9.0,satellite.y);
  if (box(panel,float2(5,4))) {
    color = float3(0.10,0.16,0.29);
    if (box(panel,float2(4,3))) {
      color = float3(0.13,0.39,0.64);
      if (mod(satellite.x+16.0,3.0) < 1.0 || mod(satellite.y+4.0,3.0) < 1.0)
        color = float3(0.40,0.70,0.85);
    }
  }
  if (box(satellite,float2(6,0.5))) color = float3(0.81,0.74,0.49);
  if (box(satellite,float2(3,4))) {
    color = satellite.x < 1.0 ? float3(0.91,0.92,0.85) : float3(0.47,0.57,0.64);
    if (satellite.y == -2.0) color = float3(0.93,0.73,0.35);
    if (box(satellite-float2(-1,1),float2(1,1))) color = float3(0.20,0.38,0.51);
  }
  if (satellite.x == 0.0 && satellite.y >= -8.0 && satellite.y < -4.0)
    color = float3(0.83,0.87,0.87);
  if (satellite.x == 0.0 && satellite.y == -8.0) color = float3(0.98,0.65,0.34);
  if (length(satellite-float2(5,-5)) < 3.0 && satellite.x+satellite.y < 1.0)
    color = float3(0.74,0.82,0.86);
  return color;
}
`;
