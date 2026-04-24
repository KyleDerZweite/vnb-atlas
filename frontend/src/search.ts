import type { Accuracy, AreaFilters } from "./types";

export interface SearchFormElements {
  form: HTMLFormElement;
  input: HTMLInputElement;
  operatorFilter: HTMLSelectElement;
  accuracyFilter: HTMLSelectElement;
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
  const operatorId = elements.operatorFilter.value || undefined;
  const accuracy = (elements.accuracyFilter.value || undefined) as Accuracy | undefined;
  return { operatorId, accuracy };
}
