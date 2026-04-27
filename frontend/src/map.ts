import L from "leaflet";
import "leaflet/dist/leaflet.css";
import type { GeoJsonObject } from "geojson";

import { asAreaFeature } from "./geojson-utils";
import { buildOperatorColors, fallbackOperatorColor } from "./map-colors";
import type { AreaFeature, AreaFeatureCollection } from "./types";

type SelectHandler = (feature: AreaFeature, focusDetail: boolean) => void;
type EmptyMapClickHandler = () => void;

const defaultFillOpacity = 0.26;
const hoverFillOpacity = 0.38;
const selectedFillOpacity = 0.44;

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
    this.map.createPane("vnbTooltips").style.zIndex = "850";
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
      pointToLayer: (feature, latlng) => {
        const areaFeature = asAreaFeature(feature);
        return L.circleMarker(latlng, {
          ...this.getAreaStyle(areaFeature),
          radius: 5,
          fillOpacity: 0.72,
        });
      },
      style: (feature) => this.getAreaStyle(asAreaFeature(feature)),
      onEachFeature: (feature, layer) => {
        const areaFeature = asAreaFeature(feature);
        const areaId = areaFeature.properties.id;
        this.featureLayers.set(areaId, layer);
        this.featuresByAreaId.set(areaId, areaFeature);
        layer.bindTooltip(areaFeature.properties.operatorName, {
          pane: "vnbTooltips",
          sticky: true,
        });
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
    } else if (layer && hasLatLng(layer)) {
      this.map.setView(layer.getLatLng(), 11);
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

  private ensureLayerVisible(layer: L.Layer): void {
    // panInside schwenkt die Karte nur dann, wenn der Punkt nicht ohnehin
    // im sichtbaren Bereich liegt. Das verhindert unnoetige Bewegung,
    // erfuellt aber WCAG 2.2 SC 2.4.11.
    const padding: L.PointTuple = [60, 60];
    if (hasBounds(layer)) {
      const bounds = layer.getBounds();
      if (bounds.isValid()) {
        this.map.panInside(bounds.getCenter(), { padding });
        return;
      }
    }
    if (hasLatLng(layer)) {
      this.map.panInside(layer.getLatLng(), { padding });
    }
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
    return this.operatorColors.get(operatorId) ?? fallbackOperatorColor(operatorId);
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
    pathElement.addEventListener("focus", () => {
      this.applyHover(layer, feature.properties.id);
      // WCAG 2.2 SC 2.4.11 (Focus Not Obscured): wenn ein Polygon per Tab
      // fokussiert wird, das ausserhalb des sichtbaren Kartenausschnitts liegt,
      // schwenken wir die Karte sanft, damit der Fokusring sichtbar ist.
      this.ensureLayerVisible(layer);
    });
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
      if (layer instanceof L.CircleMarker) {
        layer.setRadius(7);
      }
      layer.bringToFront();
    }
  }

  private resetLayerStyle(areaId: string): void {
    const layer = this.featureLayers.get(areaId);
    const feature = this.featuresByAreaId.get(areaId);
    if (layer instanceof L.Path) {
      layer.setStyle(feature ? this.getAreaStyle(feature, areaId === this.selectedAreaId ? "selected" : "default") : {});
      if (layer instanceof L.CircleMarker) {
        layer.setRadius(areaId === this.selectedAreaId ? 7 : 5);
      }
    }
  }

  private updateSelectionStyles(): void {
    this.featureLayers.forEach((layer, areaId) => {
      const feature = this.featuresByAreaId.get(areaId);
      if (layer instanceof L.Path) {
        layer.setStyle(feature ? this.getAreaStyle(feature, areaId === this.selectedAreaId ? "selected" : "default") : {});
        if (layer instanceof L.CircleMarker) {
          layer.setRadius(areaId === this.selectedAreaId ? 7 : 5);
        }
      }
    });
  }
}

function hasBounds(layer: L.Layer): layer is L.Layer & { getBounds: () => L.LatLngBounds } {
  return "getBounds" in layer && typeof layer.getBounds === "function";
}

function hasLatLng(layer: L.Layer): layer is L.Layer & { getLatLng: () => L.LatLng } {
  return "getLatLng" in layer && typeof layer.getLatLng === "function";
}
