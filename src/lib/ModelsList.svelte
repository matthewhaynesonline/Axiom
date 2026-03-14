<script lang="ts">
  import * as aq from "arquero";

  import { createContinuousScale as createColorScale } from "./plot";
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
        {@render sortHeader("model_id", "Name")}
        {@render sortHeader("group", "Group")}
        {@render sortHeader("type", "Type")}
        {@render sortHeader("license", "License Name")}
        {@render sortHeader("license_score", "License Friendliness")}
      </tr>
    </thead>
    <tbody>
      {#each rows as row}
        <tr>
          <td>
            <a href={row.model_url} target="_blank" rel="external">
              {row.model_id} ➚
            </a>
          </td>
          <td>{row.group}</td>
          <td>{row.type}</td>
          <td>{row.license}</td>
          <td
            class="text-center hover-group"
            style="background-color: {colorScale(row.license_score)};"
          >
            <span class="show-on-parent-hover">
              {formatPercent(row.license_score)}
            </span>
          </td>
        </tr>
      {/each}
    </tbody>
  </table>
{/if}
