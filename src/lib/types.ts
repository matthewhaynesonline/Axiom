export type CssBgClass =
  | "bg-primary"
  | "bg-secondary"
  | "bg-success"
  | "bg-danger"
  | "bg-warning"
  | "bg-info"
  | "bg-light"
  | "bg-dark";

export type CssTextBgClass =
  | "text-bg-primary"
  | "text-bg-secondary"
  | "text-bg-success"
  | "text-bg-danger"
  | "text-bg-warning"
  | "text-bg-info"
  | "text-bg-light"
  | "text-bg-dark";

export type CssTextClass =
  | "text-primary"
  | "text-secondary"
  | "text-success"
  | "text-danger"
  | "text-warning"
  | "text-info"
  | "text-light"
  | "text-dark";

export type CssButtonClass =
  | "btn-primary"
  | "btn-secondary"
  | "btn-success"
  | "btn-danger"
  | "btn-warning"
  | "btn-info"
  | "btn-light"
  | "btn-dark";

export type CssButtonOutlineClass =
  | "btn-outline-primary"
  | "btn-outline-secondary"
  | "btn-outline-success"
  | "btn-outline-danger"
  | "btn-outline-warning"
  | "btn-outline-info"
  | "btn-outline-light"
  | "btn-outline-dark";

export type AppTab =
  | "Term Sentiment"
  | "Sentiment Consensus"
  | "Term Details"
  | "Models";

export type AppTabList = AppTab[];

export type ModelGroup = "Academia" | "East" | "West";
export type ModelType = "llm" | "embedding";
export type ModelLicense =
  | "Apache 2.0"
  | "CC-BY-NC 4.0"
  // | "customized-nscl-v1 NC"
  | "Gemma (Gated)"
  | "MIT"
  // | "Qwen Research License NC"
  | "Proprietary";

export interface Model {
  model_id: string;
  model_name: string;
  type: ModelType;
  group: ModelGroup;
  model_url: string;
  license: ModelLicense;
  license_score: number;
}

export type TermSentiment = {
  a_term: string;
  a_category: string;
  b_category: string;
  positive_term: string;
  negative_term: string;
  model_id: string;
  score_axis: number;
};
