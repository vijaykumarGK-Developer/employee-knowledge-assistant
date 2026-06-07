from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer

from app.core.config import settings


@lru_cache(maxsize=1)
def _get_model() -> SentenceTransformer:
    return SentenceTransformer(settings.EMBEDDINGS_MODEL)


def generate_embeddings(texts: list[str]) -> list[np.ndarray]:
    model = _get_model()
    embeddings = model.encode(texts, show_progress_bar=False, batch_size=32)
    return [emb for emb in embeddings]
