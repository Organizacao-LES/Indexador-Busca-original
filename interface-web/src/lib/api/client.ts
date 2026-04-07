import { appEnv } from "@/lib/env";

type HttpMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";

type RequestOptions = {
  method?: HttpMethod;
  body?: unknown;
  headers?: Record<string, string>;
  token?: string;
  query?: Record<string, string | number | undefined>;
};

const readStoredToken = () => {
  const raw = localStorage.getItem("ifesdoc.session");
  if (!raw) {
    return null;
  }

  try {
    const session = JSON.parse(raw) as { token?: string };
    return session.token ?? null;
  } catch {
    return null;
  }
};

const buildUrl = (path: string, query?: RequestOptions["query"]) => {
  const url = new URL(path, appEnv.apiBaseUrl);

  if (query) {
    for (const [key, value] of Object.entries(query)) {
      if (value !== undefined && value !== "") {
        url.searchParams.set(key, String(value));
      }
    }
  }

  return url.toString();
};

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

export const apiRequest = async <T>(path: string, options: RequestOptions = {}): Promise<T> => {
  const isFormData = typeof FormData !== "undefined" && options.body instanceof FormData;
  const token = options.token ?? readStoredToken();

  const response = await fetch(buildUrl(path, options.query), {
    method: options.method || "GET",
    headers: {
      ...(isFormData ? {} : { "Content-Type": "application/json" }),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
    body: options.body ? (isFormData ? (options.body as FormData) : JSON.stringify(options.body)) : undefined,
  });

  if (!response.ok) {
    let message = "Falha ao comunicar com a API.";

    try {
      const payload = await response.json();
      if (payload?.message) {
        message = payload.message;
      } else if (payload?.detail) {
        message = payload.detail;
      }
    } catch {
      // ignore invalid error bodies
    }

    throw new ApiError(message, response.status);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
};
