"""Read the Day 6 pgvector index without importing its pipeline entry point."""
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any


class Day6DenseRetriever:
    """Adapter for Day 6's strategy_chunks table and embedding implementation.

    Day 6 stores vectors by strategy. A real persisted embedding model and its
    dimensions must be configured; the starter's corpus-fitted TF-IDF fallback
    is intentionally rejected because it cannot reproduce the indexed vectors.
    """

    def __init__(self, day6_root: Path, strategy: str = "B", model_name: str | None = None):
        self.day6_root = day6_root.resolve()
        self.strategy = strategy
        if str(self.day6_root / "starter") not in sys.path:
            sys.path.insert(0, str(self.day6_root / "starter"))
        from dotenv import load_dotenv
        load_dotenv(self.day6_root / "starter" / ".env")
        load_dotenv(self.day6_root / ".env")
        self.database_url = os.environ.get("DATABASE_URL")
        if not self.database_url:
            raise RuntimeError("DATABASE_URL is unset; configure the Day 6 local PostgreSQL connection")
        model_name = model_name or os.environ.get("EMBEDDING_MODEL")
        if not model_name:
            raise RuntimeError("Set EMBEDDING_MODEL to the exact model used to create the Day 6 vectors")
        self.model_name = model_name
        if model_name.startswith("text-embedding-"):
            try:
                from openai import OpenAI
            except ImportError as exc:
                raise RuntimeError("Install the OpenAI SDK: python -m pip install openai") from exc
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                raise RuntimeError("OPENAI_API_KEY is required for OpenAI embeddings")
            self.client = OpenAI(api_key=api_key)
            self.dimensions = int(os.getenv("EMBEDDING_DIMENSIONS", "1536"))
            self.model = None
        else:
            try:
                from sentence_transformers import SentenceTransformer
            except ImportError as exc:
                raise RuntimeError("Local dense retrieval requires sentence-transformers") from exc
            self.model = SentenceTransformer(model_name)
            self.dimensions = int(self.model.get_sentence_embedding_dimension())
            self.client = None
        from src.store import PgVectorStore
        self.store = PgVectorStore(self.database_url, self.dimensions)

    def search(self, query: str, *, filters: dict[str, Any] | None = None, top_k: int = 3):
        if self.client:
            vector = self.client.embeddings.create(model=self.model_name, input=[query], dimensions=self.dimensions).data[0].embedding
        else:
            vector = self.model.encode([query], convert_to_numpy=True, show_progress_bar=False)[0]
        rows = self.store.search(self.strategy, list(map(float, vector)), top_k=top_k, filters=filters)
        return [{"id": row["chunk_id"], "text": row["text"], "source_id": row["document_id"],
                 "source": row["source"], "page": row["page"], "metadata": row["metadata"],
                 "score": row["score"], "strategy": "dense"} for row in rows]
