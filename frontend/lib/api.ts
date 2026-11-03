import type {
  AnalysisResponse,
  CasePredictResponse,
  CasePredictStatus,
  DocumentRecord,
  DocumentUploadResponse,
  SessionUser,
} from "@/lib/types";

const API_BASE_URL = (process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000").replace(/\/$/, "");

interface ApiErrorBody {
  detail?: { code?: string; message?: string } | string;
}

class ApiRequestError extends Error {
  constructor(message: string, readonly status: number) {
    super(message);
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      credentials: "include",
      headers: {
        ...(init?.headers ?? {}),
      },
      cache: "no-store",
    });
  } catch (error) {
    if (error instanceof TypeError) {
      throw new Error(
        `Cannot reach the NyayaSetu API at ${API_BASE_URL}. Start the backend and check NEXT_PUBLIC_API_BASE_URL and CORS_ORIGINS.`,
      );
    }
    throw error;
  }

  if (!response.ok) {
    let message = `Request failed (${response.status}).`;
    try {
      const body = (await response.json()) as ApiErrorBody;
      if (typeof body.detail === "string") message = body.detail;
      else if (body.detail?.message) message = body.detail.message;
    } catch {
      message = `Request failed (${response.status}).`;
    }
    throw new ApiRequestError(message, response.status);
  }

  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}

export function getCurrentUser(): Promise<SessionUser | null> {
  return request<SessionUser>("/api/auth/me").catch((error: unknown) => {
    if (error instanceof ApiRequestError && error.status === 401) return null;
    throw error;
  });
}

export async function createAccount(displayName: string, email: string, password: string) {
  const response = await request<{ user: SessionUser }>("/api/auth/signup", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ display_name: displayName, email, password }),
  });
  return response.user;
}

export async function signIn(email: string, password: string) {
  const response = await request<{ user: SessionUser }>("/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  return response.user;
}

export function signOut() {
  return request<void>("/api/auth/logout", { method: "POST" });
}

export function uploadDocument(file: File) {
  const body = new FormData();
  body.append("file", file);
  return request<DocumentUploadResponse>("/api/upload", { method: "POST", body });
}

export function analyzeDocument(documentId: string) {
  return request<AnalysisResponse>(`/api/analyze/${encodeURIComponent(documentId)}`, {
    method: "POST",
  });
}

export function listDocuments() {
  return request<DocumentRecord[]>("/api/documents");
}

export function predictCase(features: Record<string, number>) {
  return request<CasePredictResponse>("/api/predict", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ features }),
  });
}

export function getCasePredictStatus() {
  return request<CasePredictStatus>("/api/predict/status");
}
