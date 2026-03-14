<script lang="ts">
  let {
    tabs,
    activeTab = $bindable(),
  }: {
    tabs: string[];
    activeTab: string;
  } = $props();

  function changeActiveTab(newTab: string) {
    activeTab = newTab;
  }
</script>

<div>
  <ul class="nav nav-tabs">
    {#each tabs as tab}
      <li class="nav-item">
        <button
          type="button"
          class="nav-link"
          class:active={tab === activeTab}
          onclick={() => changeActiveTab(tab)}
        >
          {tab}
        </button>
      </li>
    {/each}
  </ul>
</div>
