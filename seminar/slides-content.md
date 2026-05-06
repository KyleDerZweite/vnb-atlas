# Folieninhalt

Die folgende Struktur ist als Inhaltsbasis gedacht. Design, Layout und finale Folienform können später entstehen.

## Folie 1: Titel

**API Schema Design + REST**

Untertitel:

**Live-Interaktion mit OpenAPI, fetch vs. axios**

Sprecher: A+B

Kernaussage:

> Wir erklären REST und API-Schema-Design allgemein und nutzen den VNB Atlas als konkretes Beispiel.

## Folie 2: Warum über API-Schema-Design sprechen?

Sprecher: A

- APIs sind Verträge zwischen Backend, Frontend und externen Nutzern.
- Ohne klares Schema entstehen Missverständnisse über Datenform, Fehlerfälle und Parameter.
- Ein gutes Schema macht APIs testbar, dokumentierbar und langfristig wartbar.
- OpenAPI kann aus Code entstehen, sollte aber bewusst geprüft werden.

## Folie 3: Was ist ein API-Schema?

Sprecher: A

- Beschreibung der verfügbaren Endpunkte
- Eingaben: Path-Parameter, Query-Parameter, Request Body, Header
- Ausgaben: Response Body, Statuscodes, Fehlermodelle
- Datentypen, Pflichtfelder, optionale Felder und Beispiele
- Maschinenlesbare Grundlage für Doku, Tests und Client-Generierung

## Folie 4: REST-Grundidee

Sprecher: A

- Ressourcen werden über URLs adressiert.
- HTTP-Methoden beschreiben Aktionen.
- `GET` liest Daten, `POST` erzeugt Daten, `PUT/PATCH` ändern Daten, `DELETE` löscht Daten.
- Statuscodes geben Ergebnis und Fehlerklasse an.
- Query-Parameter eignen sich für Filter, Sortierung und Pagination.

Beispiele:

```text
GET /api/operators
GET /api/operators/{operator_id}
GET /api/areas?country=DE&voltage_level=Hochspannung
```

## Folie 5: Gutes REST-Design

Sprecher: A

- Ressourcen klar benennen
- Endpunkte stabil und vorhersehbar halten
- Filter explizit machen
- Statuscodes konsistent verwenden
- Fehlerantworten standardisieren
- Antwortmodelle typisieren
- Pagination und Limits bei großen Datenmengen einplanen

## Folie 6: OpenAPI und Swagger UI

Sprecher: A

- OpenAPI ist eine maschinenlesbare REST-API-Beschreibung.
- Swagger UI macht daraus eine interaktive Dokumentation.
- Entwickler können Endpunkte direkt im Browser testen.
- Schema kann für Client-Generierung, Tests und Reviews genutzt werden.

Projekt-Showcase:

```text
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/openapi.json
```

## Folie 7: Live-Interaktion mit REST

Sprecher: A

Live zeigen:

- Swagger UI öffnen
- `GET /health`
- `GET /api/operators` mit `q=westnetz`
- `GET /api/areas` mit Filtern
- `GET /api/lookup` mit Koordinaten
- OpenAPI JSON öffnen

Kernaussage:

> Eine gute REST-API ist nicht nur Code, sondern direkt explorierbar.

## Folie 8: Projekt als Showcase

Sprecher: A

Das Projekt zeigt:

- FastAPI erzeugt OpenAPI automatisch.
- Pydantic-Modelle beschreiben viele Antworten.
- Das Frontend konsumiert die REST-API zentral.
- Die API ist lokal testbar und live demonstrierbar.

Wichtiger Befund:

- `/api/areas` ist aktuell im OpenAPI-Schema nur generisch beschrieben, weil der Endpunkt `dict[str, Any]` zurückgibt.
- Für besseres Schema-Design wäre ein konkretes `AreaFeatureCollection`-Modell sinnvoll.

## Folie 9: Die Client-Perspektive

Sprecher: B

- Frontends brauchen eine stabile Schnittstelle zum Backend.
- API-Aufrufe sollten zentral organisiert werden.
- Fehlerbehandlung sollte einheitlich sein.
- Typen helfen, aber Runtime-Fehler bleiben möglich.
- Gute API-Clients verstecken Wiederholung, nicht die API selbst.

## Folie 10: fetch

Sprecher: B

- `fetch` ist im Browser eingebaut.
- Es braucht keine zusätzliche Dependency.
- Es ist relativ niedrigschwellig und standardisiert.
- 4xx/5xx lösen keinen JavaScript-Error aus.
- JSON muss explizit ausgelesen werden.

Beispiel:

```ts
const response = await fetch("/api/operators");
if (!response.ok) {
  throw new Error(`HTTP ${response.status}`);
}
const data = await response.json();
```

## Folie 11: fetch im Projekt

Sprecher: B

Projekt-Showcase:

- Datei: `frontend/src/api-client.ts`
- Zentraler `fetchJson<T>` Wrapper
- `API_BASE_URL` wird einmal definiert
- Fehler werden in `ApiError` übersetzt
- Funktionen wie `getOperators`, `getAreas`, `lookup` kapseln konkrete Endpunkte

Kernaussage:

> Für eine überschaubare REST-API ist `fetch` mit gutem Wrapper völlig ausreichend.

## Folie 12: axios

Sprecher: B

- axios ist eine HTTP-Client-Bibliothek.
- Eine Instanz kann `baseURL`, Header und Timeout zentral definieren.
- JSON-Antworten liegen direkt in `response.data`.
- 4xx/5xx werden standardmäßig als Fehler behandelt.
- Interceptors helfen bei Auth, Logging, Retry und Fehlernormalisierung.

## Folie 13: axios-Beispiel

Sprecher: B

```ts
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

Kernaussage:

> axios lohnt sich vor allem, wenn der Client wächst und zentrale HTTP-Features wichtig werden.

## Folie 14: fetch vs. axios

Sprecher: B

| Kriterium | fetch | axios |
|---|---|---|
| Dependency | keine | zusätzliches Paket |
| 4xx/5xx | manuell prüfen | Reject per Default |
| JSON | `response.json()` | `response.data` |
| Timeout | `AbortController` | `timeout` Option |
| Interceptors | selbst bauen | eingebaut |
| Geeignet für | kleine bis mittlere Clients | größere, zentrale API-Clients |

## Folie 15: Live-Vergleich

Sprecher: B

Zeigen:

- Einen vorhandenen `fetch`-Aufruf aus dem Projekt
- Daneben eine hypothetische axios-Version
- Unterschiede bei Fehlerbehandlung, Params und Rückgabewert

Kernaussage:

> Der wichtigste Unterschied ist nicht Syntax, sondern wie zentral und konsistent HTTP-Verhalten organisiert wird.

## Folie 16: Gemeinsames Fazit

Sprecher: A+B

- API-Schema-Design macht Backend und Frontend verlässlicher.
- REST funktioniert gut, wenn Ressourcen und Use-Cases klar sind.
- OpenAPI macht REST sichtbar, testbar und maschinenlesbar.
- `fetch` reicht oft aus, wenn es sauber gekapselt wird.
- axios bringt Komfort bei wachsenden Clients.
- Das Projekt zeigt diese Konzepte konkret, ist aber nur ein Beispiel für allgemeinere Prinzipien.
