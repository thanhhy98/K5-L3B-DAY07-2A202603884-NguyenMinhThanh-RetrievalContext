"""Dense, lexical and reciprocal-rank hybrid retrieval interfaces."""
from __future__ import annotations

from typing import Any

from baseline import TfidfIndex


class LexicalRetriever:
    def __init__(self, chunks: list[dict[str, Any]]):
        self.chunks = chunks
        self.index = TfidfIndex(chunks)

    def search(self, query: str, *, filters=None, top_k: int = 3):
        allowed = self.chunks
        if filters:
            allowed = [c for c in allowed if all((c.get(k) == v if k in {"source", "source_id", "page"}
                         else (c.get("metadata") or {}).get(k) == v) for k, v in filters.items())]
        index = self.index if len(allowed) == len(self.chunks) else TfidfIndex(allowed)
        return [{**c, "strategy": "tfidf"} for c in index.search(query, top_k)]


class HybridRetriever:
    """Reciprocal rank fusion; combines rankings without assuming score scales."""
    def __init__(self, dense, lexical, rrf_k: int = 60):
        self.dense, self.lexical, self.rrf_k = dense, lexical, rrf_k

    def search(self, query: str, *, filters=None, top_k: int = 3):
        candidates = {}
        for retriever in (self.dense, self.lexical):
            rows = retriever.search(query, filters=filters, top_k=max(top_k * 3, top_k))
            for rank, row in enumerate(rows, 1):
                cid = row["id"]
                if cid not in candidates:
                    candidates[cid] = {**row, "score": 0.0, "rrf_components": {}}
                candidates[cid]["score"] += 1 / (self.rrf_k + rank)
                candidates[cid]["rrf_components"][row.get("strategy", "retriever")] = rank
        return sorted(candidates.values(), key=lambda c: (-c["score"], c["id"]))[:top_k]
