import fs from "node:fs";
import path from "node:path";
import pptxgen from "pptxgenjs";

const SEMINAR = path.resolve(".");
const SHAPE = new pptxgen().ShapeType;
const OUT = path.join(SEMINAR, "dist");
const MATERIALS = path.join(SEMINAR, "materials");
const ASSETS = path.join(SEMINAR, "assets", "screenshots");
const EXAMPLES = path.join(SEMINAR, "examples");

for (const dir of [OUT, MATERIALS, ASSETS]) fs.mkdirSync(dir, { recursive: true });

const theme = {
  bg: "F7F9FC",
  ink: "172033",
  muted: "5D697A",
  blue: "276EF1",
  green: "1E8E5A",
  orange: "D97706",
  line: "CCD6E2",
  codeBg: "101827",
  code: "E8EEF8",
};

const slides = [
  {
    no: 1,
    speaker: "A+B",
    title: "GraphQL + REST",
    subtitle: "API-Design, OpenAPI, Apollo, fetch vs. axios am Beispiel Deutschland VNB Atlas",
    bullets: ["Seminar mit Live-Demo", "Projektbezug: FastAPI-Backend, VNBdigital GraphQL, TypeScript-Frontend"],
    notes:
      "Beide Sprecher eröffnen kurz: Ziel ist kein abstrakter Vergleich, sondern ein konkreter Blick auf unser Projekt und seine API-Entscheidungen.",
  },
  {
    no: 2,
    speaker: "A",
    title: "Lernziele",
    bullets: [
      "REST-Endpunkte als bewusstes API-Design lesen und testen",
      "OpenAPI als automatisch erzeugten Vertrag verstehen",
      "fetch und axios praktisch vergleichen",
      "GraphQL und Apollo anhand von VNBdigital einordnen",
      "Architekturentscheidung erklären: GraphQL upstream, REST downstream",
    ],
    notes: "Sprecher A setzt den Rahmen. Wichtig: Wir beantworten nicht nur 'was ist besser', sondern 'wo passt was'.",
  },
  {
    no: 3,
    speaker: "B",
    title: "Projektkontext",
    bullets: [
      "Frontend zeigt Verteilnetzbetreiber auf einer Leaflet-Karte",
      "Backend liefert Operatoren, Gebiete, Suche, Lookup und Coverage",
      "Datenquelle: VNBdigital-Koordinatenabfragen über GraphQL",
      "Backend transformiert externe Daten in eigene REST-Ressourcen",
    ],
    notes:
      "Sprecher B erklärt das Projekt fachlich: Karte, Betreiber, Spannungsebenen und warum ein eigenes Backend sinnvoll ist.",
  },
  {
    no: 4,
    speaker: "A",
    title: "Architekturüberblick",
    diagram: [
      ["VNBdigital GraphQL", "Import/Mesh-Skripte", "FastAPI REST Backend", "Frontend mit fetch"],
      ["Externe flexible Abfrage", "Transformation", "Stabile Projekt-API", "Karte, Suche, Lookup"],
    ],
    notes:
      "Sprecher A nutzt die Grafik: GraphQL ist die Quellseite, REST ist unser Produktvertrag für die UI.",
  },
  {
    no: 5,
    speaker: "A",
    title: "REST in unserem Backend",
    bullets: [
      "Ressourcenorientierte Endpunkte: /api/operators, /api/areas, /api/search, /api/lookup",
      "GET-only API mit Query-Parametern für Filter",
      "Pydantic-Modelle beschreiben viele Antworttypen",
      "FastAPI erzeugt daraus Dokumentation und OpenAPI-Schema",
    ],
    code: "GET /api/operators?q=westnetz\nGET /api/areas?country=DE&federal_state=NW&voltage_level=Hochspannung\nGET /api/lookup?lat=51.4818445&lon=7.2162363",
    notes: "Sprecher A zeigt, dass REST nicht nur HTTP ist, sondern ein Vertrag aus Ressourcen, Parametern und Antwortformen.",
  },
  {
    no: 6,
    speaker: "A",
    title: "OpenAPI sichtbar",
    bullets: [
      "Swagger UI: http://127.0.0.1:8000/docs",
      "OpenAPI JSON: http://127.0.0.1:8000/openapi.json",
      "ReDoc: http://127.0.0.1:8000/redoc",
      "Nützlich für Tests, Doku, Client-Generierung und Reviews",
    ],
    screenshot: "openapi_summary.svg",
    notes:
      "Sprecher A führt live /docs vor. Danach kann /openapi.json geöffnet werden, um zu zeigen, dass die Doku maschinenlesbar ist.",
  },
  {
    no: 7,
    speaker: "A",
    title: "Schema-Qualität: wichtiger Befund",
    bullets: [
      "Die meisten Endpunkte haben Pydantic response_model",
      "/api/areas liefert aktuell dict[str, Any]",
      "Dadurch erscheint die Antwort in OpenAPI nur als generisches Objekt",
      "Verbesserung: AreaFeatureCollection als Pydantic-Modell ergänzen",
    ],
    code: "Aktuell in OpenAPI:\n{\n  \"type\": \"object\",\n  \"additionalProperties\": true\n}",
    notes:
      "Sprecher A erklärt ehrlich die Schwäche. Das ist gut für API-Design: Schema-Qualität ist Teil der Wartbarkeit.",
  },
  {
    no: 8,
    speaker: "A",
    title: "Live-Demo REST",
    bullets: [
      "Backend starten: ./scripts/dev.sh",
      "Swagger UI öffnen und Endpunkte ausführen",
      "Operator-Suche: westnetz",
      "Gebiete filtern: DE, NW, Hochspannung",
      "Lookup per Koordinate: Bochum-Beispiel",
    ],
    screenshot: "lookup_output.svg",
    notes:
      "Sprecher A macht die erste Live-Interaktion. Falls das Netzwerk egal ist: diese REST-Demo läuft lokal aus statischen Daten.",
  },
  {
    no: 9,
    speaker: "B",
    title: "Frontend-Client heute: fetch",
    bullets: [
      "Native Browser-API, keine zusätzliche Dependency",
      "Projekt nutzt zentralen fetchJson-Wrapper",
      "response.ok und Fehlertexte werden manuell behandelt",
      "Rückgabewert wird in TypeScript gecastet",
    ],
    code: "const response = await fetch(`${API_BASE_URL}${path}`, {\n  headers: { Accept: \"application/json\" },\n});\n\nif (!response.ok) throw new ApiError(detail, response.status);\nreturn (await response.json()) as T;",
    notes:
      "Sprecher B übernimmt mit dem Frontend. fetch ist nicht schlecht, aber etwas niedriger level.",
  },
  {
    no: 10,
    speaker: "B",
    title: "Alternative: axios",
    bullets: [
      "Eigene Instanz mit baseURL und Standard-Headern",
      "JSON wird automatisch verarbeitet",
      "response.data ist der zentrale Rückgabewert",
      "Interceptors eignen sich für Auth, Logging, Retry und Fehlernormierung",
    ],
    code: "const api = axios.create({\n  baseURL: API_BASE_URL,\n  headers: { Accept: \"application/json\" },\n});\n\nconst response = await api.get<Operator[]>(\"/api/operators\", { params: { q } });\nreturn response.data;",
    notes:
      "Sprecher B zeigt nicht 'axios ist immer besser', sondern wann es komfortabler wird.",
  },
  {
    no: 11,
    speaker: "B",
    title: "fetch vs. axios",
    compare: [
      ["Kriterium", "fetch", "axios"],
      ["Dependency", "Keine", "Zusätzliches Paket"],
      ["Fehler bei 4xx/5xx", "Manuell über response.ok", "Reject per Default"],
      ["JSON", "response.json()", "Automatisch in data"],
      ["Timeouts", "AbortController", "Option timeout"],
      ["Interceptors", "Selbst bauen", "Eingebaut"],
    ],
    notes:
      "Sprecher B führt die Tabelle durch. Für unser Projekt reicht fetch; bei wachsender API kann axios den Client ordnen.",
  },
  {
    no: 12,
    speaker: "B",
    title: "GraphQL-Grundidee",
    bullets: [
      "Ein Endpoint, Query beschreibt die benötigten Felder",
      "Client kann verschachtelte Daten gezielt anfordern",
      "Schema definiert Typen, Queries, Mutations und Inputs",
      "Stark bei flexiblen Datenbedürfnissen und UI-Komposition",
    ],
    notes:
      "Sprecher B wechselt zum zweiten API-Paradigma. Fokus auf Datenform und Client-Bedürfnisse.",
  },
  {
    no: 13,
    speaker: "B",
    title: "VNBdigital GraphQL",
    bullets: [
      "Projekt nutzt den öffentlichen GraphQL-Endpunkt von VNBdigital",
      "Query fragt Koordinate, Regionen und VNBs ab",
      "Variablen steuern Koordinate, Spannungsebenen und Filter",
      "Ergebnisse werden offline zu Mesh- und Polygon-Daten verarbeitet",
    ],
    code: "https://www.vnbdigital.de/gateway/graphql\n\nvnb_coordinates(coordinates: $coordinates) {\n  regions(filter: $filter) { _id name bbox layerUrl }\n  vnbs(filter: $filter) { _id name types voltageTypes bbox }\n}",
    notes:
      "Sprecher B zeigt die echte Projektquery aus vnbdigital/simple_client.py, aber gekürzt für die Folie.",
  },
  {
    no: 14,
    speaker: "B",
    title: "Apollo im GraphQL-Client",
    bullets: [
      "Apollo Client verwaltet Queries, Variablen, Cache, Loading und Errors",
      "useQuery verbindet UI-Zustand direkt mit GraphQL-Daten",
      "Normalized Cache reduziert doppelte Requests",
      "Passt besonders gut, wenn das Frontend direkt GraphQL spricht",
    ],
    code: "const { data, loading, error } = useQuery(GET_VNB_BY_COORDINATES, {\n  variables: { coordinates: \"51.4818445,7.2162363\", filter },\n});",
    notes:
      "Sprecher B erklärt Apollo als spezialisierten Client, nicht als Server-Technologie.",
  },
  {
    no: 15,
    speaker: "A",
    title: "REST und GraphQL im Vergleich",
    compare: [
      ["Frage", "REST", "GraphQL"],
      ["API-Form", "Mehrere Ressourcen-URLs", "Meist ein Endpoint"],
      ["Datenumfang", "Server definiert Antwort", "Client wählt Felder"],
      ["Caching", "HTTP-nah und einfach", "Client-/Query-basiert"],
      ["Doku", "OpenAPI sehr verbreitet", "GraphQL Schema + Explorer"],
      ["Risiko", "Over-/Underfetching", "Query-Komplexität"],
    ],
    notes:
      "Sprecher A kommt zurück und ordnet ein. Wichtig: Es geht um Tradeoffs, nicht Gewinner.",
  },
  {
    no: 16,
    speaker: "A",
    title: "Warum unser Projekt beides nutzt",
    bullets: [
      "VNBdigital bietet flexible GraphQL-Abfragen für Koordinaten",
      "Unser Backend kapselt diese externe API und Datenaufbereitung",
      "Frontend braucht stabile, einfache, domänenspezifische Endpunkte",
      "REST + OpenAPI macht die lokale Demo und den Vertrag gut sichtbar",
    ],
    notes:
      "Sprecher A liefert die Architekturbegründung: GraphQL ist Quelle, REST ist Produkt-API.",
  },
  {
    no: 17,
    speaker: "A",
    title: "API-Design-Lektionen aus dem Projekt",
    bullets: [
      "Endpunkte nach UI-Use-Cases und Domänenbegriffen schneiden",
      "Filter explizit als Query-Parameter modellieren",
      "Antwortmodelle konsequent typisieren",
      "OpenAPI regelmäßig prüfen, nicht nur Code schreiben",
      "Externe APIs hinter eigener Stabilitätsschicht kapseln",
    ],
    notes: "Sprecher A zieht konkrete Regeln aus dem Projekt, statt allgemeine Best Practices abstrakt zu halten.",
  },
  {
    no: 18,
    speaker: "B",
    title: "Live-Demo GraphQL/Apollo-Konzept",
    bullets: [
      "Projektquery aus vnbdigital/simple_client.py zeigen",
      "Variablen erklären: coordinates, filter, voltageTypes",
      "Apollo-Beispielcode zeigen",
      "Abgrenzung: In unserem Projekt läuft GraphQL derzeit nicht direkt im Browser",
    ],
    screenshot: "graphql_input.svg",
    notes:
      "Sprecher B kann den echten Endpoint nennen, aber die Demo sollte nicht von externer Erreichbarkeit abhängen. Der vorbereitete Code reicht.",
  },
  {
    no: 19,
    speaker: "B",
    title: "Wann was einsetzen?",
    bullets: [
      "REST: stabile Ressourcen, einfache HTTP-Semantik, gute Tooling-Unterstützung",
      "GraphQL: flexible verschachtelte Daten, viele UI-Sichten, gezielte Feldauswahl",
      "fetch: kleine bis mittlere Clients ohne Zusatzpaket",
      "axios: größere Clients mit Interceptors, Timeouts und einheitlichen Fehlern",
      "Apollo: GraphQL-Frontend mit Cache und Query-State",
    ],
    notes: "Sprecher B fasst die Entscheidungsmatrix zusammen.",
  },
  {
    no: 20,
    speaker: "A+B",
    title: "Abschluss",
    bullets: [
      "Unser Projekt ist ein gutes Beispiel für API-Grenzen",
      "OpenAPI macht REST live testbar und dokumentiert",
      "VNBdigital zeigt GraphQL als flexible Datenquelle",
      "fetch, axios und Apollo sind Client-Werkzeuge für unterschiedliche Situationen",
    ],
    notes:
      "Beide Sprecher schließen gemeinsam. Danach Q&A und bei Zeit kurze Wiederholung der Live-Demo.",
  },
];

