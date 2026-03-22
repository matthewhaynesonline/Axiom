<script lang="ts">
  import type { Snippet } from "svelte";
  import { fade } from "svelte/transition";

  interface Props {
    show: boolean;
    title?: string;
    onclose: () => void;
    children: Snippet;
    footer?: Snippet;
  }

  let { show, title = "", onclose, children, footer }: Props = $props();
</script>

{#if show}
  <div class="modal-backdrop show" transition:fade={{ duration: 150 }}></div>

  <div
    class="modal modal-lg show d-block"
    tabindex="-1"
    role="dialog"
    onclick={onclose}
    transition:fade={{ duration: 150 }}
  >
    <div
      class="modal-dialog modal-dialog-centered"
      role="document"
      onclick={(e) => e.stopPropagation()}
    >
      <div class="modal-content">
        {#if title}
          <div class="modal-header">
            <h5 class="modal-title">{title}</h5>
            <button
              type="button"
              class="btn-close"
              aria-label="Close"
              onclick={onclose}
            ></button>
          </div>
        {/if}

        <div class="modal-body">
          {@render children()}
        </div>

        {#if footer}
          <div class="modal-footer">
            {@render footer()}
          </div>
        {/if}
      </div>
    </div>
  </div>
{/if}
