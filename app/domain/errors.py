class LLMError(Exception):
    """Base error from the LLM port."""


class LLMUnavailable(LLMError):
    """Upstream LLM temporarily unavailable (e.g. 503)."""


class LLMRateLimited(LLMError):
    """Upstream LLM rate limit hit (e.g. 429)."""


class LLMInvalidRequest(LLMError):
    """Bad request to the LLM (e.g. 400, invalid input)."""
