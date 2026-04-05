<script lang="ts">
  import { onMount } from "svelte";
  import * as aq from "arquero";

  import type { AppTabList, AppTab, Model } from "./lib/types";

  import config from "./config.json";
  import { loadDtFromArrow } from "./lib/utils";

  import Filters from "./lib/ui/Filters.svelte";
  import ModelsList from "./lib/models/ModelsList.svelte";
  import SentimentConsensus from "./lib/sentiment_plot/SentimentConsensus.svelte";
  import Tabs from "./lib/ui/Tabs.svelte";
  import ThemeSelector from "./lib/ui/ThemeSelector.svelte";
  import TermsList from "./lib/TermsList.svelte";
  import TermsHeatmap from "./lib/TermsHeatmap.svelte";
  import ValueSystems from "./lib/ValueSystems.svelte";

  const TABS: AppTabList = [
    "Sentiment Heatmap",
    "Where Models Disagree",
    "Per Term Breakdown",
    "Value Systems",
    "Models",
  ];

  const NON_MODEL_COLS = [
    "a_term",
    "a_category",
    "b_category",
    "positive_term",
    "negative_term",
    "avg_score",
  ];

  let filtersExpanded = $state(true);

  let activeTab: AppTab = $state("Sentiment Heatmap");
  let showCompositeGroups: boolean = $state(true);

  let modelsMeta: aq.ColumnTable | null = $state(null);
  let termSentimentDt: aq.ColumnTable | null = $state(null);
  let valueSystemRankingsDt: aq.ColumnTable | null = $state(null);

  let loaded = $derived(modelsMeta && termSentimentDt && valueSystemRankingsDt);

  let activeTermSentimentDt = $derived.by(() => {
    if (!termSentimentDt) return null;

    if (showCompositeGroups) {
      return termSentimentDt;
    }

    return termSentimentDt.filter(
      aq.escape((d) => !d.model_id.startsWith("composite_")),
    );
  });

  let termSentimentDtPivot = $derived.by(() => {
    if (!activeTermSentimentDt) return null;

    return activeTermSentimentDt
      .select(
        "a_term",
        "a_category",
        "b_category",
        "positive_term",
        "negative_term",
        "model_id",
        "score_axis",
      )
      .groupby(
        "a_term",
        "a_category",
        "b_category",
        "positive_term",
        "negative_term",
      )
      .derive({ avg_score: (d) => aq.op.mean(d.score_axis) })
      .groupby(
        "a_term",
        "a_category",
        "b_category",
        "positive_term",
        "negative_term",
        "avg_score",
      )
      .pivot("model_id", "score_axis");
  });

  let models = $derived.by(() => {
    if (!activeTermSentimentDt || !modelsMeta) return null;

    return activeTermSentimentDt
      .select("model_id")
      .dedupe()
      .join_left(
        modelsMeta.derive({ model_id: (d: any) => aq.op.lower(d.model_id) }),
        "model_id",
      )
      .derive({
        model_name: (d: any) => d.model_name ?? d.model_id,
      })
      .derive({
        group: (d: any) => d.group ?? "composite",
      })
      .orderby("group", "model_id")
      .objects() as Model[];
  });

  let rawSelectedModels: Model[] = $state([]);

  let selectedModels: Model[] = $derived.by(() => {
    if (showCompositeGroups) {
      return rawSelectedModels;
    }

    return rawSelectedModels.filter(
      (m) => !m.model_id.startsWith("composite_"),
    );
  });

  let selectedModelIds: string[] = $derived(
    selectedModels.map((m) => m.model_id),
  );

  let selectedModelsEmpty = $derived(selectedModels.length === 0);

  let termCategories: string[] = $derived(
    activeTermSentimentDt
      ?.select("a_category")
      .dedupe()
      .array("a_category")
      .sort() ?? [],
  ) as string[];

  let selectedTermCategory = $state(null);

  let judgementTermsCategories: string[] = $derived(
    activeTermSentimentDt
      ?.select("b_category")
      .dedupe()
      .array("b_category")
      .sort() ?? [],
  ) as string[];

  let selectedJudgementTermsCategory = $state(null);

  let filteredTermSentimentDt = $derived.by(() => {
    return activeTermSentimentDt?.filter(
      aq.escape(
        (d) =>
          selectedModelIds.includes(d.model_id) &&
          (selectedTermCategory === null ||
            d.a_category === selectedTermCategory) &&
          (selectedJudgementTermsCategory === null ||
            d.b_category === selectedJudgementTermsCategory),
      ),
    );
  });

  let filteredTermSentimentDtPivot = $derived.by(() => {
    const baseFiltered = termSentimentDtPivot?.filter(
      aq.escape(
        (d) =>
          (selectedTermCategory === null ||
            d.a_category === selectedTermCategory) &&
          (selectedJudgementTermsCategory === null ||
            d.b_category === selectedJudgementTermsCategory),
      ),
    );

    if (selectedModelsEmpty || !baseFiltered) return baseFiltered;

    const keepModelCols = baseFiltered
      .columnNames()
      .filter(
        (col) =>
          !NON_MODEL_COLS.includes(col as any) &&
          selectedModelIds.includes(col),
      );

    return baseFiltered.select([...NON_MODEL_COLS, ...keepModelCols]);
  });

  let filteredValueSystemRankingsDt = $derived.by(() => {
    return valueSystemRankingsDt?.filter(
      aq.escape((d) => selectedModelIds.includes(d.model_id)),
    );
  });

  onMount(async () => {
    await loadModelsMeta();
    await processData();

    if (models) {
      rawSelectedModels = [...models];
    }
  });

  async function loadModelsMeta() {
    const response = await fetch(config.files.modelsMeta);
    const csvText = await response.text();

    modelsMeta = aq
      .fromCSV(csvText)
      .derive({
        license_score: (d: any) => aq.op.parse_float(d.license_score),
      })
      .select(
        "model_id",
        "model_name",
        "type",
        "group",
        "model_url",
        "license",
        "license_score",
      );
  }

  async function processData() {
    termSentimentDt = await loadDtFromArrow(config.files.termSentiment);
    valueSystemRankingsDt = await loadDtFromArrow(
      config.files.valueSystemRankings,
    );

    valueSystemRankingsDt = valueSystemRankingsDt
      .join_left(
        modelsMeta.derive({ model_id: (d: any) => aq.op.lower(d.model_id) }),
        "model_id",
      )
      .derive({
        model_name: (d: any) => d.model_name ?? d.model_id,
      })
      .select(aq.not("type", "model_url", "license", "license_score"))
      .orderby("group", "model_id");
  }
