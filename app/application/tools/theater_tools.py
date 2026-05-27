import json
import logging
from typing import Any

from opik import track

from app.application.tools.base import Tool
from app.application.use_cases.search_theaters import SearchTheaters
from app.domain.ports.llm_client import ToolSpec

logger = logging.getLogger(__name__)


def build_get_theaters_tool(search_theaters: SearchTheaters) -> Tool:
    spec = ToolSpec(
        name="get_theaters",
        description=(
            "Retrieve cinemas/theaters. Optionally filter by name and/or city. "
            "Prefer passing a name when the user mentions a specific cinema "
            "(e.g. 'Verdi', 'Yelmo Ideal') to avoid returning the full list. "
            "Use when the user asks about theaters, cinemas, locations, prices, "
            "discounts, or where movies play."
        ),
        parameters={
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Theater name or substring (e.g. 'Verdi'). Omit if unknown.",
                },
                "city": {
                    "type": "string",
                    "description": "City name to filter by (e.g. 'Madrid'). Omit if unknown.",
                },
            },
        },
    )

    @track(name="tool.get_theaters", project_name="cinema-chatbot")
    def handler(args: dict[str, Any]) -> str:
        name = (args.get("name") or "").strip() or None
        city = (args.get("city") or "").strip() or None
        theaters = search_theaters(name=name, city=city)
        logger.info(
            "get_theaters called name=%r city=%r -> %d results", name, city, len(theaters)
        )
        payload = [
            {
                "id": t.id,
                "name": t.name,
                "location": t.location,
                "price": str(t.price) if t.price is not None else None,
                "discounted_price": str(t.discounted_price) if t.discounted_price is not None else None,
                "discounted_days": t.discounted_days,
                "website": t.website,
            }
            for t in theaters
        ]
        return json.dumps({"theaters": payload})

    return Tool(spec=spec, handler=handler)
