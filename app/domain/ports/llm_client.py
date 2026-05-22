from dataclasses import dataclass, field
from typing import Any, Literal, Protocol


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    parameters: dict[str, Any]  # JSON Schema for the tool args


@dataclass(frozen=True)
class ToolCall:
    name: str
    args: dict[str, Any]
    id: str = ""


@dataclass(frozen=True)
class Message:
    role: Literal["user", "model", "tool"]
    content: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)
    tool_name: str = ""  # set when role == "tool"


@dataclass(frozen=True)
class LLMResponse:
    text: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)


class LLMClient(Protocol):
    def generate_with_tools(
        self,
        messages: list[Message],
        tools: list[ToolSpec],
        system_prompt: str = "",
    ) -> LLMResponse: ...
