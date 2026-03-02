<script lang="ts" generics="T extends ChartType = 'bar'">
  import { onMount } from "svelte";

  import Chart, {
    type ChartData,
    type ChartOptions,
    type ChartType,
  } from "chart.js/auto";

  interface Props {
    type?: T;
    data: ChartData<T>;
    options?: ChartOptions<T>;
  }

  // @ts-ignore
  let { data, options = {}, type = "bar" as T }: Props = $props();

  let canvasElement: HTMLCanvasElement;
  let chartInstance: Chart<T> | undefined;

  $effect(() => {
    if (chartInstance && data) {
      // @ts-ignore
      chartInstance.data = $state.snapshot(data);
      chartInstance.options = $state.snapshot(options) as ChartOptions<T>;
      chartInstance.update();
    }
  });

  onMount(() => {
    // @ts-ignore
    chartInstance = new Chart(canvasElement, {
      type,
      // @ts-ignore
      data: $state.snapshot(data),
      options: $state.snapshot(options) as ChartOptions<T>,
    });

    return () => {
      chartInstance?.destroy();
    };
  });
</script>

<div class="chart-container">
  <canvas bind:this={canvasElement}></canvas>
</div>

<style>
  .chart-container {
    position: relative;
    height: 400px;
    width: 100%;
  }
</style>
