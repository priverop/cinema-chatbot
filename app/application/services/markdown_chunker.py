import re
from pathlib import Path


def chunk_markdown(path: Path, text: str) -> list[tuple[str, str]]:
    """Split markdown text into (section_title, content) pairs by ## headings.

    Falls back to a single chunk using the # title if no ## headings are found.
    """
    source = path.name
    sections = re.split(r"^## (.+)$", text, flags=re.MULTILINE)

    if len(sections) == 1:
        # No ## headings — use # title as section name if present
        title_match = re.search(r"^# (.+)$", text, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else source
        content = text.strip()
        return [(title, content)] if content else []

    # sections = [preamble, heading1, body1, heading2, body2, ...]
    chunks: list[tuple[str, str]] = []
    for i in range(1, len(sections), 2):
        heading = sections[i].strip()
        body = sections[i + 1].strip()
        if body:
            chunks.append((heading, body))
    return chunks
