import { describe, it, expect } from "vitest";
import { concentrationFromWeights, normalizeWeights } from "../src/index.js";

describe("concentration", () => {
  it("equal weight 5 => effectiveN~5", () => {
    const r = concentrationFromWeights([20,20,20,20,20]);
    expect(Math.round(r.effectiveN)).toBe(5);
    expect(r.top1).toBeCloseTo(0.2, 5);
    expect(r.top3).toBeCloseTo(0.6, 5);
  });
  it("concentrated => small effectiveN", () => {
    const r = concentrationFromWeights([60,10,10,10,10]);
    expect(r.effectiveN).toBeLessThan(3);
    expect(r.top1).toBeCloseTo(0.6, 5);
  });
});
