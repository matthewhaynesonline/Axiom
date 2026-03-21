<script lang="ts">
  import type { CssTextBgClass } from "../types";

  let {
    label,
    bgClass,
  }: {
    label: string;
    bgClass: CssTextBgClass;
  } = $props();
</script>

<span class="badge rounded-pill {bgClass}">
  {label}
</span>
