"""Sentence Transformers embeddings for legal document search."""
from sentence_transformers import SentenceTransformer
from backend.config import get_settings
import numpy as np
from functools import lru_cache

settings = get_settings()


class EmbeddingEngine:
    """Manages embedding generation using Sentence Transformers."""
    
    _instance = None
    _model = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def _load_model(self):
        if self._model is None:
            print(f"📦 Loading embedding model: {settings.EMBEDDING_MODEL}...")
            self._model = SentenceTransformer(settings.EMBEDDING_MODEL)
            print("✅ Embedding model loaded.")
        return self._model
    
    def embed_text(self, text: str) -> list[float]:
        """Generate embedding for a single text string."""
        model = self._load_model()
        embedding = model.encode(text, normalize_embeddings=True)
        return embedding.tolist()
    
    def embed_texts(self, texts: list[str], batch_size: int = 32) -> list[list[float]]:
        """Generate embeddings for multiple texts."""
        model = self._load_model()
        embeddings = model.encode(texts, batch_size=batch_size, normalize_embeddings=True, show_progress_bar=True)
        return embeddings.tolist()
    
    def similarity(self, text1: str, text2: str) -> float:
        """Compute cosine similarity between two texts."""
        emb1 = np.array(self.embed_text(text1))
        emb2 = np.array(self.embed_text(text2))
        return float(np.dot(emb1, emb2))


# Singleton
embedding_engine = EmbeddingEngine()
