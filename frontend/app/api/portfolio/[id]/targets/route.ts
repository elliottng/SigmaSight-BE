/**
 * Next.js route handler that proxies to backend GET {BACKEND_BASE}/get_* endpoints.
 * Requires env: NEXT_PUBLIC_BACKEND_BASE, SIGMASIGHT_API_TOKEN
 */

import { NextRequest } from "next/server";
export async function GET(_req: NextRequest, { params }: { params: { id: string } }) {
  const base = process.env.NEXT_PUBLIC_BACKEND_BASE!;
  const token = process.env.SIGMASIGHT_API_TOKEN!;
  const r = await fetch(`${base}/get_targets?portfolio_id=${params.id}`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  return new Response(await r.text(), { status: r.status, headers: { "Content-Type": r.headers.get("Content-Type") || "application/json" } });
}

export async function POST(req: NextRequest, { params }: { params: { id: string } }) {
  const base = process.env.NEXT_PUBLIC_BACKEND_BASE!;
  const token = process.env.SIGMASIGHT_API_TOKEN!;
  const body = await req.text();
  const r = await fetch(`${base}/set_targets?portfolio_id=${params.id}`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
    body
  });
  return new Response(await r.text(), { status: r.status, headers: { "Content-Type": r.headers.get("Content-Type") || "application/json" } });
}
