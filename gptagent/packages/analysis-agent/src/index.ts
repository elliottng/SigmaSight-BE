import OpenAI from "openai";
import { z } from "zod";
import { AgentResponse } from "@sigmasight/schemas";
import { SYSTEM_PROMPT } from "./system-prompt.js";
import { BackendClient, TPortfolioSnapshot, TPosition, TPositionFactorExposure, TRiskMetrics, TStressTestResult } from "./backend-client.js";

// Export BackendClient and types for external use
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

export class SigmaSightAgent {
  private client: OpenAI;
  private backend: BackendClient;
  private options: SigmaSightAgentOptions;

  constructor(apiKey: string, options?: SigmaSightAgentOptions) {
    this.client = new OpenAI({ apiKey });
    this.backend = new BackendClient(options?.backendUrl, options?.authToken);
    this.options = {
      model: options?.model ?? "gpt-4",
      temperature: options?.temperature ?? 0,
      tools: options?.tools ?? this.getDefaultTools()
    };
  }

  private getDefaultTools(): ToolDef[] {
    return [
      {
        name: "get_portfolio_snapshot",
        description: "Get current portfolio snapshot with exposures and values from backend",
        parameters: {
          type: "object",
          properties: {
            portfolio_id: { type: "string", description: "Portfolio UUID" },
            as_of: { type: "string", description: "Date in YYYY-MM-DD format (optional)" }
          },
          required: ["portfolio_id"]
        }
      },
      {
        name: "get_positions",
        description: "Get all positions in portfolio with market values and P&L from backend",
        parameters: {
          type: "object",
          properties: {
            portfolio_id: { type: "string", description: "Portfolio UUID" },
            as_of: { type: "string", description: "Date in YYYY-MM-DD format (optional)" }
          },
          required: ["portfolio_id"]
        }
      },
      {
        name: "get_factor_exposures",
        description: "Get factor exposures for all positions from backend quantitative engine",
        parameters: {
          type: "object",
          properties: {
            portfolio_id: { type: "string", description: "Portfolio UUID" },
            as_of: { type: "string", description: "Date in YYYY-MM-DD format (optional)" }
          },
          required: ["portfolio_id"]
        }
      },
      {
        name: "get_risk_metrics",
        description: "Get VaR and Expected Shortfall metrics from backend risk engine",
        parameters: {
          type: "object",
          properties: {
            portfolio_id: { type: "string", description: "Portfolio UUID" },
            as_of: { type: "string", description: "Date in YYYY-MM-DD format (optional)" }
          },
          required: ["portfolio_id"]
        }
      },
      {
        name: "run_stress_test",
        description: "Run stress test scenarios using backend stress testing engine",
        parameters: {
          type: "object",
          properties: {
            portfolio_id: { type: "string", description: "Portfolio UUID" },
            scenarios: { 
              type: "array", 
              items: { type: "string" },
              description: "List of stress test scenario names"
            }
          },
          required: ["portfolio_id", "scenarios"]
        }
      }
    ];
  }

  private async executeTool(name: string, args: Record<string, unknown>): Promise<unknown> {
    const portfolioId = args.portfolio_id as string;
    const asOf = args.as_of as string | undefined;

    switch (name) {
      case "get_portfolio_snapshot":
        const snapshot = await this.backend.getPortfolioSnapshot(portfolioId, asOf);
        return snapshot ? { 
          success: true, 
          data: snapshot,
          source: "backend_database" 
        } : { 
          success: false, 
          error: "Portfolio snapshot not found or backend unavailable",
          gaps: ["portfolio_snapshot_missing"] 
        };

      case "get_positions":
        const positions = await this.backend.getPositions(portfolioId, asOf);
        return { 
          success: true, 
          data: positions, 
          count: positions.length,
          source: "backend_database" 
        };

      case "get_factor_exposures":
        const factors = await this.backend.getFactorExposures(portfolioId, asOf);
        return { 
          success: true, 
          data: factors, 
          count: factors.length,
          source: "backend_quantitative_engine" 
        };

      case "get_risk_metrics":
        const risk = await this.backend.getRiskMetrics(portfolioId, asOf);
        return risk ? { 
          success: true, 
          data: risk,
          source: "backend_risk_engine" 
        } : { 
          success: false, 
          error: "Risk metrics not available",
          gaps: ["var_es_calculations_missing"] 
        };

      case "run_stress_test":
        const scenarios = args.scenarios as string[];
        const stressResults = await this.backend.runStressTest(portfolioId, scenarios);
        return { 
          success: true, 
          data: stressResults, 
          scenarios_tested: scenarios.length,
          source: "backend_stress_engine" 
        };

      default:
        return { 
          success: false, 
          error: `Unknown tool: ${name}` 
        };
    }
  }

  async run(input: Record<string, unknown>) {
    const messages: OpenAI.ChatCompletionMessageParam[] = [
      { role: "system", content: SYSTEM_PROMPT },
      { role: "user", content: JSON.stringify(input) }
    ];

    const tools = this.options.tools?.map(t => ({
      type: "function" as const,
      function: { name: t.name, description: t.description, parameters: t.parameters }
    })) ?? [];

    let maxIterations = 10; // Prevent infinite loops
    let currentIteration = 0;

    while (currentIteration < maxIterations) {
      currentIteration++;
      
      const res = await this.client.chat.completions.create({
        model: this.options.model!,
        temperature: this.options.temperature,
        messages,
        tools
      });

      const choice = res.choices[0];
      const msg = choice.message;

      messages.push(msg);

      const toolCalls = msg.tool_calls ?? [];
      if (toolCalls.length === 0) {
        const content = msg.content ?? "{}";
        let parsed: unknown;
        try {
          parsed = JSON.parse(content);
        } catch {
          throw new Error("Model did not return valid JSON.");
        }
        const valid = AgentResponse.safeParse(parsed);
        if (!valid.success) {
          throw new Error("Output failed schema validation: " + valid.error.toString());
        }
        return valid.data;
      }

      // Execute all tool calls
      for (const call of toolCalls) {
        const fnName = call.function.name;
        const args = JSON.parse(call.function.arguments ?? "{}");

        try {
          const toolResult = await this.executeTool(fnName, args);
          messages.push({
            role: "tool",
            tool_call_id: call.id,
            content: JSON.stringify(toolResult)
          });
        } catch (error) {
          const errorResult = {
            success: false,
            error: error instanceof Error ? error.message : "Tool execution failed",
            gaps: [`${fnName}_execution_failed`]
          };
          messages.push({
            role: "tool",
            tool_call_id: call.id,
            content: JSON.stringify(errorResult)
          });
        }
      }
    }

    throw new Error(`Maximum iterations (${maxIterations}) reached without completion`);
  }
}
