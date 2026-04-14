import warnings

import numpy as np
import polars as pl

from polars import DataFrame
from sentence_transformers import SentenceTransformer

from .ml_models import EncodingFn, _default_encoding_fn

######
# Embedding cache
#
# Structure: { (model_id, category): np.ndarray }
# WARNING: this is module-level global state. Avoid hot-reloading this module
# mid-session, and do not use across parallel workers without clearing first.
######
_EMBEDDING_CACHE: dict[tuple[str, str], np.ndarray] = {}


def get_embeddings(
    model_id: str,
    model: SentenceTransformer,
    terms: list[str],
    category: str,
    encoding_fn: EncodingFn | None = None,
) -> np.ndarray:
    key = (model_id, category)

    if key not in _EMBEDDING_CACHE:
        warnings.warn(
            f"Cache miss for ({model_id!r}, {category!r}) — falling back to default "
            f"model.encode. Call precompute_embeddings first to use model-specific "
            f"encoding functions.",
            stacklevel=2,
        )
        _EMBEDDING_CACHE[key] = (encoding_fn or _default_encoding_fn)(model, terms)

    return _EMBEDDING_CACHE[key]


def clear_embedding_cache() -> None:
    _EMBEDDING_CACHE.clear()


def precompute_embeddings_raw(
    model_id: str,
    model: SentenceTransformer,
    encoding_fn: EncodingFn | None,
    terms: list[str],
    category: str,
) -> None:
    key = (model_id, category)

    if key in _EMBEDDING_CACHE:
        return

    _EMBEDDING_CACHE[key] = (encoding_fn or _default_encoding_fn)(model, terms)


def precompute_embeddings(
    model_id: str,
    model: SentenceTransformer,
    encoding_fn: EncodingFn | None,
    data_df: DataFrame,
    category_column: str,
    term_column: str,
    categories: list[str],
) -> None:
    # Collect terms per category (preserving insertion order for index tracking)
    category_terms: dict[str, list[str]] = {}

    for category in categories:
        key = (model_id, category)

        if key not in _EMBEDDING_CACHE:
            rows = data_df.filter(pl.col(category_column) == category)
            category_terms[category] = rows[term_column].to_list()

    if not category_terms:
        return

    # Build one flat list for batch encode and then boundary indices for slicing after encoding
    all_terms: list[str] = []
    # category, start index, end index
    boundaries: list[tuple[str, int, int]] = []

    for category, terms in category_terms.items():
        start = len(all_terms)
        all_terms.extend(terms)
        boundaries.append((category, start, len(all_terms)))

    embeddings = (encoding_fn or _default_encoding_fn)(model, all_terms)

    for category, start, end in boundaries:
        _EMBEDDING_CACHE[(model_id, category)] = embeddings[start:end]