</script>

<main>
  <nav class="navbar bg-body-tertiary">
    <div class="container-fluid">
      <div class="d-flex align-items-center">
        <span class="navbar-brand me-2">Axiom</span>
        <span>
          <small>
            by <a
              class="text-decoration-none me-2"
              href="https://github.com/matthewhaynesonline"
            >
              @matthewhaynesonline
            </a>

            <a
              class="text-decoration-none"
              href="https://github.com/matthewhaynesonline/Axiom">Repo</a
            >
          </small>
        </span>
      </div>
      <div class="d-flex">
        <ThemeSelector />
      </div>
    </div>
  </nav>

  <div class="container-fluid py-3">
    {#if loaded}
      <Tabs tabs={TABS} bind:activeTab />

      {#if activeTab === "Sentiment Heatmap"}
        <Filters
          bind:expanded={filtersExpanded}
          {models}
          bind:selectedModels={rawSelectedModels}
          {termCategories}
          bind:selectedTermCategory
          {judgementTermsCategories}
          bind:selectedJudgementTermsCategory
          bind:showCompositeGroups
        />

        <TermsHeatmap
          dt={filteredTermSentimentDtPivot}
          models={selectedModels}
          {selectedTermCategory}
          {selectedJudgementTermsCategory}
        />
      {:else if activeTab === "Where Models Disagree"}
        <Filters
          bind:expanded={filtersExpanded}
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
      {:else if activeTab === "Per Term Breakdown"}
        <Filters
          bind:expanded={filtersExpanded}
          {models}
          bind:selectedModels={rawSelectedModels}
          {termCategories}
          bind:selectedTermCategory
          {judgementTermsCategories}
          bind:selectedJudgementTermsCategory
          bind:showCompositeGroups
        />

        <TermsList
          dt={filteredTermSentimentDt}
          termCategory={selectedTermCategory}
          judgementCategory={selectedJudgementTermsCategory}
        />
      {:else if activeTab === "Value Systems"}
        <Filters
          bind:expanded={filtersExpanded}
          {models}
          bind:selectedModels={rawSelectedModels}
          bind:showCompositeGroups
        />

        <ValueSystems dt={filteredValueSystemRankingsDt} />
      {:else if activeTab === "Models"}
        <ModelsList dt={modelsMeta} />
      {:else}
        This is unexpected, a tab should be loaded. Whoops?
      {/if}
    {/if}
  </div>
</main>
