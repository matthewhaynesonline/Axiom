<script lang="ts">
  let {
    active = false,
    sortDesc = false,
  }: {
    active: boolean;
    sortDesc: boolean;
  } = $props();

  const SORT_ICONS = {
    asc: "▲",
    desc: "▼",
  };

  let sortIcon = $derived(sortDesc ? SORT_ICONS.desc : SORT_ICONS.asc);
</script>

{#if active}
  <span>{sortIcon}</span>
{/if}
