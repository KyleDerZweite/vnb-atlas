import type {
  AreaFeatureCollection,
  AreaFilters,
  Coverage,
  FederalState,
  LookupResponse,
  Operator,
  SearchResponse,
} from "./types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status?: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export async function getOperators(params: { q?: string } = {}): Promise<Operator[]> {
  const search = new URLSearchParams();
  if (params.q) search.set("q", params.q);
  return fetchJson<Operator[]>(`/api/operators${withQuery(search)}`);
}

export async function getAreas(filters: AreaFilters = {}): Promise<AreaFeatureCollection> {
  const search = new URLSearchParams();
  if (filters.country) search.set("country", filters.country);
  if (filters.federalState) search.set("federal_state", filters.federalState);
  if (filters.operatorId) search.set("operator_id", filters.operatorId);
  return fetchJson<AreaFeatureCollection>(`/api/areas${withQuery(search)}`);
}

export async function getFederalStates(): Promise<FederalState[]> {
  return fetchJson<FederalState[]>("/api/federal-states");
}

export async function getCoverage(): Promise<Coverage> {
  return fetchJson<Coverage>("/api/coverage");
}

export async function search(query: string): Promise<SearchResponse> {
  const searchParams = new URLSearchParams({ q: query });
  return fetchJson<SearchResponse>(`/api/search?${searchParams.toString()}`);
}

export async function lookup(lat: number, lon: number): Promise<LookupResponse> {
  const searchParams = new URLSearchParams({ lat: String(lat), lon: String(lon) });
  return fetchJson<LookupResponse>(`/api/lookup?${searchParams.toString()}`);
}

async function fetchJson<T>(path: string): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      headers: { Accept: "application/json" },
    });
  } catch (error) {
    throw new ApiError("API nicht erreichbar. Laeuft das Backend auf Port 8000?", undefined);
  }

  if (!response.ok) {
    let detail = `API-Fehler ${response.status}`;
    try {
      const body = (await response.json()) as { detail?: string };
      if (body.detail) detail = body.detail;
    } catch {
      // The status code is enough when the body is not JSON.
    }
    throw new ApiError(detail, response.status);
  }

  return (await response.json()) as T;
}

function withQuery(search: URLSearchParams): string {
  const query = search.toString();
  return query ? `?${query}` : "";
}
