export function normalizeWeights(ws) {
    const finite = ws.filter((x) => Number.isFinite(x) && x >= 0);
    const sum = finite.reduce((a, b) => a + b, 0);
    if (sum === 0)
        return finite;
    // If looks like 0-100, scale
    if (sum > 1.5)
        return finite.map(x => x / 100);
    // If already normalized or arbitrary, normalize to 1
    return finite.map(x => x / sum);
}
export function concentrationFromWeights(ws) {
    const w = normalizeWeights(ws);
    const sorted = [...w].sort((a, b) => b - a);
    const top1 = sorted[0] ?? 0;
    const top3 = sorted.slice(0, 3).reduce((a, b) => a + b, 0);
    const top5 = sorted.slice(0, 5).reduce((a, b) => a + b, 0);
    const hhi = w.reduce((a, b) => a + b * b, 0);
    const effectiveN = hhi > 0 ? 1 / hhi : 0;
    return { top1, top3, top5, hhi, effectiveN };
}
