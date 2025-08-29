import { z } from "zod";
export const FactorExposure = z.object({
    name: z.string(),
    exposure: z.number()
});
export const ScenarioItem = z.object({
    name: z.string(),
    pnl_pct: z.number()
});
export const MachineReadable = z.object({
    snapshot: z.object({
        total_value: z.number().optional(),
        long: z.number().optional(),
        short: z.number().optional(),
        gross: z.number().optional(),
        net: z.number().optional(),
        invested_pct: z.number().optional()
    }).strict(),
    concentration: z.object({
        top1: z.number().optional(),
        top3: z.number().optional(),
        top5: z.number().optional(),
        hhi: z.number().optional(),
        effective_n: z.number().optional()
    }).strict(),
    factors: z.array(FactorExposure).optional(),
    scenarios: z.object({
        best: z.array(ScenarioItem).optional(),
        worst: z.array(ScenarioItem).optional()
    }).strict().optional(),
    gaps: z.array(z.string()).optional(),
    actions: z.array(z.string()).optional()
}).strict();
export const AgentResponse = z.object({
    summary_markdown: z.string(),
    machine_readable: MachineReadable
}).strict();
export const AnalyzeBody = z.object({
    portfolio_report: z.unknown().optional(),
    positions_table_csv: z.string().optional().nullable(),
    price_history: z.unknown().optional().nullable(),
    factor_history: z.unknown().optional().nullable()
}).strict();
