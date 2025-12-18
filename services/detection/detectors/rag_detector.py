"""
RAG-based detector for evaluation: uses a tiny in-memory corpus and cosine similarity
to retrieve context, then produces a heuristic label and confidence. Designed for
lightweight demos without external dependencies.
"""
import sys
import os
from typing import List, Dict, Any
from math import sqrt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'schemas')))
from models import DetectionRequest, DetectionResult
from detector import Detector, DetectorRegistry


def tokenize(text: str) -> List[str]:
    return [t for t in text.lower().split() if t.isalpha() or t.isalnum()]


def tf_vector(tokens: List[str]) -> Dict[str, float]:
    counts: Dict[str, int] = {}
    for t in tokens:
        counts[t] = counts.get(t, 0) + 1
    total = sum(counts.values()) or 1
    return {k: v / total for k, v in counts.items()}


def cosine(a: Dict[str, float], b: Dict[str, float]) -> float:
    keys = set(a.keys()) | set(b.keys())
    dot = sum(a.get(k, 0.0) * b.get(k, 0.0) for k in keys)
    na = sqrt(sum(v * v for v in a.values()))
    nb = sqrt(sum(v * v for v in b.values()))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


class RagDetector(Detector):
    """Minimal RAG detector that retrieves top-k snippets and scores faithfulness."""

    def __init__(self, config: dict):
        super().__init__(config)
        # In-memory corpus
        self.docs: List[Dict[str, Any]] = config.get("docs", [
            {"id": "d1", "text": "AI-generated text often shows patterns like repetition and generic phrasing."},
            {"id": "d2", "text": "Human-written content varies in style and may include personal anecdotes."},
            {"id": "d3", "text": "SQLite provides ACID compliance with minimal operational overhead for small systems."},
        ])
        self.k = int(config.get("top_k", 2))

    @property
    def model_name(self) -> str:
        return "rag-minimal"

    async def detect(self, request: DetectionRequest) -> DetectionResult:
        q_tokens = tokenize(request.text)
        q_vec = tf_vector(q_tokens)
        scored = []
        for doc in self.docs:
            v = tf_vector(tokenize(doc["text"]))
            s = cosine(q_vec, v)
            scored.append((s, doc))
        scored.sort(key=lambda x: x[0], reverse=True)
        top = scored[: self.k]
        avg_sim = sum(s for s, _ in top) / (len(top) or 1)

        # Simple heuristic: if similarity high and mentions 'ai', label AI-generated, else human
        lower = request.text.lower()
        if "ai" in lower and avg_sim >= 0.25:
            label = "AI-generated"
            conf = min(0.9, 0.6 + avg_sim)
        else:
            label = "human-written"
            conf = min(0.85, 0.5 + avg_sim)

        return DetectionResult(
            label=label,
            confidence=float(conf),
            detector_model=self.model_name,
            metadata={
                "top_docs": [{"id": d["id"], "text": d["text"], "sim": float(s)} for s, d in top],
                "avg_similarity": float(avg_sim),
            },
        )


DetectorRegistry.register("rag", RagDetector)
