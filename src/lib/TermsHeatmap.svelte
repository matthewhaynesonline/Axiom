<script lang="ts">
  import * as aq from "arquero";

  import type { Model } from "./types";

  import config from "../config.json";
  import { createContinuousSentimentScale as createColorScale } from "./plot";
  import { changeSort, formatPercent } from "./utils";

  import MethodologyModal from "./ui/MethodologyModal.svelte";
  import SortIcon from "./ui/SortIcon.svelte";
  import ScoreVal from "./ui/ScoreVal.svelte";

  let {
    dt,
    models,
    selectedTermCategory,
    selectedJudgementTermsCategory = null,
    avg_score_column = "avg_score",
  }: {
    dt?: aq.ColumnTable;
    models: Model[] | null;
    selectedTermCategory: string | null;
    selectedJudgementTermsCategory?: string | null;
    avg_score_column?: string;
  } = $props();

  let colorScale = $state();

  // we just want to default the sort based on prop
  // not update sort if prop changes (prop shouldn't change)
  const initialSort = avg_score_column;
  let sortColumn = $state(initialSort);

  let sortDesc = $state(true);

  let sortAqColumn = $derived(sortDesc ? aq.desc(sortColumn) : sortColumn);
  let sortedDt = $derived(dt?.orderby(sortAqColumn));
  let rows = $derived(sortedDt?.objects() ?? []);

  let positiveTerm = $derived.by(() => {
    if (!selectedJudgementTermsCategory) return null;
    return rows[0].positive_term;
  });

  let negativeTerm = $derived.by(() => {
    if (!selectedJudgementTermsCategory) return null;
    return rows[0].negative_term;
  });

  let title = $derived.by(() => {
    let title = selectedTermCategory ? selectedTermCategory : "All";
    if (positiveTerm && negativeTerm) {
      title += `: "${positiveTerm}" vs "${negativeTerm}"`;
    }
    return title;
  });

  let loaded = $derived(!!colorScale);

  // let dtHTML = $derived(dt.toHTML());

  $effect(() => {
    colorScale = createColorScale();
  });

  function doChangeSort(column: string) {
    [sortColumn, sortDesc] = changeSort(sortColumn, sortDesc, column);
  }
</script>

{#snippet sortHeader(columnId: string, label: string, extraClass: string = "")}
  <th
    scope="col"
    class="cursor-pointer {config.theme.headingCssClasses} {extraClass}"
    onclick={() => doChangeSort(columnId)}
  >
    <div>
      {label}
      <SortIcon active={sortColumn === columnId} {sortDesc} />
    </div>
  </th>
{/snippet}

<MethodologyModal>
  <p>
    Each term is scored against a semantic axis defined by a pair of opposing
    anchors (e.g. good vs evil). The axis is derived by subtracting the negative
    pole embedding from the positive pole embedding, producing a directional
    vector in embedding space. Each term's embedding is then projected onto that
    axis via dot product. The resulting score reflects how closely the term
    aligns with the positive pole versus the negative pole. Scores are
    normalized using a tanh scaled z-score to keep values in a comparable range
    across models. Rows are terms, columns are models; color encodes direction
    and intensity of alignment.
  </p>
</MethodologyModal>

<h5 class="border-start border-4 border-primary my-4 ps-2">
  {title}
</h5>

{#if loaded}
  <!-- {@html dtHTML} -->
  <div class="table-responsive">
    <table class="table table-hover">
      <thead>
        <tr class="text-wrap text-break">
          {@render sortHeader("a_term", "Term", "text-end pe-3")}
          {#each models as model}
            {@render sortHeader(model.model_id, model.model_name, "angled")}
          {/each}
          {@render sortHeader(avg_score_column, "All Average", "angled")}
        </tr>
      </thead>
      <tbody>
        {#each rows as row}
          <tr class="align-middle">
            <td class="text-end pe-3">
              {row.a_term}
              {#if !selectedJudgementTermsCategory && row.positive_term && row.negative_term}
                ({row.positive_term} vs {row.negative_term})
              {/if}
            </td>

            {#each models as model}
              <td class="text-center p-1">
                <div
                  class="rounded hover-group"
                  style="background-color: {colorScale(row[model.model_id])};"
                >
                  <span class="show-on-parent-hover">
                    {formatPercent(row[model.model_id], config.scale.offset)}
                  </span>
                </div>
              </td>
            {/each}

            <td>
              <ScoreVal score={row[avg_score_column]} />
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
{/if}

<style>
  th.angled {
    height: 160px;
    vertical-align: bottom;
  }

  th.angled > div {
    transform: rotate(-35deg);
    transform-origin: left bottom;
    width: 55px;
    white-space: nowrap;
  }
</style>
