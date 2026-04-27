from dataclasses import dataclass
from typing import List

from django.conf import settings


@dataclass
class RetrievedChunk:
    source_id: str
    text: str


class _SentenceTransformerEmbeddingFn:
    def __init__(self, model_name: str):
        from sentence_transformers import SentenceTransformer

        self.model = SentenceTransformer(model_name)

    def __call__(self, input: List[str]) -> List[List[float]]:
        vectors = self.model.encode(input, convert_to_numpy=True)
        return vectors.tolist()

    def name(self) -> str:
        return "sentence-transformers-local"


def _get_collection():
    import chromadb

    persist_dir = getattr(settings, "RAG_PERSIST_DIR", "chroma_db")
    collection_name = getattr(settings, "RAG_COLLECTION", "welltrack_guidelines")
    model_name = getattr(
        settings, "RAG_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
    )

    client = chromadb.PersistentClient(path=persist_dir)
    embedding_fn = _SentenceTransformerEmbeddingFn(model_name)
    return client.get_or_create_collection(name=collection_name, embedding_function=embedding_fn)


def retrieve_context(query: str, limit: int | None = None) -> List[RetrievedChunk]:
    if not getattr(settings, "RAG_ENABLED", True):
        return []
    q = (query or "").strip()
    if not q:
        return []

    n_results = limit or getattr(settings, "RAG_TOP_K", 4)
    try:
        collection = _get_collection()
        result = collection.query(
            query_texts=[q],
            n_results=n_results,
            include=["documents", "metadatas"],
        )
    except Exception:
        return []

    docs = (result.get("documents") or [[]])[0]
    metas = (result.get("metadatas") or [[]])[0]
    chunks: List[RetrievedChunk] = []
    for idx, doc in enumerate(docs):
        md = metas[idx] if idx < len(metas) and metas[idx] else {}
        source_id = str(md.get("source_id") or md.get("source") or f"source-{idx+1}")
        chunks.append(RetrievedChunk(source_id=source_id, text=doc))
    return chunks
