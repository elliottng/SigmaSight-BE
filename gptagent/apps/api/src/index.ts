import Fastify from "fastify";
import cors from "@fastify/cors";
import rateLimit from "@fastify/rate-limit";
import { analyzeRoute } from "./routes/analyze.js";
import { toolsRoutes } from "./routes/tools.js";
import * as dotenv from "dotenv";

// Load environment configuration
dotenv.config({ path: "../../.env" }); // Load from gptagent root
dotenv.config(); // Load from current directory if exists

const app = Fastify({ 
  logger: {
    level: process.env.LOG_LEVEL || "info"
  }
});

// CORS configuration for frontend integration
await app.register(cors, { 
  origin: [
    "http://localhost:3000", // Frontend development server
    "http://localhost:3001", // Alternate frontend port
    /^https:\/\/.*\.vercel\.app$/, // Vercel deployments
    /^https:\/\/.*\.netlify\.app$/, // Netlify deployments
  ],
  credentials: true
});

// Rate limiting configuration
const rateLimitMax = Number(process.env.RATE_LIMIT_MAX || 60);
const rateLimitWindow = process.env.RATE_LIMIT_WINDOW || "1 minute";
await app.register(rateLimit, { max: rateLimitMax, timeWindow: rateLimitWindow });

// Health check endpoint
app.get("/health", async (req, reply) => {
  return {
    status: "ok",
    service: "sigmasight-gpt-agent",
    version: "0.1.0",
    environment: process.env.NODE_ENV || "development",
    backend_url: process.env.BACKEND_URL || "http://localhost:8000",
    timestamp: new Date().toISOString()
  };
});

// Register routes
app.register(analyzeRoute, { prefix: "/analyze" });
app.register(toolsRoutes, { prefix: "/tools" });

// Error handling
app.setErrorHandler((error, request, reply) => {
  app.log.error(error);
  reply.status(500).send({
    error: "Internal Server Error",
    message: error.message,
    timestamp: new Date().toISOString()
  });
});

// Graceful shutdown
process.on("SIGINT", async () => {
  app.log.info("Received SIGINT, shutting down gracefully...");
  await app.close();
  process.exit(0);
});

process.on("SIGTERM", async () => {
  app.log.info("Received SIGTERM, shutting down gracefully...");
  await app.close();
  process.exit(0);
});

// Start server
const port = Number(process.env.PORT || 8787);
const host = "0.0.0.0";

try {
  await app.listen({ port, host });
  app.log.info(`🚀 SigmaSight GPT Agent API listening on http://${host}:${port}`);
  app.log.info(`📊 Backend URL: ${process.env.BACKEND_URL || "http://localhost:8000"}`);
  app.log.info(`🔑 OpenAI API Key: ${process.env.OPENAI_API_KEY ? "✅ Set" : "❌ Missing"}`);
} catch (err) {
  app.log.error(err);
  process.exit(1);
}
