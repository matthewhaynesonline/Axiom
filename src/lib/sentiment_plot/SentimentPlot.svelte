<script lang="ts">
  import * as aq from "arquero";

  import { Tween } from "svelte/motion";
  import { cubicOut } from "svelte/easing";

  import {
    Plot,
    Dot,
    RuleX,
    RuleY,
    Text,
    Brush,
    GridX,
    GridY,
  } from "svelteplot";

  import config from "../../config.json";

  const domainMax = config.scale.sentiment.max;
  const defaultDomainX = [-domainMax, domainMax];
  const defaultDomainY = [-0.1, 0.35];

  // const labelThreshold = 0.0;
  const plotPadding = 0.05;
  const defaultHeight = 800;
  const plotHeightPercentOfWindow = 0.65;

  const theme = {
    animation: {
      options: {
        duration: 400,
        easing: cubicOut,
      },
    },
    grid: {
      strokeOpacity: 0.1,
    },
    rule: {
      strokeDasharray: "4",
      strokeOpacity: 0.4,
    },
    text: {
      size: 12,
      fill: `var(${config.theme.cssVars.colors.muted})`,
    },
    quadrantLabel: {
      paddingX: 16,
      paddingY: 24,
    },
    stroke: {
      color: "grey",
    },
    colors: {
      positive: `var(${config.theme.cssVars.colors.positive})`,
      negative: `var(${config.theme.cssVars.colors.negative})`,
      neutral: `var(${config.theme.cssVars.colors.neutral})`,
    },
  };

  let {
    dt,
    positiveTerm = "good",
    negativeTerm = "evil",
  }: {
    dt: aq.ColumnTable;
    positiveTerm: string;
    negativeTerm: string;
  } = $props();

  let windowHeight = $state(defaultHeight);
  let plotHeight = $derived(windowHeight * plotHeightPercentOfWindow);

  let brush = $state({ enabled: false });
  let zoomDomainX = $state<[number, number] | null>(null);
  let zoomDomainY = $state<[number, number] | null>(null);

  let points = $derived(dt ? dt.objects() : []);

  let stats = $derived.by(() => {
    if (!dt) return null;

    return dt
      .rollup({
        median_std: (d) => aq.op.median(d.std_disagreement),
        x_min: (d) => aq.op.min(d.mean_sentiment),
        x_max: (d) => aq.op.max(d.mean_sentiment),
        y_min: (d) => aq.op.min(d.std_disagreement),
        y_max: (d) => aq.op.max(d.std_disagreement),
      })
      .object(0);
  });

  let xPad = $derived(stats ? (stats.x_max - stats.x_min) * plotPadding : 0);
  // let yPad = $derived(stats ? stats.y_max * plotPadding : 0);

  // Use static domains so that different datasets are comparable
  // let defaultDomainX = $derived(
  //   stats ? [stats.x_min - xPad, stats.x_max + xPad] : [0, 1],
  // );
  // let defaultDomainY = $derived(stats ? [0, stats.y_max + yPad] : [0, 1]);

  let animatedDomainX = Tween.of(
    () => zoomDomainX || defaultDomainX,
    theme.animation.options,
  );

  let animatedDomainY = Tween.of(
    () => zoomDomainY || defaultDomainY,
    theme.animation.options,
  );

  const getDotColor = (d) => {
    if (d.mean_sentiment > 0) {
      return theme.colors.positive;
    } else if (d.mean_sentiment < 0) {
      return theme.colors.negative;
    } else {
      return theme.colors.neutral;
    }
  };

  const getDotOpacity = (d) => {
    return Math.min(1, 0.4 + Math.abs(d.mean_sentiment) / domainMax);
  };
</script>

<svelte:window bind:innerHeight={windowHeight} />

