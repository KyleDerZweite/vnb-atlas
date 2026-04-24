import L from "leaflet";
import "leaflet/dist/leaflet.css";
import type { GeoJsonObject } from "geojson";

import type { AreaFeature, AreaFeatureCollection } from "./types";

type SelectHandler = (feature: AreaFeature, focusDetail: boolean) => void;
type EmptyMapClickHandler = () => void;
type BoundsTuple = [number, number, number, number];

const defaultFillOpacity = 0.26;
const hoverFillOpacity = 0.38;
const selectedFillOpacity = 0.44;
const baseSaturation = 72;
const baseLightness = 40;
const adjacencyPaddingDegrees = 0.04;
const goldenAngle = 137.508;

const germanyCenter: L.LatLngExpression = [51.1657, 10.4515];
const germanyViewBounds: L.LatLngBoundsExpression = [
  [46.9, 4.8],
  [55.4, 16.1],
];
const germanyPanBounds: L.LatLngBoundsExpression = [
  [45.4, 2.5],
  [56.7, 18.8],
];

export class AtlasMap {
  private readonly map: L.Map;
  private layer: L.GeoJSON | null = null;
  private featureLayers = new Map<string, L.Layer>();
  private featuresByAreaId = new Map<string, AreaFeature>();
  private operatorColors = new Map<string, string>();
  private selectedAreaId: string | null = null;

  constructor(containerId: string, onSelect: SelectHandler, onEmptyMapClick: EmptyMapClickHandler) {
    this.map = L.map(containerId, {
      center: germanyCenter,
      zoom: 6,
      minZoom: 6,
      maxBounds: germanyPanBounds,
      maxBoundsViscosity: 0.85,
      keyboard: true,
      scrollWheelZoom: true,
    });
    this.createPanes();

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 18,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    }).addTo(this.map);

    this.onSelect = onSelect;
    this.onEmptyMapClick = onEmptyMapClick;
    this.map.on("click", () => this.onEmptyMapClick());
  }

  private readonly onSelect: SelectHandler;
  private readonly onEmptyMapClick: EmptyMapClickHandler;

  private createPanes(): void {
    this.map.createPane("vnbAreas").style.zIndex = "650";
  }

  renderAreas(collection: AreaFeatureCollection): void {
    if (this.layer) {
      this.map.removeLayer(this.layer);
    }
    this.featureLayers.clear();
    this.featuresByAreaId.clear();
    this.operatorColors = buildOperatorColors(collection.features);

    this.layer = L.geoJSON(collection as unknown as GeoJsonObject, {
      pane: "vnbAreas",
      style: (feature) => this.getAreaStyle(feature as unknown as AreaFeature),
      onEachFeature: (feature, layer) => {
        const areaFeature = feature as unknown as AreaFeature;
        const areaId = areaFeature.properties.id;
        this.featureLayers.set(areaId, layer);
        this.featuresByAreaId.set(areaId, areaFeature);
        layer.bindTooltip(`${areaFeature.properties.name} - ${areaFeature.properties.operatorName}`);
        layer.on({
          click: (event) => {
            L.DomEvent.stopPropagation(event);
            this.selectArea(areaFeature, true);
          },
          mouseover: () => this.applyHover(layer, areaId),
          mouseout: () => this.resetLayerStyle(areaId),
          add: () => this.makeLayerFocusable(layer, areaFeature),
        });
      },
    }).addTo(this.map);
    this.layer.bringToFront();
  }

  selectArea(feature: AreaFeature, focusDetail: boolean): void {
    this.selectedAreaId = feature.properties.id;
    this.updateSelectionStyles();
    const layer = this.featureLayers.get(feature.properties.id);
    if (layer instanceof L.Path) {
      layer.bringToFront();
    }
    this.onSelect(feature, focusDetail);
  }

  focusArea(areaId: string): void {
    const layer = this.featureLayers.get(areaId);
    if (layer && hasBounds(layer)) {
      const bounds = layer.getBounds();
      if (bounds.isValid()) {
        this.fitBounds(bounds.pad(0.35), 11);
      }
    }
  }

  fitRenderedAreas(): void {
    if (!this.layer) {
      this.showGermanyView();
      return;
    }

    const bounds = this.layer.getBounds();
    if (bounds.isValid()) {
      this.fitBounds(bounds.pad(0.18), 10);
    } else {
      this.showGermanyView();
    }
  }

  invalidateSize(): void {
    this.map.invalidateSize();
  }

  showGermanyView(): void {
    this.map.fitBounds(germanyViewBounds, { padding: [18, 18], maxZoom: 6 });
  }

  private fitBounds(bounds: L.LatLngBounds, maxZoom: number): void {
    this.map.fitBounds(bounds, {
      maxZoom,
      ...this.getOverlayAwarePadding(),
    });
  }

  private getOverlayAwarePadding(): L.FitBoundsOptions {
    const width = this.map.getContainer().clientWidth;
    if (width <= 960) {
      return { padding: [18, 18] };
    }

    return {
      paddingTopLeft: [430, 40],
      paddingBottomRight: [380, 40],
    };
  }

  private getAreaStyle(feature: AreaFeature, state: "default" | "hover" | "selected" = "default"): L.PathOptions {
    const color = this.getOperatorColor(feature.properties.operatorId);
    const isSelected = state === "selected";
    return {
      color,
      fillColor: color,
      weight: isSelected ? 5 : state === "hover" ? 4 : 3,
      fillOpacity: isSelected ? selectedFillOpacity : state === "hover" ? hoverFillOpacity : defaultFillOpacity,
    };
  }

  private getOperatorColor(operatorId: string): string {
    return this.operatorColors.get(operatorId) ?? hslToHex(stableHue(operatorId), baseSaturation, baseLightness);
  }

  private makeLayerFocusable(layer: L.Layer, feature: AreaFeature): void {
    const element = layer.getPane()?.querySelector(`[class~="leaflet-interactive"]`);
    const pathElement = layer instanceof L.Path ? layer.getElement() : element;
    if (!pathElement) {
      return;
    }
    pathElement.setAttribute("tabindex", "0");
    pathElement.setAttribute("role", "button");
    pathElement.setAttribute("aria-label", `${feature.properties.name}, ${feature.properties.operatorName}`);
    pathElement.addEventListener("focus", () => this.applyHover(layer, feature.properties.id));
    pathElement.addEventListener("blur", () => this.resetLayerStyle(feature.properties.id));
    pathElement.addEventListener("keydown", (event) => {
      if (event instanceof KeyboardEvent && (event.key === "Enter" || event.key === " ")) {
        event.preventDefault();
        this.selectArea(feature, true);
      }
    });
  }

  private applyHover(layer: L.Layer, areaId: string): void {
    if (layer instanceof L.Path) {
      const feature = this.featuresByAreaId.get(areaId);
      if (feature) {
        layer.setStyle(this.getAreaStyle(feature, "hover"));
      }
      layer.bringToFront();
    }
  }

  private resetLayerStyle(areaId: string): void {
    const layer = this.featureLayers.get(areaId);
    const feature = this.featuresByAreaId.get(areaId);
    if (layer instanceof L.Path) {
      layer.setStyle(feature ? this.getAreaStyle(feature, areaId === this.selectedAreaId ? "selected" : "default") : {});
    }
  }

  private updateSelectionStyles(): void {
    this.featureLayers.forEach((layer, areaId) => {
      const feature = this.featuresByAreaId.get(areaId);
      if (layer instanceof L.Path) {
        layer.setStyle(feature ? this.getAreaStyle(feature, areaId === this.selectedAreaId ? "selected" : "default") : {});
      }
    });
  }
}

