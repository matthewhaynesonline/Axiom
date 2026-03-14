<script lang="ts">
  import * as aq from "arquero";

  import config from "../config.json";
  import { createContinuousSentimentScale as createColorScale } from "./plot";
  import { changeSort, formatPercent } from "./utils";

  import SortIcon from "./ui/SortIcon.svelte";

  let {
    dt,
  }: {
    dt: aq.Table[];
  } = $props();

  let colorScale = $state();

  let sortColumn = $state("model_id");
  let sortDesc = $state(false);

  let sortAqColumn = $derived(sortDesc ? aq.desc(sortColumn) : sortColumn);
  let sortedDt = $derived(dt?.orderby(sortAqColumn));
  let rows = $derived(sortedDt?.objects() ?? []);

  function doChangeSort(column: string) {
    [sortColumn, sortDesc] = changeSort(sortColumn, sortDesc, column);
  }

  let loaded = $derived(!!colorScale);

  $effect(() => {
    colorScale = createColorScale();
  });
</script>

{#snippet sortHeader(columnId: string, label: string)}
  <th scope="col" class="cursor-pointer" onclick={() => doChangeSort(columnId)}>
    {label}
    <SortIcon active={sortColumn === columnId} {sortDesc} />
  </th>
{/snippet}

{#if loaded}
  <table class="table table-striped table-hover">
    <thead>
      <tr>
        {@render sortHeader("model_id", "Model")}
        {@render sortHeader("a_term", "Term")}
        {@render sortHeader("positive_term", "Positive Term")}
        {@render sortHeader("negative_term", "Negative Term")}
        {@render sortHeader("score_axis", "Score")}
      </tr>
    </thead>
    <tbody>
      {#each rows as row}
        <tr>
          <td>{row.model_id}</td>
          <td>{row.a_term}</td>
          <td>{row.positive_term}</td>
          <td>{row.negative_term}</td>
          <td
            class="text-center hover-group"
            style="background-color: {colorScale(row.score_axis)};"
          >
            <span class="show-on-parent-hover">
              {formatPercent(row.score_axis, config.scale.offset)}
            </span>
          </td>
        </tr>
      {/each}
    </tbody>
  </table>
{/if}
