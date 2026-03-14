import { tableFromIPC } from "apache-arrow";
import * as aq from "arquero";

import config from "../config.json";

export function formatPercent(value: number, offset: number = 0.0): number {
  return Math.round((value + offset) * 100);
}

export async function loadDtFromArrow(
  arrowFile: string,
  lowerCaseModelId: boolean = true,
): Promise<aq.ColumnTable> {
  const fileResponse = await fetch(arrowFile);
  const arrowTable = tableFromIPC(await fileResponse.arrayBuffer());

  // @ts-ignore
  let dt = aq.fromArrow(arrowTable);

  if (lowerCaseModelId) {
    dt = dt.derive({
      model_id: (d) => aq.op.lower(d.model_id),
    });
  }

  return dt;
}

export function changeSort(
  sortColumn: string,
  sortDesc: boolean,
  column: string,
): [string, boolean] {
  if (sortColumn === column) {
    sortDesc = !sortDesc;
  } else {
    sortDesc = false;
  }

  sortColumn = column;

  return [sortColumn, sortDesc];
}

export function getThemePositiveColorValue(): string {
  return getDocumentCssVarValue(config.theme.cssVars.colors.positive);
}

export function getThemeNegativeColorValue(): string {
  return getDocumentCssVarValue(config.theme.cssVars.colors.negative);
}

export function getThemeNeutralColorValue(): string {
  return getDocumentCssVarValue(config.theme.cssVars.colors.neutral);
}

function getDocumentCssVarValue(varName: string): string {
  if (typeof window === "undefined") {
    return config.theme.cssVars.colors.fallbackValue;
  }

  return getComputedStyle(document.documentElement)
    .getPropertyValue(varName)
    .trim();
}
