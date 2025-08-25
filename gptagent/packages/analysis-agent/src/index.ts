import OpenAI from "openai";
import { z } from "zod";
import { AgentResponse } from "@sigmasight/schemas";
import { SYSTEM_PROMPT } from "./system-prompt.js";

type ToolDef = {
  name: string;
  description: string;
  parameters: Record<string, unknown>;
};

export type SigmaSightAgentOptions = {
  model?: string;
  temperature?: number;
  tools?: ToolDef[];
};

export class SigmaSightAgent {
  private client: OpenAI;
  private options: SigmaSightAgentOptions;

  constructor(apiKey: string, options?: SigmaSightAgentOptions) {
    this.client = new OpenAI({ apiKey });
    this.options = {
      model: options?.model ?? "gpt-5-thinking",
      temperature: options?.temperature ?? 0,
      tools: options?.tools ?? []
    };
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

    while (true) {
      const res = await this.client.chat.completions.create({
        model: this.options.model!,
        temperature: this.options.temperature,
        messages,
        tools
      });

      const choice = res.choices[0];
      const msg = choice.message;

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

      // handle the first tool call (simple loop)
      const call = toolCalls[0];
      const fnName = call.function.name;
      const args = JSON.parse(call.function.arguments ?? "{}");

      // We expect your API to be callable locally from the server; here we just echo a stub.
      const toolResult = { ok: true, tool: fnName, args };

      messages.push({
        role: "tool",
        tool_call_id: call.id,
        name: fnName,
        content: JSON.stringify(toolResult)
      });
    }
  }
}
