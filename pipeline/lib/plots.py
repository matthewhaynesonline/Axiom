import time

from typing import Any

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import polars as pl

from matplotlib import colormaps
from matplotlib.patches import Patch
from polars import DataFrame
# from sklearn.decomposition import PCA

from .pipeline import (
    ensure_dirs,
    get_avg_sentiment_independent_normalization,
    get_sentiment_compare_df,
    ScoringStrategy,
    build_all_avgs,
)

DEFAULT_FIG_DIMENSION = 7


######
# Plots: All
######
def plot_sentiment_vs_disagreement(
    model_results: list[dict],
    a_category: str,
    b_category: str,
    positive_term: str,
    negative_term: str,
    strategy: ScoringStrategy = ScoringStrategy.AXIS_PROJECTION,
    label_threshold: float = 0.08,
) -> DataFrame:
    """
    Sentiment vs disagreement scatter.

    x = mean sentiment across all models  (negative = negative term, positive = positive term)
    y = consensus across all models       (low = consensus, high = contested)

    This gives four quadrants:
        top left  : contested & negative  — models disagree but lean negative
        top right : contested & positive  — models disagree but lean positive
        bot left  : consensus negative    — all models agree: negative leaning
        bot right : consensus positive    — all models agree: positive leaning

    Terms near the origin are both low-sentiment and low-disagreement —
    the embedding models treat them as effectively neutral.  Terms far from
    the origin are either strongly opinionated (far left/right) or highly
    contested (high up), or both. Colour encodes mean absolute sentiment so
    the most charged terms stand out regardless of direction.
    """
    all_avgs = build_all_avgs(
        model_results, a_category, b_category, positive_term, negative_term, strategy
    )

    model_ids = list(all_avgs.keys())
    terms = sorted(next(iter(all_avgs.values())).keys())

    # Per term stats across models
    scores_matrix = np.array(
        [[all_avgs[model_id][term] for model_id in model_ids] for term in terms]
    )

    mean_sentiment = scores_matrix.mean(axis=1)
    std_disagreement = scores_matrix.std(axis=1)
    abs_sentiment = np.abs(mean_sentiment)

    fig, ax = plt.subplots(figsize=(9, 7))

    scatter = ax.scatter(
        mean_sentiment,
        std_disagreement,
        c=abs_sentiment,
        cmap="RdPu",
        s=60,
        alpha=0.85,
        vmin=0,
        vmax=abs_sentiment.max(),
    )

    plt.colorbar(scatter, ax=ax, label="mean |sentiment| (higher = more charged)")

    # Quadrant dividers
    ax.axvline(0, color="grey", linewidth=0.8, linestyle="--", alpha=0.6)

    # Horizontal guide at median std so "high" vs "low" disagreement is clear
    median_std = float(np.median(std_disagreement))

    ax.axhline(
        median_std,
        color="grey",
        linewidth=0.6,
        linestyle=":",
        alpha=0.5,
        label=f"median disagreement ({median_std:.3f})",
    )

    # Quadrant labels — placed at chart edges, not near data
    x_min, x_max = mean_sentiment.min(), mean_sentiment.max()
    x_pad = (x_max - x_min) * 0.03

    y_min, y_max = std_disagreement.min(), std_disagreement.max()
    y_pad = y_max * 0.03

    quadrant_style: dict[str, Any] = dict(fontsize=8, alpha=0.4, fontstyle="italic")

    ax.text(
        x_min + x_pad,
        y_max - y_pad,
        "contested negative",
        ha="left",
        va="top",
        color="red",
        **quadrant_style,
    )

    ax.text(
        x_max - x_pad,
        y_max - y_pad,
        "contested positive",
        ha="right",
        va="top",
        color="green",
        **quadrant_style,
    )

    ax.text(
        x_min + x_pad,
        y_min + y_pad,
        "consensus negative",
        ha="left",
        va="bottom",
        color="red",
        **quadrant_style,
    )

    ax.text(
        x_max - x_pad,
        y_min + y_pad,
        "consensus positive",
        ha="right",
        va="bottom",
        color="green",
        **quadrant_style,
    )

    # Label the most contested or most charged terms
    for term, x, y, charge in zip(
        terms, mean_sentiment, std_disagreement, abs_sentiment
    ):
        if y > label_threshold or charge > label_threshold:
            ax.annotate(
                term,
                (x, y),
                textcoords="offset points",
                xytext=(4, 4),
                fontsize=7,
                alpha=0.9,
            )

    ax.set_xlabel(
        f"{negative_term} ← mean sentiment across {len(model_ids)} models → {positive_term}"
    )

    ax.set_ylabel("std across models  (low = consensus, high = contested)")

    ax.set_title(
        f"{a_category}  ·  {positive_term} / {negative_term}  [{strategy.value}]\n"
        f"sentiment vs disagreement — {len(terms)} terms"
    )

    ax.legend(fontsize=8)

    plt.tight_layout()
    plt.show()

    return pl.DataFrame(
        {
            "term": terms,
            "mean_sentiment": mean_sentiment.tolist(),
            "std_disagreement": std_disagreement.tolist(),
        }
    ).sort("std_disagreement", descending=True)


