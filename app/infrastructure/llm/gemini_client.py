import time
from dataclasses import dataclass

from google import genai
from google.genai import errors as genai_errors

from app.domain.errors import (
    LLMError,
    LLMInvalidRequest,
    LLMRateLimited,
    LLMUnavailable,
)

MAX_ATTEMPTS = 3  # 1 initial + 2 retries
BACKOFF_SECONDS = 1.0


@dataclass
class GeminiClient:
    api_key: str
    model: str

    def generate(self, prompt: str) -> str:
        client = genai.Client(api_key=self.api_key)
        last_error: Exception | None = None

        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                response = client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                )
                return response.text or ""
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
