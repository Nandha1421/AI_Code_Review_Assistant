from typing import List

def get_embeddings(texts: List[str]):
    """Return embeddings for a list of texts using sentence-transformers.

    If sentence-transformers is not installed, returns empty vectors.
    """
    try:
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer("all-MiniLM-L6-v2")
        vectors = model.encode(texts, show_progress_bar=False)
        return vectors.tolist() if hasattr(vectors, "tolist") else list(map(list, vectors))
    except Exception:
        # Return zero-length vectors as placeholders
        return [[0.0] for _ in texts]