def plot_all_models_sentiment(
    model_results: list[dict],
    a_category: str,
    b_category: str,
    positive_term: str,
    negative_term: str,
    out_dir: str,
    strategy: ScoringStrategy = ScoringStrategy.AXIS_PROJECTION,
) -> DataFrame:
    """
    Heatmap of avg sentiment for every term (rows) and every model (columns)
    """
    ensure_dirs(out_dir)

    all_avgs = build_all_avgs(
        model_results, a_category, b_category, positive_term, negative_term, strategy
    )

    strategy_label = strategy.value
    model_ids = list(all_avgs.keys())
    terms = sorted(next(iter(all_avgs.values())).keys())

    scores_matrix = np.array(
        [[all_avgs[model_id][term] for model_id in model_ids] for term in terms]
    )

    row_order = np.argsort(scores_matrix.mean(axis=1))[::-1]
    scores_matrix = scores_matrix[row_order]
    terms = [terms[i] for i in row_order]

    title = (
        f"{a_category} — avg sentiment across all models\n"
        f"({positive_term} / {negative_term})  [{strategy_label}]"
    )

    _plot_heatmap(scores_matrix, terms, model_ids, title, positive_term, negative_term)

    return pl.DataFrame(
        {
            "term": terms,
            **{mid: scores_matrix[:, i].tolist() for i, mid in enumerate(model_ids)},
        }
    )


def _plot_heatmap(
    matrix: np.ndarray,
    terms: list[str],
    model_ids: list[str],
    title: str,
    positive_term: str,
    negative_term: str,
    explained_var: float | None = None,
) -> None:
    fig_width = max(6, len(model_ids) * 2.5)
    fig_height = max(6, len(terms) * 0.28)
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))

    # Adjust color scale to map better to values
    values_abs = np.abs(matrix).max()
    im = ax.imshow(
        matrix, aspect="auto", cmap="RdYlGn", vmin=-values_abs, vmax=values_abs
    )

    plt.colorbar(im, ax=ax, label=f"{negative_term} ← sentiment → {positive_term}")

    ax.set_xticks(range(len(model_ids)))
    ax.set_xticklabels(model_ids, rotation=25, ha="right", fontsize=8)

    ax.set_yticks(range(len(terms)))
    ax.set_yticklabels(terms, fontsize=8)

    ax.set_title(title)

    plt.tight_layout()
    plt.show()


# def plot_all_models_scatter(
#     model_results: list[dict],
#     a_category: str,
#     b_category: str,
#     positive_term: str,
#     negative_term: str,
#     label_threshold: float = 0.05,
#     strategy: ScoringStrategy = ScoringStrategy.AXIS_PROJECTION,
# ) -> DataFrame:
#     """
#     PCA scatter of all terms coloured by cross-model disagreement (std).
#     Prints explained variance so you can judge how much signal the 2D
#     projection retains (trustworthy above ~0.90, defer to heatmap below that).

#     strategy param mirrors plot_all_models_sentiment.

#     Returns a DataFrame with columns:
#         term, pc1, pc2, std_disagreement, mean_sentiment
#     sorted by std_disagreement descending.
#     """
#     all_avgs = build_all_avgs(
#         model_results, a_category, b_category, positive_term, negative_term, strategy
#     )
#     strategy_label = strategy.value

#     model_ids = list(all_avgs.keys())
#     terms = sorted(next(iter(all_avgs.values())).keys())

#     matrix = np.array([[all_avgs[mid][term] for mid in model_ids] for term in terms])

#     pca = PCA(n_components=2)
#     coords = pca.fit_transform(matrix)
#     explained = pca.explained_variance_ratio_
#     total_explained = explained.sum()

