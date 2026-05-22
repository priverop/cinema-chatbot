from dataclasses import dataclass
from typing import Any, Callable

from app.domain.ports.llm_client import ToolSpec


@dataclass(frozen=True)
class Tool:
    spec: ToolSpec
    handler: Callable[[dict[str, Any]], Any]
