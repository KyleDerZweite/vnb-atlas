import type { AreaFeature } from "./types";

type BoundsTuple = [number, number, number, number];

const baseSaturation = 72;
const baseLightness = 40;
const adjacencyPaddingDegrees = 0.04;
const goldenAngle = 137.508;

export function buildOperatorColors(features: AreaFeature[]): Map<string, string> {
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

export function fallbackOperatorColor(operatorId: string): string {
  return hslToHex(stableHue(operatorId), baseSaturation, baseLightness);
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
  const [red, green, blue] = rgbSector(chroma, x, huePrime);

  return `#${[red, green, blue]
    .map((channel) =>
      Math.round((channel + match) * 255)
        .toString(16)
        .padStart(2, "0"),
    )
    .join("")}`;
}

function rgbSector(chroma: number, x: number, huePrime: number): [number, number, number] {
  if (huePrime < 1) {
    return [chroma, x, 0];
  }
  if (huePrime < 2) {
    return [x, chroma, 0];
  }
  if (huePrime < 3) {
    return [0, chroma, x];
  }
  if (huePrime < 4) {
    return [0, x, chroma];
  }
  if (huePrime < 5) {
    return [x, 0, chroma];
  }
  return [chroma, 0, x];
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
