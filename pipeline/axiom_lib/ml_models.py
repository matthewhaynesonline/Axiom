import csv
import json

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import numpy as np

from sentence_transformers import SentenceTransformer

EncodingFn = Callable[[SentenceTransformer, list[str]], np.ndarray]

LICENSE_SCORE_CONFIG_PATH = Path(__file__).parent.parent / "data/license_scores.json"

with open(LICENSE_SCORE_CONFIG_PATH, "r", encoding="utf-8") as f:
    LICENSE_SCORE_CONFIG = json.load(f)


@dataclass(frozen=True)
class ModelConfig:
    model_id: str
    model_name: str
    model_url: str
    type: str
    group: str
    license: str
    license_score: float = 0.0
    url_extra: str = ""
    st_model: SentenceTransformer | None = field(
        default=None, compare=False, hash=False
    )
    query_encoding_fn: EncodingFn | None = None
    document_encoding_fn: EncodingFn | None = None

    def encode_queries(self, inputs: list[str]) -> np.ndarray | None:
        if self.st_model is None:
            return None

        fn = self.query_encoding_fn or _default_encoding_fn

        return fn(self.st_model, inputs)

    def encode_documents(self, inputs: list[str]) -> np.ndarray | None:
        if self.st_model is None:
            return None

        fn = self.document_encoding_fn or _default_encoding_fn

        return fn(self.st_model, inputs)

    @classmethod
    def load_models(
        cls,
        filename: str,
        enabled_models: list[str] | None = None,
        should_load_st_models: bool = True,
    ) -> list["ModelConfig"]:
        csv_path = Path(__file__).parent.parent / f"data/{filename}"

        with open(csv_path, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))

        configs = [cls._row_to_config(row) for row in rows]

        if enabled_models:
            configs = [c for c in configs if c.model_id in enabled_models]

        if should_load_st_models:
            configs = [cls._with_st_model(c) for c in configs]

        return configs

    @classmethod
    def _row_to_config(cls, row: dict) -> "ModelConfig":
        url = row["model_url"]
        model_id = cls._get_model_id_from_url(url)
        license = row["license"]

        return ModelConfig(
            model_id=model_id,
            model_name=row["model_name"],
            model_url=url,
            type=row["type"],
            group=row["group"],
            license=license,
            license_score=cls._calculate_license_score(license),
            url_extra=row.get("url_extra", ""),
        )

    @classmethod
    def _with_st_model(cls, config: "ModelConfig") -> "ModelConfig":
        st_model = SentenceTransformer(config.model_id, trust_remote_code=True)

        MODEL_ENCODING_FNS_MAPPING = {
            "Qwen/Qwen3-Embedding-0.6B": {
                "query": _qwen3_query_encoding_fn,
                "document": _default_encoding_fn,
            },
            "google/embeddinggemma-300m": {
                "query": _gemma_query_encoding_fn,
                "document": _gemma_document_encoding_fn,
            },
            "nomic-ai/nomic-embed-text-v2-moe": {
                "query": _nomic_v2_query_encoding_fn,
                "document": _nomic_v2_document_encoding_fn,
            },
            "nvidia/NV-Embed-v2": {
                "query": _nv_embed_v2_query_encoding_fn,
                "document": _nv_embed_v2_document_encoding_fn,
            },
            "jinaai/jina-embeddings-v3": {
                "query": _jina_v3_query_encoding_fn,
                "document": _jina_v3_document_encoding_fn,
            },
            "jinaai/jina-embeddings-v4": {
                "query": _jina_v4_query_encoding_fn,
                "document": _jina_v4_document_encoding_fn,
            },
        }

        query_encoding_fn = None
        document_encoding_fn = None

        if config.model_id in MODEL_ENCODING_FNS_MAPPING:
            query_encoding_fn = MODEL_ENCODING_FNS_MAPPING[config.model_id]["query"]
            document_encoding_fn = MODEL_ENCODING_FNS_MAPPING[config.model_id][
                "document"
            ]

        return ModelConfig(
            model_id=config.model_id,
            model_name=config.model_name,
            model_url=config.model_url,
            type=config.type,
            group=config.group,
            license=config.license,
            license_score=config.license_score,
            url_extra=config.url_extra,
            st_model=st_model,
            query_encoding_fn=query_encoding_fn,
            document_encoding_fn=document_encoding_fn,
        )

    @classmethod
    def _get_model_id_from_url(cls, model_url: str) -> str:
        return model_url.removeprefix("https://huggingface.co/")

    @classmethod
    def _calculate_license_score(cls, license_str: str) -> float:
        """Calculates license score based on external JSON configuration."""
        l_str = license_str.lower()

        for keyword, score in sorted(
            LICENSE_SCORE_CONFIG["mappings"].items(),
            key=lambda item: len(item[0]),
            reverse=True,
        ):
            if keyword in l_str:
                return float(score)

        return float(LICENSE_SCORE_CONFIG["default"])


