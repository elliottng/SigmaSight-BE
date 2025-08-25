import Fastify from "fastify";
import cors from "@fastify/cors";
import rateLimit from "@fastify/rate-limit";
import { analyzeRoute } from "./routes/analyze.js";
import { toolsRoutes } from "./routes/tools.js";
import * as dotenv from "dotenv";
dotenv.config();

const app = Fastify({ logger: true });
await app.register(cors, { origin: true });
await app.register(rateLimit, { max: 60, timeWindow: "1 minute" });

app.register(analyzeRoute, { prefix: "/analyze" });
app.register(toolsRoutes, { prefix: "/tools" });

const port = Number(process.env.PORT || 8787);
app.listen({ port, host: "0.0.0.0" }).then(() => {
  app.log.info(`API listening on :${port}`);
});
