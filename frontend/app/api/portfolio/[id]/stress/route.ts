/**
 * Next.js route handler that proxies to backend GET {BACKEND_BASE}/get_* endpoints.
 * Requires env: NEXT_PUBLIC_BACKEND_BASE, SIGMASIGHT_API_TOKEN
 */

import { NextRequest } from "next/server";
export async function GET(req: NextRequest, { params }: { params: { id: string } }) {
  const base = process.env.NEXT_PUBLIC_BACKEND_BASE!;
  const token = process.env.SIGMASIGHT_API_TOKEN!;
  const url = new URL(req.url);
  const scenarios = url.searchParams.getAll("scenario");
  const q = scenarios.map(s => `scenarios=${encodeURIComponent(s)}`).join("&");
  const r = await fetch(`${base}/get_stress_results?portfolio_id=${params.id}&${q}`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  return new Response(await r.text(), { status: r.status, headers: { "Content-Type": r.headers.get("Content-Type") || "application/json" } });
}
