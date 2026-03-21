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
    termCategories: string[];
    selectedTermCategory: string | null;
    judgementTermsCategories: string[];
    selectedJudgementTermsCategory: string | null;
    showCompositeGroups: boolean;
  } = $props();

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

  function doReset(): void {
    selectedTermCategory = null;
    selectedJudgementTermsCategory = null;

    showCompositeGroups = true;

    if (selectedModels !== undefined) {
      selectedModels = models;
    }
  }
</script>

<div class="card bg-body-tertiary my-3">
  <div class="card-body">
    {#if expanded}
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

      <div class="row">
        <div class="col">
          <div class="row">
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

          <div class="row align-items-end mt-3">
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
              <div class="mb-3 form-check form-switch">
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
                  Include Composite Group Averages (e.g. West, Academia)
                </label>
              </div>
            </div>
          </div>
        </div>

        <div class="col">
          {#if models && selectedModels}
            <div>
              <label class="form-label {config.theme.headingCssClasses}">
                Models
              </label>
            </div>

            {#each models as model}
              <button
                type="button"
                class="btn btn-sm m-1 rounded
              {selectedModels.some((m) => m.model_id === model.model_id)
                  ? modelGroupToCssButtonClass(model.group)[0]
                  : modelGroupToCssButtonClass(model.group)[1]}"
                onclick={() => toggleSelectedModel(model)}
              >
                {model.model_name}
              </button>
            {/each}
          {:else}
            <span class="form-label {config.theme.headingCssClasses}">
              Models Filter Not Applicable
            </span>
          {/if}
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
