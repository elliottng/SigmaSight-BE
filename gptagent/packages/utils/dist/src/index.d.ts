export declare function normalizeWeights(ws: number[]): number[];
export declare function concentrationFromWeights(ws: number[]): {
    top1: number;
    top3: number;
    top5: number;
    hhi: number;
    effectiveN: number;
};
