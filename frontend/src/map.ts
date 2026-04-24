import L from "leaflet";
import "leaflet/dist/leaflet.css";
import type { GeoJsonObject } from "geojson";

import type { AreaFeature, AreaFeatureCollection } from "./types";

type SelectHandler = (feature: AreaFeature, focusDetail: boolean) => void;

const defaultStyle: L.PathOptions = {
  color: "#176c5f",
  weight: 2,
  fillColor: "#6fc7a6",
  fillOpacity: 0.38,
};

const selectedStyle: L.PathOptions = {
  color: "#8a4b00",
  weight: 4,
  fillColor: "#f2b84b",
  fillOpacity: 0.54,
};

export class AtlasMap {
  private readonly map: L.Map;
  private layer: L.GeoJSON | null = null;
  private featureLayers = new Map<string, L.Layer>();
  private selectedAreaId: string | null = null;

  constructor(containerId: string, onSelect: SelectHandler) {
    this.map = L.map(containerId, {
      center: [51.4332, 7.6616],
      zoom: 8,
      keyboard: true,
      scrollWheelZoom: true,
    });

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 18,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    }).addTo(this.map);

    this.onSelect = onSelect;
  }

  private readonly onSelect: SelectHandler;

  renderAreas(collection: AreaFeatureCollection): void {
    if (this.layer) {
      this.map.removeLayer(this.layer);
    }
    this.featureLayers.clear();

    this.layer = L.geoJSON(collection as unknown as GeoJsonObject, {
      style: () => defaultStyle,
      onEachFeature: (feature, layer) => {
        const areaFeature = feature as unknown as AreaFeature;
        const areaId = areaFeature.properties.id;
        this.featureLayers.set(areaId, layer);
        layer.bindTooltip(`${areaFeature.properties.name} - ${areaFeature.properties.operatorName}`);
        layer.on({
          click: () => this.selectArea(areaFeature, true),
          mouseover: () => this.applyHover(layer),
          mouseout: () => this.resetLayerStyle(areaId),
          add: () => this.makeLayerFocusable(layer, areaFeature),
        });
      },
    }).addTo(this.map);

    const bounds = this.layer.getBounds();
    if (bounds.isValid()) {
      this.map.fitBounds(bounds.pad(0.2), { maxZoom: 10 });
    }
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
        this.map.fitBounds(bounds.pad(0.35), { maxZoom: 11 });
      }
    }
  }

  invalidateSize(): void {
    this.map.invalidateSize();
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
    pathElement.addEventListener("focus", () => this.applyHover(layer));
    pathElement.addEventListener("blur", () => this.resetLayerStyle(feature.properties.id));
    pathElement.addEventListener("keydown", (event) => {
      if (event instanceof KeyboardEvent && (event.key === "Enter" || event.key === " ")) {
        event.preventDefault();
        this.selectArea(feature, true);
      }
    });
  }

  private applyHover(layer: L.Layer): void {
    if (layer instanceof L.Path) {
      layer.setStyle({ weight: 4, fillOpacity: 0.5 });
      layer.bringToFront();
    }
  }

  private resetLayerStyle(areaId: string): void {
    const layer = this.featureLayers.get(areaId);
    if (layer instanceof L.Path) {
      layer.setStyle(areaId === this.selectedAreaId ? selectedStyle : defaultStyle);
    }
  }

  private updateSelectionStyles(): void {
    this.featureLayers.forEach((layer, areaId) => {
      if (layer instanceof L.Path) {
        layer.setStyle(areaId === this.selectedAreaId ? selectedStyle : defaultStyle);
      }
    });
  }
}

function hasBounds(layer: L.Layer): layer is L.Layer & { getBounds: () => L.LatLngBounds } {
  return "getBounds" in layer && typeof layer.getBounds === "function";
}
