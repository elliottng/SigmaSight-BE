/**
 * Next.js route handler that proxies to backend GET {BACKEND_BASE}/get_* endpoints.
 * Requires env: NEXT_PUBLIC_BACKEND_BASE, SIGMASIGHT_API_TOKEN
 */

export async function GET(_req: Request, { params }: { params: { id: string } }) {
  const base = process.env.NEXT_PUBLIC_BACKEND_BASE!;
  const token = process.env.SIGMASIGHT_API_TOKEN!;
  const r = await fetch(`${base}/get_short_metrics?portfolio_id=${params.id}`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  return new Response(await r.text(), { status: r.status, headers: { "Content-Type": r.headers.get("Content-Type") || "application/json" } });
}
