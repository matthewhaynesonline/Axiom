<script lang="ts">
  import * as aq from "arquero";

  import type { Model } from "../types";

  import config from "../../config.json";
  import { changeSort } from "../utils";
  import {
    modelGroupToCssClass,
    modelLicenseScoreToCssClass,
  } from "./model_utils";

  import Badge from "../ui/Badge.svelte";
  import SortIcon from "../ui/SortIcon.svelte";

  let {
    dt,
  }: {
    dt: aq.ColumnTable | null;
  } = $props();

  let sortColumn = $state("model_id");
  let sortDesc = $state(false);

  let sortAqColumn = $derived(sortDesc ? aq.desc(sortColumn) : sortColumn);
  let sortedDt = $derived(dt?.orderby(sortAqColumn));
  let rows: Model[] = $derived(sortedDt?.objects() ?? []) as Model[];

  function doChangeSort(column: string) {
    [sortColumn, sortDesc] = changeSort(sortColumn, sortDesc, column);
  }
</script>

{#snippet sortHeader(columnId: string, label: string)}
  <th
    scope="col"
    class="cursor-pointer {config.theme.headingCssClasses}"
    onclick={() => doChangeSort(columnId)}
  >
    {label}
    <SortIcon active={sortColumn === columnId} {sortDesc} />
  </th>
{/snippet}

<div class="table-responsive">
  <table class="table table-borderless table-hover">
    <thead>
      <tr>
        {@render sortHeader("model_id", "Name")}
        {@render sortHeader("group", "Group")}
        {@render sortHeader("type", "Type")}
        {@render sortHeader("license", "License Name")}
      </tr>
    </thead>
    <tbody>
      {#each rows as model}
        <tr>
          <td>
            <a href={model.model_url} target="_blank" rel="external">
              {model.model_id} ➚
            </a>
          </td>
          <td>
            <Badge
              label={model.group}
              bgClass={modelGroupToCssClass(model.group)}
            />
          </td>
          <td>{model.type}</td>
          <td>
            <Badge
              label={model.license}
              bgClass={modelLicenseScoreToCssClass(model.license_score)}
            />
          </td>
        </tr>
      {/each}
    </tbody>
  </table>
</div>
