<script lang="ts">
  import * as aq from "arquero";

  import judgementCategoriesMapping from "../../judgement_categories_mapping.json";

  import { prepSentimentVsDisagreement } from "../plot";

  import SentimentPlot from "./SentimentPlot.svelte";

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
