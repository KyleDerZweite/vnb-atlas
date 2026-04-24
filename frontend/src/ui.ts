import type { AreaFeature, FederalState, Operator } from "./types";

export interface UiElements {
  status: HTMLElement;
  formError: HTMLElement;
  resultsList: HTMLOListElement;
  detailPanel: HTMLElement;
  detailContent: HTMLElement;
  federalStateFilter: HTMLSelectElement;
  operatorFilter: HTMLSelectElement;
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
    button.innerHTML = `
      <span class="result-title">${escapeHtml(feature.properties.name)}</span>
      <span>${escapeHtml(feature.properties.operatorName)}</span>
      <span class="meta-line">Pilotdatensatz: ${escapeHtml(feature.properties.federalState)}</span>
      <span class="meta-line">${escapeHtml(feature.properties.places.join(", "))}</span>
    `;
    button.addEventListener("click", () => onSelect(feature, true));
    item.append(button);
    elements.resultsList.append(item);
  }
}

export function renderDetails(elements: UiElements, feature: AreaFeature, focusDetail = true): void {
  const properties = feature.properties;
  elements.detailContent.innerHTML = `
    <p class="notice">${escapeHtml(properties.mockNotice)}</p>
    <dl class="detail-list">
      <div><dt>Gebiet</dt><dd>${escapeHtml(properties.name)}</dd></div>
      <div><dt>Betreiber</dt><dd>${escapeHtml(properties.operatorName)}</dd></div>
      <div><dt>Pilotdatensatz</dt><dd>${escapeHtml(properties.country)} / ${escapeHtml(properties.federalState)}</dd></div>
      <div><dt>Orte</dt><dd>${escapeHtml(properties.places.join(", "))}</dd></div>
      <div><dt>PLZ</dt><dd>${escapeHtml(properties.postalCodes.join(", "))}</dd></div>
      <div><dt>Quelle</dt><dd>${escapeHtml(properties.source)}</dd></div>
      <div><dt>Aktualisiert</dt><dd>${escapeHtml(properties.updatedAt)}</dd></div>
    </dl>
  `;
  highlightResultButton(properties.id);
  if (focusDetail) {
    elements.detailPanel.focus();
  }
}

export function announceAreaCount(elements: UiElements, count: number, coverageLabel: string): void {
  const suffix = count === 1 ? "Gebiet" : "Gebiete";
  setStatus(elements, `${count} ${suffix} sichtbar. MVP-Datenabdeckung: ${coverageLabel}. Mock-Daten / nicht amtlich.`);
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

function escapeHtml(value: string): string {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
