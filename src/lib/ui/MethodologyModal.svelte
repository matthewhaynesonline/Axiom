<!-- MethodologyModal.svelte -->
<script lang="ts">
  import type { Snippet } from "svelte";
  import Modal from "./Modal.svelte";

  interface Props {
    children: Snippet;
  }

  let { children }: Props = $props();

  let showModal = $state(false);
</script>

<Modal show={showModal} title="Methodology" onclose={() => (showModal = false)}>
  {@render children()}
</Modal>

<button
  type="button"
  class="btn btn-link btn-sm float-end"
  onclick={() => (showModal = true)}
>
  Methodology
</button>
