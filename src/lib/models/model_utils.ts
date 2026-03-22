import type {
  Model,
  ModelGroup,
  ModelLicense,
  CssTextBgClass,
  CssButtonClass,
  CssButtonOutlineClass,
} from "../types";

const GROUP_CLASS_MAP: Record<ModelGroup, CssTextBgClass> = {
  Academia: "text-bg-primary",
  East: "text-bg-warning",
  West: "text-bg-info",
};

export function modelGroupToCssClass(group: ModelGroup): CssTextBgClass {
  return GROUP_CLASS_MAP[group] ?? "text-bg-secondary";
}

const LICENSE_CLASS_MAP: Record<ModelLicense, CssTextBgClass> = {
  "Apache 2.0": "text-bg-success",
  MIT: "text-bg-success",
  "Gemma (Gated)": "text-bg-warning",
  "CC-BY-NC 4.0": "text-bg-warning",
  Proprietary: "text-bg-danger",
};

export function modelLicenseToCssClass(license: ModelLicense): CssTextBgClass {
  return LICENSE_CLASS_MAP[license] ?? "text-bg-dark";
}

export function modelLicenseScoreToCssClass(score: number): CssTextBgClass {
  if (score >= 0.8) return "text-bg-success";
  if (score >= 0.3) return "text-bg-warning";
  if (score >= 0) return "text-bg-danger";

  return "text-bg-dark";
}

type ButtonClasses = [CssButtonClass, CssButtonOutlineClass];

const GROUP_BUTTON_CLASS_MAP: Record<ModelGroup, ButtonClasses> = {
  Academia: ["btn-primary", "btn-outline-primary"],
  East: ["btn-warning", "btn-outline-warning"],
  West: ["btn-info", "btn-outline-info"],
};

export function modelGroupToCssButtonClass(group: ModelGroup): ButtonClasses {
  return (
    GROUP_BUTTON_CLASS_MAP[group] ?? ["btn-secondary", "btn-outline-secondary"]
  );
}

export const groupSortKey = (group: string | undefined) =>
  group === "composite" ? 1 : 0;

export function sortModels(models: Model[]): Model[] {
  return [...models].sort((a, b) => {
    const groupComparison = groupSortKey(a.group) - groupSortKey(b.group);

    if (groupComparison !== 0) {
      return groupComparison;
    }

    const groupA = a.group ?? "";
    const groupB = b.group ?? "";
    const namedGroupComparison = groupA.localeCompare(groupB);

    if (namedGroupComparison !== 0) {
      return namedGroupComparison;
    }

    return a.model_id.localeCompare(b.model_id);
  });
}
