import time
from collections.abc import Sequence

from opik.evaluation.metrics import BaseMetric, GEval
from opik.evaluation.metrics.score_result import ScoreResult

# Delay before calling Gemini. Each scored item triggers 1 extra LLM call; with
# HallucinationGuarded also active, 3 Gemini calls fire per item. Without per-metric
# throttling, back-to-back judge calls burst past the 15 RPM free-tier limit.
_JUDGE_THROTTLE_SECONDS = 5


class CorrectnessJudge(BaseMetric):
    """LLM-judge that checks factual correctness against a reference answer.

    Embeds the assistant reply, tool context, and reference answer into a
    single composite string passed to GEval, since GEval.score only accepts
    an `output` parameter.

    Skips items without an expected_output (rag/edge cases) by returning
    scoring_failed=True so Opik excludes them from the metric average.
    """

    def __init__(self):
        super().__init__(name="correctness_judge")
        self._inner = GEval(
            name="correctness_judge",
            task_introduction=(
                "You are evaluating a cinema-assistant reply for factual correctness. "
                "You will receive three sections: ASSISTANT_REPLY (the reply to evaluate), "
                "TOOL_CONTEXT (raw data from the cinema database tools), and "
                "REFERENCE_ANSWER (the expected correct answer)."
            ),
            evaluation_criteria=(
                "Score the ASSISTANT_REPLY from 0.0 to 1.0 based on factual correctness:\n"
                "1.0 — All key facts in REFERENCE_ANSWER are present and accurate in the reply. "
                "Minor phrasing differences are fine.\n"
                "0.7 — Most facts correct; one minor omission or slight imprecision.\n"
                "0.4 — Some facts correct but significant omissions or one wrong fact.\n"
                "0.0 — Reply contradicts REFERENCE_ANSWER or contains clearly wrong facts.\n"
                "Base scoring on TOOL_CONTEXT as the ground truth. "
                "Penalise facts absent from TOOL_CONTEXT that appear in the reply."
            ),
            model="gemini/gemini-3.1-flash-lite",
        )

    def score(
        self,
        output: str,
        expected_output: str | None = None,
        context: Sequence[str] | None = None,
        **_ignored,
    ) -> ScoreResult:
        if not expected_output:
            return ScoreResult(
                name=self.name,
                value=None,
                scoring_failed=True,
                reason="skipped: no reference answer",
            )

        tool_context = "\n".join(context) if context else "(none)"
        composite = (
            f"ASSISTANT_REPLY:\n{output}\n\n"
            f"TOOL_CONTEXT:\n{tool_context}\n\n"
            f"REFERENCE_ANSWER:\n{expected_output}"
        )
        time.sleep(_JUDGE_THROTTLE_SECONDS)
        result = self._inner.score(output=composite)
        result.name = self.name
        return result
