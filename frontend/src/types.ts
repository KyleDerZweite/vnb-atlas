export type OperatorType = "VNB" | "ÜNB" | "UNKNOWN";
export type Accuracy = "mock" | "municipality_approximation" | "verified";

export interface Operator {
  id: string;
  name: string;
  type: OperatorType;
  website: string;
  parentCompany: string | null;
  description: string;
  voltageLevels: string[];
  mockNotice: string;
}

export interface AreaProperties {
  id: string;
  name: string;
  operatorId: string;
  operatorName: string;
  accuracy: Accuracy;
  source: string;
  updatedAt: string;
  mockNotice: string;
  places: string[];
  postalCodes: string[];
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
}

export interface AreaFilters {
  operatorId?: string;
  accuracy?: Accuracy;
}
