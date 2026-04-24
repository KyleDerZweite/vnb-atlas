import type { AreaFilters } from "./types";

export interface SearchFormElements {
  form: HTMLFormElement;
  input: HTMLInputElement;
  federalStateFilter: HTMLSelectElement;
  operatorFilter: HTMLSelectElement;
}

export function readSearchQuery(input: HTMLInputElement): string {
  return input.value.trim();
}

export function validateSearchQuery(query: string): string | null {
  if (!query) {
    return null;
  }
  if (query.length > 80) {
    return "Die Suche darf hoechstens 80 Zeichen enthalten.";
  }
  return null;
}

export function readFilters(elements: SearchFormElements): AreaFilters {
  const federalState = elements.federalStateFilter.value || undefined;
  const operatorId = elements.operatorFilter.value || undefined;
  return { country: "DE", federalState, operatorId };
}
