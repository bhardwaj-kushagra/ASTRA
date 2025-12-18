"""
Evaluate the RAG detector on a small synthetic set and print RAGAS-like metrics.
This is a light placeholder that computes:
- answer relevancy (similarity of output label to intent keywords)
- context precision/recall (how relevant retrieved docs are)
- faithfulness proxy (whether label aligns with top evidence doc category)
"""
import json
from typing import List, Dict
import requests

DET_URL = "http://127.0.0.1:8002/detect"

DATA = [
    {"q": "AI content often repeats generic phrasing.", "expect": "AI-generated"},
    {"q": "Personal anecdotes in blogs sound human.", "expect": "human-written"},
    {"q": "SQLite gives ACID with low overhead.", "expect": "human-written"},
]

KEYS_AI = {"ai", "generic", "phrasing"}
KEYS_HUM = {"personal", "anecdotes", "human"}


def sim_keywords(text: str, keys: set) -> float:
    toks = set(t.lower().strip("., ") for t in text.split())
    inter = toks & keys
    return len(inter) / (len(keys) or 1)


def score_example(q: str, expect: str) -> Dict:
    resp = requests.post(DET_URL, json={"text": q}, timeout=20)
    js = resp.json()
    label = js["label"].lower()
    meta = js.get("metadata", {})
    top = meta.get("top_docs", [])

    # Answer relevancy: does label match intent keywords
    if label.startswith("ai"):
        ans_rel = sim_keywords(q, KEYS_AI)
    else:
        ans_rel = sim_keywords(q, KEYS_HUM)

    # Context precision/recall: relevance of retrieved docs to the query intent
    sims = [d.get("sim", 0.0) for d in top]
    ctx_prec = sum(1 for s in sims if s >= 0.2) / (len(sims) or 1)
    ctx_recall = (sum(sims) / (len(sims) or 1))  # proxy

    # Faithfulness proxy: top doc category vs predicted label
    faithful = 0.0
    if top:
        t0 = top[0]["text"].lower()
        if "ai" in t0 and label.startswith("ai"):
            faithful = 1.0
        elif "human" in t0 and label.startswith("human"):
            faithful = 1.0
        elif "sqlite" in t0 and label.startswith("human"):
            faithful = 0.8

    return {
        "question": q,
        "expect": expect,
        "pred": label,
        "confidence": js.get("confidence"),
        "ans_relevancy": round(ans_rel, 3),
        "ctx_precision": round(ctx_prec, 3),
        "ctx_recall": round(ctx_recall, 3),
        "faithfulness": round(faithful, 3),
    }


def main():
    rows: List[Dict] = []
    for ex in DATA:
        rows.append(score_example(ex["q"], ex["expect"]))
    print(json.dumps({"results": rows, "summary": {
        "ans_relevancy_mean": round(sum(r["ans_relevancy"] for r in rows)/len(rows), 3),
        "ctx_precision_mean": round(sum(r["ctx_precision"] for r in rows)/len(rows), 3),
        "ctx_recall_mean": round(sum(r["ctx_recall"] for r in rows)/len(rows), 3),
        "faithfulness_mean": round(sum(r["faithfulness"] for r in rows)/len(rows), 3),
    }}, indent=2))

if __name__ == "__main__":
    main()
