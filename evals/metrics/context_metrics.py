import time

from opik.evaluation.metrics import BaseMetric, ContextPrecision, ContextRecall
from opik.evaluation.metrics.score_result import ScoreResult

_JUDGE_THROTTLE_SECONDS = 5
_JUDGE_MODEL = "gemini/gemini-3.1-flash-lite"


class ContextPrecisionThrottled(BaseMetric):
    """Wraps Opik's ContextPrecision for RAG cases; skips when inputs are missing."""

    def __init__(self):
        super().__init__(name="context_precision")
        self._inner = ContextPrecision(model=_JUDGE_MODEL)

    def score(self, input, output, expected_output=None, retrieved_chunks=None, **_ignored):
        if not retrieved_chunks or not expected_output:
            return ScoreResult(
                name=self.name,
                value=None,
                reason="skipped: missing retrieved_chunks or expected_output",
                scoring_failed=True,
            )
        time.sleep(_JUDGE_THROTTLE_SECONDS)
        result = self._inner.score(
            input=input,
            output=output,
            expected_output=expected_output,
            context=list(retrieved_chunks),
        )
        result.name = self.name
        return result


class ContextRecallThrottled(BaseMetric):
    """Wraps Opik's ContextRecall for RAG cases; skips when inputs are missing."""

    def __init__(self):
        super().__init__(name="context_recall")
        self._inner = ContextRecall(model=_JUDGE_MODEL)

    def score(self, input, output, expected_output=None, retrieved_chunks=None, **_ignored):
        if not retrieved_chunks or not expected_output:
            return ScoreResult(
                name=self.name,
                value=None,
                reason="skipped: missing retrieved_chunks or expected_output",
                scoring_failed=True,
            )
        time.sleep(_JUDGE_THROTTLE_SECONDS)
        result = self._inner.score(
            input=input,
            output=output,
            expected_output=expected_output,
            context=list(retrieved_chunks),
        )
        result.name = self.name
        return result
