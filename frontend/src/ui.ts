import type { AreaFeature, FederalState, Operator } from "./types";

export interface UiElements {
  status: HTMLElement;
  formError: HTMLElement;
  resultsList: HTMLOListElement;
  detailPanel: HTMLElement;
  detailContent: HTMLElement;
  federalStateFilter: HTMLSelectElement;
  operatorFilter: HTMLSelectElement;
  voltageLevelFilter: HTMLSelectElement;
}

export function setStatus(elements: UiElements, message: string): void {
  elements.status.textContent = message;
}

export function setError(elements: UiElements, message: string | null): void {
  elements.formError.hidden = !message;
  elements.formError.textContent = message ?? "";
}

export function renderOperatorFilter(select: HTMLSelectElement, operators: Operator[]): void {
  const currentValue = select.value;
  select.replaceChildren(new Option("Alle Betreiber", ""));
  for (const operator of operators) {
    select.append(new Option(operator.name, operator.id));
  }
  select.value = operators.some((operator) => operator.id === currentValue) ? currentValue : "";
}

export function renderFederalStateFilter(select: HTMLSelectElement, federalStates: FederalState[]): void {
  const currentValue = select.value;
  select.replaceChildren(new Option("Alle verfuegbaren Daten", ""));
  for (const federalState of federalStates) {
    const status = federalState.hasAreaData ? "Pilotdaten" : "keine Daten";
    const option = new Option(`${federalState.name} (${status})`, federalState.id);
    option.disabled = !federalState.hasAreaData;
    select.append(option);
  }
  select.value = federalStates.some((state) => state.id === currentValue && state.hasAreaData) ? currentValue : "";
}

export function renderResults(
  elements: UiElements,
  features: AreaFeature[],
  onSelect: (feature: AreaFeature, focusDetail: boolean) => void,
): void {
  elements.resultsList.replaceChildren();
  if (features.length === 0) {
    const item = document.createElement("li");
    item.className = "empty-result";
    item.textContent = "Keine Gebiete fuer die aktuelle Suche oder Filterauswahl gefunden.";
    elements.resultsList.append(item);
    return;
  }

  for (const feature of features) {
    const item = document.createElement("li");
    const button = document.createElement("button");
    button.type = "button";
    button.className = "result-button";
    button.dataset.areaId = feature.properties.id;
    button.setAttribute("aria-controls", "detail-panel");
    button.append(
      createSpan(feature.properties.name, "result-title"),
      createSpan(feature.properties.operatorName),
      createSpan(`VNBdigital-Mesh: ${feature.properties.federalState}`, "meta-line"),
      createSpan(formatVoltageLevels(feature.properties.voltageLevels), "meta-line"),
      createSpan(feature.properties.places.join(", "), "meta-line"),
    );
    button.addEventListener("click", () => onSelect(feature, true));
    item.append(button);
    elements.resultsList.append(item);
  }
}

export function renderDetails(elements: UiElements, feature: AreaFeature, focusDetail = true): void {
  const properties = feature.properties;
  const notice = document.createElement("p");
  notice.className = "notice";
  notice.textContent = properties.mockNotice;

  const details = document.createElement("dl");
  details.className = "detail-list";
  details.append(
    createDetailItem("Gebiet", properties.name),
    createDetailItem("Betreiber", properties.operatorName),
    createDetailItem("Spannungsebene", formatVoltageLevels(properties.voltageLevels)),
    createDetailItem("Datensatz", `${properties.country} / ${properties.federalState}`),
    createDetailItem("Orte", properties.places.join(", ")),
    createDetailItem("PLZ", properties.postalCodes.join(", ")),
    createDetailItem("Quelle", properties.source),
    createDetailItem("Aktualisiert", properties.updatedAt),
  );

  elements.detailContent.replaceChildren(notice, details);
  highlightResultButton(properties.id);
  if (focusDetail) {
    elements.detailPanel.focus();
  }
}

export function announceAreaCount(elements: UiElements, count: number, coverageLabel: string): void {
  const suffix = count === 1 ? "Gebiet" : "Gebiete";
  setStatus(elements, `${count} ${suffix} sichtbar. MVP-Datenabdeckung: ${coverageLabel}. VNBdigital-Meshdaten / nicht amtlich.`);
}

export function showNoCoverageMessage(elements: UiElements): void {
  setStatus(elements, "Fuer dieses Gebiet liegen im MVP noch keine VNB-GIS-Daten vor.");
}

function highlightResultButton(areaId: string): void {
  document.querySelectorAll<HTMLButtonElement>(".result-button").forEach((button) => {
    const active = button.dataset.areaId === areaId;
    button.classList.toggle("is-active", active);
    button.setAttribute("aria-pressed", String(active));
  });
}

function createSpan(text: string, className?: string): HTMLSpanElement {
  const span = document.createElement("span");
  if (className) {
    span.className = className;
  }
  span.textContent = text;
  return span;
}

function createDetailItem(termText: string, descriptionText: string): HTMLDivElement {
  const wrapper = document.createElement("div");
  const term = document.createElement("dt");
  const description = document.createElement("dd");
  term.textContent = termText;
  description.textContent = descriptionText;
  wrapper.append(term, description);
  return wrapper;
}

function formatVoltageLevels(voltageLevels: string[]): string {
  return voltageLevels.length > 0 ? voltageLevels.join(", ") : "Spannungsebene unbekannt";
}
