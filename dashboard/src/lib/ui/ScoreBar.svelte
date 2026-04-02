<script lang="ts">
  import type { CssBgClass } from "../types";

  import config from "../../config.json";

  import { getDisplayScore } from "./ui_utils";

  import ScoreVal from "./ScoreVal.svelte";

  let {
    score,
  }: {
    score: number;
  } = $props();

  let normalizedScore = $derived(score + config.scale.offset);
  let scorePercent = $derived(Math.abs(scoreToPercent(score)));
  let bgClass = $derived(scoreToCssClass(score));

  let displayScore = $derived(getDisplayScore(score));

  function scoreToPercent(score: number): number {
    return (normalizedScore / config.scale.normalizedScaleScoreMax) * 100;
  }

  function scoreToCssClass(score: number): CssBgClass {
    if (score > 0) return "bg-success";
    if (score == 0) return "bg-secondary";
    if (score < 0) return "bg-danger";

    return "bg-dark";
  }
</script>

<div class="d-flex flex-row align-items-center">
  <div class="px-2 flex-grow-1">
    <div
      class="progress"
      role="progressbar"
      aria-label="Score"
      aria-valuenow={scorePercent}
      aria-valuemin="0"
      aria-valuemax="100"
    >
      <div class="progress-bar {bgClass}" style="width: {scorePercent}%"></div>
    </div>
  </div>

  <div class="px-2">
    <ScoreVal {score} />
  </div>
</div>

<style>
  /* since other items don't transition, temp disable this animation */
  .progress-bar {
    transition: none;
  }
</style>
