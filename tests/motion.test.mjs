import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import ts from 'typescript';

const source = readFileSync(new URL('../src/features/world/motion.ts', import.meta.url), 'utf8');
const { outputText } = ts.transpileModule(source, {
  compilerOptions: { module: ts.ModuleKind.ES2022, target: ts.ScriptTarget.ES2022 },
});
const MOTION = await import(
  `data:text/javascript;base64,${Buffer.from(outputText).toString('base64')}`
);
const { ANIMATION_FPS, SPIN, animationTime, animationStep, spinSpeed, poseAt, bobAt, phaseAt } = MOTION;

test('the clock ticks in whole animation frames', () => {
  assert.equal(ANIMATION_FPS, 12);
  assert.equal(animationTime(0), 0);
  assert.equal(animationTime(83), 0, 'still the first frame');
  assert.equal(animationTime(84), 1 / 12);
  assert.equal(animationTime(1000), 1);
  // Every frame in a second maps to one of 12 values, so an idle scene redraws 12 times a second.
  const ticks = new Set(Array.from({ length: 60 }, (_, i) => animationTime((i * 1000) / 60)));
  assert.equal(ticks.size, 12);
});

test('clock steps are never negative and a long pause becomes one short step', () => {
  assert.ok(Math.abs(animationStep(1, 1 + 1 / 12) - 1 / 12) < 1e-12);
  assert.equal(animationStep(2, 1), 0);
  assert.equal(animationStep(1, 30), 0.25);
});

test('the planet waits after input, eases into its spin, and stops spinning as the board takes over', () => {
  // Still while the player is active, and for SPIN.idleSeconds after.
  assert.equal(spinSpeed(0, 0), 0);
  assert.equal(spinSpeed(0, SPIN.idleSeconds), 0);
  // Full speed once idle long enough, at planet zoom: one turn in two minutes.
  assert.equal(spinSpeed(0, SPIN.idleSeconds + SPIN.rampSeconds), SPIN.degreesPerSecond);
  assert.equal(360 / SPIN.degreesPerSecond, 120);
  // Eases in: halfway through the ramp is half speed, and speed never decreases while idle.
  assert.equal(spinSpeed(0, SPIN.idleSeconds + SPIN.rampSeconds / 2), SPIN.degreesPerSecond / 2);
  let previous = 0;
  for (let idle = 0; idle <= 10; idle += 0.25) {
    const speed = spinSpeed(0, idle);
    assert.ok(speed >= previous);
    previous = speed;
  }
  // Fades with zoom and is gone from the continent board onwards.
  assert.equal(spinSpeed(SPIN.fullBelowZoom, 60), SPIN.degreesPerSecond);
  assert.ok(spinSpeed(1.0, 60) > 0 && spinSpeed(1.0, 60) < SPIN.degreesPerSecond);
  assert.equal(spinSpeed(SPIN.noneFromZoom, 60), 0);
  assert.equal(spinSpeed(5, 60), 0);
});

test('animals mostly stand still, blink briefly and shift their weight now and then', () => {
  const counts = [0, 0, 0];
  for (let t = 1 / 12; t < 600; t += 1 / 12) counts[poseAt('animal', t, 0.3, 10)]++;
  const total = counts[0] + counts[1] + counts[2];
  assert.ok(counts[0] / total > 0.7, `still ${counts[0] / total}`);
  assert.ok(counts[1] > 0 && counts[1] / total < 0.05, `blinking ${counts[1] / total}`);
  assert.ok(counts[2] / total > 0.1 && counts[2] / total < 0.3, `shifting ${counts[2] / total}`);
  // A blink lasts two frames.
  let longest = 0;
  for (let t = 1 / 12, run = 0; t < 60; t += 1 / 12) {
    run = poseAt('animal', t, 0.3, 10) === 1 ? run + 1 : 0;
    longest = Math.max(longest, run);
  }
  assert.equal(longest, 2);
  // Two animals at different sites do not blink in step.
  const blinks = (phase) => Array.from({ length: 720 }, (_, i) => poseAt('animal', (i + 1) / 12, phase, 0) === 1);
  assert.notDeepEqual(blinks(phaseAt(10, 48)), blinks(phaseAt(11, 47)));
});

test('gusts sweep east: trees further east lean a little later', () => {
  const firstLean = (longitude) => {
    for (let t = 1 / 12; t < 14; t += 1 / 12) if (poseAt('sway', t, 0, longitude) === 1) return t;
    return Infinity;
  };
  // Starting just after a gust has passed 0 degrees, it reaches 10 and 20 degrees east in turn.
  const at0 = firstLean(0), at10 = firstLean(10), at20 = firstLean(20);
  assert.ok(at0 < at10 && at10 < at20, `${at0} ${at10} ${at20}`);
  assert.ok(Math.abs(at20 - at10 - 7 * (10 / 40)) < 0.2, 'the gust moves 40 degrees in 7 seconds');
});

test('windmills turn, ash puffs, wings flap and boats bob; reduce motion keeps every still frame', () => {
  assert.deepEqual([0, 1, 2, 3].map((i) => poseAt('turn', 1 / 12 + i / 3, 0, 0)), [0, 1, 2, 0]);
  assert.deepEqual([0, 1, 2].map((i) => poseAt('smoke', 0.1 + i / 1.5, 0, 0)), [0, 1, 2]);
  assert.deepEqual([0, 1].map((i) => poseAt('flap', 0.01 + i / 4, 0, 0)), [0, 1]);
  assert.deepEqual([0.1, 0.9].map((t) => bobAt(t, 0)), [0, 1]);
  for (const motion of ['animal', 'sway', 'turn', 'smoke', 'flap']) assert.equal(poseAt(motion, 0, 0.5, 0), 0);
  assert.equal(bobAt(0, 0.9), 0);
  for (const [lon, lat] of [[0, 0], [10.5, 48.2], [-120, -33]]) {
    const phase = phaseAt(lon, lat);
    assert.ok(phase >= 0 && phase < 1);
  }
});

test('on opening, the planet eases into its spin at once instead of waiting', () => {
  const { OPENING_INPUT } = MOTION;
  // The clock starts at 0 when the planet appears; the opening counts as input OPENING_INPUT ago.
  assert.ok(spinSpeed(0, 1 / 12 - OPENING_INPUT) > 0, 'already turning on the first ticks');
  assert.equal(spinSpeed(0, SPIN.rampSeconds - OPENING_INPUT), SPIN.degreesPerSecond, 'full speed after the ease-in');
  // After a real touch it still waits.
  assert.equal(spinSpeed(0, 1), 0);
});

test('capital pennants flutter and chimneys smoke only while the clock runs', () => {
  assert.deepEqual([0, 1, 2, 3].map((i) => poseAt('flutter', 0.01 + i / 3, 0, 0)), [0, 1, 2, 0]);
  const smoke = Array.from({ length: 30 }, (_, i) => poseAt('chimney', (i + 1) / 12, 0.4, 0));
  assert.ok(smoke.every((pose) => pose >= 1 && pose <= 3), 'always a wisp while animating');
  assert.equal(new Set(smoke).size, 3);
  assert.equal(poseAt('flutter', 0, 0.4, 0), 0);
  assert.equal(poseAt('chimney', 0, 0.4, 0), 0, 'reduce motion: no smoke');
});
