import json
import time
from dataclasses import dataclass

from google import genai
from google.genai import errors as genai_errors
from google.genai import types

from app.domain.errors import (
    LLMError,
    LLMInvalidRequest,
    LLMRateLimited,
    LLMUnavailable,
)
from app.domain.ports.llm_client import (
    LLMResponse,
    Message,
    ToolCall,
    ToolSpec,
)

MAX_ATTEMPTS = 3  # 1 initial + 2 retries
BACKOFF_SECONDS = 1.0


@dataclass
class GeminiClient:
    api_key: str
    model: str

    def generate_with_tools(
        self,
        messages: list[Message],
        tools: list[ToolSpec],
        system_prompt: str = "",
    ) -> LLMResponse:
        client = genai.Client(api_key=self.api_key)
        contents = [self._to_content(m) for m in messages]
        config = types.GenerateContentConfig(
            system_instruction=system_prompt or None,
            tools=[self._to_gemini_tool(tools)] if tools else None,
        )
        return self._call_with_retry(client, contents, config)

    def _call_with_retry(
        self,
        client: genai.Client,
        contents: list[types.Content],
        config: types.GenerateContentConfig,
    ) -> LLMResponse:
        last_error: Exception | None = None
        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                response = client.models.generate_content(
                    model=self.model,
                    contents=contents,
                    config=config,
                )
                return self._parse_response(response)
            except genai_errors.ServerError as exc:
                last_error = exc
                if attempt < MAX_ATTEMPTS:
                    time.sleep(BACKOFF_SECONDS * attempt)
                    continue
                raise LLMUnavailable(str(exc)) from exc
            except genai_errors.ClientError as exc:
                code = getattr(exc, "code", None)
                if code == 429:
                    raise LLMRateLimited(str(exc)) from exc
                raise LLMInvalidRequest(str(exc)) from exc
            except genai_errors.APIError as exc:
                raise LLMError(str(exc)) from exc

        raise LLMUnavailable(str(last_error))

    @staticmethod
    def _to_gemini_tool(tools: list[ToolSpec]) -> types.Tool:
        return types.Tool(
            function_declarations=[
                types.FunctionDeclaration(
                    name=t.name,
                    description=t.description,
                    parameters=t.parameters,
                )
                for t in tools
            ]
        )

    @staticmethod
    def _to_content(msg: Message) -> types.Content:
        if msg.role == "tool":
            return types.Content(
                role="user",
                parts=[
                    types.Part.from_function_response(
                        name=msg.tool_name,
                        response=GeminiClient._parse_tool_payload(msg.content),
                    )
                ],
            )
        if msg.role == "model":
            parts: list[types.Part] = []
            if msg.content:
                parts.append(types.Part.from_text(text=msg.content))
            for call in msg.tool_calls:
                parts.append(
                    types.Part.from_function_call(name=call.name, args=call.args)
                )
            return types.Content(role="model", parts=parts)
        # user
        return types.Content(role="user", parts=[types.Part.from_text(text=msg.content)])

    @staticmethod
    def _parse_tool_payload(content: str) -> dict:
        try:
            data = json.loads(content)
            return data if isinstance(data, dict) else {"result": data}
        except json.JSONDecodeError:
            return {"result": content}

    @staticmethod
    def _parse_response(response) -> LLMResponse:
        text_chunks: list[str] = []
        tool_calls: list[ToolCall] = []
        candidates = getattr(response, "candidates", None) or []
        if candidates:
            parts = getattr(candidates[0].content, "parts", None) or []
            for part in parts:
                fn = getattr(part, "function_call", None)
                if fn and getattr(fn, "name", None):
                    tool_calls.append(
                        ToolCall(name=fn.name, args=dict(fn.args or {}))
                    )
                    continue
                text = getattr(part, "text", None)
                if text:
                    text_chunks.append(text)
        return LLMResponse(text="".join(text_chunks), tool_calls=tool_calls)
