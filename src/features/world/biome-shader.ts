// Soft geographic art regions, not measured land-cover or elevation data.
export const biomeShader = `
float3 tintRegion(float3 color, float2 location, float2 center, float2 extent, float3 tint) {
  float2 offset = (location-center)/extent;
  float weight = 1.0-smoothstep(0.18,1.0,dot(offset,offset));
  return mix(color,tint,weight*0.72);
}

float3 continentTerrain(float3 original, float2 location, float terrain, float grain) {
  float lon = location.x, lat = location.y;
  float3 color = mix(original,float3(0.55,0.72,0.33),0.20);
  if (lon > -30.0 && lon < 55.0 && lat > 34.0) {
    color = tintRegion(color,location,float2(18,62),float2(32,14),float3(0.32,0.55,0.39));
    color = tintRegion(color,location,float2(15,49),float2(28,10),float3(0.61,0.75,0.37));
    color = tintRegion(color,location,float2(12,38),float2(25,7),float3(0.74,0.76,0.39));
  }
  if (lon > -20.0 && lon < 55.0 && lat < 36.0 && lat > -36.0) {
    color = tintRegion(color,location,float2(15,24),float2(37,13),float3(0.87,0.74,0.47));
    color = tintRegion(color,location,float2(20,-2),float2(22,13),float3(0.27,0.56,0.34));
    color = tintRegion(color,location,float2(32,-15),float2(19,24),float3(0.72,0.70,0.36));
  }
  if (lon > 45.0 && lat > -10.0) {
    color = tintRegion(color,location,float2(100,61),float2(67,15),float3(0.34,0.53,0.40));
    color = tintRegion(color,location,float2(93,44),float2(34,12),float3(0.74,0.72,0.42));
    color = tintRegion(color,location,float2(105,29),float2(18,12),float3(0.45,0.68,0.40));
    color = tintRegion(color,location,float2(102,10),float2(25,19),float3(0.27,0.59,0.38));
  }
  if (lon < -32.0 && lat > 7.0) {
    color = tintRegion(color,location,float2(-110,57),float2(49,17),float3(0.33,0.56,0.40));
    color = tintRegion(color,location,float2(-101,41),float2(22,15),float3(0.74,0.76,0.42));
    color = tintRegion(color,location,float2(-111,29),float2(18,13),float3(0.83,0.68,0.44));
  }
  if (lon < -32.0 && lat < 13.0 && lat > -60.0) {
    color = tintRegion(color,location,float2(-64,-7),float2(24,17),float3(0.28,0.59,0.32));
    color = tintRegion(color,location,float2(-73,-21),float2(7,31),float3(0.62,0.64,0.43));
    color = tintRegion(color,location,float2(-63,-38),float2(16,19),float3(0.65,0.72,0.47));
  }
  if (lon > 110.0 && lat < -10.0) {
    color = tintRegion(color,location,float2(132,-25),float2(22,14),float3(0.83,0.57,0.36));
    color = tintRegion(color,location,float2(149,-29),float2(11,18),float3(0.53,0.67,0.42));
    color = tintRegion(color,location,float2(173,-41),float2(7,11),float3(0.32,0.61,0.43));
  }
  if (lat < -60.0) return mix(float3(0.75,0.87,0.88),float3(0.95,0.97,0.89),floor(terrain*4.0)/4.0);
  return color*(0.97+floor(grain*3.0)*0.015);
}
`;
