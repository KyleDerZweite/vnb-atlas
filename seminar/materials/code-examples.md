# Code-Beispiele

## fetch im Projekt

```ts
async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { Accept: "application/json" },
  });

  if (!response.ok) {
    throw new ApiError(`API-Fehler ${response.status}`, response.status);
  }

  return (await response.json()) as T;
}
```

## axios-Variante

```ts
import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000",
  headers: { Accept: "application/json" },
  timeout: 10_000,
});

export async function getOperators(q?: string): Promise<Operator[]> {
  const response = await api.get<Operator[]>("/api/operators", { params: { q } });
  return response.data;
}
```

## Apollo-Beispiel

```tsx
import { gql, useQuery } from "@apollo/client";

const GET_VNB_BY_COORDINATES = gql`
  query GetVnbByCoordinates($coordinates: String, $filter: vnb_FilterInput) {
    vnb_coordinates(coordinates: $coordinates) {
      vnbs(filter: $filter) {
        _id
        name
        types
        voltageTypes
        bbox
      }
    }
  }
`;

export function VnbLookup() {
  const { data, loading, error } = useQuery(GET_VNB_BY_COORDINATES, {
    variables: {
      coordinates: "51.4818445,7.2162363",
      filter: {
        voltageTypes: ["Niederspannung", "Mittelspannung", "Hochspannung"],
        withRegions: true,
      },
    },
  });

  if (loading) return <p>Lädt...</p>;
  if (error) return <p>Fehler: {error.message}</p>;
  return <pre>{JSON.stringify(data, null, 2)}</pre>;
}
```
