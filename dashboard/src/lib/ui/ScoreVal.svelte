<script lang="ts">
  import type { CssTextClass } from "../types";

  import { getDisplayScore } from "./ui_utils";

  let {
    score,
  }: {
    score: number;
  } = $props();

  let cssClass = $derived(scoreToCssClass(score));
  let displayScore = $derived(getDisplayScore(score));

  function scoreToCssClass(score: number): CssTextClass {
    if (score > 0) return "text-success";
    if (score == 0) return "text-secondary";
    if (score < 0) return "text-danger";

    return "text-dark";
  }
</script>

<pre class="{cssClass} mb-0">{displayScore}</pre>