#     controversy = matrix.std(axis=1)

#     fig, ax = plt.subplots(figsize=(9, 7))

#     scatter = ax.scatter(
#         coords[:, 0],
#         coords[:, 1],
#         c=controversy,
#         cmap="plasma",
#         s=60,
#         alpha=0.85,
#     )
#     plt.colorbar(scatter, ax=ax, label="std across models (higher = more disagreement)")

#     for i, (term, std) in enumerate(zip(terms, controversy)):
#         if std > label_threshold:
#             ax.annotate(
#                 term,
#                 coords[i],
#                 textcoords="offset points",
#                 xytext=(4, 4),
#                 fontsize=7,
#                 alpha=0.9,
#             )

#     ax.set_xlabel(f"PC1 ({explained[0]:.1%})")
#     ax.set_ylabel(f"PC2 ({explained[1]:.1%})")
#     ax.set_title(
#         f"{a_category} — cross-model sentiment space  [{strategy_label}]\n"
#         f"({positive_term} / {negative_term})  ·  "
#         f"colour = disagreement across {len(model_ids)} models  ·  "
#         f"total explained: {total_explained:.1%}"
#     )

#     plt.tight_layout()
#     plt.show()

#     return pl.DataFrame(
#         {
#             "term": terms,
#             "pc1": coords[:, 0].tolist(),
#             "pc2": coords[:, 1].tolist(),
#             "std_disagreement": controversy.tolist(),
#             "mean_sentiment": matrix.mean(axis=1).tolist(),
#         }
#     ).sort("std_disagreement", descending=True)


######
# Plots: Pairs
######
def plot_sentiment_compare(
    model_id_1: str,
    results_df_1: DataFrame,
    model_id_2: str,
    results_df_2: DataFrame,
    a_category: str,
    b_category: str,
    out_dir: str,
    positive_term: str,
    negative_term: str,
    write_results: bool = False,
) -> DataFrame:
    ensure_dirs(out_dir)

    avg_1 = get_avg_sentiment_independent_normalization(
        results_df_1, a_category, b_category, positive_term, negative_term
    )

    avg_2 = get_avg_sentiment_independent_normalization(
        results_df_2, a_category, b_category, positive_term, negative_term
    )

    compare_df = get_sentiment_compare_df(model_id_1, avg_1, model_id_2, avg_2)

    if write_results:
        timestamp = time.time()
        out_file = f"{model_id_1}__{model_id_2}__{a_category}__{b_category}__{timestamp}.csv".replace(
            "/", "--"
        )

        compare_df.write_csv(f"{out_dir}/compare/{out_file}")

    labels = compare_df["label"].to_list()

    model_1_values = compare_df[model_id_1].to_list()
    model_2_values = compare_df[model_id_2].to_list()

    all_positive = [v for v in model_1_values + model_2_values if v >= 0]
    all_negative = [v for v in model_1_values + model_2_values if v < 0]

    positive_normalized = mcolors.Normalize(
        vmin=0, vmax=max(all_positive) if all_positive else 1
    )

    negative_normalized = mcolors.Normalize(
        vmin=min(all_negative) if all_negative else -1, vmax=0
    )

    def bar_color(val, cmap_pos, cmap_neg):
        if val >= 0:
            return cmap_pos(0.3 + 0.7 * positive_normalized(val))
        return cmap_neg(0.3 + 0.7 * negative_normalized(abs(val)))

    bar_width_per_label = 0.7

    fig_width = max(8, len(labels) * bar_width_per_label)
    fig_height = DEFAULT_FIG_DIMENSION
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))

    width = 0.35

    x = np.arange(len(labels)) * 3

    for i, (model_1_value, model_2_value) in enumerate(
        zip(model_1_values, model_2_values)
    ):
        ax.bar(
            x[i] - width / 2,
            model_1_value,
            width,
            color=bar_color(model_1_value, colormaps["Blues"], colormaps["Reds"]),
        )

        ax.bar(
            x[i] + width / 2,
            model_2_value,
            width,
            color=bar_color(model_2_value, colormaps["Purples"], colormaps["Oranges"]),
        )

    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.axhline(0, color="black", linewidth=0.8)

    ax.set_ylabel(f"{negative_term} ← Avg Sentiment → {positive_term}")

    ax.set_title(f"{a_category} — model comparison\n{model_id_1}\nvs {model_id_2}")

    ax.legend(
        handles=[
            Patch(facecolor=colormaps["Blues"](0.75), label=f"{model_id_1} (pos)"),
            Patch(facecolor=colormaps["Reds"](0.75), label=f"{model_id_1} (neg)"),
            Patch(facecolor=colormaps["Purples"](0.75), label=f"{model_id_2} (pos)"),
            Patch(facecolor=colormaps["Oranges"](0.75), label=f"{model_id_2} (neg)"),
        ]
    )

    plt.tight_layout()
    plt.show()

    return compare_df


