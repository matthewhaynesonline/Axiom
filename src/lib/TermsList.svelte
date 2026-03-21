<script lang="ts">
  import * as aq from "arquero";

  import type { TermSentiment } from "./types";

  import { createContinuousSentimentScale as createColorScale } from "./plot";
  import { changeSort } from "./utils";

  import ScoreBar from "./ui/ScoreBar.svelte";
  import SortIcon from "./ui/SortIcon.svelte";

  let {
    dt,
    termCategory = null,
    judgementCategory = null,
  }: {
    dt?: aq.ColumnTable;
    termCategory?: string | null;
    judgementCategory?: string | null;
  } = $props();

  let colorScale = $state();

  let sortColumn = $state("model_id");
  let sortDesc = $state(false);

  let sortAqColumn = $derived(sortDesc ? aq.desc(sortColumn) : sortColumn);
  let sortedDt = $derived(dt?.orderby(sortAqColumn));
  let rows = $derived(sortedDt?.objects() ?? []) as TermSentiment[];

  function doChangeSort(column: string) {
    [sortColumn, sortDesc] = changeSort(sortColumn, sortDesc, column);
  }

  let active = $derived(!!colorScale && !!termCategory && !!judgementCategory);

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

{#if active}
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
          <td>
            <ScoreBar score={row.score_axis} />
          </td>
        </tr>
      {/each}
    </tbody>
  </table>
{:else}
  Please select a category and judgment category.
{/if}
