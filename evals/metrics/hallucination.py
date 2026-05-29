import time

from opik.evaluation.metrics import BaseMetric, Hallucination
from opik.evaluation.metrics.score_result import ScoreResult

# Delay before calling Gemini to avoid RPM bursts when multiple judge metrics
# fire back-to-back after a task call. See CorrectnessJudge for the same pattern.
_JUDGE_THROTTLE_SECONDS = 5


class HallucinationGuarded(BaseMetric):
    """Wraps Opik's built-in Hallucination, skipping items with no tool context."""

    def __init__(self):
        super().__init__(name="hallucination_guarded")
        self._inner = Hallucination(model="gemini/gemini-3.1-flash-lite")

    def score(self, input, output, context, **_ignored):
        if not context:
            return ScoreResult(
                name=self.name,
                value=0.0,
                reason="skipped: no tool context",
            )
        time.sleep(_JUDGE_THROTTLE_SECONDS)
        result = self._inner.score(input=input, output=output, context=list(context))
        result.name = self.name
        return result
