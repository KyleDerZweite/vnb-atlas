import type { Feature } from "geojson";

import type { AreaFeature } from "./types";

export function asAreaFeature(feature: Feature | undefined): AreaFeature {
  if (!feature) {
    throw new Error("Leaflet callback did not provide a GeoJSON feature.");
  }
  return feature as unknown as AreaFeature;
}
