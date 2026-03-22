<script lang="ts">
  import * as aq from "arquero";

  import judgementCategoriesMapping from "../../judgement_categories_mapping.json";

  import { prepSentimentVsDisagreement } from "../plot";

  import SentimentPlot from "./SentimentPlot.svelte";
  import MethodologyModal from "../ui/MethodologyModal.svelte";

  let {
    dt,
    termCategory = null,
    judgementCategory = null,
  }: {
    dt: aq.ColumnTable | null;
    termCategory?: string | null;
    judgementCategory?: string | null;
  } = $props();

  let active = $derived(!!termCategory && !!judgementCategory);

  let judgementCategoryMapping = $derived.by(() => {
    if (!judgementCategory) {
      return null;
    }

    return judgementCategoriesMapping[judgementCategory] ?? null;
  });

  let positiveTerm = $derived.by(() => {
    if (!judgementCategoryMapping) {
      return null;
    }

    return judgementCategoryMapping.positiveTerm;
  });

  let negativeTerm = $derived.by(() => {
    if (!judgementCategoryMapping) {
      return null;
    }

    return judgementCategoryMapping.negativeTerm;
  });

  let consensusDt = $derived.by(() => {
    if (!active) {
      return null;
    }

    return prepSentimentVsDisagreement(
      dt,
      termCategory,
      judgementCategory,
      positiveTerm,
      negativeTerm,
    );
  });
</script>

<MethodologyModal>
  <p>
    Uses the same axis projection scores as the Sentiment Heatmap. For each
    term, the mean score and standard deviation across all models are computed.
    Mean score (x-axis) shows the overall direction of alignment, whether models
    collectively lean positive or negative. Standard deviation (y-axis) shows
    how much models disagree. Terms in the upper left are contested and lean
    negative; upper right are contested and lean positive; lower quadrants
    represent consensus. Bubble size encodes consensus strength; opacity encodes
    intensity.
  </p>
</MethodologyModal>

<div>
  {#if active}
    <SentimentPlot
      dt={consensusDt}
      aCategory={termCategory}
      bCategory={judgementCategory}
      {positiveTerm}
      {negativeTerm}
    />
  {:else}
    Please select a category and judgment category.
  {/if}
</div>
