// Mirrors the FastAPI response models in api.py (Answer / Source).

export type Source = {
  page: number | null;
  excerpt: string;
};

export type AskResponse = {
  question: string;
  answer: string;
  sources: Source[];
};

export type AskError = { error: string };

export const MAX_QUESTION_LENGTH = 500;

function isSource(value: unknown): value is Source {
  if (typeof value !== "object" || value === null) return false;
  const v = value as Record<string, unknown>;
  return (typeof v.page === "number" || v.page === null) && typeof v.excerpt === "string";
}

/** Runtime check so a backend change can't silently break the UI. */
export function isAskResponse(value: unknown): value is AskResponse {
  if (typeof value !== "object" || value === null) return false;
  const v = value as Record<string, unknown>;
  return (
    typeof v.question === "string" &&
    typeof v.answer === "string" &&
    Array.isArray(v.sources) &&
    v.sources.every(isSource)
  );
}
