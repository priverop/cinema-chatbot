from typing import Protocol

from app.domain.entities.knowledge_chunk import KnowledgeChunk


class KnowledgeRepository(Protocol):
    def search(self, query_embedding: list[float], k: int) -> list[KnowledgeChunk]:
        ...

    def upsert(self, chunks: list[KnowledgeChunk], embeddings: list[list[float]]) -> None:
        ...

    def clear(self) -> None:
        ...
