<script lang="ts">
  let {
    models,
    selectedModel = $bindable(),
    termCategories,
    selectedTermCategory = $bindable(),
    judgementTermsCategories,
    selectedJudgementTermsCategory = $bindable(),
    showCompositeGroups = $bindable(),
  }: {
    models: string[];
    selectedModel: string;
    termCategories: string[];
    selectedTermCategory: string;
    judgementTermsCategories: string[];
    selectedJudgementTermsCategory: string;
    showCompositeGroups: boolean;
  } = $props();

  function doReset(): void {
    selectedModel = null;
    selectedTermCategory = null;
    selectedJudgementTermsCategory = null;
    showCompositeGroups = true;
  }
</script>

{#if models}
  <label for="model-select">Model</label>
  <select name="model-select" bind:value={selectedModel}>
    <option value={null}> - All - </option>

    {#each models as model}
      <option value={model}>
        {model}
      </option>
    {/each}
  </select>
{/if}

{#if termCategories}
  <label for="category-select">Category</label>
  <select name="category-select" bind:value={selectedTermCategory}>
    <option value={null}> - All - </option>

    {#each termCategories as termCategory}
      <option value={termCategory}>
        {termCategory}
      </option>
    {/each}
  </select>
{/if}

{#if judgementTermsCategories}
  <label for="judgement-select">Judgement Criteria</label>
  <select name="judgement-select" bind:value={selectedJudgementTermsCategory}>
    <option value={null}> - All - </option>

    {#each judgementTermsCategories as judgementTermsCategy}
      <option value={judgementTermsCategy}>
        {judgementTermsCategy}
      </option>
    {/each}
  </select>
{/if}

<div class="mb-3 form-check form-switch">
  <input
    class="form-check-input cursor-pointer"
    type="checkbox"
    role="switch"
    id="compositeToggle"
    bind:checked={showCompositeGroups}
  />
  <label class="form-check-label cursor-pointer" for="compositeToggle">
    Include Composite Group Averages (e.g. West, Academia)
  </label>
</div>

{#if models || termCategories || judgementTermsCategories}
  <button
    type="button"
    class="btn btn-outline-secondary btn-sm"
    onclick={doReset}
  >
    Reset
  </button>
{/if}
