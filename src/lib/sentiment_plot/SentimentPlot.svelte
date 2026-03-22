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

  const DOMAIN_MAX = config.scale.sentiment.max;
  const DEFAULT_DOMAIN_X: [number, number] = [-DOMAIN_MAX, DOMAIN_MAX];
  const DEFAULT_DOMAIN_Y: [number, number] = [-0.1, 0.35];

  const PLOT_THEME = {
    defaultHeight: 800,
    heightPercentOfWindow: 0.65,
    padding: 0.05,
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
    dt: aq.ColumnTable | null;
    positiveTerm: string | null;
    negativeTerm: string | null;
  } = $props();

  let windowHeight = $state(PLOT_THEME.defaultHeight);
  let plotHeight = $derived(windowHeight * PLOT_THEME.heightPercentOfWindow);

  let brush = $state({ enabled: false });
  let zoomDomainX = $state<[number, number] | null>(null);
  let zoomDomainY = $state<[number, number] | null>(null);

  let points = $derived(dt?.objects() ?? []);

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

  let xPad = $derived(
    stats ? (stats.x_max - stats.x_min) * PLOT_THEME.padding : 0,
  );

  let animatedDomainX = Tween.of(
    () => zoomDomainX ?? DEFAULT_DOMAIN_X,
    PLOT_THEME.animation.options,
  );

  let animatedDomainY = Tween.of(
    () => zoomDomainY ?? DEFAULT_DOMAIN_Y,
    PLOT_THEME.animation.options,
  );

  function getDotColor(d): string {
    if (d.mean_sentiment > 0) return PLOT_THEME.colors.positive;
    if (d.mean_sentiment < 0) return PLOT_THEME.colors.negative;
    return PLOT_THEME.colors.neutral;
  }

  function getDotOpacity(d): number {
    return Math.min(1, 0.4 + Math.abs(d.mean_sentiment) / DOMAIN_MAX);
  }

  function handleBrushEnd(e) {
    if (e?.brush?.x1 !== undefined && e?.brush?.x2 !== undefined) {
      zoomDomainX = [e.brush.x1, e.brush.x2];
      zoomDomainY = [e.brush.y1, e.brush.y2];
      e.brush.enabled = false;
    } else {
      zoomDomainX = null;
      zoomDomainY = null;
    }
  }
</script>

<svelte:window bind:innerHeight={windowHeight} />

{#if stats && points.length > 0}
  <div class="plot-wrapper">
    <Plot
      r={{ domain: [0, DOMAIN_MAX], range: [35, 8] }}
      x={{
        domain: animatedDomainX.current,
        label: `${negativeTerm} ← mean sentiment → ${positiveTerm}`,
      }}
      y={{ domain: animatedDomainY.current }}
      height={plotHeight}
    >
      <GridX strokeOpacity={PLOT_THEME.grid.strokeOpacity} />
      <GridY strokeOpacity={PLOT_THEME.grid.strokeOpacity} />

      <RuleX
        x={0}
        stroke={PLOT_THEME.stroke.color}
        strokeDasharray={PLOT_THEME.rule.strokeDasharray}
        strokeOpacity={PLOT_THEME.rule.strokeOpacity}
      />
      <RuleY
        y={stats.median_std}
        stroke={PLOT_THEME.stroke.color}
        strokeDasharray={PLOT_THEME.rule.strokeDasharray}
        strokeOpacity={PLOT_THEME.rule.strokeOpacity}
      />

      <Text
        x={stats.x_max + xPad}
        y={stats.median_std}
        text={`median disagreement (${stats.median_std.toFixed(3)})`}
        dy={-5}
        textAnchor="end"
        fill={PLOT_THEME.text.fill}
        fontSize={PLOT_THEME.text.size}
      />

      <!-- Quadrant labels -->
      <Text
        x={DEFAULT_DOMAIN_X[0]}
        y={DEFAULT_DOMAIN_Y[1]}
        dx={PLOT_THEME.quadrantLabel.paddingX}
        dy={PLOT_THEME.quadrantLabel.paddingY}
        text="negative contested"
        fontSize={PLOT_THEME.text.size}
        textAnchor="start"
        fill={PLOT_THEME.text.fill}
      />

      <Text
        x={DEFAULT_DOMAIN_X[1]}
        y={DEFAULT_DOMAIN_Y[1]}
        dx={-PLOT_THEME.quadrantLabel.paddingX}
        dy={PLOT_THEME.quadrantLabel.paddingY}
        text="positive contested"
        fontSize={PLOT_THEME.text.size}
        textAnchor="end"
        fill={PLOT_THEME.text.fill}
      />

      <Text
        x={DEFAULT_DOMAIN_X[0]}
        y={DEFAULT_DOMAIN_Y[0]}
        dx={PLOT_THEME.quadrantLabel.paddingX}
        dy={-PLOT_THEME.quadrantLabel.paddingY}
        text="negative consensus"
        fontSize={PLOT_THEME.text.size}
        textAnchor="start"
        fill={PLOT_THEME.text.fill}
      />

      <Text
        x={DEFAULT_DOMAIN_X[1]}
        y={DEFAULT_DOMAIN_Y[0]}
        dx={-PLOT_THEME.quadrantLabel.paddingX}
        dy={-PLOT_THEME.quadrantLabel.paddingY}
        text="positive consensus"
        fontSize={PLOT_THEME.text.size}
        textAnchor="end"
        fill={PLOT_THEME.text.fill}
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

      {#each points as point}
        <Text
          x={point.mean_sentiment}
          y={point.std_disagreement}
          text={point.term}
          dx={6}
          dy={-6}
          fontSize={PLOT_THEME.text.size}
          fillOpacity={0.9}
        />
      {/each}

      <Brush
        bind:brush
        cursor={zoomDomainX ? "zoom-out" : "zoom-in"}
        onbrushend={handleBrushEnd}
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
