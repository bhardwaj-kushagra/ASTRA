"""Utility script to download the RAG embedding model locally.

This script downloads a Sentence Transformer model (e.g., all-MiniLM-L6-v2)
and saves it into a local directory inside the repo.
"""
import os
from pathlib import Path
try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("Error: sentence-transformers not installed. Run: pip install sentence-transformers")
    exit(1)

def get_repo_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent

def main() -> None:
    model_id = os.getenv("RAG_MODEL_ID", "sentence-transformers/all-MiniLM-L6-v2")
    
    repo_root = get_repo_root()
    folder_name = model_id.replace("/", "-")
    default_dir = repo_root / "astra-models" / folder_name
    
    target_dir_str = os.getenv("RAG_MODEL_PATH", str(default_dir))
    target_dir = Path(target_dir_str)
    
    print(f"Downloading embedding model '{model_id}' to '{target_dir}'...")
    
    # SentenceTransformer handles saving differently than transformers
    model = SentenceTransformer(model_id)
    model.save(str(target_dir))
    
    print("Download complete. Set RAG_MODEL_PATH to this directory for offline use.")

if __name__ == "__main__":
    main()
