import { getAreas, getCoverage, getFederalStates, getOperators, search } from "./api-client";
import { AtlasMap } from "./map";
import { readFilters, readSearchQuery, validateSearchQuery, type SearchFormElements } from "./search";
import { DEFAULT_VOLTAGE_LEVEL, type AreaFeature, type Operator, type SearchResult } from "./types";
import {
  announceAreaCount,
  renderFederalStateFilter,
  renderDetails,
  renderOperatorFilter,
  renderResults,
  setError,
  setStatus,
  showNoCoverageMessage,
  type UiElements,
} from "./ui";

const elements = getElements();
let allOperators: Operator[] = [];
let visibleFeatures: AreaFeature[] = [];
let coverageLabel = "Nordrhein-Westfalen";

const atlasMap = new AtlasMap("map", (feature, focusDetail) => {
  renderDetails(elements.ui, feature, focusDetail);
}, () => {
  showNoCoverageMessage(elements.ui);
});

void initialize();

async function initialize(): Promise<void> {
  setStatus(elements.ui, "Lade Betreiber und Gebiete...");
  try {
    elements.form.voltageLevelFilter.value = DEFAULT_VOLTAGE_LEVEL;
    const [operators, federalStates, coverage] = await Promise.all([
      getOperators({ voltageLevel: DEFAULT_VOLTAGE_LEVEL }),
      getFederalStates(),
      getCoverage(),
    ]);
    allOperators = operators;
    renderOperatorFilter(elements.ui.operatorFilter, allOperators);
    renderFederalStateFilter(elements.ui.federalStateFilter, federalStates);
    coverageLabel =
      Object.values(coverage.federalStates)
        .filter((state) => state.hasAreas)
        .map((state) => state.name)
        .join(", ") || coverageLabel;
    setStatus(elements.ui, `MVP-Datenabdeckung: ${coverageLabel}. Andere Bundeslaender sind vorbereitet.`);
    await loadAreas();
    bindEvents();
    window.setTimeout(() => atlasMap.invalidateSize(), 100);
  } catch (error) {
    setStatus(elements.ui, "API nicht erreichbar.");
    setError(elements.ui, error instanceof Error ? error.message : "Unbekannter Fehler beim Laden.");
  }
}

function bindEvents(): void {
  elements.form.form.addEventListener("submit", (event) => {
    event.preventDefault();
    void runSearch();
  });
  elements.form.operatorFilter.addEventListener("change", () => {
    void loadAreas();
  });
  elements.form.federalStateFilter.addEventListener("change", () => {
    void loadAreas();
  });
  elements.form.voltageLevelFilter.addEventListener("change", async () => {
    const filters = readFilters(elements.form);
    allOperators = await getOperators({ voltageLevel: filters.voltageLevel });
    renderOperatorFilter(elements.ui.operatorFilter, allOperators);
    void loadAreas();
  });
}

async function runSearch(): Promise<void> {
  const query = readSearchQuery(elements.form.input);
  const validationError = validateSearchQuery(query);
  if (validationError) {
    setError(elements.ui, validationError);
    elements.form.input.focus();
    return;
  }
  setError(elements.ui, null);

  if (!query) {
    await loadAreas();
    return;
  }

  setStatus(elements.ui, "Suche laeuft...");
  try {
    const response = await search(query);
    const areaIds = new Set(response.results.map(resultToAreaId).filter(isString));
    await loadAreas(areaIds);
    if (visibleFeatures.length === 0) {
      showNoCoverageMessage(elements.ui);
      return;
    }
    setStatus(elements.ui, `${response.total} Suchtreffer, ${visibleFeatures.length} passende Pilotgebiete sichtbar.`);
  } catch (error) {
    setStatus(elements.ui, "Suche fehlgeschlagen.");
    setError(elements.ui, error instanceof Error ? error.message : "Unbekannter Suchfehler.");
  }
}

async function loadAreas(allowedAreaIds?: Set<string>): Promise<void> {
  setStatus(elements.ui, "Lade Gebiete...");
  try {
    const collection = await getAreas(readFilters(elements.form));
    visibleFeatures = allowedAreaIds
      ? collection.features.filter((feature) => allowedAreaIds.has(feature.properties.id))
      : collection.features;
    const visibleCollection = { ...collection, features: visibleFeatures };
    atlasMap.renderAreas(visibleCollection);
    renderResults(elements.ui, visibleFeatures, (feature, focusDetail) => {
      atlasMap.selectArea(feature, focusDetail);
      atlasMap.focusArea(feature.properties.id);
    });
    atlasMap.fitRenderedAreas();
    announceAreaCount(elements.ui, visibleFeatures.length, coverageLabel);
  } catch (error) {
    visibleFeatures = [];
    renderResults(elements.ui, [], () => undefined);
    setStatus(elements.ui, "Gebiete konnten nicht geladen werden.");
    setError(elements.ui, error instanceof Error ? error.message : "Unbekannter Ladefehler.");
  }
}

function resultToAreaId(result: SearchResult): string | null {
  if (result.areaId) {
    return result.areaId;
  }
  const operatorArea = visibleFeatures.find((feature) => feature.properties.operatorId === result.operatorId);
  return operatorArea?.properties.id ?? null;
}

function isString(value: string | null): value is string {
  return typeof value === "string";
}

function getElements(): { form: SearchFormElements; ui: UiElements } {
  const form = requireElement<HTMLFormElement>("search-form");
  const input = requireElement<HTMLInputElement>("search-input");
  const operatorFilter = requireElement<HTMLSelectElement>("operator-filter");
  const federalStateFilter = requireElement<HTMLSelectElement>("federal-state-filter");
  const voltageLevelFilter = requireElement<HTMLSelectElement>("voltage-level-filter");

  return {
    form: {
      form,
      input,
      federalStateFilter,
      operatorFilter,
      voltageLevelFilter,
    },
    ui: {
      status: requireElement("status"),
      formError: requireElement("form-error"),
      resultsList: requireElement<HTMLOListElement>("results-list"),
      detailPanel: requireElement("detail-panel"),
      detailContent: requireElement("detail-content"),
      federalStateFilter,
      operatorFilter,
      voltageLevelFilter,
    },
  };
}

function requireElement<T extends HTMLElement>(id: string): T {
  const element = document.getElementById(id);
  if (!element) {
    throw new Error(`Missing element #${id}`);
  }
  return element as T;
}
