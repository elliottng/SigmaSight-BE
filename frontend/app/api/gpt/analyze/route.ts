/**
 * Proxy that forwards chat prompts to backend GPT orchestrator if you have one,
 * or directly to your server that runs the model/tool loop.
 */
export async function POST(req: Request) {
  const base = process.env.NEXT_PUBLIC_BACKEND_BASE!;
  const token = process.env.SIGMASIGHT_API_TOKEN!;
  const body = await req.text();
  const r = await fetch(`${base}/gpt/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
    body
  });
  return new Response(await r.text(), { status: r.status, headers: { "Content-Type": r.headers.get("Content-Type") || "application/json" } });
}
