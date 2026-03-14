<script lang="ts">
  let {
    active = false,
    sortDesc = false,
  }: {
    active: boolean;
    sortDesc: boolean;
  } = $props();

  const sortIcons = {
    asc: "▲",
    desc: "▼",
  };

  let sortIcon = $derived(sortDesc ? sortIcons.desc : sortIcons.asc);
</script>

{#if active}
  <span>{sortIcon}</span>
{/if}