def plot_sentiment_delta(
    model_id_1: str,
    results_df_1: DataFrame,
    model_id_2: str,
    results_df_2: DataFrame,
    a_category: str,
    b_category: str,
    out_dir: str,
    positive_term: str,
    negative_term: str,
) -> DataFrame:
    ensure_dirs(out_dir)

    avg_1 = get_avg_sentiment_independent_normalization(
        results_df_1, a_category, b_category, positive_term, negative_term
    )

    avg_2 = get_avg_sentiment_independent_normalization(
        results_df_2, a_category, b_category, positive_term, negative_term
    )

    compare_df = get_sentiment_compare_df(model_id_1, avg_1, model_id_2, avg_2)

    labels = compare_df["label"].to_list()

    model_1_values = compare_df[model_id_1].to_list()
    model_2_values = compare_df[model_id_2].to_list()

    deltas = [v1 - v2 for v1, v2 in zip(model_1_values, model_2_values)]

    order = np.argsort(deltas)

    labels = [labels[i] for i in order]
    deltas = [deltas[i] for i in order]

    colors = [
        colormaps["Blues"](0.65) if d >= 0 else colormaps["Oranges"](0.65)
        for d in deltas
    ]

    fig_width = DEFAULT_FIG_DIMENSION
    fig_height = max(4, len(labels) * 0.28)
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))

    y = np.arange(len(labels))

    ax.barh(y, deltas, color=colors, height=0.7)

    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=8)
    ax.axvline(0, color="black", linewidth=0.8)

    ax.set_xlabel(f"← {model_id_2} more positive   |   {model_id_1} more positive →")

    ax.set_title(
        f"{a_category} — sentiment delta\n"
        f"{model_id_2}  vs  {model_id_1}\n"
        f"(judgement: {positive_term} / {negative_term})"
    )

    plt.tight_layout()
    plt.show()

    return compare_df


def plot_sentiment_scatter(
    model_id_1: str,
    results_df_1: DataFrame,
    model_id_2: str,
    results_df_2: DataFrame,
    a_category: str,
    b_category: str,
    out_dir: str,
    positive_term: str,
    negative_term: str,
    label_threshold: float = 0.05,
) -> DataFrame:
    ensure_dirs(out_dir)

    avg_1 = get_avg_sentiment_independent_normalization(
        results_df_1, a_category, b_category, positive_term, negative_term
    )

    avg_2 = get_avg_sentiment_independent_normalization(
        results_df_2, a_category, b_category, positive_term, negative_term
    )

    compare_df = get_sentiment_compare_df(model_id_1, avg_1, model_id_2, avg_2)

    labels = compare_df["label"].to_list()

    model_1_values = np.array(compare_df[model_id_1].to_list())
    model_2_values = np.array(compare_df[model_id_2].to_list())

    deltas = np.abs(model_1_values - model_2_values)

    r = float(np.corrcoef(model_1_values, model_2_values)[0, 1])

    fig_width = DEFAULT_FIG_DIMENSION
    fig_height = DEFAULT_FIG_DIMENSION
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))

    scatter = ax.scatter(
        model_1_values, model_2_values, c=deltas, cmap="plasma", s=50, alpha=0.8
    )

    plt.colorbar(scatter, ax=ax, label="|delta|")

    lim_min = min(model_1_values.min(), model_2_values.min()) - 0.05
    lim_max = max(model_1_values.max(), model_2_values.max()) + 0.05

    ax.plot([lim_min, lim_max], [lim_min, lim_max], "k--", linewidth=0.7, alpha=0.5)

    for label, x, y, d in zip(labels, model_1_values, model_2_values, deltas):
        if d > label_threshold:
            ax.annotate(
                label,
                (x, y),
                textcoords="offset points",
                xytext=(4, 4),
                fontsize=7,
                alpha=0.85,
            )

    ax.axhline(0, color="grey", linewidth=0.5, linestyle=":")
    ax.axvline(0, color="grey", linewidth=0.5, linestyle=":")

    ax.set_xlabel(f"{model_id_1}  avg sentiment")
    ax.set_ylabel(f"{model_id_2}  avg sentiment")

    ax.set_title(
        f"{a_category}  ·  {positive_term}/{negative_term}\n"
        f"r = {r:.3f}  ({model_id_1} vs {model_id_2})"
    )

    plt.tight_layout()
    plt.show()

    return compare_df


