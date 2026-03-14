import * as aq from "arquero";
import { scaleLinear } from "d3-scale";

import config from "../config.json";
import {
  getThemePositiveColorValue,
  getThemeNegativeColorValue,
  getThemeNeutralColorValue,
} from "./utils";

export function createContinuousSentimentScale() {
  return createContinuousScale(
    config.scale.sentiment.min,
    (config.scale.sentiment.min + config.scale.sentiment.max) / 2,
    config.scale.sentiment.max,
  );
}

export function createContinuousScale(
  min: number = 0.0,
  mid: number = 0.5,
  max = 1.0,
) {
  const positive = getThemePositiveColorValue();
  const negative = getThemeNegativeColorValue();
  const neutral = getThemeNeutralColorValue();

  return scaleLinear()
    .domain([min, mid, max])
    .range([negative, neutral, positive]);
}

export function prepSentimentVsDisagreement(
  dt: aq.Table,
  a_category: string,
  b_category: string,
  positive_term: string,
  negative_term: string,
): aq.Table {
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
