from dataclasses import dataclass


@dataclass(frozen=True)
class KnowledgeChunk:
    id: str
    content: str
    source: str
    section: str
    score: float | None = None
