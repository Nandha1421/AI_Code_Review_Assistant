from typing import List, Optional
import os

from app.embeddings import get_embeddings

try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except Exception:
    CHROMA_AVAILABLE = False

try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    LANGCHAIN_SPLITTER = True
except Exception:
    LANGCHAIN_SPLITTER = False


class SimpleRAG:
    def __init__(self, collection_name: str = "code_examples"):
        self.collection_name = collection_name
        self.client = None
        self.collection = None
        if CHROMA_AVAILABLE:
            self.client = chromadb.Client(Settings())
            try:
                self.collection = self.client.get_collection(name=self.collection_name)
            except Exception:
                self.collection = self.client.create_collection(name=self.collection_name)

    def _split_texts(self, texts: List[str], chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
        if LANGCHAIN_SPLITTER:
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size, chunk_overlap=chunk_overlap, separators=["\n\n", "\n", " "]
            )
            docs = []
            for t in texts:
                docs.extend(splitter.split_text(t))
            return docs

        out = []
        for t in texts:
            start = 0
            L = len(t)
            while start < L:
                end = min(start + chunk_size, L)
                out.append(t[start:end])
                start = max(end - chunk_overlap, end)
                if start == end:
                    break
        return out

    def add_documents(self, texts: List[str], metadatas: Optional[List[dict]] = None):
        if not CHROMA_AVAILABLE:
            return

        chunks = self._split_texts(texts)
        embeddings = get_embeddings(chunks)
        ids = [f"doc-{i}" for i in range(len(chunks))]
        metas = metadatas or [{} for _ in chunks]
        try:
            self.collection.add(ids=ids, documents=chunks, metadatas=metas, embeddings=embeddings)
        except Exception:
            try:
                self.client.delete_collection(name=self.collection_name)
            except Exception:
                pass
            self.collection = self.client.create_collection(name=self.collection_name)
            self.collection.add(ids=ids, documents=chunks, metadatas=metas, embeddings=embeddings)

    def query(self, text: str, k: int = 3) -> List[str]:
        if not CHROMA_AVAILABLE:
            return []
        emb = get_embeddings([text])[0]
        try:
            res = self.collection.query(query_embeddings=[emb], n_results=k)
            docs = []
            for arr in res.get("documents", []):
                if isinstance(arr, list):
                    docs.extend(arr)
            out = []
            for d in docs:
                if d and d not in out:
                    out.append(d)
                if len(out) >= k:
                    break
            return out
        except Exception:
            return []
