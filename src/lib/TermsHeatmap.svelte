<script lang="ts">
  import * as aq from "arquero";

  import config from "../config.json";
  import { createContinuousSentimentScale as createColorScale } from "./plot";
  import { changeSort, formatPercent } from "./utils";

  import SortIcon from "./ui/SortIcon.svelte";

  let {
    dt,
    models,
    termCategory,
    judgementCategory = null,
    avg_score_column = "avg_score",
  }: {
    dt: aq.Table[];
    models: string[];
    termCategory: string;
    judgementCategory?: string | null;
    avg_score_column: string;
  } = $props();

  let colorScale = $state();

  // Use fn to init state so svelte doesn't complain
  // we just want to default the sort based on prop
  // not update sort if prop changes (prop shouldn't change)
  let sortColumn = $state(() => avg_score_column);
  let sortDesc = $state(true);

  let sortAqColumn = $derived(sortDesc ? aq.desc(sortColumn) : sortColumn);
  let sortedDt = $derived(dt?.orderby(sortAqColumn));
  let rows = $derived(sortedDt?.objects() ?? []);

  let positiveTerm = $derived.by(() => {
    if (!judgementCategory) return null;
    return rows[0].positive_term;
  });

  let negativeTerm = $derived.by(() => {
    if (!judgementCategory) return null;
    return rows[0].negative_term;
  });

  let title = $derived.by(() => {
    let title = termCategory ? termCategory : "All";
    if (positiveTerm && negativeTerm) {
      title += ` ("${positiveTerm}" vs "${negativeTerm}")`;
    }
    return title;
  });

  let loaded = $derived(!!colorScale);

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
    class="cursor-pointer {extraClass}"
    onclick={() => doChangeSort(columnId)}
  >
    {label}
    <SortIcon active={sortColumn === columnId} {sortDesc} />
  </th>
{/snippet}

<h3>{title}</h3>
{#if loaded}
  <table class="table table-hover table-borderless">
    <thead>
      <tr class="text-wrap text-break">
        {@render sortHeader("a_term", "Term", "text-end pe-2")}
        {#each models as model}
          {@render sortHeader(model, model)}
        {/each}
        {@render sortHeader(avg_score_column, "Average")}
      </tr>
    </thead>
    <tbody>
      {#each rows as row}
        <tr>
          <td class="text-end pe-2">
            {row.a_term}
            {#if !judgementCategory && row.positive_term && row.negative_term}
              ({row.positive_term} vs {row.negative_term})
            {/if}
          </td>

          {#each models as model}
            <td
              class="text-center hover-group"
              style="background-color: {colorScale(row[model])};"
            >
              <span class="show-on-parent-hover">
                {formatPercent(row[model], config.scale.offset)}
              </span>
            </td>
          {/each}

          <td
            class="text-center hover-group"
            style="background-color: {colorScale(row[avg_score_column])};"
          >
            <span class="show-on-parent-hover">
              {formatPercent(row[avg_score_column], config.scale.offset)}
            </span>
          </td>
        </tr>
      {/each}
    </tbody>
  </table>
{/if}

<style>
  table {
    border-spacing: 0;
    table-layout: fixed;
  }
</style>
