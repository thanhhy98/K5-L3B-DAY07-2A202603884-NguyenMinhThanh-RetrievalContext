"""Run Day 7 retrieval/agent on the Day 6 corpus and benchmark."""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

from agentic import run_agent
from day6_adapter import Day6DenseRetriever
from retrieval_methods import HybridRetriever, LexicalRetriever
from provider_controller import OpenAIController


def load_day6_chunks(day6_root: Path, strategy: str) -> list[dict]:
    """Reconstruct lexical candidates from Day 6's canonical page text."""
    starter = day6_root / "starter"
    sys.path.insert(0, str(starter))
    from src.chunking import by_paragraph, fixed_size
    from src.ingestion import load_pdf
    source_id = "student_handbook_2025"
    pdf = day6_root / "data/student_handbook_2025.pdf"
    manifest = json.loads((day6_root / "data/manifest.json").read_text(encoding="utf-8"))
    page_meta = {int(p["page"]): p for p in manifest["pages"]}
    pages = load_pdf(pdf, source_id, source_id)
    chunks = []
    for page in pages:
        if strategy == "A": rows = fixed_size(page, size=500, overlap=80)
        else: rows = by_paragraph(page, max_size=600)
        meta = page_meta.get(page.page, {})
        for row in rows:
            chunks.append({"id": f"{strategy}:{row.chunk_id}", "text": row.text, "source_id": row.document_id,
                           "source": row.source, "page": row.page,
                           "metadata": {**row.metadata, **meta}})
    return chunks


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--day6", type=Path, required=True)
    p.add_argument("--split", choices=["dev", "test"], required=True)
    p.add_argument("--method", choices=["dense", "tfidf", "hybrid"], required=True)
    p.add_argument("--strategy", choices=["A", "B", "C"], default="B")
    p.add_argument("--top-k", type=int, default=3)
    p.add_argument("--budget", type=int, default=3000)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--questions", type=Path, help="optional JSON array of questions; otherwise use Day 6 benchmark")
    p.add_argument("--agent", action="store_true", help="also run the real model controller")
    args = p.parse_args()
    day6 = args.day6.resolve()
    questions_path = args.questions or (day6 / "starter/benchmark/questions.json")
    questions = [q for q in json.loads(questions_path.read_text(encoding="utf-8")) if q["split"] == args.split]
    chunks = load_day6_chunks(day6, args.strategy)
    dense = Day6DenseRetriever(day6, strategy=args.strategy) if args.method in ("dense", "hybrid") else None
    lexical = LexicalRetriever(chunks) if args.method in ("tfidf", "hybrid") else None
    retriever = dense if args.method == "dense" else lexical if args.method == "tfidf" else HybridRetriever(dense, lexical)
    controller = OpenAIController() if args.agent else None
    traces = []
    for q in questions:
        start = time.perf_counter()
        filters = q.get("filter")
        if controller:
            result = run_agent(q["question"], controller, retriever, filters=filters, top_k=args.top_k, budget=args.budget)
            traces.append({"query_id": q["id"], "question": q["question"], **result,
                           "elapsed_ms": (time.perf_counter()-start)*1000})
        else:
            results = retriever.search(q["question"], filters=filters, top_k=args.top_k)
            traces.append({"query_id": q["id"], "split": q["split"], "question": q["question"],
                           "method": args.method, "filter": filters, "results": results,
                           "elapsed_ms": (time.perf_counter()-start)*1000})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(traces, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"split": args.split, "method": args.method, "n": len(traces), "trace": str(args.output)}, indent=2))


if __name__ == "__main__": main()
