import time

from enum import Enum
from pathlib import Path

import numpy as np
import polars as pl

from polars import DataFrame
from sentence_transformers import SentenceTransformer

from .embedding import get_embeddings
from .normalization import zscore, minmax, tanh_scale_np


######
# Scoring
######
class ScoringStrategy(Enum):
    # Normalize positive and negative similarity columns independently, then combine.
    # Fixes where a model with a compressed score range could appear artificially extreme.
    INDEPENDENT_NORMALIZATION = "independent_normalization"

    # Project each term onto a derived semantic axis (embed(positive) - embed(negative)).
    # A single coherent direction replaces two separate proximity measurements, making the
    # score more robust for terms that sit near both poles.
    AXIS_PROJECTION = "axis_projection"


######
# FS Utils
######
def ensure_dirs(out_dir: str) -> None:
    Path(out_dir, "scores").mkdir(parents=True, exist_ok=True)
    Path(out_dir, "compare").mkdir(parents=True, exist_ok=True)


######
# Processing
######
def process_data(
    model_id: str,
    model: SentenceTransformer,
    data_df: DataFrame,
    category_column: str,
    term_column: str,
    a_category: str,
    b_category: str,
    out_dir: str,
    write_results: bool = False,
) -> DataFrame:
    ensure_dirs(out_dir)

    a_rows = data_df.filter(pl.col(category_column) == a_category)
    a_list = a_rows[term_column].to_list()

    b_rows = data_df.filter(pl.col(category_column) == b_category)
    b_list = b_rows[term_column].to_list()

    a_embeddings = get_embeddings(model_id, model, a_list, a_category)
    b_embeddings = get_embeddings(model_id, model, b_list, b_category)

    scores = model.similarity(a_embeddings, b_embeddings)

    results = [
        {a_category: a_list[i], b_category: b_list[j], "score": score.item()}
        for i, row in enumerate(scores)
        for j, score in enumerate(row)
    ]

    timestamp = time.time()
    results_out_file = (
        f"{model_id}__{a_category}__{b_category}__{timestamp}.csv".replace("/", "--")
    )

    results_df = (
        pl.DataFrame(results)
        .sort("score", descending=True)
        .with_columns(
            pl.col("score").map_batches(zscore).alias("score_z"),
            pl.col("score")
            .map_batches(lambda s: minmax(zscore(s)))
            .alias("score_norm"),
        )
    )

    if write_results:
        results_df.write_csv(f"{out_dir}/scores/{results_out_file}")

    return results_df


######
# Sentiment scoring
######
def get_avg_sentiment_independent_normalization(
    results_df: DataFrame,
    a_category: str,
    b_category: str,
    positive_term: str,
    negative_term: str,
) -> dict:
    """
    Strategy A: per column normalization fix.

    Pivots the results table, normalizes the positive and negative similarity
    columns *independently* (tanh scaling after zscore, each on its own range),
    then combines them into a single sentiment score per term.

    Scores are in the open interval (-0.5, 0.5) — never exactly ±0.5

    Replaces the old shared normalization approach where both columns were
    normalized together, which let a model with a compressed score range appear
    more extreme than it really was.
    """
    plot_df = results_df.pivot(
        index=a_category, on=b_category, values="score_norm"
    ).sort(a_category)

    labels = plot_df[a_category].to_list()

    # Normalize each polarity column independently so the two scales are
    # comparable before combining.
    positive_values = np.array(plot_df[positive_term].to_list(), dtype=float)
    negative_values = np.array(plot_df[negative_term].to_list(), dtype=float)

    positive_normalized = tanh_scale_np(positive_values)
    negative_normalized = tanh_scale_np(negative_values)

    # Both outputs are already centred on 0, so subtract the negative
    # from the positive and halve to stay in (-0.5, 0.5).
    avg_vals = (positive_normalized - negative_normalized) / 2

    return dict(zip(labels, avg_vals.tolist()))


def get_avg_sentiment_axis_projection(
    positive_term: str,
    negative_term: str,
    a_embeddings: np.ndarray,
    a_terms: list[str],
    b_embeddings: np.ndarray,
    b_terms: list[str],
) -> dict:
    """
    Strategy B: semantic axis projection.

    Derives a sentiment direction vector by subtracting the negative pole
    embedding from the positive pole embedding:

        axis = embed(positive) - embed(negative)

    Each term is then projected onto this axis via cosine similarity. A single
    coherent direction replaces two independent proximity measurements, which
    avoids the asymmetry in Strategy A and is more robust for terms that sit in
    a dense region of the embedding space near both poles.

    The projected scores are zscore & minmax normalized per model (same as
    Strategy A's per column fix) so the two strategies are directly comparable.
    """
    positive_index = b_terms.index(positive_term)
    negative_index = b_terms.index(negative_term)

    positive_embedding = b_embeddings[positive_index]
    negative_embedding = b_embeddings[negative_index]

    # Semantic axis: "direction" from negative pole to positive pole.
    # This isolates the distilled conceptual vector for positive value.
    # Then using this, we can cosine sim terms against it to find the
    # the alignment
    # (1.0 / 0deg = perfect align / perfect positive)
    # (-1.0 / 180deg = opposite align / perfect negative)
    # (0.0 / ~90deg = sideways / unrelated)
    axis = positive_embedding - negative_embedding

    # We normalize to unit length so cosine similarity is well defined.
    axis_norm = np.linalg.norm(axis)

    if axis_norm == 0:
        raise ValueError(
            f"Positive and negative embeddings are identical for "
            f"({positive_term!r}, {negative_term!r}) — cannot form an axis."
        )

    axis = axis / axis_norm

    # Project each term embedding onto the axis.
    # a_embeddings are already unit-normalized so this is just a dot product.
    projections = a_embeddings @ axis

    # Per-model soft-clip normalization so the display scale matches Strategy A.
    # tanh_scale_np avoids the hard ±0.5 bounds of zscore & minmax that cause a
    # single outlier term to pin the scale and compress everything else.
    projections_norm = tanh_scale_np(projections)

    return dict(zip(a_terms, projections_norm.tolist()))


def get_sentiment_compare_df(
    model_id_1: str,
    avg_1: dict,
    model_id_2: str,
    avg_2: dict,
) -> DataFrame:
    labels = sorted(set(avg_1) & set(avg_2))

    return pl.DataFrame(
        {
            "label": labels,
            model_id_1: [avg_1[label] for label in labels],
            model_id_2: [avg_2[label] for label in labels],
        }
    )


######
# All-models helpers
######
def build_all_avgs(
    model_results: list[dict],
    a_category: str,
    b_category: str,
    positive_term: str,
    negative_term: str,
    strategy: ScoringStrategy = ScoringStrategy.AXIS_PROJECTION,
) -> dict[str, dict]:
    """
    Dispatch to the correct scoring function and return {model_id: {term: score}}.
    """
    if strategy is ScoringStrategy.INDEPENDENT_NORMALIZATION:
        return {
            r["model_id"]: get_avg_sentiment_independent_normalization(
                r["data"], a_category, b_category, positive_term, negative_term
            )
            for r in model_results
        }

    # Default to AXIS_PROJECTION
    return {
        r["model_id"]: get_avg_sentiment_axis_projection(
            positive_term=positive_term,
            negative_term=negative_term,
            a_embeddings=r["a_embeddings"],
            a_terms=r["a_terms"],
            b_embeddings=r["b_embeddings"],
            b_terms=r["b_terms"],
        )
        for r in model_results
    }
