# GPT User Interface Rebuild Instructions

## Overview
Rebuild the GPT user interface to integrate with the existing frontend at `frontend/src/app/chat/page.tsx`. The interface should accept user inputs from this page and maintain an ongoing conversation.

## Instructions

1. **Input Handling**
    - Capture user messages from the chat input on `page.tsx`.
    - Ensure the input is sent to the backend GPT API endpoint.

2. **API Integration**
    - Use `fetch` or an HTTP client to send user messages to the GPT backend.
    - Await the response and handle errors gracefully.

3. **Conversation State**
    - Store the conversation history in a state variable (e.g., using React's `useState` or `useReducer`).
    - Append new messages (both user and GPT responses) to the conversation history.

4. **UI Updates**
    - Render the conversation history as a chat log.
    - Display user messages and GPT responses with clear distinction (e.g., different styles or alignment).

5. **Continuous Conversation**
    - After each response, keep the input field focused for the next user message.
    - Allow the user to send follow-up messages, continuing the conversation seamlessly.

6. Example code 

1. Install dependencies
npm install openai

# + tailwind if you’re using it

2. Use the API key in the .env file in the gptagent directory:

OPENAI_API_KEY=sk-your_api_key_here

3. Create API route

If you’re using Next.js App Router (i.e., app/ folder):

app/api/chat/route.ts

import OpenAI from "openai";

export const runtime = "edge"; // optional, makes it run on Vercel edge

const client = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

export async function POST(req: Request) {
  try {
    const { messages } = await req.json();

    const completion = await client.chat.completions.create({
      model: "gpt-5",   // 👈 this is the current model
      messages,         // expects array of { role: "system"|"user"|"assistant", content: string }
      temperature: 0.7,
    });

    return new Response(
      JSON.stringify({ content: completion.choices[0].message?.content }),
      { headers: { "Content-Type": "application/json" } }
    );
  } catch (err: any) {
    return new Response(JSON.stringify({ error: err.message }), { status: 500 });
  }
}

4. Example client-side call

From a React component in Next.js:

async function sendMessage(userMessage: string) {
  const res = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      messages: [
        { role: "system", content: "You are a helpful assistant." },
        { role: "user", content: userMessage }
      ],
    }),
  });

  const data = await res.json();
  return data.content;
}

and then to make it a streaming conversation, 
import OpenAI from "openai";

// (Edge optional; works fine on Node runtime too)
export const runtime = "edge";

const client = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY!,
});

type Role = "system" | "user" | "assistant";
type Message = { role: Role; content: string };

export async function POST(req: Request) {
  try {
    const { messages, model } = (await req.json()) as {
      messages: Message[];
      model?: string;
    };

    // pick your model; default shown here
    const modelName = model ?? "gpt-5";

    // Ask OpenAI for a streaming chat completion
    const stream = await client.chat.completions.create({
      model: modelName,
      messages,
      temperature: 0.2,
      stream: true, // 👈 key bit
    });

    // Convert the async iterator into a web ReadableStream for the browser
    const encoder = new TextEncoder();

    const readable = new ReadableStream({
      async start(controller) {
        try {
          for await (const chunk of stream) {
            // Each chunk can contain deltas; pull out the text
            const delta = chunk.choices?.[0]?.delta?.content ?? "";
            if (delta) controller.enqueue(encoder.encode(delta));
          }
        } catch (err) {
          controller.error(err);
          return;
        } finally {
          controller.close();
        }
      },
    });

    return new Response(readable, {
      headers: {
        // plain text keeps it simple to parse on the client
        "Content-Type": "text/plain; charset=utf-8",
        "Cache-Control": "no-cache",
      },
    });
  } catch (err: any) {
    return new Response(JSON.stringify({ error: err?.message ?? "Unknown error" }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });
  }
}
2) Client: read the stream and render tokens

components/Chat.tsx

"use client";

import { useState, useRef, useEffect } from "react";

type Role = "system" | "user" | "assistant";
type Message = { role: Role; content: string };

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([
    { role: "system", content: "You are a concise, helpful assistant." },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const scroller = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scroller.current?.scrollTo({ top: scroller.current.scrollHeight, behavior: "smooth" });
  }, [messages, loading]);

  async function send() {
    const prompt = input.trim();
    if (!prompt || loading) return;

    const msgOut = [...messages, { role: "user" as const, content: prompt }];
    setMessages(msgOut);
    setInput("");
    setLoading(true);

    // Optimistically add an assistant message we'll fill as tokens arrive
    setMessages((prev) => [...prev, { role: "assistant", content: "" }]);

    try {
      const res = await fetch("/api/chat/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: msgOut }),
      });

      if (!res.ok || !res.body) throw new Error(`HTTP ${res.status}`);

      const reader = res.body.getReader();
      const decoder = new TextDecoder();

      let acc = "";
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        acc += decoder.decode(value, { stream: true });

        // Update the last assistant message in place
        setMessages((prev) => {
          const copy = [...prev];
          const last = copy[copy.length - 1];
          if (last?.role === "assistant") {
            copy[copy.length - 1] = { ...last, content: acc };
          }
          return copy;
        });
      }
    } catch (e) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Sorry, streaming failed." },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function onKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  }

  return (
    <div className="flex h-[80vh] flex-col rounded-xl border border-gray-200 bg-white">
      <div ref={scroller} className="flex-1 space-y-4 overflow-y-auto p-4">
        {messages
          .filter((m) => m.role !== "system")
          .map((m, i) => (
            <Bubble key={i} isUser={m.role === "user"} text={m.content} />
          ))}
        {loading && <p className="text-sm text-gray-500">Thinking…</p>}
      </div>
      <div className="border-t border-gray-200 p-3">
        <div className="flex items-end gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={onKeyDown}
            placeholder="Type a message…"
            className="min-h-[48px] max-h-40 flex-1 resize-y rounded-lg border border-gray-300 p-3 outline-none focus:border-gray-400"
          />
          <button
            onClick={send}
            disabled={loading || !input.trim()}
            className="h-[48px] shrink-0 rounded-lg border border-gray-300 px-4 font-medium hover:bg-gray-50 disabled:opacity-50"
          >
            Send
          </button>
        </div>
        <p className="mt-2 text-xs text-gray-500">Enter to send • Shift+Enter for newline</p>
      </div>
    </div>
  );
}

function Bubble({ isUser, text }: { isUser: boolean; text: string }) {
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[80%] whitespace-pre-wrap rounded-2xl border px-4 py-3 text-[15px] leading-relaxed ${
          isUser ? "border-gray-300 bg-white" : "border-gray-100 bg-gray-50"
        }`}
      >
        {text}
      </div>
    </div>
  );
}


app/page.tsx

import Chat from "@/components/Chat";

export default function Page() {
  return (
    <main className="flex min-h-screen w-full justify-center">
      <div className="w-full max-w-3xl px-4 py-6">
        <h1 className="mb-2 text-2xl font-semibold">Chat</h1>
        <Chat />
      </div>
    </main>
  );
}