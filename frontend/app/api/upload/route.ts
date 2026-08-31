import { NextResponse } from "next/server";

export async function POST(request: Request) {
  const backendUrl = process.env.BACKEND_API_URL ?? "http://127.0.0.1:8000";

  const incomingForm = await request.formData();
  const file = incomingForm.get("file");

  if (!file) {
    return NextResponse.json({ error: "No file provided" }, { status: 400 });
  }

  const forwardForm = new FormData();
  forwardForm.append("file", file);

  let res: Response;
  try {
    res = await fetch(`${backendUrl}/upload`, {
      method: "POST",
      body: forwardForm,
    });
  } catch {
    return NextResponse.json({ error: "Could not reach the agent backend" }, { status: 502 });
  }

  if (!res.ok) {
    const body = await res.json().catch(() => null);
    return NextResponse.json(
      { error: body?.detail ?? "The agent backend returned an error" },
      { status: res.status }
    );
  }

  const data = await res.json();
  return NextResponse.json(data);
}
