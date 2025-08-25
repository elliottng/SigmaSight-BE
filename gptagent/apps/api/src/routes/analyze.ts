import { FastifyPluginAsync } from "fastify";
import { z } from "zod";
import { AnalyzeBody } from "@sigmasight/schemas";
import { SigmaSightAgent } from "@sigmasight/analysis-agent";

// Simple chat message schema for testing
const ChatMessage = z.object({
  message: z.string(),
  portfolio_context: z.string().optional()
});

export const analyzeRoute: FastifyPluginAsync = async (app) => {
  app.post("/", {
    preHandler: async (req, reply) => {
      const auth = req.headers.authorization;
      if (!auth || !auth.startsWith("Bearer ")) {
        return reply.code(401).send({ error: "Unauthorized" });
      }
    }
  }, async (req, reply) => {
    try {
      app.log.info(`=== ANALYZE ROUTE HIT ===`);
      app.log.info(`Received request: ${JSON.stringify(req.body)}`);
      
      // Try to parse as chat message first (for testing)
      const chatParsed = ChatMessage.safeParse(req.body);
    if (chatParsed.success) {
      app.log.info(`Processing chat message: ${chatParsed.data.message}`);
      
      try {
        // Simple GPT response for chat messages
        const response = await fetch("https://api.openai.com/v1/chat/completions", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${process.env.OPENAI_API_KEY}`
          },
          body: JSON.stringify({
            model: "gpt-4",
            messages: [
              {
                role: "system",
                content: "You are a portfolio risk management assistant. Provide helpful insights about portfolio analysis, risk management, and investment strategies. Keep responses concise and professional."
              },
              {
                role: "user",
                content: chatParsed.data.message
              }
            ],
            max_tokens: 300,
            temperature: 0.7
          })
        });

        if (!response.ok) {
          throw new Error(`OpenAI API error: ${response.status}`);
        }

        const data = await response.json();
        const aiResponse = data.choices?.[0]?.message?.content || "I'm sorry, I couldn't generate a response.";
        
        app.log.info(`GPT response generated successfully`);
        return reply.send({ 
          response: aiResponse,
          mode: "chat" 
        });
      } catch (error) {
        app.log.error(`Chat response failed: ${error instanceof Error ? error.message : "Unknown error"}`);
        return reply.code(500).send({ 
          error: "Chat response failed", 
          details: error instanceof Error ? error.message : "Unknown error" 
        });
      }
    }
    
    // Fall back to original portfolio analysis logic
    const parsed = AnalyzeBody.safeParse(req.body);
    if (!parsed.success) {
      app.log.error(`Invalid request format: ${JSON.stringify(parsed.error.flatten())}`);
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
      app.log.error(`Portfolio analysis failed: ${error instanceof Error ? error.message : "Unknown error"}`);
      return reply.code(500).send({ 
        error: "Analysis failed", 
        details: error instanceof Error ? error.message : "Unknown error" 
      });
    }
    } catch (outerError) {
      app.log.error(`=== OUTER CATCH ERROR ===`);
      app.log.error(`Outer error: ${outerError instanceof Error ? outerError.message : "Unknown error"}`);
      app.log.error(`Outer error stack: ${outerError instanceof Error ? outerError.stack : "No stack"}`);
      return reply.code(500).send({ 
        error: "Route handler failed", 
        details: outerError instanceof Error ? outerError.message : "Unknown error" 
      });
    }
  });
};
