import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import ts from 'typescript';

const source = readFileSync(new URL('../src/features/world/motion.ts', import.meta.url), 'utf8');
const { outputText } = ts.transpileModule(source, {
  compilerOptions: { module: ts.ModuleKind.ES2022, target: ts.ScriptTarget.ES2022 },
});
const { ANIMATION_FPS, SPIN, animationTime, animationStep, spinSpeed } = await import(
  `data:text/javascript;base64,${Buffer.from(outputText).toString('base64')}`
);

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
