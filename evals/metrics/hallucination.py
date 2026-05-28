from opik.evaluation.metrics import BaseMetric, Hallucination
from opik.evaluation.metrics.score_result import ScoreResult


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
        return self._inner.score(input=input, output=output, context=list(context))
