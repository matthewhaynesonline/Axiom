<script lang="ts">
  import { onMount } from "svelte";

  import { tableFromIPC } from "apache-arrow";
  import * as aq from "arquero";
  import { op } from "arquero";
  import type { ChartData, ChartOptions } from "chart.js";

  import { interpolateRdYlGn } from "d3-scale-chromatic";

  import ChartComponent from "./lib/Chart.svelte";

  // NOTE: if generated from polars, need to use old compat:
  // `control_rows.write_ipc("control_rows.arrow", compat_level=pl.CompatLevel.oldest())`
  // as the default polars export will throw `Unrecognized type: "undefined" (24)` in js
  const dataFile = "aie_results.arrow";

  let chartData: ChartData = $state({
    labels: ["Red", "Blue", "Yellow", "Green", "Purple", "Orange"],
    datasets: [
      {
        label: "Votes",

        data: [12, 19, 3, 5, 2, 3],
        borderWidth: 2,
        backgroundColor: "rgba(54, 162, 235, 0.5)",
        borderColor: "rgba(54, 162, 235, 1)",
      },
    ],
  });

  const chartOptions: ChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { position: "top" },
    },
  };

  let dt: aq.ColumnTable | null = $state(null);

  // let dtHTML = $derived.by(() => {
  //   return dt?.toHTML();
  // });

  let rows = $derived(dt ? dt.objects() : []);

  let models = $derived.by(() => {
    return dt?.select("model_id").dedupe().array("model_id");
  });

  let terms = $derived.by(() => {
    return dt?.select("a_term").dedupe().array("a_term");
  });

  let judgementTerms = $derived.by(() => {
    return dt?.select("b_term").dedupe().array("b_term");
  });

  let loaded = $derived(models && terms && judgementTerms);

  async function processData() {
    const response = await fetch(dataFile);
    const arrowTable = tableFromIPC(await response.arrayBuffer());

    // @ts-ignore
    dt = aq.fromArrow(arrowTable);
  }

  onMount(() => {
    processData();
  });

  function formatPercent(value: number): number {
    return Math.round(value * 100);
  }
</script>

<main>
  <h1>Arrow Test</h1>

  {#if loaded}
    <ChartComponent type="bar" data={chartData} options={chartOptions} />

    <!-- {@html dtHTML} -->

    <table>
      <thead>
        <tr>
          <th scope="col">Model</th>
          <th scope="col">Term</th>
          <th scope="col">Value</th>
          <th scope="col">Score</th>
        </tr>
      </thead>
      <tbody>
        {#each rows as row}
          <tr>
            <td>{row.model_id}</td>
            <td>{row.a_term}</td>
            <td>{row.b_term}</td>
            <td style="background-color: {interpolateRdYlGn(row.score_norm)};">
              <span class="text-outline">{formatPercent(row.score_norm)}</span>
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  {/if}
</main>

<style>
  main {
    width: 100%;
    max-width: 1000px;
  }

  table {
    width: 100%;
  }

  .text-outline {
    -webkit-text-stroke: 0.5px rgba(0, 0, 0, 0.75);
  }
</style>
