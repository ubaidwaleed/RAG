import { NextResponse } from "next/server";

import type { QueryRequest, QueryResponse } from "@/lib/types";

export async function POST(request: Request) {
  const body: QueryRequest = await request.json();
  const backendUrl = process.env.BACKEND_API_URL ?? "http://127.0.0.1:8000";

  let res: Response;
  try {
    res = await fetch(`${backendUrl}/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  } catch {
    return NextResponse.json({ error: "Could not reach the agent backend" }, { status: 502 });
  }

  if (!res.ok) {
    return NextResponse.json(
      { error: "The agent backend returned an error" },
      { status: res.status }
    );
  }

  const data: QueryResponse = await res.json();
  return NextResponse.json(data);
}
