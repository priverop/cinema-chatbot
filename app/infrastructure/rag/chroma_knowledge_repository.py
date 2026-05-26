from dataclasses import dataclass

import chromadb

from app.domain.entities.knowledge_chunk import KnowledgeChunk

COLLECTION_NAME = "cinema_knowledge"


@dataclass
class ChromaKnowledgeRepository:
    path: str

    def _collection(self) -> chromadb.Collection:
        client = chromadb.PersistentClient(path=self.path)
        return client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

    def search(self, query_embedding: list[float], k: int) -> list[KnowledgeChunk]:
        collection = self._collection()
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(k, collection.count() or 1),
            include=["documents", "metadatas", "distances"],
        )
        chunks: list[KnowledgeChunk] = []
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            chunks.append(
                KnowledgeChunk(
                    id=meta["id"],
                    content=doc,
                    source=meta["source"],
                    section=meta["section"],
                    score=round(1.0 - dist, 4),
                )
            )
        return chunks

    def upsert(self, chunks: list[KnowledgeChunk], embeddings: list[list[float]]) -> None:
        collection = self._collection()
        collection.upsert(
            ids=[c.id for c in chunks],
            documents=[c.content for c in chunks],
            embeddings=embeddings,
            metadatas=[
                {"id": c.id, "source": c.source, "section": c.section}
                for c in chunks
            ],
        )

    def clear(self) -> None:
        client = chromadb.PersistentClient(path=self.path)
        try:
            client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass
        client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
