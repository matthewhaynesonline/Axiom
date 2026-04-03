<script lang="ts">
  import * as aq from "arquero";

  import type { TermSentiment } from "./types";

  import config from "../config.json";
  import { createContinuousSentimentScale as createColorScale } from "./plot";

  import MethodologyModal from "./ui/MethodologyModal.svelte";
  import ScoreBar from "./ui/ScoreBar.svelte";

  let {
    dt,
    termCategory = null,
    judgementCategory = null,
  }: {
    dt?: aq.ColumnTable;
    termCategory?: string | null;
    judgementCategory?: string | null;
  } = $props();

  type GroupByOption = "term" | "model";

  let groupBy: GroupByOption = $state("term");

  let colorScale = $state(null);

  let sortColumn = $state("model_id");
  let sortDesc = $state(false);

  let sortAqColumn = $derived(sortDesc ? aq.desc(sortColumn) : sortColumn);
  let sortedDt = $derived(dt?.orderby(sortAqColumn));
  let rows = $derived((sortedDt?.objects() ?? []) as TermSentiment[]);

  let groupedRows = $derived(
    groupBy === "term"
      ? groupRowsBy(rows, (row) => row.a_term)
      : groupRowsBy(rows, (row) => row.model_id),
  );

  let active = $derived(!!colorScale && !!termCategory && !!judgementCategory);

  function groupRowsBy(
    rows: TermSentiment[],
    key: (row: TermSentiment) => string,
  ): Record<string, TermSentiment[]> {
    const grouped = rows.reduce<Record<string, TermSentiment[]>>((acc, row) => {
      const rowKey = key(row);

      if (!acc[rowKey]) acc[rowKey] = [];
      acc[rowKey].push(row);

      return acc;
    }, {});

    return Object.fromEntries(
      Object.entries(grouped).sort(([a], [b]) => a.localeCompare(b)),
    );
  }

  $effect(() => {
    colorScale = createColorScale();
  });
</script>

<MethodologyModal>
  <p>
    Displays the raw axis projection score for each term broken down by
    individual model, using the same scoring method as the Sentiment Heatmap.
    Allows direct comparison of how a specific term is encoded across models and
    origin groups.
  </p>
</MethodologyModal>

{#if active}
  <div class="d-flex align-items-center gap-2 mb-2">
    <label for="sort-select" class={config.theme.headingCssClasses}>
      Group By
    </label>

    <select
      class="form-select form-select-sm w-auto"
      id="sort-select"
      bind:value={groupBy}
    >
      <option value="term">By Term then Model</option>
      <option value="model">By Model then Term</option>
    </select>
  </div>

  <table class="table table-striped table-hover">
    <thead>
      <tr>
        <th scope="col">
          {groupBy === "term" ? "Term / Model" : "Model / Term"}
        </th>
        <th scope="col">Positive</th>
        <th scope="col">Negative</th>
        <th scope="col">Score</th>
      </tr>
    </thead>
    <tbody>
      {#each Object.entries(groupedRows) as [groupName, groupedRowItems]}
        <tr>
          <td class="fw-bold" colspan="4">{groupName}</td>
        </tr>

        <tr>
          <td class="p-0" colspan="4">
            <table class="table table-borderless table-hover nested-table mb-0">
              <tbody>
                {#each groupedRowItems as row}
                  <tr>
                    <td class="ps-4">
                      {groupBy === "term" ? row.model_id : row.a_term}
                    </td>
                    <td>{row.positive_term}</td>
                    <td>{row.negative_term}</td>
                    <td>
                      <ScoreBar score={row.score_axis} />
                    </td>
                  </tr>
                {/each}
              </tbody>
            </table>
          </td>
        </tr>
      {/each}
    </tbody>
  </table>
{:else}
  Please select a category and judgment category.
{/if}

<style>
  .table {
    table-layout: fixed;
  }

  .table th:last-of-type,
  .table td:last-of-type {
    width: 30%;
  }
</style>
