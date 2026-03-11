"""FAISS vector store for legal document storage and retrieval."""
import os
import json
import numpy as np
import faiss
from typing import Optional
from backend.config import get_settings
from backend.ai.embeddings import embedding_engine

app_settings = get_settings()

SAVE_BATCH_SIZE = 200  # Save to disk every N documents to avoid file-handle overflow


class VectorStore:
    """FAISS vector store manager for legal documents."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.persist_dir = app_settings.CHROMA_PERSIST_DIR
            os.makedirs(self.persist_dir, exist_ok=True)
            self.index_path = os.path.join(self.persist_dir, "faiss.index")
            self.data_path = os.path.join(self.persist_dir, "faiss_data.json")
            
            self.index = None
            self.documents = []
            self.metadatas = []
            self.ids = []
            self._unsaved_count = 0
            
            self.load()
            self.initialized = True
            
    def load(self):
        if os.path.exists(self.index_path) and os.path.exists(self.data_path):
            try:
                self.index = faiss.read_index(self.index_path)
                with open(self.data_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.documents = data.get("documents", [])
                    self.metadatas = data.get("metadatas", [])
                    self.ids = data.get("ids", [])
            except Exception as e:
                print(f"Error loading FAISS index: {e}")
                self._init_empty()
        else:
            self._init_empty()
            
    def _init_empty(self):
        dummy = embedding_engine.embed_text("test")
        dim = len(dummy)
        self.index = faiss.IndexFlatL2(dim)
        self.documents = []
        self.metadatas = []
        self.ids = []
        
    def save(self):
        """Save index and metadata to disk with retry logic."""
        for attempt in range(3):
            try:
                faiss.write_index(self.index, self.index_path)
                with open(self.data_path, 'w', encoding='utf-8') as f:
                    json.dump({
                        "documents": self.documents,
                        "metadatas": self.metadatas,
                        "ids": self.ids
                    }, f, ensure_ascii=False)
                self._unsaved_count = 0
                return True
            except Exception as e:
                print(f"[VectorStore] Save attempt {attempt+1} failed: {e}")
        return False
    
    def add_documents(
        self,
        documents: list[str],
        metadatas: list[dict],
        ids: list[str],
    ):
        """Add documents with metadata to the vector store."""
        embeddings = embedding_engine.embed_texts(documents)
        embeddings_np = np.array(embeddings).astype('float32')
        
        self.index.add(embeddings_np)
        self.documents.extend(documents)
        self.metadatas.extend(metadatas)
        self.ids.extend(ids)
        self._unsaved_count += len(documents)
        
        # Only persist every SAVE_BATCH_SIZE docs to avoid Windows file-handle overflow
        if self._unsaved_count >= SAVE_BATCH_SIZE:
            self.save()
        
        return len(documents)
    
    def flush(self):
        """Force save any pending unsaved documents."""
        if self._unsaved_count > 0:
            self.save()
    
    def search(
        self,
        query_text: str,
        n_results: int = 5,
        metadata_filter: Optional[dict] = None,
    ) -> dict:
        """Search for relevant documents using semantic similarity."""
        if self.index is None or self.index.ntotal == 0:
            return {"documents": [[]], "metadatas": [[]], "distances": [[]], "ids": [[]]}
            
        query_embedding = embedding_engine.embed_text(query_text)
        query_np = np.array([query_embedding]).astype('float32')
        
        k_fetch = min(n_results * 5 if metadata_filter else n_results, self.index.ntotal)
        distances, indices = self.index.search(query_np, k_fetch)
        
        res_docs, res_metas, res_dists, res_ids = [], [], [], []
        
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1:
                continue
            meta = self.metadatas[idx]
            
            if metadata_filter:
                match = all(meta.get(k) == v for k, v in metadata_filter.items() if v)
                if not match:
                    continue
                    
            res_docs.append(self.documents[idx])
            res_metas.append(meta)
            res_dists.append(float(dist))
            res_ids.append(self.ids[idx])
            
            if len(res_docs) >= n_results:
                break
                
        return {
            "documents": [res_docs],
            "metadatas": [res_metas],
            "distances": [res_dists],
            "ids": [res_ids]
        }
    
    def get_collection_stats(self) -> dict:
        return {
            "total_documents": len(self.documents),
            "collection_name": app_settings.CHROMA_COLLECTION_NAME,
        }
    
    def delete_collection(self):
        self._init_empty()
        self.save()


# Singleton
vector_store = VectorStore()