function hasBounds(layer: L.Layer): layer is L.Layer & { getBounds: () => L.LatLngBounds } {
  return "getBounds" in layer && typeof layer.getBounds === "function";
}

function buildOperatorColors(features: AreaFeature[]): Map<string, string> {
  const featuresByOperator = groupFeaturesByOperator(features);
  const operatorIds = [...featuresByOperator.keys()];
  const adjacentOperators = buildOperatorAdjacency(featuresByOperator);
  const orderedOperatorIds = operatorIds.sort((left, right) => {
    const degreeDelta = (adjacentOperators.get(right)?.size ?? 0) - (adjacentOperators.get(left)?.size ?? 0);
    return degreeDelta || left.localeCompare(right);
  });
  const colors = new Map<string, string>();
  const assignedHues = new Map<string, number>();
  const candidateHues = createCandidateHues(Math.max(24, operatorIds.length * 4));

  for (const operatorId of orderedOperatorIds) {
    const hue = chooseHue(operatorId, candidateHues, assignedHues, adjacentOperators.get(operatorId) ?? new Set());
    assignedHues.set(operatorId, hue);
    colors.set(operatorId, hslToHex(hue, baseSaturation, baseLightness));
  }

  return colors;
}

function groupFeaturesByOperator(features: AreaFeature[]): Map<string, AreaFeature[]> {
  const groups = new Map<string, AreaFeature[]>();
  for (const feature of features) {
    const operatorId = feature.properties.operatorId;
    groups.set(operatorId, [...(groups.get(operatorId) ?? []), feature]);
  }
  return groups;
}

function buildOperatorAdjacency(featuresByOperator: Map<string, AreaFeature[]>): Map<string, Set<string>> {
  const operatorIds = [...featuresByOperator.keys()];
  const adjacency = new Map(operatorIds.map((operatorId) => [operatorId, new Set<string>()]));

  for (let leftIndex = 0; leftIndex < operatorIds.length; leftIndex += 1) {
    for (let rightIndex = leftIndex + 1; rightIndex < operatorIds.length; rightIndex += 1) {
      const leftOperatorId = operatorIds[leftIndex];
      const rightOperatorId = operatorIds[rightIndex];
      const leftFeatures = featuresByOperator.get(leftOperatorId) ?? [];
      const rightFeatures = featuresByOperator.get(rightOperatorId) ?? [];
      if (leftFeatures.some((left) => rightFeatures.some((right) => areFeaturesAdjacent(left, right)))) {
        adjacency.get(leftOperatorId)?.add(rightOperatorId);
        adjacency.get(rightOperatorId)?.add(leftOperatorId);
      }
    }
  }

  return adjacency;
}

