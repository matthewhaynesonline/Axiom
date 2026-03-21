<script lang="ts">
  import type { AppTabList, AppTab } from "../types";

  let {
    activeTab = $bindable(),
    tabs,
  }: {
    activeTab: AppTab;
    tabs: AppTabList;
  } = $props();

  function onTabClick(tab: AppTab): void {
    activeTab = tab;
  }
</script>

<ul class="nav nav-underline mb-2" role="tablist">
  {#each tabs as tab}
    <li class="nav-item" role="presentation">
      <button
        type="button"
        class="nav-link"
        class:active={tab === activeTab}
        role="tab"
        aria-selected={tab === activeTab}
        onclick={() => onTabClick(tab)}
      >
        {tab}
      </button>
    </li>
  {/each}
</ul>
