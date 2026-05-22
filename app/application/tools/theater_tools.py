import json
import logging
from typing import Any

from app.application.tools.base import Tool
from app.application.use_cases.list_theaters import ListTheaters
from app.domain.ports.llm_client import ToolSpec

logger = logging.getLogger(__name__)


def build_get_theaters_tool(list_theaters: ListTheaters) -> Tool:
    spec = ToolSpec(
        name="get_theaters",
        description=(
            "Retrieve cinemas/theaters. Optionally filter by city. "
            "Use when the user asks about theaters, cinemas, locations, or where movies play."
        ),
        parameters={
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "City name to filter theaters by (e.g. 'Madrid'). Omit to return all.",
                },
            },
        },
    )

    def handler(args: dict[str, Any]) -> str:
        city = (args.get("city") or "").strip().lower()
        theaters = list_theaters()
        if city:
            theaters = [
                t for t in theaters if t.location and city in t.location.lower()
            ]
        logger.info("get_theaters called city=%r -> %d results", city or None, len(theaters))
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
