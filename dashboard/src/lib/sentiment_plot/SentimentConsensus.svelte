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

  let judgementCategoryMapping = $derived(
    judgementCategory
      ? (judgementCategoriesMapping[judgementCategory] ?? null)
      : null,
  );

  let positiveTerm = $derived(judgementCategoryMapping?.positiveTerm ?? null);
  let negativeTerm = $derived(judgementCategoryMapping?.negativeTerm ?? null);

  let consensusDt = $derived.by(() => {
    if (!active || !dt || !positiveTerm || !negativeTerm) return null;

    return prepSentimentVsDisagreement(dt, {
      a_category: termCategory,
      b_category: judgementCategory,
      positive_term: positiveTerm,
      negative_term: negativeTerm,
    });
  });
</script>

<MethodologyModal>
  <p>Uses the same axis projection scores as the Sentiment Heatmap.</p>

  <p>
    For each term, the mean score and standard deviation across all models are
    computed. Mean score (x-axis) shows the overall direction of alignment,
    whether models collectively lean positive or negative. Standard deviation
    (y-axis) shows how much models disagree.
  </p>

  <p>
    Terms in the upper left are contested and lean negative; upper right are
    contested and lean positive; lower quadrants represent consensus. Bubble
    size encodes consensus strength; opacity encodes intensity.
  </p>
</MethodologyModal>

<div>
  {#if active}
    <SentimentPlot dt={consensusDt} {positiveTerm} {negativeTerm} />
  {:else}
    Please select a category and judgment category.
  {/if}
</div>
