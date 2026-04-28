import type { AreaFeature } from "./types";

// Operator polygons need visually distinguishable colors. We achieve this by
// walking the hue circle in golden-angle steps (~137.5 degrees), which spreads
// successive hues as far apart as possible. With ~30-40 operators in Germany
// the chance of two adjacent operators landing on perceptually similar hues
// is small, and hover/select styling disambiguates the rest.
const goldenAngleDegrees = 137.508;
const baseSaturation = 72;
const baseLightness = 40;

export function buildOperatorColors(features: AreaFeature[]): Map<string, string> {
  const operatorIds = [...new Set(features.map((feature) => feature.properties.operatorId))].sort();
  return new Map(
    operatorIds.map((operatorId, index) => [operatorId, hslToHex((index * goldenAngleDegrees) % 360, baseSaturation, baseLightness)]),
  );
}

export function fallbackOperatorColor(operatorId: string): string {
  return hslToHex(stableHue(operatorId), baseSaturation, baseLightness);
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

function stableHue(value: string): number {
  let hash = 0;
  for (const char of value) {
    hash = (hash * 31 + char.charCodeAt(0)) % 360;
  }
  return hash;
}
