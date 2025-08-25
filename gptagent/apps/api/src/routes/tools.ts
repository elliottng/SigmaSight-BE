import { FastifyPluginAsync } from "fastify";
import { z } from "zod";

export const toolsRoutes: FastifyPluginAsync = async (app) => {

  app.post("/get_prices", async (req, reply) => {
    const Body = z.object({
      symbols: z.array(z.string()),
      lookback_days: z.number().min(5).max(365)
    });
    const parsed = Body.safeParse(req.body);
    if (!parsed.success) return reply.code(400).send({ error: parsed.error.flatten() });

    // Stub response
    const prices = Object.fromEntries(parsed.data.symbols.map(s => [s, [
      { d: "2025-08-20", c: 100.0 },
      { d: "2025-08-21", c: 101.2 },
      { d: "2025-08-22", c: 100.7 }
    ]]));
    return { prices };
  });

  app.post("/get_factor_loadings", async (req, reply) => {
    const Body = z.object({
      symbols: z.array(z.string()),
      model: z.enum(["short","long"])
    });
    const parsed = Body.safeParse(req.body);
    if (!parsed.success) return reply.code(400).send({ error: parsed.error.flatten() });

    const loads = Object.fromEntries(parsed.data.symbols.map(s => [s, { value: 1.05, growth: 0.74, momentum: 0.74, size: 0.87 }]));
    return { loadings: loads };
  });

  app.post("/run_scenarios", async (req, reply) => {
    const Body = z.object({
      positions: z.record(z.any()),
      scenarios: z.array(z.string())
    });
    const parsed = Body.safeParse(req.body);
    if (!parsed.success) return reply.code(400).send({ error: parsed.error.flatten() });

    // Simple linear beta * shock stub
    const out = parsed.data.scenarios.map((name, i) => ({ name, pnl_pct: (i % 2 === 0 ? 0.05 : -0.08) }));
    return { scenarios: out };
  });

  app.post("/lookup_borrow_metrics", async (req, reply) => {
    const Body = z.object({ symbols: z.array(z.string()) });
    const parsed = Body.safeParse(req.body);
    if (!parsed.success) return reply.code(400).send({ error: parsed.error.flatten() });

    const out = Object.fromEntries(parsed.data.symbols.map(s => [s, { short_interest_pct: 12.3, days_to_cover: 3.1, borrow_rate: 4.8 }]));
    return { borrow: out };
  });

};
