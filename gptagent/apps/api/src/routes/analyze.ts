import { FastifyPluginAsync } from "fastify";
import { z } from "zod";
import { AnalyzeBody } from "@sigmasight/schemas";
import { SigmaSightAgent } from "@sigmasight/analysis-agent";

export const analyzeRoute: FastifyPluginAsync = async (app) => {
  app.post("/", {
    preHandler: async (req, reply) => {
      const auth = req.headers.authorization;
      if (!auth || !auth.startsWith("Bearer ")) {
        return reply.code(401).send({ error: "Unauthorized" });
      }
    }
  }, async (req, reply) => {
    const parsed = AnalyzeBody.safeParse(req.body);
    if (!parsed.success) {
      return reply.code(400).send({ error: parsed.error.flatten() });
    }

    try {
      const agent = new SigmaSightAgent(process.env.OPENAI_API_KEY || "", {
        backendUrl: process.env.BACKEND_URL || "http://localhost:8000",
        authToken: req.headers.authorization?.replace("Bearer ", "")
      });
      
      const result = await agent.run(parsed.data);
      return reply.send(result);
    } catch (error) {
      app.log.error(`Analysis failed: ${error instanceof Error ? error.message : "Unknown error"}`);
      return reply.code(500).send({ 
        error: "Analysis failed", 
        details: error instanceof Error ? error.message : "Unknown error" 
      });
    }
  });
};
