<script lang="ts">
  import type { Model } from "../types";

  import config from "../../config.json";

  import {
    modelGroupToCssButtonClass,
    sortModels,
  } from "../models/model_utils";

  let {
    expanded = $bindable(),
    models,
    selectedModels = $bindable(),
    termCategories,
    selectedTermCategory = $bindable(),
    judgementTermsCategories,
    selectedJudgementTermsCategory = $bindable(),
    showCompositeGroups = $bindable(),
  }: {
    expanded: boolean;
    models?: Model[] | null;
    selectedModels?: Model[];
    termCategories?: string[];
    selectedTermCategory?: string | null;
    judgementTermsCategories?: string[];
    selectedJudgementTermsCategory?: string | null;
    showCompositeGroups: boolean;
  } = $props();

  let groupedModels = $derived.by(() => {
    return models.reduce((acc, model) => {
      const group = model.group;

      if (!acc[group]) {
        acc[group] = [];
      }

      acc[group].push(model);

      return acc;
    }, {});
  });

  function toggleExpanded(): void {
    expanded = !expanded;
  }

  function toggleSelectedModel(model: Model): void {
    if (models == undefined || selectedModels == undefined) {
      return;
    }

    const modelIndex = selectedModels.findIndex(
      (m) => m.model_id === model.model_id,
    );

    if (modelIndex > -1) {
      selectedModels.splice(modelIndex, 1);
    } else {
      selectedModels.push(model);
      selectedModels = sortModels(selectedModels);
    }
  }

  function enableAllModels(): void {
    if (selectedModels !== undefined) {
      selectedModels = models;
    }
  }

  function disableAllModels(): void {
    selectedModels = [];
  }

  function doReset(): void {
    selectedTermCategory = null;
    selectedJudgementTermsCategory = null;

    showCompositeGroups = true;

    if (selectedModels !== undefined) {
      selectedModels = models;
    }
  }
</script>

<div class="card bg-body-tertiary my-4">
  <div class="card-body">
    {#if expanded}
      <div class="row">
        <div class="col-12 col-md-6 col-lg-7 col-xl-8 border-end">
          {#if models && selectedModels}
            <div>
              <label class="form-label {config.theme.headingCssClasses}">
                Models
              </label>
            </div>

            <div class="row row-cols-2">
              {#each Object.entries(groupedModels) as [groupName, groupModels]}
                <div class="col mt-2">
                  <div>{groupName}</div>
                  {#each groupModels as model}
                    <button
                      type="button"
                      class="btn btn-sm m-1 rounded px-1 py-0
              {selectedModels.some((m) => m.model_id === model.model_id)
                        ? modelGroupToCssButtonClass(model.group)[0]
                        : modelGroupToCssButtonClass(model.group)[1]}"
                      onclick={() => toggleSelectedModel(model)}
                    >
                      {model.model_name}
                    </button>
                  {/each}
                </div>
              {/each}
            </div>

            <div class="mt-3">
              <button
                type="button"
                class="btn btn-sm btn-link text-decoration-none"
                onclick={enableAllModels}
              >
                Enable All
              </button>

              <button
                type="button"
                class="btn btn-sm btn-link text-decoration-none"
                onclick={disableAllModels}
              >
                Disable All
              </button>

              <div class="form-check form-switch d-inline-block ms-2">
                <input
                  class="form-check-input cursor-pointer"
                  type="checkbox"
                  role="switch"
                  id="compositeToggle"
                  bind:checked={showCompositeGroups}
                />
                <label
                  class="form-check-label cursor-pointer"
                  for="compositeToggle"
                >
                  Composite Groups
                </label>
              </div>
            </div>
          {:else}
            <div class="form-label {config.theme.headingCssClasses}">
              Models
            </div>

            <span class="fst-italic">
              Individual Models Filter Not Applicable
            </span>

            <div class="mt-3 form-check form-switch">
              <input
                class="form-check-input cursor-pointer"
                type="checkbox"
                role="switch"
                id="compositeToggle"
                bind:checked={showCompositeGroups}
              />
              <label
                class="form-check-label cursor-pointer"
                for="compositeToggle"
              >
                Composite Groups
              </label>
            </div>
          {/if}
        </div>

        <div class="col-12 col-md-6 col-lg-5 col-xl-4 d-flex flex-column">
          <div class="row mb-3">
            {#if termCategories}
              <div class="col">
                <label
                  class="form-label {config.theme.headingCssClasses}"
                  for="category-select">Category</label
                >
                <select
                  class="form-select"
                  name="category-select"
                  bind:value={selectedTermCategory}
                >
                  <option value={null}> - All - </option>

                  {#each termCategories as termCategory}
                    <option value={termCategory}>
                      {termCategory}
                    </option>
                  {/each}
                </select>
              </div>
            {/if}

            {#if judgementTermsCategories}
              <div class="col">
                <label
                  class="form-label {config.theme.headingCssClasses}"
                  for="judgement-select">Judgement Criteria</label
                >
                <select
                  class="form-select"
                  name="judgement-select"
                  bind:value={selectedJudgementTermsCategory}
                >
                  <option value={null}> - All - </option>

                  {#each judgementTermsCategories as judgementTermsCategy}
                    <option value={judgementTermsCategy}>
                      {judgementTermsCategy}
                    </option>
                  {/each}
                </select>
              </div>
            {/if}
          </div>

          <div class="row mt-auto">
            {#if models || termCategories || judgementTermsCategories}
              <div class="col">
                <button
                  type="button"
                  class="btn btn-secondary btn-sm px-4 bg-body border-secondary-subtle"
                  onclick={doReset}
                >
                  Reset
                </button>
              </div>
            {/if}

            <div class="col">
              <button
                type="button"
                class="btn btn-secondary btn-sm px-4 bg-body border-secondary-subtle float-end"
                onclick={toggleExpanded}
              >
                {#if expanded}
                  hide ▲
                {:else}
                  show ▼
                {/if}
              </button>
            </div>
          </div>
        </div>
      </div>
    {:else}
      <div class="row">
        <div>
          <span class="form-label {config.theme.headingCssClasses}">
            Filters
          </span>

          <span class="badge rounded-pill text-bg-secondary ms-2">
            Category
          </span>

          <span class="badge rounded-pill text-bg-secondary ms-2">
            Judgement Criteria
          </span>

          <span class="badge rounded-pill text-bg-secondary ms-2">Models</span>

          <button
            type="button"
            class="btn btn-secondary btn-sm px-4 bg-body border-secondary-subtle float-end"
            onclick={toggleExpanded}
          >
            {#if expanded}
              hide ▲
            {:else}
              show ▼
            {/if}
          </button>
        </div>
      </div>
    {/if}
  </div>
</div>
