import { BackendClient, TPortfolioSnapshot, TPosition, TPositionFactorExposure, TRiskMetrics, TStressTestResult } from "./backend-client.js";
export { BackendClient, TPortfolioSnapshot, TPosition, TPositionFactorExposure, TRiskMetrics, TStressTestResult };
type ToolDef = {
    name: string;
    description: string;
    parameters: Record<string, unknown>;
};
export type SigmaSightAgentOptions = {
    model?: string;
    temperature?: number;
    tools?: ToolDef[];
    backendUrl?: string;
    authToken?: string;
};
export declare class SigmaSightAgent {
    private client;
    private backend;
    private options;
    constructor(apiKey: string, options?: SigmaSightAgentOptions);
    private getDefaultTools;
    private executeTool;
    run(input: Record<string, unknown>): Promise<{
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
}
