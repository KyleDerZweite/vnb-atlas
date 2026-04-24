import { getAreas, getOperators, search } from "./api-client";
import { AtlasMap } from "./map";
import { readFilters, readSearchQuery, validateSearchQuery, type SearchFormElements } from "./search";
import type { AreaFeature, Operator, SearchResult } from "./types";
import {
  announceAreaCount,
  renderDetails,
  renderOperatorFilter,
  renderResults,
  setError,
  setStatus,
  type UiElements,
} from "./ui";

const elements = getElements();
let allOperators: Operator[] = [];
let visibleFeatures: AreaFeature[] = [];

const atlasMap = new AtlasMap("map", (feature, focusDetail) => {
  renderDetails(elements.ui, feature, focusDetail);
});

void initialize();

async function initialize(): Promise<void> {
  setStatus(elements.ui, "Lade Betreiber und Gebiete...");
  try {
    allOperators = await getOperators();
    renderOperatorFilter(elements.ui.operatorFilter, allOperators);
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
  elements.form.accuracyFilter.addEventListener("change", () => {
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
    setStatus(elements.ui, `${response.total} Suchtreffer, ${visibleFeatures.length} passende Gebiete sichtbar.`);
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
    announceAreaCount(elements.ui, visibleFeatures.length);
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
  const accuracyFilter = requireElement<HTMLSelectElement>("accuracy-filter");

  return {
    form: {
      form,
      input,
      operatorFilter,
      accuracyFilter,
    },
    ui: {
      status: requireElement("status"),
      formError: requireElement("form-error"),
      resultsList: requireElement<HTMLOListElement>("results-list"),
      detailPanel: requireElement("detail-panel"),
      detailContent: requireElement("detail-content"),
      operatorFilter,
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