function xmlEscape(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function truncateJson(value, max = 1800) {
  const text = JSON.stringify(value, null, 2);
  return text.length > max ? `${text.slice(0, max)}\n...` : text;
}

function readJson(name) {
  const file = path.join(EXAMPLES, name);
  if (!fs.existsSync(file)) return null;
  return JSON.parse(fs.readFileSync(file, "utf-8"));
}

function makeScreenshot(name, title, command, body) {
  const lines = `${command}\n\n${body}`.split("\n").slice(0, 32);
  const lineHeight = 24;
  const height = 96 + lines.length * lineHeight;
  const text = lines
    .map((line, i) => `<text x="34" y="${86 + i * lineHeight}" class="code">${xmlEscape(line)}</text>`)
    .join("\n");
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="${height}" viewBox="0 0 1400 ${height}">
  <rect width="1400" height="${height}" rx="18" fill="#101827"/>
  <rect width="1400" height="54" rx="18" fill="#202A3A"/>
  <circle cx="34" cy="27" r="8" fill="#EF4444"/>
  <circle cx="60" cy="27" r="8" fill="#F59E0B"/>
  <circle cx="86" cy="27" r="8" fill="#22C55E"/>
  <text x="120" y="35" class="title">${xmlEscape(title)}</text>
  ${text}
  <style>
    .title { font: 600 22px Arial, sans-serif; fill: #E8EEF8; }
    .code { font: 18px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; fill: #E8EEF8; white-space: pre; }
  </style>
</svg>`;
  fs.writeFileSync(path.join(ASSETS, name), svg, "utf-8");
}

function buildScreenshots() {
  const summary = readJson("openapi_summary.json");
  const lookup = readJson("lookup_bochum.json");
  makeScreenshot(
    "openapi_summary.svg",
    "OpenAPI Schema Auszug",
    "GET http://127.0.0.1:8000/openapi.json",
    truncateJson(summary ?? { error: "Bitte zuerst npm run examples ausführen." }, 1600),
  );
  makeScreenshot(
    "lookup_output.svg",
    "REST Lookup Ausgabe",
    'curl "http://127.0.0.1:8000/api/lookup?lat=51.4818445&lon=7.2162363"',
    truncateJson(lookup ?? { error: "Bitte zuerst npm run examples ausführen." }, 1900),
  );
  makeScreenshot(
    "graphql_input.svg",
    "GraphQL Query Eingabe",
    "POST https://www.vnbdigital.de/gateway/graphql",
    `query ($coordinates: String, $filter: vnb_FilterInput) {
  vnb_coordinates(coordinates: $coordinates) {
    regions(filter: $filter) {
      _id
      name
      bbox
      layerUrl
    }
    vnbs(filter: $filter) {
      _id
      name
      bbox
      types
      voltageTypes
    }
  }
}

variables:
{
  "coordinates": "51.4818445,7.2162363",
  "filter": {
    "voltageTypes": ["Niederspannung", "Mittelspannung", "Hochspannung"],
    "withRegions": true
  }
}`,
  );
}

function addFooter(slide, item) {
  slide.addText(`Sprecher ${item.speaker}`, {
    x: 0.45,
    y: 7.08,
    w: 3.3,
    h: 0.22,
    fontSize: 8.5,
    color: theme.muted,
  });
  slide.addText(`${item.no}/20`, {
    x: 12.05,
    y: 7.08,
    w: 0.8,
    h: 0.22,
    fontSize: 8.5,
    color: theme.muted,
    align: "right",
  });
}

function addTitle(slide, title, subtitle) {
  slide.addText(title, {
    x: 0.55,
    y: 0.35,
    w: 11.9,
    h: 0.45,
    fontFace: "Arial",
    fontSize: 24,
    bold: true,
    color: theme.ink,
    margin: 0,
    breakLine: false,
  });
  if (subtitle) {
    slide.addText(subtitle, {
      x: 0.58,
      y: 0.92,
      w: 11.5,
      h: 0.45,
      fontSize: 12,
      color: theme.muted,
      margin: 0,
    });
  }
}

function addBullets(slide, bullets, x = 0.75, y = 1.28, w = 5.6, h = 4.7) {
  slide.addText(
    bullets.map((text) => ({ text, options: { bullet: { indent: 14 }, hanging: 4 } })),
    {
      x,
      y,
      w,
      h,
      fontSize: 14,
      color: theme.ink,
      breakLine: false,
      fit: "shrink",
      valign: "top",
      paraSpaceAfterPt: 8,
    },
  );
}

function addCode(slide, code, x = 6.75, y = 1.35, w = 5.85, h = 4.8) {
  slide.addShape(SHAPE.roundRect, {
    x,
    y,
    w,
    h,
    rectRadius: 0.08,
    fill: { color: theme.codeBg },
    line: { color: theme.codeBg },
  });
  slide.addText(code, {
    x: x + 0.22,
    y: y + 0.22,
    w: w - 0.44,
    h: h - 0.44,
    fontFace: "Consolas",
    fontSize: 10.5,
    color: theme.code,
    margin: 0,
    fit: "shrink",
    valign: "top",
    breakLine: false,
  });
}

function addCompare(slide, rows) {
  const x = 0.7;
  const y = 1.28;
  const widths = [3.0, 4.35, 4.35];
  const rowH = 0.58;
  rows.forEach((row, r) => {
    let cx = x;
    row.forEach((cell, c) => {
      slide.addShape(SHAPE.rect, {
        x: cx,
        y: y + r * rowH,
        w: widths[c],
        h: rowH,
        fill: { color: r === 0 ? "E8F0FE" : "FFFFFF" },
        line: { color: theme.line, width: 1 },
      });
      slide.addText(cell, {
        x: cx + 0.12,
        y: y + r * rowH + 0.12,
        w: widths[c] - 0.24,
        h: rowH - 0.16,
        fontSize: r === 0 ? 11.5 : 10.5,
        bold: r === 0,
        color: theme.ink,
        fit: "shrink",
        margin: 0,
      });
      cx += widths[c];
    });
  });
}

function addDiagram(slide, diagram) {
  const labels = diagram[0];
  const subs = diagram[1];
  const x0 = 0.75;
  const y = 2.05;
  const w = 2.65;
  labels.forEach((label, i) => {
    const x = x0 + i * 3.1;
    slide.addShape(SHAPE.roundRect, {
      x,
      y,
      w,
      h: 1.05,
      rectRadius: 0.06,
      fill: { color: i % 2 ? "ECFDF5" : "E8F0FE" },
      line: { color: i % 2 ? theme.green : theme.blue, width: 1.2 },
    });
    slide.addText(label, { x: x + 0.12, y: y + 0.18, w: w - 0.24, h: 0.28, fontSize: 12.2, bold: true, color: theme.ink, align: "center", margin: 0 });
    slide.addText(subs[i], { x: x + 0.12, y: y + 0.56, w: w - 0.24, h: 0.32, fontSize: 9.4, color: theme.muted, align: "center", margin: 0, fit: "shrink" });
    if (i < labels.length - 1) {
      slide.addShape(SHAPE.line, { x: x + w + 0.12, y: y + 0.52, w: 0.45, h: 0, line: { color: theme.muted, width: 1.3, beginArrowType: "none", endArrowType: "triangle" } });
    }
  });
}

async function buildPptx() {
  const pptx = new pptxgen();
  pptx.layout = "LAYOUT_WIDE";
  pptx.author = "VNB Atlas Seminar";
  pptx.subject = "GraphQL + REST - API-Design, Apollo, fetch vs. axios";
  pptx.title = "GraphQL + REST";
  pptx.company = "Deutschland VNB Atlas";
  pptx.lang = "de-DE";
  pptx.theme = {
    headFontFace: "Arial",
    bodyFontFace: "Arial",
    lang: "de-DE",
  };

  for (const item of slides) {
    const slide = pptx.addSlide();
    slide.background = { color: theme.bg };
    addTitle(slide, item.title, item.subtitle);

    if (item.no === 1) {
      slide.addShape(SHAPE.rect, { x: 0.6, y: 1.55, w: 12.0, h: 0.08, fill: { color: theme.blue }, line: { color: theme.blue } });
      addBullets(slide, item.bullets, 0.8, 2.0, 11.2, 2.0);
    } else if (item.compare) {
      addCompare(slide, item.compare);
    } else if (item.diagram) {
      addDiagram(slide, item.diagram);
    } else {
      addBullets(slide, item.bullets, 0.72, 1.22, item.code || item.screenshot ? 5.7 : 11.7, 5.6);
      if (item.code) addCode(slide, item.code);
      if (item.screenshot) {
        slide.addImage({
          path: path.join(ASSETS, item.screenshot),
          x: 6.65,
          y: 1.35,
          w: 5.95,
          h: 4.75,
          sizingCrop: false,
        });
      }
    }

    addFooter(slide, item);
    if (typeof slide.addNotes === "function") {
      slide.addNotes(`Sprecher ${item.speaker}: ${item.notes}`);
    }
  }

  await pptx.writeFile({ fileName: path.join(OUT, "graphql-rest-api-design-vnb-atlas.pptx") });
}

function writeMaterials() {
  const script = slides
    .map((s) => `## Folie ${s.no}: ${s.title}\n\n**Sprecher:** ${s.speaker}\n\n${s.notes}\n\nKernaussagen:\n${(s.bullets ?? []).map((b) => `- ${b}`).join("\n") || "- Siehe Vergleich/Tabelle auf der Folie."}\n`)
    .join("\n");
  fs.writeFileSync(path.join(MATERIALS, "sprecher-skript.md"), `# Sprecher-Skript\n\n${script}`, "utf-8");

  const handout = `# Lernmaterial: GraphQL + REST im VNB Atlas

## Kurzfassung

Unser Projekt nutzt zwei API-Welten sinnvoll kombiniert: VNBdigital wird als externe GraphQL-Datenquelle verwendet, während unser eigenes FastAPI-Backend eine stabile REST-API für das Frontend bereitstellt.

## REST im Projekt

- API-Dokumentation: \`http://127.0.0.1:8000/docs\`
- Maschinenlesbares Schema: \`http://127.0.0.1:8000/openapi.json\`
- Wichtige Endpunkte: \`/api/operators\`, \`/api/areas\`, \`/api/search\`, \`/api/lookup\`

## GraphQL im Projekt

Die Datei \`vnbdigital/simple_client.py\` enthält die GraphQL-Query gegen VNBdigital. Sie fragt Daten für Koordinaten ab und nutzt Variablen für Filter wie Spannungsebenen.

## fetch vs. axios

\`fetch\` ist im Browser eingebaut und reicht für kleine API-Clients gut aus. axios bietet mehr Komfort bei Fehlerbehandlung, Timeouts, Interceptors und zentraler Konfiguration.

## Apollo

Apollo Client ist ein spezialisierter GraphQL-Client. Er verwaltet Query-Ausführung, Cache, Loading-Status und Fehlerzustände. Apollo wäre sinnvoll, wenn unser Frontend direkt GraphQL konsumieren würde.

## Wichtigster Projektbefund

\`/api/areas\` sollte ein konkretes Pydantic-Response-Model erhalten, damit OpenAPI die GeoJSON-Struktur genauer dokumentiert.
`;
  fs.writeFileSync(path.join(MATERIALS, "lernmaterial.md"), handout, "utf-8");

  const demo = `# Demo-Ablauf

## Vorbereitung

\`\`\`bash
./scripts/dev.sh
\`\`\`

## REST-Demo

1. Öffne \`http://127.0.0.1:8000/docs\`.
2. Führe \`GET /api/operators\` mit \`q=westnetz\` aus.
3. Führe \`GET /api/areas\` mit \`country=DE\`, \`federal_state=NW\`, \`voltage_level=Hochspannung\` aus.
4. Führe \`GET /api/lookup\` mit \`lat=51.4818445\`, \`lon=7.2162363\` aus.
5. Öffne \`http://127.0.0.1:8000/openapi.json\`.

## Frontend-Demo

1. Öffne \`http://127.0.0.1:5173\`.
2. Zeige Suche, Karte und Filter.
3. Öffne \`frontend/src/api-client.ts\` und erkläre den fetch-Wrapper.

## GraphQL/Apollo-Demo

1. Öffne \`vnbdigital/simple_client.py\`.
2. Zeige die Query \`COORDINATES_QUERY\`.
3. Erkläre Variablen: \`coordinates\`, \`filter\`, \`voltageTypes\`.
4. Zeige \`materials/code-examples.md\` für Apollo.
`;
  fs.writeFileSync(path.join(MATERIALS, "demo-ablauf.md"), demo, "utf-8");

  const codeExamples = `# Code-Beispiele

## fetch im Projekt

\`\`\`ts
async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(\`\${API_BASE_URL}\${path}\`, {
    headers: { Accept: "application/json" },
  });

  if (!response.ok) {
    throw new ApiError(\`API-Fehler \${response.status}\`, response.status);
  }

  return (await response.json()) as T;
}
\`\`\`

## axios-Variante

\`\`\`ts
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
\`\`\`

## Apollo-Beispiel

\`\`\`tsx
import { gql, useQuery } from "@apollo/client";

const GET_VNB_BY_COORDINATES = gql\`
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
\`;

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
\`\`\`
`;
  fs.writeFileSync(path.join(MATERIALS, "code-examples.md"), codeExamples, "utf-8");
}

buildScreenshots();
writeMaterials();
await buildPptx();

console.log(`Generated ${path.join(OUT, "graphql-rest-api-design-vnb-atlas.pptx")}`);
