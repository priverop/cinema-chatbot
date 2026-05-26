"""
Index markdown docs from db/knowledge/ into ChromaDB.

Usage:
    python -m app.scripts.index_knowledge
"""

import hashlib
from pathlib import Path

from app.application.services.markdown_chunker import chunk_markdown
from app.domain.entities.knowledge_chunk import KnowledgeChunk
from app.infrastructure.config.settings import get_settings
from app.infrastructure.llm.gemini_embedding_client import GeminiEmbeddingClient
from app.infrastructure.rag.chroma_knowledge_repository import ChromaKnowledgeRepository


def _chunk_id(source: str, section: str) -> str:
    return hashlib.md5(f"{source}::{section}".encode()).hexdigest()


def main() -> None:
    settings = get_settings()
    knowledge_dir = Path(settings.knowledge_path)
    md_files = sorted(knowledge_dir.glob("*.md"))

    if not md_files:
        print(f"No .md files found in {knowledge_dir}")
        return

    embedder = GeminiEmbeddingClient(
        api_key=settings.gemini_api_key,
        model=settings.gemini_embedding_model,
    )
    repo = ChromaKnowledgeRepository(path=settings.chroma_path)

    all_chunks: list[KnowledgeChunk] = []
    for md_file in md_files:
        text = md_file.read_text(encoding="utf-8")
        pairs = chunk_markdown(md_file, text)
        for section, content in pairs:
            chunk = KnowledgeChunk(
                id=_chunk_id(md_file.name, section),
                content=content,
                source=md_file.name,
                section=section,
            )
            all_chunks.append(chunk)
        print(f"  {md_file.name}: {len(pairs)} chunks")

    if not all_chunks:
        print("No chunks generated.")
        return

    print(f"\nEmbedding {len(all_chunks)} chunks via Gemini ({settings.gemini_embedding_model})...")
    embeddings = embedder.embed([c.content for c in all_chunks])

    print("Clearing existing index and upserting...")
    repo.clear()
    repo.upsert(all_chunks, embeddings)

    print(f"\nDone. {len(md_files)} docs, {len(all_chunks)} chunks indexed -> {settings.chroma_path}")


if __name__ == "__main__":
    main()
