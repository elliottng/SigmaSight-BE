import { FastifyPluginAsync } from "fastify";
import { z } from "zod";
import { BackendClient } from "@sigmasight/analysis-agent";

export const toolsRoutes: FastifyPluginAsync = async (app) => {

  // Individual tool endpoints for direct access
  app.post("/portfolio_snapshot", async (req, reply) => {
    const Body = z.object({
      portfolio_id: z.string(),
      as_of: z.string().optional()
    });
    const parsed = Body.safeParse(req.body);
    if (!parsed.success) return reply.code(400).send({ error: parsed.error.flatten() });

    const authToken = req.headers.authorization?.replace("Bearer ", "");
    const backend = new BackendClient(process.env.BACKEND_URL, authToken);
    
    try {
      const snapshot = await backend.getPortfolioSnapshot(parsed.data.portfolio_id, parsed.data.as_of);
      return { success: true, data: snapshot };
    } catch (error) {
      return reply.code(500).send({ 
        success: false, 
        error: error instanceof Error ? error.message : "Failed to get portfolio snapshot" 
      });
    }
  });

  app.post("/positions", async (req, reply) => {
    const Body = z.object({
      portfolio_id: z.string(),
      as_of: z.string().optional()
    });
    const parsed = Body.safeParse(req.body);
    if (!parsed.success) return reply.code(400).send({ error: parsed.error.flatten() });

    const authToken = req.headers.authorization?.replace("Bearer ", "");
    const backend = new BackendClient(process.env.BACKEND_URL, authToken);
    
    try {
      const positions = await backend.getPositions(parsed.data.portfolio_id, parsed.data.as_of);
      return { success: true, data: positions, count: positions.length };
    } catch (error) {
      return reply.code(500).send({ 
        success: false, 
        error: error instanceof Error ? error.message : "Failed to get positions" 
      });
    }
  });

  app.post("/factor_exposures", async (req, reply) => {
    const Body = z.object({
      portfolio_id: z.string(),
      as_of: z.string().optional()
    });
    const parsed = Body.safeParse(req.body);
    if (!parsed.success) return reply.code(400).send({ error: parsed.error.flatten() });

    const authToken = req.headers.authorization?.replace("Bearer ", "");
    const backend = new BackendClient(process.env.BACKEND_URL, authToken);
    
    try {
      const factors = await backend.getFactorExposures(parsed.data.portfolio_id, parsed.data.as_of);
      return { success: true, data: factors, count: factors.length };
    } catch (error) {
      return reply.code(500).send({ 
        success: false, 
        error: error instanceof Error ? error.message : "Failed to get factor exposures" 
      });
    }
  });

  app.post("/risk_metrics", async (req, reply) => {
    const Body = z.object({
      portfolio_id: z.string(),
      as_of: z.string().optional()
    });
    const parsed = Body.safeParse(req.body);
    if (!parsed.success) return reply.code(400).send({ error: parsed.error.flatten() });

    const authToken = req.headers.authorization?.replace("Bearer ", "");
    const backend = new BackendClient(process.env.BACKEND_URL, authToken);
    
    try {
      const risk = await backend.getRiskMetrics(parsed.data.portfolio_id, parsed.data.as_of);
      return { success: true, data: risk };
    } catch (error) {
      return reply.code(500).send({ 
        success: false, 
        error: error instanceof Error ? error.message : "Failed to get risk metrics" 
      });
    }
  });

  app.post("/stress_test", async (req, reply) => {
    const Body = z.object({
      portfolio_id: z.string(),
      scenarios: z.array(z.string())
    });
    const parsed = Body.safeParse(req.body);
    if (!parsed.success) return reply.code(400).send({ error: parsed.error.flatten() });

    const authToken = req.headers.authorization?.replace("Bearer ", "");
    const backend = new BackendClient(process.env.BACKEND_URL, authToken);
    
    try {
      const results = await backend.runStressTest(parsed.data.portfolio_id, parsed.data.scenarios);
      return { success: true, data: results, scenarios_tested: parsed.data.scenarios.length };
    } catch (error) {
      return reply.code(500).send({ 
        success: false, 
        error: error instanceof Error ? error.message : "Failed to run stress test" 
      });
    }
  });

  // Health check endpoint
  app.get("/health", async (req, reply) => {
    const authToken = req.headers.authorization?.replace("Bearer ", "");
    const backend = new BackendClient(process.env.BACKEND_URL, authToken);
    
    const backendHealthy = await backend.healthCheck();
    
    return {
      status: "ok",
      backend_connected: backendHealthy,
      backend_url: process.env.BACKEND_URL || "http://localhost:8000"
    };
  });

};
