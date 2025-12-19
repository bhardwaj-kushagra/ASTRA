"""
RAG-based detector using local embeddings (Sentence Transformers).
Retrieves similar examples from a knowledge base to classify content.
"""
import sys
import os
from typing import List, Dict, Any
import torch

try:
    from sentence_transformers import SentenceTransformer, util
    _has_st = True
except ImportError:
    _has_st = False

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'schemas')))
from models import DetectionRequest, DetectionResult
from detector import Detector, DetectorRegistry


class RagDetector(Detector):
    """
    RAG detector that uses semantic embeddings to retrieve similar labeled examples.
    Uses sentence-transformers/all-MiniLM-L6-v2 by default.
    """

    def __init__(self, config: dict):
        super().__init__(config)
        if not _has_st:
            raise RuntimeError("sentence-transformers not installed. Run: pip install sentence-transformers")

        # Load model
        model_path = config.get("model_path") or os.getenv("RAG_MODEL_PATH")
        model_id = config.get("model_id", "sentence-transformers/all-MiniLM-L6-v2")
        
        # If model_path is set, use it; otherwise download/cache model_id
        load_path = model_path if model_path else model_id
        self.model = SentenceTransformer(load_path)

        # Knowledge base of labeled examples (Few-Shot RAG)
        # In a real system, this would come from a vector DB (Chroma/Pinecone)
        self.knowledge_base = [
            {"text": "As an AI language model, I cannot provide that information.", "label": "AI-generated"},
            {"text": "I'm sorry, but I don't have feelings or personal opinions.", "label": "AI-generated"},
            {"text": "Here is a summary of the text you provided.", "label": "AI-generated"},
            {"text": "The following is a generated response based on your query.", "label": "AI-generated"},
            {"text": "I really loved that movie! The acting was superb and I cried at the end.", "label": "human-written"},
            {"text": "Can you believe what happened yesterday? It was absolutely crazy.", "label": "human-written"},
            {"text": "The quick brown fox jumps over the lazy dog.", "label": "human-written"},
            {"text": "I think we should go to the park later.", "label": "human-written"},
        ]
        
        # Pre-compute embeddings for the knowledge base
        texts = [doc["text"] for doc in self.knowledge_base]
        self.kb_embeddings = self.model.encode(texts, convert_to_tensor=True)
        self.k = int(config.get("top_k", 1))

    @property
    def model_name(self) -> str:
        return "rag-embedding-knn"

    async def detect(self, request: DetectionRequest) -> DetectionResult:
        """
        Detect by finding the most semantically similar example in the knowledge base.
        """
        # Embed the input text
        query_embedding = self.model.encode(request.text, convert_to_tensor=True)

        # Compute cosine similarity with all KB entries
        # cos_sim returns a tensor of shape (1, len(kb))
        cos_scores = util.cos_sim(query_embedding, self.kb_embeddings)[0]

        # Find top k matches
        # top_results is a named tuple (values, indices)
        top_k = min(self.k, len(self.knowledge_base))
        top_results = torch.topk(cos_scores, k=top_k)
        
        top_scores = top_results.values.tolist()
        top_indices = top_results.indices.tolist()

        # Retrieve the best match
        best_idx = top_indices[0]
        best_score = top_scores[0]
        best_match = self.knowledge_base[best_idx]
        
        # Decision logic: Label of the nearest neighbor
        # Confidence is the similarity score (clamped 0-1)
        label = best_match["label"]
        confidence = max(0.0, min(1.0, float(best_score)))

        # Construct metadata for explainability
        top_docs = []
        for score, idx in zip(top_scores, top_indices):
            doc = self.knowledge_base[idx]
            top_docs.append({
                "text": doc["text"],
                "label": doc["label"],
                "similarity": float(score)
            })

        return DetectionResult(
            label=label,
            confidence=confidence,
            detector_model=self.model_name,
            metadata={
                "method": "knn-embedding",
                "top_docs": top_docs
            }
        )


DetectorRegistry.register("rag", RagDetector)
