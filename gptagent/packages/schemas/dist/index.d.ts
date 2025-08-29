import { z } from "zod";
export declare const FactorExposure: z.ZodObject<{
    name: z.ZodString;
    exposure: z.ZodNumber;
}, "strip", z.ZodTypeAny, {
    name: string;
    exposure: number;
}, {
    name: string;
    exposure: number;
}>;
export declare const ScenarioItem: z.ZodObject<{
    name: z.ZodString;
    pnl_pct: z.ZodNumber;
}, "strip", z.ZodTypeAny, {
    name: string;
    pnl_pct: number;
}, {
    name: string;
    pnl_pct: number;
}>;
export declare const MachineReadable: z.ZodObject<{
    snapshot: z.ZodObject<{
        total_value: z.ZodOptional<z.ZodNumber>;
        long: z.ZodOptional<z.ZodNumber>;
        short: z.ZodOptional<z.ZodNumber>;
        gross: z.ZodOptional<z.ZodNumber>;
        net: z.ZodOptional<z.ZodNumber>;
        invested_pct: z.ZodOptional<z.ZodNumber>;
    }, "strict", z.ZodTypeAny, {
        total_value?: number | undefined;
        long?: number | undefined;
        short?: number | undefined;
        gross?: number | undefined;
        net?: number | undefined;
        invested_pct?: number | undefined;
    }, {
        total_value?: number | undefined;
        long?: number | undefined;
        short?: number | undefined;
        gross?: number | undefined;
        net?: number | undefined;
        invested_pct?: number | undefined;
    }>;
    concentration: z.ZodObject<{
        top1: z.ZodOptional<z.ZodNumber>;
        top3: z.ZodOptional<z.ZodNumber>;
        top5: z.ZodOptional<z.ZodNumber>;
        hhi: z.ZodOptional<z.ZodNumber>;
        effective_n: z.ZodOptional<z.ZodNumber>;
    }, "strict", z.ZodTypeAny, {
        top1?: number | undefined;
        top3?: number | undefined;
        top5?: number | undefined;
        hhi?: number | undefined;
        effective_n?: number | undefined;
    }, {
        top1?: number | undefined;
        top3?: number | undefined;
        top5?: number | undefined;
        hhi?: number | undefined;
        effective_n?: number | undefined;
    }>;
    factors: z.ZodOptional<z.ZodArray<z.ZodObject<{
        name: z.ZodString;
        exposure: z.ZodNumber;
    }, "strip", z.ZodTypeAny, {
        name: string;
        exposure: number;
    }, {
        name: string;
        exposure: number;
    }>, "many">>;
    scenarios: z.ZodOptional<z.ZodObject<{
        best: z.ZodOptional<z.ZodArray<z.ZodObject<{
            name: z.ZodString;
            pnl_pct: z.ZodNumber;
        }, "strip", z.ZodTypeAny, {
            name: string;
            pnl_pct: number;
        }, {
            name: string;
            pnl_pct: number;
        }>, "many">>;
        worst: z.ZodOptional<z.ZodArray<z.ZodObject<{
            name: z.ZodString;
            pnl_pct: z.ZodNumber;
        }, "strip", z.ZodTypeAny, {
            name: string;
            pnl_pct: number;
        }, {
            name: string;
            pnl_pct: number;
        }>, "many">>;
    }, "strict", z.ZodTypeAny, {
        best?: {
            name: string;
            pnl_pct: number;
        }[] | undefined;
        worst?: {
            name: string;
            pnl_pct: number;
        }[] | undefined;
    }, {
        best?: {
            name: string;
            pnl_pct: number;
        }[] | undefined;
        worst?: {
            name: string;
            pnl_pct: number;
        }[] | undefined;
    }>>;
    gaps: z.ZodOptional<z.ZodArray<z.ZodString, "many">>;
    actions: z.ZodOptional<z.ZodArray<z.ZodString, "many">>;
}, "strict", z.ZodTypeAny, {
    snapshot: {
        total_value?: number | undefined;
        long?: number | undefined;
        short?: number | undefined;
        gross?: number | undefined;
        net?: number | undefined;
        invested_pct?: number | undefined;
    };
    concentration: {
        top1?: number | undefined;
        top3?: number | undefined;
        top5?: number | undefined;
        hhi?: number | undefined;
        effective_n?: number | undefined;
    };
    factors?: {
        name: string;
        exposure: number;
    }[] | undefined;
    scenarios?: {
        best?: {
            name: string;
            pnl_pct: number;
        }[] | undefined;
        worst?: {
            name: string;
            pnl_pct: number;
        }[] | undefined;
    } | undefined;
    gaps?: string[] | undefined;
    actions?: string[] | undefined;
}, {
    snapshot: {
        total_value?: number | undefined;
        long?: number | undefined;
        short?: number | undefined;
        gross?: number | undefined;
        net?: number | undefined;
        invested_pct?: number | undefined;
    };
    concentration: {
        top1?: number | undefined;
        top3?: number | undefined;
        top5?: number | undefined;
        hhi?: number | undefined;
        effective_n?: number | undefined;
    };
    factors?: {
        name: string;
        exposure: number;
    }[] | undefined;
    scenarios?: {
        best?: {
            name: string;
            pnl_pct: number;
        }[] | undefined;
        worst?: {
            name: string;
            pnl_pct: number;
        }[] | undefined;
    } | undefined;
    gaps?: string[] | undefined;
    actions?: string[] | undefined;
}>;
export declare const AgentResponse: z.ZodObject<{
    summary_markdown: z.ZodString;
    machine_readable: z.ZodObject<{
        snapshot: z.ZodObject<{
            total_value: z.ZodOptional<z.ZodNumber>;
            long: z.ZodOptional<z.ZodNumber>;
            short: z.ZodOptional<z.ZodNumber>;
            gross: z.ZodOptional<z.ZodNumber>;
            net: z.ZodOptional<z.ZodNumber>;
            invested_pct: z.ZodOptional<z.ZodNumber>;
        }, "strict", z.ZodTypeAny, {
            total_value?: number | undefined;
            long?: number | undefined;
            short?: number | undefined;
            gross?: number | undefined;
            net?: number | undefined;
            invested_pct?: number | undefined;
        }, {
            total_value?: number | undefined;
            long?: number | undefined;
            short?: number | undefined;
            gross?: number | undefined;
            net?: number | undefined;
            invested_pct?: number | undefined;
        }>;
        concentration: z.ZodObject<{
            top1: z.ZodOptional<z.ZodNumber>;
            top3: z.ZodOptional<z.ZodNumber>;
            top5: z.ZodOptional<z.ZodNumber>;
            hhi: z.ZodOptional<z.ZodNumber>;
            effective_n: z.ZodOptional<z.ZodNumber>;
        }, "strict", z.ZodTypeAny, {
            top1?: number | undefined;
            top3?: number | undefined;
            top5?: number | undefined;
            hhi?: number | undefined;
            effective_n?: number | undefined;
        }, {
            top1?: number | undefined;
            top3?: number | undefined;
            top5?: number | undefined;
            hhi?: number | undefined;
            effective_n?: number | undefined;
        }>;
        factors: z.ZodOptional<z.ZodArray<z.ZodObject<{
            name: z.ZodString;
            exposure: z.ZodNumber;
        }, "strip", z.ZodTypeAny, {
            name: string;
            exposure: number;
        }, {
            name: string;
            exposure: number;
        }>, "many">>;
        scenarios: z.ZodOptional<z.ZodObject<{
            best: z.ZodOptional<z.ZodArray<z.ZodObject<{
                name: z.ZodString;
                pnl_pct: z.ZodNumber;
            }, "strip", z.ZodTypeAny, {
                name: string;
                pnl_pct: number;
            }, {
                name: string;
                pnl_pct: number;
            }>, "many">>;
            worst: z.ZodOptional<z.ZodArray<z.ZodObject<{
                name: z.ZodString;
                pnl_pct: z.ZodNumber;
            }, "strip", z.ZodTypeAny, {
                name: string;
                pnl_pct: number;
            }, {
                name: string;
                pnl_pct: number;
            }>, "many">>;
        }, "strict", z.ZodTypeAny, {
            best?: {
                name: string;
                pnl_pct: number;
            }[] | undefined;
            worst?: {
                name: string;
                pnl_pct: number;
            }[] | undefined;
        }, {
            best?: {
                name: string;
                pnl_pct: number;
            }[] | undefined;
            worst?: {
                name: string;
                pnl_pct: number;
            }[] | undefined;
        }>>;
        gaps: z.ZodOptional<z.ZodArray<z.ZodString, "many">>;
        actions: z.ZodOptional<z.ZodArray<z.ZodString, "many">>;
    }, "strict", z.ZodTypeAny, {
        snapshot: {
            total_value?: number | undefined;
            long?: number | undefined;
            short?: number | undefined;
            gross?: number | undefined;
            net?: number | undefined;
            invested_pct?: number | undefined;
        };
        concentration: {
            top1?: number | undefined;
            top3?: number | undefined;
            top5?: number | undefined;
            hhi?: number | undefined;
            effective_n?: number | undefined;
        };
        factors?: {
            name: string;
            exposure: number;
        }[] | undefined;
        scenarios?: {
            best?: {
                name: string;
                pnl_pct: number;
            }[] | undefined;
            worst?: {
                name: string;
                pnl_pct: number;
            }[] | undefined;
        } | undefined;
        gaps?: string[] | undefined;
        actions?: string[] | undefined;
    }, {
        snapshot: {
            total_value?: number | undefined;
            long?: number | undefined;
            short?: number | undefined;
            gross?: number | undefined;
            net?: number | undefined;
            invested_pct?: number | undefined;
        };
        concentration: {
            top1?: number | undefined;
            top3?: number | undefined;
            top5?: number | undefined;
            hhi?: number | undefined;
            effective_n?: number | undefined;
        };
        factors?: {
            name: string;
            exposure: number;
        }[] | undefined;
        scenarios?: {
            best?: {
                name: string;
                pnl_pct: number;
            }[] | undefined;
            worst?: {
                name: string;
                pnl_pct: number;
            }[] | undefined;
        } | undefined;
        gaps?: string[] | undefined;
        actions?: string[] | undefined;
    }>;
}, "strict", z.ZodTypeAny, {
    summary_markdown: string;
    machine_readable: {
        snapshot: {
            total_value?: number | undefined;
            long?: number | undefined;
            short?: number | undefined;
            gross?: number | undefined;
            net?: number | undefined;
            invested_pct?: number | undefined;
        };
        concentration: {
            top1?: number | undefined;
            top3?: number | undefined;
            top5?: number | undefined;
            hhi?: number | undefined;
            effective_n?: number | undefined;
        };
        factors?: {
            name: string;
            exposure: number;
        }[] | undefined;
        scenarios?: {
            best?: {
                name: string;
                pnl_pct: number;
            }[] | undefined;
            worst?: {
                name: string;
                pnl_pct: number;
            }[] | undefined;
        } | undefined;
        gaps?: string[] | undefined;
        actions?: string[] | undefined;
    };
}, {
    summary_markdown: string;
    machine_readable: {
        snapshot: {
            total_value?: number | undefined;
            long?: number | undefined;
            short?: number | undefined;
            gross?: number | undefined;
            net?: number | undefined;
            invested_pct?: number | undefined;
        };
        concentration: {
            top1?: number | undefined;
            top3?: number | undefined;
            top5?: number | undefined;
            hhi?: number | undefined;
            effective_n?: number | undefined;
        };
        factors?: {
            name: string;
            exposure: number;
        }[] | undefined;
        scenarios?: {
            best?: {
                name: string;
                pnl_pct: number;
            }[] | undefined;
            worst?: {
                name: string;
                pnl_pct: number;
            }[] | undefined;
        } | undefined;
        gaps?: string[] | undefined;
        actions?: string[] | undefined;
    };
}>;
export declare const AnalyzeBody: z.ZodObject<{
    portfolio_report: z.ZodOptional<z.ZodUnknown>;
    positions_table_csv: z.ZodNullable<z.ZodOptional<z.ZodString>>;
    price_history: z.ZodNullable<z.ZodOptional<z.ZodUnknown>>;
    factor_history: z.ZodNullable<z.ZodOptional<z.ZodUnknown>>;
}, "strict", z.ZodTypeAny, {
    portfolio_report?: unknown;
    positions_table_csv?: string | null | undefined;
    price_history?: unknown;
    factor_history?: unknown;
}, {
    portfolio_report?: unknown;
    positions_table_csv?: string | null | undefined;
    price_history?: unknown;
    factor_history?: unknown;
}>;
export type TAgentResponse = z.infer<typeof AgentResponse>;
export type TAnalyzeBody = z.infer<typeof AnalyzeBody>;
