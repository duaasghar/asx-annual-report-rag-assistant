import { isAskResponse, MAX_QUESTION_LENGTH, type AskError, type AskResponse } from "@/lib/types";

// Allow time for a Render free-tier cold start (~30-60s).
export const maxDuration = 60;
const BACKEND_TIMEOUT_MS = 55_000;

function error(message: string, status: number) {
  return Response.json({ error: message } satisfies AskError, { status });
}

export async function POST(req: Request) {
  const backend = process.env.BACKEND_URL;
  if (!backend) {
    console.error("BACKEND_URL is not set");
    return error("Server not configured.", 500);
  }

  let question: unknown;
  try {
    ({ question } = (await req.json()) as { question?: unknown });
  } catch {
    return error("Invalid request.", 400);
  }

  if (typeof question !== "string" || !question.trim()) {
    return error("Please enter a question.", 400);
  }
  const trimmed = question.trim();
  if (trimmed.length > MAX_QUESTION_LENGTH) {
    return error(`Questions must be ${MAX_QUESTION_LENGTH} characters or fewer.`, 400);
  }

  // Pass the visitor's IP on so the backend can rate-limit per user, not per Vercel server.
  const clientIp = req.headers.get("x-forwarded-for")?.split(",")[0]?.trim();

  try {
    const res = await fetch(`${backend.replace(/\/$/, "")}/ask`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(clientIp ? { "X-Forwarded-For": clientIp } : {}),
      },
      body: JSON.stringify({ question: trimmed }),
      signal: AbortSignal.timeout(BACKEND_TIMEOUT_MS),
      cache: "no-store",
    });

    if (res.status === 429) {
      return error("Too many questions. Please wait a minute and try again.", 429);
    }
    if (res.status === 503) {
      return error("The AI model is busy right now. Please try again in a minute.", 503);
    }
    if (!res.ok) {
      console.error(`Backend returned ${res.status}`);
      return error("The assistant is unavailable right now. Please try again shortly.", 502);
    }

    const data: unknown = await res.json();
    if (!isAskResponse(data)) {
      console.error("Backend response did not match AskResponse");
      return error("The assistant returned an unexpected response.", 502);
    }
    return Response.json(data satisfies AskResponse);
  } catch (err) {
    console.error("Backend request failed:", err);
    return error("The server may be waking up. Please try again in about 30 seconds.", 504);
  }
}
