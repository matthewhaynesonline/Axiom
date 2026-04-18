import warnings

import numpy as np
from sentence_transformers import SentenceTransformer

from .ml_models import EncodingFn, _default_encoding_fn

######
# Embeddings cache
#
# Structure: { (model_id, key): np.ndarray }
# WARNING: this is module-level global state. Avoid hot-reloading this module
# mid-session, and do not use across parallel workers without clearing first.
######
_EMBEDDINGS_CACHE: dict[tuple[str, str], np.ndarray] = {}


def get_or_compute_embeddings(
    model_id: str,
    model: SentenceTransformer,
    key: str,
    inputs: list[str],
    encoding_fn: EncodingFn | None = None,
) -> np.ndarray:
    cache_key = _cache_key(model_id, key)

    if cache_key not in _EMBEDDINGS_CACHE:
        warnings.warn(f"Cache miss for {cache_key!r}", stacklevel=2)
        
        _EMBEDDINGS_CACHE[cache_key] = (encoding_fn or _default_encoding_fn)(
            model, inputs
        )

    return _EMBEDDINGS_CACHE[cache_key]


def get_embeddings(
    model_id: str,
    key: str,
) -> np.ndarray | None:
    cache_key = _cache_key(model_id, key)

    return _EMBEDDINGS_CACHE.get(cache_key)


def clear_embeddings_cache() -> None:
    _EMBEDDINGS_CACHE.clear()


def precompute_embeddings_bulk(
    model_id: str,
    model: SentenceTransformer,
    boundaries: list[tuple[str, int, int]],  # key, start index, end index
    all_inputs: list[str],
    encoding_fn: EncodingFn | None = None,
) -> None:
    embeddings = (encoding_fn or _default_encoding_fn)(model, all_inputs)

    for key, start, end in boundaries:
        cache_key = _cache_key(model_id, key)
        _EMBEDDINGS_CACHE[cache_key] = embeddings[start:end]


def precompute_embeddings(
    model_id: str,
    model: SentenceTransformer,
    key: str,
    inputs: list[str],
    encoding_fn: EncodingFn | None = None,
) -> None:
    cache_key = _cache_key(model_id, key)

    if cache_key in _EMBEDDINGS_CACHE:
        return

    _EMBEDDINGS_CACHE[cache_key] = (encoding_fn or _default_encoding_fn)(model, inputs)


def _cache_key(namespace: str, key: str) -> tuple[str, str]:
    return (namespace, key)
