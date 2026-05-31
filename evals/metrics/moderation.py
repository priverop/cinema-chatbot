"""ModerationGuarded metric — wraps opik.evaluation.metrics.Moderation.

Confirmed available in opik==2.0.48. The import is still guarded with
try/except and MODERATION_AVAILABLE is exported so run_evals.py can
conditionally register the metric — defensive against future version changes.

Opik's Moderation.score() accepts only `output`. It scores 0.0 for safe
content and 1.0 for harmful content (higher = more harmful).
"""
import time

from opik.evaluation.metrics import BaseMetric
from opik.evaluation.metrics.score_result import ScoreResult

_JUDGE_THROTTLE_SECONDS = 5

try:
    from opik.evaluation.metrics import Moderation as _Moderation

    MODERATION_AVAILABLE = True
except ImportError:
    MODERATION_AVAILABLE = False


class ModerationGuarded(BaseMetric):
    """Wraps Opik's Moderation judge; scores all items for harmful content."""

    def __init__(self):
        super().__init__(name="moderation_guarded")
        if not MODERATION_AVAILABLE:
            raise RuntimeError(
                "opik.evaluation.metrics.Moderation not available in this opik version. "
                "Check MODERATION_AVAILABLE before instantiating."
            )
        self._inner = _Moderation(model="gemini/gemini-3.1-flash-lite")

    def score(self, output: str, **_ignored) -> ScoreResult:
        time.sleep(_JUDGE_THROTTLE_SECONDS)
        result = self._inner.score(output=output)
        result.name = self.name
        return result