def _default_encoding_fn(model: SentenceTransformer, inputs: list[str]) -> np.ndarray:
    return model.encode(inputs, normalize_embeddings=True)


def _qwen3_query_encoding_fn(
    model: SentenceTransformer, inputs: list[str]
) -> np.ndarray:
    return model.encode(inputs, prompt_name="query", normalize_embeddings=True)


def _gemma_query_encoding_fn(model: SentenceTransformer, inputs: list[str]):
    return model.encode_query(inputs, normalize_embeddings=True)


def _gemma_document_encoding_fn(model: SentenceTransformer, inputs: list[str]):
    return model.encode_document(inputs, normalize_embeddings=True)


def _nomic_v2_query_encoding_fn(
    model: SentenceTransformer, inputs: list[str]
) -> np.ndarray:
    return model.encode(inputs, prompt_name="query", normalize_embeddings=True)


def _nomic_v2_document_encoding_fn(
    model: SentenceTransformer, inputs: list[str]
) -> np.ndarray:
    return model.encode(inputs, prompt_name="passage", normalize_embeddings=True)


def _nv_embed_v2_query_encoding_fn(
    model: SentenceTransformer, inputs: list[str]
) -> np.ndarray:
    prompt = "Instruct: Given a question, retrieve passages that answer the question\nQuery: "

    return model.encode(
        _nv_embed_v2_add_eos(model, inputs), prompt=prompt, normalize_embeddings=True
    )


def _nv_embed_v2_document_encoding_fn(
    model: SentenceTransformer, inputs: list[str]
) -> np.ndarray:
    return model.encode(_nv_embed_v2_add_eos(model, inputs), normalize_embeddings=True)


def _nv_embed_v2_add_eos(model: SentenceTransformer, inputs: list[str]) -> list[str]:
    wrapped_inputs = [input_doc + model.tokenizer.eos_token for input_doc in inputs]

    return wrapped_inputs


def _jina_v3_query_encoding_fn(
    model: SentenceTransformer, inputs: list[str]
) -> np.ndarray:
    task = "retrieval.query"
    return model.encode(inputs, task=task, prompt_name=task, normalize_embeddings=True)


def _jina_v3_document_encoding_fn(
    model: SentenceTransformer, inputs: list[str]
) -> np.ndarray:
    task = "retrieval.passage"
    return model.encode(inputs, task=task, prompt_name=task, normalize_embeddings=True)


def _jina_v4_query_encoding_fn(
    model: SentenceTransformer, inputs: list[str]
) -> np.ndarray:
    return model.encode(
        inputs, task="retrieval", prompt_name="query", normalize_embeddings=True
    )


def _jina_v4_document_encoding_fn(
    model: SentenceTransformer, inputs: list[str]
) -> np.ndarray:
    return model.encode(
        inputs, task="retrieval", prompt_name="passage", normalize_embeddings=True
    )


def export_models_to_csv(models: list[ModelConfig], csv_path: str) -> None:
    """
    Exports a list of ModelConfigs back to a CSV file in the data/ directory.
    """

    # Define the fields we care about for the frontend
    fieldnames = [
        "model_id",
        "type",
        "group",
        "model_name",
        "model_url",
        "url_extra",
        "license",
        "license_score",
    ]

    with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for m in models:
            writer.writerow(
                {
                    "model_id": m.model_id,
                    "type": m.type,
                    "group": m.group,
                    "model_name": m.model_name,
                    "model_url": m.model_url,
                    "url_extra": m.url_extra,
                    "license": m.license,
                    "license_score": m.license_score,
                }
            )


def generate_models_docs(models: list[ModelConfig]) -> str:
    header = (
        "| Group | Model Name | Model URL (Hugging Face) | Type | License / Restrictions |\n"
        "| --- | --- | --- | --- | --- |"
    )

    rows = [
        f"| **{m.group}** | {m.model_name} | [{m.model_id}]({m.model_url}{m.url_extra}) | {m.type} | **{m.license}** |"
        for m in models
    ]

    return header + "\n" + "\n".join(rows)
