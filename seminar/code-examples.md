# Code-Beispiele

## fetch: einfacher Aufruf

```ts
const response = await fetch("http://127.0.0.1:8000/api/operators");

if (!response.ok) {
  throw new Error(`HTTP ${response.status}`);
}

const operators = await response.json();
```

## fetch: zentraler Wrapper

```ts
const API_BASE_URL = "http://127.0.0.1:8000";

class ApiError extends Error {
  constructor(
    message: string,
    public readonly status?: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function fetchJson<T>(path: string): Promise<T> {
  let response: Response;

  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      headers: { Accept: "application/json" },
    });
  } catch {
    throw new ApiError("API nicht erreichbar");
  }

  if (!response.ok) {
    throw new ApiError(`API-Fehler ${response.status}`, response.status);
  }

  return (await response.json()) as T;
}

export async function getOperators(q?: string): Promise<Operator[]> {
  const params = new URLSearchParams();
  if (q) params.set("q", q);

  const query = params.toString();
  return fetchJson<Operator[]>(`/api/operators${query ? `?${query}` : ""}`);
}
```

## axios: vergleichbarer Client

```ts
import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
  headers: { Accept: "application/json" },
  timeout: 10_000,
});

export async function getOperators(q?: string): Promise<Operator[]> {
  const response = await api.get<Operator[]>("/api/operators", {
    params: { q },
  });

  return response.data;
}
```

## axios: zentrale Fehlerbehandlung

```ts
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (axios.isAxiosError(error)) {
      const status = error.response?.status;
      const message = error.response?.data?.detail ?? "API-Fehler";
      throw new ApiError(message, status);
    }

    throw error;
  },
);
```

## Direkte REST-Testaufrufe

```bash
curl http://127.0.0.1:8000/health
curl "http://127.0.0.1:8000/api/operators?q=westnetz"
curl "http://127.0.0.1:8000/api/areas?country=DE&federal_state=NW&voltage_level=Hochspannung"
curl "http://127.0.0.1:8000/api/lookup?lat=51.4818445&lon=7.2162363"
```
