export type OperatorType = "VNB" | "ÜNB" | "UNKNOWN";
export type Accuracy = "mock" | "municipality_approximation" | "verified";
export type VoltageLevel = "Niederspannung" | "Mittelspannung" | "Hochspannung";
export const DEFAULT_VOLTAGE_LEVEL: VoltageLevel = "Niederspannung";

export interface Operator {
  id: string;
  name: string;
  type: OperatorType;
  website: string;
  parentCompany: string | null;
  description: string;
  voltageLevels: string[];
  country: "DE";
  federalStates: string[];
  dataCoverage: "none" | "mock" | "partial" | "verified";
  mockNotice: string;
}

export interface AreaProperties {
  id: string;
  name: string;
  operatorId: string;
  operatorName: string;
  country: "DE";
  federalState: string;
  accuracy: Accuracy;
  source: string;
  updatedAt: string;
  mockNotice: string;
  places: string[];
  postalCodes: string[];
  voltageLevels: string[];
  voltageLevel?: string;
  vnbdigitalId?: string;
  samplePointCount?: number;
}

export interface AreaFeature {
  type: "Feature";
  properties: AreaProperties;
  geometry: GeoJSON.Geometry;
  bbox?: number[];
}

export interface AreaFeatureCollection {
  type: "FeatureCollection";
  features: AreaFeature[];
  mockNotice: string;
}

export interface SearchResult {
  type: "operator" | "area" | "place" | "postalCode";
  label: string;
  operatorId: string;
  operatorName: string;
  areaId: string | null;
  areaName: string | null;
  accuracy: Accuracy | null;
  matchedField: string;
}

export interface SearchResponse {
  query: string;
  total: number;
  results: SearchResult[];
}

export interface LookupResponse {
  match: null | {
    area: AreaFeature;
    operator: Operator;
  };
  matches: Array<{
    area: AreaFeature;
    operator: Operator;
  }>;
}

export interface AreaFilters {
  operatorId?: string;
  country?: "DE";
  federalState?: string;
  voltageLevel?: VoltageLevel;
}

export interface FederalState {
  id: string;
  name: string;
  hasAreaData: boolean;
  dataStatus: "mock" | "partial" | "verified" | "not_available";
}

export interface Coverage {
  country: "DE";
  federalStates: Record<
    string,
    {
      id: string;
      name: string;
      hasAreas: boolean;
      status: "mock" | "partial" | "verified" | "not_available";
    }
  >;
}