{#if stats && points.length > 0}
  <div class="plot-wrapper">
    <Plot
      r={{
        domain: [0, domainMax],
        range: [35, 8],
      }}
      x={{
        domain: animatedDomainX.current,
        label: `${negativeTerm} ← mean sentiment → ${positiveTerm}`,
      }}
      y={{
        domain: animatedDomainY.current,
        // flip y so positive is at the top
        // reverse: true,
      }}
      height={plotHeight}
    >
      <GridX strokeOpacity={theme.grid.strokeOpacity} />
      <GridY strokeOpacity={theme.grid.strokeOpacity} />

      <RuleX
        x={0}
        stroke={theme.stroke.color}
        strokeDasharray={theme.rule.strokeDasharray}
        strokeOpacity={theme.rule.strokeOpacity}
      />
      <RuleY
        y={stats.median_std}
        stroke={theme.stroke.color}
        strokeDasharray={theme.rule.strokeDasharray}
        strokeOpacity={theme.rule.strokeOpacity}
      />

      <Text
        x={stats.x_max + xPad}
        y={stats.median_std}
        text={`median disagreement (${stats.median_std.toFixed(3)})`}
        dy={-5}
        textAnchor="end"
        fill={theme.text.fill}
        fontSize={theme.text.size}
      />

      <Dot
        data={points}
        x="mean_sentiment"
        y="std_disagreement"
        r="std_disagreement"
        fill={getDotColor}
        fillOpacity={getDotOpacity}
        stroke={getDotColor}
        strokeOpacity={0.8}
        strokeWidth={1.5}
      />

      <!-- Quadrant labels -->
      <Text
        x={defaultDomainX[0]}
        y={defaultDomainY[1]}
        text="negative contested"
        dx={theme.quadrantLabel.paddingX}
        dy={theme.quadrantLabel.paddingY}
        fontSize={theme.text.size}
        textAnchor="start"
        fill={theme.text.fill}
      />
      <Text
        x={defaultDomainX[1]}
        y={defaultDomainY[1]}
        text="positive contested"
        dx={-theme.quadrantLabel.paddingX}
        dy={theme.quadrantLabel.paddingY}
        fontSize={theme.text.size}
        textAnchor="end"
        fill={theme.text.fill}
      />
      <Text
        x={defaultDomainX[0]}
        y={defaultDomainY[0]}
        text="negative consensus"
        dx={theme.quadrantLabel.paddingX}
        dy={-theme.quadrantLabel.paddingY}
        fontSize={theme.text.size}
        textAnchor="start"
        fill={theme.text.fill}
      />
      <Text
        x={defaultDomainX[1]}
        y={defaultDomainY[0]}
        text="positive consensus"
        dx={-theme.quadrantLabel.paddingX}
        dy={-theme.quadrantLabel.paddingY}
        fontSize={theme.text.size}
        textAnchor="end"
        fill={theme.text.fill}
      />

      {#each points as point}
        <Text
          x={point.mean_sentiment}
          y={point.std_disagreement}
          text={point.term}
          dx={6}
          dy={-6}
          fontSize={theme.text.size}
          fillOpacity={0.9}
        />
      {/each}

      <Brush
        bind:brush
        cursor={zoomDomainX ? "zoom-out" : "zoom-in"}
        onbrushend={(e) => {
          if (e?.brush?.x1 !== undefined && e?.brush?.x2 !== undefined) {
            zoomDomainX = [e.brush.x1, e.brush.x2];
            zoomDomainY = [e.brush.y1, e.brush.y2];
            e.brush.enabled = false;
          } else {
            zoomDomainX = null;
            zoomDomainY = null;
          }
        }}
      />
    </Plot>
  </div>

  <div class="plot-legend d-flex flex-row bg-body-secondary p-2 rounded-2">
    <div class="legend-item d-flex align-items-center">
      <span class="dot-sample size-large d-inline-block rounded-circle"></span>
      <span class="dot-sample size-small d-inline-block rounded-circle"></span>
      <p class="mb-0">
        <strong>Diameter (Y Axis):</strong> Larger = High Consensus
      </p>
    </div>

    <div class="legend-item d-flex align-items-center">
      <span class="dot-sample opacity-solid d-inline-block rounded-circle"
      ></span>
      <span class="dot-sample opacity-faint d-inline-block rounded-circle"
      ></span>
      <p class="mb-0">
        <strong>Opacity (X Axis):</strong> More Solid = High Intensity
      </p>
    </div>
  </div>
{/if}

<style>
  .plot-legend {
    gap: 2rem;
  }

  .legend-item {
    gap: 0.75rem;
  }

  .dot-sample {
    background: currentColor;
  }

  .size-large {
    width: 14px;
    height: 14px;
  }

  .size-small {
    width: 6px;
    height: 6px;
  }

  .opacity-solid {
    width: 10px;
    height: 10px;
    opacity: 1;
  }

  .opacity-faint {
    width: 10px;
    height: 10px;
    opacity: 0.3;
  }
</style>
