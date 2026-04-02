import * as aq from "arquero";
import { scaleLinear } from "d3-scale";

import config from "../config.json";
import {
  getThemePositiveColorValue,
  getThemeNegativeColorValue,
  getThemeNeutralColorValue,
} from "./utils";

const { min, max } = config.scale.sentiment;

const SENTIMENT_MID = (min + max) / 2;

export function createContinuousSentimentScale() {
  return createContinuousScale(min, SENTIMENT_MID, max);
}

export function createContinuousScale(
  min: number = 0.0,
  mid: number = 0.5,
  max: number = 1.0,
) {
  return scaleLinear()
    .domain([min, mid, max])
    .range([
      getThemeNegativeColorValue(),
      getThemeNeutralColorValue(),
      getThemePositiveColorValue(),
    ]);
}

export interface SentimentVsDisagreementParams {
  a_category: string;
  b_category: string;
  positive_term: string;
  negative_term: string;
}

export function prepSentimentVsDisagreement(
  dt: aq.ColumnTable,
  {
    a_category,
    b_category,
    positive_term,
    negative_term,
  }: SentimentVsDisagreementParams,
): aq.ColumnTable {
  return (
    dt
      .params({
        a_cat: a_category,
        b_cat: b_category,
        pos: positive_term,
        neg: negative_term,
      })
      // The '$' represents the parameters we just passed in
      .filter(
        (d, $) =>
          d.a_category === $.a_cat &&
          d.b_category === $.b_cat &&
          d.positive_term === $.pos &&
          d.negative_term === $.neg,
      )
      // Group by 'a_term' and rename it to 'term' on the fly
      .groupby({ term: (d) => d.a_term })
      // Calculate mean and standard deviation across the models
      .rollup({
        mean_sentiment: (d) => aq.op.mean(d.score_axis),
        std_disagreement: (d) => aq.op.stdevp(d.score_axis),
      })
      // Calculate absolute sentiment (for plot coloring)
      .derive({
        abs_sentiment: (d) => aq.op.abs(d.mean_sentiment),
      })
      .orderby(aq.desc("std_disagreement"))
  );
}