function areFeaturesAdjacent(left: AreaFeature, right: AreaFeature): boolean {
  return bboxesIntersect(expandBbox(featureBbox(left), adjacencyPaddingDegrees), expandBbox(featureBbox(right), adjacencyPaddingDegrees));
}

function featureBbox(feature: AreaFeature): BoundsTuple {
  if (feature.bbox?.length === 4) {
    return [feature.bbox[0], feature.bbox[1], feature.bbox[2], feature.bbox[3]];
  }

  const points = collectCoordinatePairs(geometryCoordinates(feature.geometry));
  const lons = points.map((point) => point[0]);
  const lats = points.map((point) => point[1]);
  return [Math.min(...lons), Math.min(...lats), Math.max(...lons), Math.max(...lats)];
}

function collectCoordinatePairs(value: unknown): Array<[number, number]> {
  if (!Array.isArray(value)) {
    return [];
  }
  if (value.length >= 2 && typeof value[0] === "number" && typeof value[1] === "number") {
    return [[value[0], value[1]]];
  }
  return value.flatMap((item) => collectCoordinatePairs(item));
}

function expandBbox([minLon, minLat, maxLon, maxLat]: BoundsTuple, padding: number): BoundsTuple {
  return [minLon - padding, minLat - padding, maxLon + padding, maxLat + padding];
}

function bboxesIntersect(left: BoundsTuple, right: BoundsTuple): boolean {
  return !(left[2] < right[0] || right[2] < left[0] || left[3] < right[1] || right[3] < left[1]);
}

function createCandidateHues(count: number): number[] {
  return Array.from({ length: count }, (_, index) => Math.round((index * goldenAngle) % 360));
}

function chooseHue(
  operatorId: string,
  candidates: number[],
  assignedHues: Map<string, number>,
  adjacentOperatorIds: Set<string>,
): number {
  const adjacentHues = [...adjacentOperatorIds].map((id) => assignedHues.get(id)).filter(isNumber);
  const allHues = [...assignedHues.values()];
  const unusedCandidates = candidates.filter((hue) => !allHues.includes(hue));
  let bestHue = candidates[0] ?? stableHue(operatorId);
  let bestScore = Number.NEGATIVE_INFINITY;

  for (const hue of unusedCandidates.length > 0 ? unusedCandidates : candidates) {
    const adjacentDistance = minHueDistance(hue, adjacentHues);
    const globalDistance = minHueDistance(hue, allHues);
    const score = adjacentDistance * 10 + globalDistance + stableTieBreaker(operatorId, hue);
    if (score > bestScore) {
      bestHue = hue;
      bestScore = score;
    }
  }

  return bestHue;
}

function minHueDistance(hue: number, otherHues: number[]): number {
  if (otherHues.length === 0) {
    return 180;
  }
  return Math.min(...otherHues.map((otherHue) => hueDistance(hue, otherHue)));
}

function hueDistance(left: number, right: number): number {
  const delta = Math.abs(left - right) % 360;
  return Math.min(delta, 360 - delta);
}

function hslToHex(hue: number, saturation: number, lightness: number): string {
  const normalizedSaturation = saturation / 100;
  const normalizedLightness = lightness / 100;
  const chroma = (1 - Math.abs(2 * normalizedLightness - 1)) * normalizedSaturation;
  const huePrime = hue / 60;
  const x = chroma * (1 - Math.abs((huePrime % 2) - 1));
  const match = normalizedLightness - chroma / 2;
  const [red, green, blue] =
    huePrime < 1
      ? [chroma, x, 0]
      : huePrime < 2
        ? [x, chroma, 0]
        : huePrime < 3
          ? [0, chroma, x]
          : huePrime < 4
            ? [0, x, chroma]
            : huePrime < 5
              ? [x, 0, chroma]
              : [chroma, 0, x];

  return `#${[red, green, blue]
    .map((channel) =>
      Math.round((channel + match) * 255)
        .toString(16)
        .padStart(2, "0"),
    )
    .join("")}`;
}

function geometryCoordinates(geometry: GeoJSON.Geometry): unknown {
  return "coordinates" in geometry ? geometry.coordinates : [];
}

function stableHue(value: string): number {
  let hash = 0;
  for (const char of value) {
    hash = (hash * 31 + char.charCodeAt(0)) % 360;
  }
  return hash;
}

function stableTieBreaker(operatorId: string, hue: number): number {
  return ((stableHue(`${operatorId}:${hue}`) % 100) / 100) * 0.001;
}

function isNumber(value: number | undefined): value is number {
  return typeof value === "number";
}