######
# Utils
######
def plot_strategy_comparison(
    model_results: list[dict],
    a_category: str,
    b_category: str,
    positive_term: str,
    negative_term: str,
    label_threshold: float = 0.08,
) -> DataFrame:
    """
    Scatter of per term mean scores under INDEPENDENT_NORMALIZATION (x-axis)
    vs AXIS_PROJECTION (y-axis), averaged across all models.

    Each point is one term. Points on the diagonal agree perfectly between
    strategies.

    Color encodes |delta| between strategies: bright yellow points are where
    the choice of strategy matters most.

    Pearson r in the title summarises overall agreement: above ~0.95 the strategies
    are telling the same story; below that, the divergent terms (labelled) are worth
    investigating before committing to one approach.
    """
    avgs_independent_norm = build_all_avgs(
        model_results,
        a_category,
        b_category,
        positive_term,
        negative_term,
        ScoringStrategy.INDEPENDENT_NORMALIZATION,
    )

    avgs_axis_projection = build_all_avgs(
        model_results,
        a_category,
        b_category,
        positive_term,
        negative_term,
        ScoringStrategy.AXIS_PROJECTION,
    )

    # Average each term's score across all models for each strategy
    model_ids = list(avgs_independent_norm.keys())
    terms = sorted(next(iter(avgs_independent_norm.values())).keys())

    def mean_across_models(avgs: dict[str, dict], term: str) -> float:
        return float(np.mean([avgs[mid][term] for mid in model_ids]))

    scores_independent_norm = np.array(
        [mean_across_models(avgs_independent_norm, t) for t in terms]
    )

    scores_axis_projection = np.array(
        [mean_across_models(avgs_axis_projection, t) for t in terms]
    )

    deltas = np.abs(scores_independent_norm - scores_axis_projection)

    r = float(np.corrcoef(scores_independent_norm, scores_axis_projection)[0, 1])

    fig_width = DEFAULT_FIG_DIMENSION
    fig_height = DEFAULT_FIG_DIMENSION
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))

    scatter = ax.scatter(
        scores_independent_norm,
        scores_axis_projection,
        c=deltas,
        cmap="plasma",
        s=60,
        alpha=0.85,
    )

    plt.colorbar(scatter, ax=ax, label="|delta| between strategies")

    # Diagonal reference line
    lim = (
        max(np.abs(scores_independent_norm).max(), np.abs(scores_axis_projection).max())
        + 0.05
    )

    ax.plot([-lim, lim], [-lim, lim], "k--", linewidth=0.7, alpha=0.5)

    # Quadrant lines
    ax.axhline(0, color="grey", linewidth=0.5, linestyle=":")
    ax.axvline(0, color="grey", linewidth=0.5, linestyle=":")

    # Label the most divergent terms
    for term, x, y, d in zip(
        terms, scores_independent_norm, scores_axis_projection, deltas
    ):
        if d > label_threshold:
            ax.annotate(
                term,
                (x, y),
                textcoords="offset points",
                xytext=(4, 4),
                fontsize=7,
                alpha=0.9,
            )

    ax.set_xlabel(f"mean score  [{ScoringStrategy.INDEPENDENT_NORMALIZATION.value}]")
    ax.set_ylabel(f"mean score  [{ScoringStrategy.AXIS_PROJECTION.value}]")

    ax.set_title(
        f"{a_category}  ·  {positive_term} / {negative_term}\n"
        f"strategy comparison  ·  Pearson r = {r:.3f} across {len(terms)} terms"
    )

    plt.tight_layout()
    plt.show()

    result_df = pl.DataFrame(
        {
            "term": terms,
            "score_independent_normalization": scores_independent_norm.tolist(),
            "score_axis_projection": scores_axis_projection.tolist(),
            "delta": deltas.tolist(),
        }
    ).sort("delta", descending=True)

    return result_df
