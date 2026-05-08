from pathlib import Path

from chromadb import PersistentClient

from config import settings


class ChromaVectorStore:
    def __init__(self) -> None:
        Path(settings.chroma_persist_dir).mkdir(parents=True, exist_ok=True)
        self.client = PersistentClient(path=settings.chroma_persist_dir)
        self.collection = self.client.get_or_create_collection("academic_documents")

    def add_chunks(
        self,
        ids: list[str],
        texts: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict[str, str]],
    ) -> None:
        self.collection.add(ids=ids, documents=texts, metadatas=metadatas, embeddings=embeddings)

    def query(self, query_embedding: list[float], metadata_filter: dict[str, str], top_k: int = 5) -> dict:
        where = metadata_filter or None
        return self.collection.query(query_embeddings=[query_embedding], n_results=top_k, where=where)


vector_store = ChromaVectorStore()
