from dataclasses import dataclass

from app.domain.entities.knowledge_chunk import KnowledgeChunk
from app.domain.ports.embedding_client import EmbeddingClient
from app.domain.ports.knowledge_repository import KnowledgeRepository


@dataclass
class SearchKnowledge:
    embedder: EmbeddingClient
    repository: KnowledgeRepository

    def __call__(self, query: str, k: int = 3) -> list[KnowledgeChunk]:
        (vector,) = self.embedder.embed([query])
        return self.repository.search(vector, k)
