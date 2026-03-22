<script lang="ts">
  import * as aq from "arquero";

  import type { ValueSystemRanking } from "./types";

  import definitions from "../definitions.json";

  import { createContinuousScale as createColorScale } from "./plot";
  import { formatDecimal } from "./utils";

  import { groupSortKey } from "./models/model_utils";

  import MethodologyModal from "./ui/MethodologyModal.svelte";

  let {
    dt,
  }: {
    dt?: aq.ColumnTable | null;
  } = $props();

  let colorScale = $state();

  let rows: ValueSystemRanking[] = $derived(
    dt?.objects() ?? [],
  ) as ValueSystemRanking[];

  let groupedRows = $derived.by(() => {
    const grouped = rows.reduce((acc, row) => {
      const { query, model_name } = row;

      if (!acc[query]) acc[query] = {};
      if (!acc[query][model_name]) acc[query][model_name] = [];

      acc[query][model_name].push(row);

      return acc;
    }, {});

    for (const query of Object.keys(grouped)) {
      const modelMap = grouped[query];

      // Sort each model's rankings by original rank first
      for (const rankings of Object.values(modelMap)) {
        rankings.sort((a, b) => Number(a.rank) - Number(b.rank));
      }

      const optionRankAccum = {};

      for (const rankings of Object.values(modelMap)) {
        for (const row of rankings) {
          if (!optionRankAccum[row.option]) {
            optionRankAccum[row.option] = {
              totalRank: 0,
              totalScore: 0,
              totalScoreNorm: 0,
              count: 0,
            };
          }
          optionRankAccum[row.option].totalRank += Number(row.rank);
          optionRankAccum[row.option].totalScore += row.score;
          optionRankAccum[row.option].totalScoreNorm += row.score_norm;
          optionRankAccum[row.option].count += 1;
        }
      }

      // Attach averages to each row without clobbering the original rank
      for (const rankings of Object.values(modelMap)) {
        for (const row of rankings) {
          const accum = optionRankAccum[row.option];
          row.avg_rank = accum.totalRank / accum.count;
          row.avg_score = accum.totalScore / accum.count;
          row.avg_score_norm = accum.totalScoreNorm / accum.count;
        }
      }

      const sortedModelEntries = Object.entries(modelMap).sort(
        ([, aRankings], [, bRankings]) => {
          const aGroup = aRankings[0]?.model_group ?? "";
          const bGroup = bRankings[0]?.model_group ?? "";

          const groupComparison = groupSortKey(aGroup) - groupSortKey(bGroup);
          if (groupComparison !== 0) return groupComparison;

          return aGroup.localeCompare(bGroup);
        },
      );

      grouped[query] = {
        Average: Object.entries(optionRankAccum)
          .map(
            ([option, { totalRank, totalScore, totalScoreNorm, count }]) => ({
              option,
              rank: totalRank / count,
              score: totalScore / count,
              score_norm: totalScoreNorm / count,
            }),
          )
          .sort((a, b) => a.rank - b.rank),
        ...Object.fromEntries(sortedModelEntries),
      };
    }

    return grouped;
  });

  let loaded = $derived(!!colorScale);

  // let dtHTML = $derived(dt.toHTML());

  $effect(() => {
    colorScale = createColorScale();
  });
</script>

<MethodologyModal>
  <p>
    <strong>
      Note: this does not use the axis projection scoring method that the other
      insights use.
    </strong>
  </p>

  <p>
    Each question (e.g. Best type of economy) and each candidate answer (e.g.
    capitalism, socialism) are encoded using each model's query encoding
    function. Similarity between the question embedding and each answer
    embedding is computed via cosine similarity. Results are then min-max
    normalized within each model so scores are comparable across questions with
    different numbers of options.
  </p>

  <p>
    The final ranking reflects which answers each model places geometrically
    closest to the question in embedding space.
  </p>
</MethodologyModal>

<!-- {@html dtHTML} -->

<p class="fst-italic">
  Hover over a result to see the definition and non normalized score.
</p>

{#if loaded}
  {#each Object.entries(groupedRows) as [query, modelMap]}
    <h5 class="border-start border-4 border-success my-4 ps-2">
      {query}
    </h5>

    <div class="model-rank-row d-flex flex-row mb-5">
      {#each Object.entries(modelMap) as [model_name, rankings]}
        <div class="model-rank-card">
          <div class="card bg-body-tertiary h-100">
            <div class="card-body">
              <h6 class="card-subtitle mb-2 text-body-secondary">
                {model_name}
              </h6>

              <ol>
                {#each rankings as row}
                  <li>
                    <div
                      class="d-flex rank-item rounded hover-group align-items-center justify-content-between px-2 py-1 mb-1"
                      style="background-color: {colorScale(row.score_norm)};"
                      title={definitions[row.option]}
                      onmouseenter={(e) =>
                        (e.currentTarget.style.backgroundColor = colorScale(
                          row.score,
                        ))}
                      onmouseleave={(e) =>
                        (e.currentTarget.style.backgroundColor = colorScale(
                          row.score_norm,
                        ))}
                    >
                      <span class="rank-label text-truncate">{row.option}</span>
                      <span class="show-on-parent-hover rank-score">
                        {formatDecimal(row.score)}
                      </span>
                    </div>

                    <!-- <div
                      class="d-flex rank-item rounded hover-group align-items-center justify-content-between px-2 py-1 mb-1"
                      style="background-color: {colorScale(row.score)};"
                      title={row.option}
                    >
                      <span class="rank-label text-truncate">{row.option}</span>
                      <span class="show-on-parent-hover rank-score">
                        {formatDecimal(row.score)}
                      </span>
                    </div> -->
                  </li>
                {/each}
              </ol>
            </div>
          </div>
        </div>
      {/each}
    </div>
  {/each}
{/if}

<style>
  .rank-item {
    min-height: 30px;
    transition: all 150ms ease;
  }

  ol {
    padding-left: 1.25rem;
    margin-bottom: 0;
  }

  .model-rank-row {
    gap: 12px;
    overflow-x: auto;
  }

  .model-rank-card {
    flex: 0 0 225px;
    min-width: 0;
  }
</style>
