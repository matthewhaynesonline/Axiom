<script lang="ts">
  import type { Snippet } from "svelte";
  import Modal from "./Modal.svelte";

  let { csv, children }: { csv: string; children?: Snippet } = $props();

  let showModal = $state(false);
  let copied = $state(false);

  async function copyCsv() {
    try {
      await navigator.clipboard.writeText(csv);
      copied = true;

      setTimeout(() => {
        copied = false;
      }, 1500);
    } catch (err) {
      console.error("Failed to copy CSV:", err);
    }
  }
</script>

<Modal show={showModal} title="Export Data" onclose={() => (showModal = false)}>
  {#if children}
    {@render children()}
  {/if}

  <div class="csv-wrapper overflow-auto">
    <pre><code>{csv}</code></pre>
  </div>

  <button type="button" class="btn btn-primary btn-sm mt-3" onclick={copyCsv}>
    {copied ? "Copied!" : "Click to Copy"}
  </button>
</Modal>

<button
  type="button"
  class="btn btn-link btn-sm float-end"
  onclick={() => (showModal = true)}
>
  Export Data
</button>

<style>
  .csv-wrapper {
    max-height: 40vh;
  }
</style>
