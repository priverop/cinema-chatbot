import json
import logging

from opik import track

from app.application.tools.base import Tool
from app.application.use_cases.search_knowledge import SearchKnowledge
from app.domain.ports.llm_client import ToolSpec

logger = logging.getLogger(__name__)


def build_search_knowledge_tool(search_knowledge: SearchKnowledge) -> Tool:
    spec = ToolSpec(
        name="search_knowledge",
        description=(
            "Search Cinemapi's internal documentation: FAQ, legal disclaimer, "
            "and policies. Use when the user asks about how Cinemapi works, "
            "data accuracy, ticket purchasing, refunds, error reporting, "
            "pricing disclaimers, legal responsibility, or any question about "
            "the service itself rather than specific movies or showtimes."
        ),
        parameters={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Natural language question to search in docs.",
                }
            },
            "required": ["query"],
        },
    )

    @track(name="tool.search_knowledge", project_name="cinema-chatbot")
    def handler(args: dict) -> str:
        query = (args.get("query") or "").strip()
        chunks = search_knowledge(query, k=3)
        logger.info("search_knowledge query=%r -> %d chunks", query, len(chunks))
        payload = [
            {
                "source": c.source,
                "section": c.section,
                "content": c.content,
                "score": c.score,
            }
            for c in chunks
        ]
        return json.dumps({"results": payload})

    return Tool(spec=spec, handler=handler)
