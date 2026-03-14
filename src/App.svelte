<script lang="ts">
  import { onMount } from "svelte";

  import * as aq from "arquero";

  import config from "./config.json";
  import { loadDtFromArrow } from "./lib/utils";

  import Filters from "./lib/ui/Filters.svelte";
  import ModelsList from "./lib/ModelsList.svelte";
  import SentimentConsensus from "./lib/sentiment_plot/SentimentConsensus.svelte";
  import Tabs from "./lib/ui/Tabs.svelte";
  import TermsList from "./lib/TermsList.svelte";
  import TermsHeatmap from "./lib/TermsHeatmap.svelte";

  const tabs = [
    "Term Sentiment",
    "Sentiment Consensus",
    "Term Details",
    "Models",
  ];

  let activeTab = $state(tabs[0]);
  let showCompositeGroups = $state(true);

  let modelsMeta: aq.ColumnTable | null = $state(null);
  // let termPairsDt: aq.ColumnTable | null = $state(null);
  let termSentimentDt: aq.ColumnTable | null = $state(null);

  let loaded = $derived(modelsMeta && termSentimentDt);

  let activeTermSentimentDt = $derived.by(() => {
    if (!termSentimentDt) return null;

    if (showCompositeGroups) {
      return termSentimentDt;
    }

    // Filter out rows where the model_id starts with "composite_"
    return termSentimentDt.filter(
      aq.escape((d) => !d.model_id.startsWith("composite_")),
    );
  });

  let termSentimentDtPivot = $derived.by(() => {
    return (
      activeTermSentimentDt
        ?.select(
          "a_term",
          "a_category",
          "b_category",
          "positive_term",
          "negative_term",
          "model_id",
          "score_axis",
        )

        // 2. Group by the term to calculate the mean score across all models
        .groupby(
          "a_term",
          "a_category",
          "b_category",
          "positive_term",
          "negative_term",
        )
        .derive({ avg_score: (d) => aq.op.mean(d.score_axis) })

        // 3. Regroup by term AND the new average so they become our row identifiers
        .groupby(
          "a_term",
          "a_category",
          "b_category",
          "positive_term",
          "negative_term",
          "avg_score",
        )

        // 4. Pivot the models into columns, filling them with the score_axis values
        .pivot("model_id", "score_axis")
    );
  });

  let models = $derived.by(() => {
    return activeTermSentimentDt
      ?.select("model_id")
      .dedupe()
      .array("model_id")
      .sort();
  });

  let selectedModel = $state(null);

  let termCategories = $derived.by(() => {
    return activeTermSentimentDt
      ?.select("a_category")
      .dedupe()
      .array("a_category")
      .sort();
  });

  let selectedTermCategory = $state(null);

  let judgementTermsCategories = $derived.by(() => {
    return activeTermSentimentDt
      ?.select("b_category")
      .dedupe()
      .array("b_category")
      .sort();
  });

  let selectedJudgementTermsCategory = $state(null);

  let filteredTermSentimentDt = $derived.by(() => {
    return activeTermSentimentDt?.filter(
      aq.escape(
        (d) =>
          (selectedModel === null || d.model_id === selectedModel) &&
          (selectedTermCategory === null ||
            d.a_category === selectedTermCategory) &&
          (selectedJudgementTermsCategory === null ||
            d.b_category === selectedJudgementTermsCategory),
      ),
    );
  });

  let filteredTermSentimentDtPivot = $derived.by(() => {
    return termSentimentDtPivot?.filter(
      aq.escape(
        (d) =>
          // (selectedModel === null || d.model_id === selectedModel) &&
          (selectedTermCategory === null ||
            d.a_category === selectedTermCategory) &&
          (selectedJudgementTermsCategory === null ||
            d.b_category === selectedJudgementTermsCategory),
      ),
    );
  });

  onMount(async () => {
    await Promise.all([loadModelsMeta(), processData()]);
  });

  async function loadModelsMeta() {
    const response = await fetch(config.files.modelsMeta);
    const csvText = await response.text();

    modelsMeta = aq.fromCSV(csvText);
  }

  async function processData() {
    // termPairsDt = await loadDtFromArrow(config.files.termPairs);
    termSentimentDt = await loadDtFromArrow(config.files.termSentiment);
  }
</script>

<main>
  <div class="container-fluid">
    <div class="row">
      <div class="col">
        <h1>Arrow Test</h1>

        {#if loaded}
          <Tabs {tabs} bind:activeTab />

          {#if activeTab === tabs[0]}
            <Filters
              {termCategories}
              bind:selectedTermCategory
              {judgementTermsCategories}
              bind:selectedJudgementTermsCategory
              bind:showCompositeGroups
            />

            <TermsHeatmap
              dt={filteredTermSentimentDtPivot}
              {models}
              termCategory={selectedTermCategory}
              judgementCategory={selectedJudgementTermsCategory}
            />
          {:else if activeTab === tabs[1]}
            <Filters
              {termCategories}
              bind:selectedTermCategory
              {judgementTermsCategories}
              bind:selectedJudgementTermsCategory
              bind:showCompositeGroups
            />

            <SentimentConsensus
              dt={activeTermSentimentDt}
              termCategory={selectedTermCategory}
              judgementCategory={selectedJudgementTermsCategory}
            />
          {:else if activeTab === tabs[2]}
            <Filters
              {models}
              bind:selectedModel
              {termCategories}
              bind:selectedTermCategory
              {judgementTermsCategories}
              bind:selectedJudgementTermsCategory
              bind:showCompositeGroups
            />

            <TermsList dt={filteredTermSentimentDt} />
          {:else if activeTab === tabs[3]}
            <ModelsList dt={modelsMeta} />
          {:else}
            This is unexpected, a tab should be loaded. Whoops?
          {/if}
        {/if}
      </div>
    </div>
  </div>
</main>
