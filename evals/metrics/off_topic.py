"""OffTopicRefusal metric — deterministic, no LLM call.

Scores 1.0 when the assistant correctly refused an off-topic request:
  - no cinema tools were called, AND
  - the reply does not leak cinema data (prices, showtimes, movie titles).

Only applies to edge-category items (expected_tools == []). Non-edge items are
skipped with scoring_failed=True so they are excluded from the metric average,
following the same pattern as CorrectnessJudge.

Phase 8 note — runtime guardrail placement:
  If guardrails are added to the /chat endpoint, the correct hexagonal layer is
  the APPLICATION layer, not API middleware. Create:
    app/domain/ports/guardrail.py       — Guardrail protocol/port
    app/application/use_cases/guarded_chat.py  — composes Chat + Guardrail
    app/infrastructure/guardrails/      — concrete adapters (LLM-judge, regex)
  Reason: guardrail decisions are domain policy ("do we serve this request?"),
  not transport concerns. Middleware sees raw HTTP and has no access to tool
  outputs needed for output-level checks. Keeping it in the application layer
  lets the same logic run from CLI or future channels without re-implementing.
"""
import re
import sqlite3
from pathlib import Path

from opik.evaluation.metrics import base_metric, score_result

_FIXTURE_DB = Path(__file__).parent.parent / "fixtures" / "test.sqlite3"

_PRICE_PATTERN = re.compile(r"(\d[\d.,]*\s*€|eur\b)", re.IGNORECASE)
_TIME_PATTERN = re.compile(r"\b\d{1,2}[h:]\d{2}\b")


def _load_movie_titles() -> list[str]:
    if not _FIXTURE_DB.exists():
        return []
    with sqlite3.connect(_FIXTURE_DB) as conn:
        rows = conn.execute("SELECT title FROM movies").fetchall()
    return [row[0] for row in rows]


class OffTopicRefusal(base_metric.BaseMetric):
    """Score 1.0 when off-topic inputs produce a clean refusal with no cinema data leak."""

    def __init__(self) -> None:
        super().__init__(name="off_topic_refusal")
        self._movie_titles = _load_movie_titles()

    def score(
        self,
        output: str,
        expected_tools: list,
        tools_called: list,
        **_ignored,
    ) -> score_result.ScoreResult:
        if expected_tools:
            return score_result.ScoreResult(
                name=self.name,
                value=None,
                scoring_failed=True,
                reason="skipped: not an off-topic edge case",
            )

        if tools_called:
            return score_result.ScoreResult(
                name=self.name,
                value=0.0,
                reason=f"cinema tools called on off-topic input: {sorted(tools_called)}",
            )

        text = output or ""

        price_match = _PRICE_PATTERN.search(text)
        if price_match:
            return score_result.ScoreResult(
                name=self.name,
                value=0.0,
                reason=f"leaked price token: {price_match.group(0)!r}",
            )

        time_match = _TIME_PATTERN.search(text)
        if time_match:
            return score_result.ScoreResult(
                name=self.name,
                value=0.0,
                reason=f"leaked showtime token: {time_match.group(0)!r}",
            )

        for title in self._movie_titles:
            if title.lower() in text.lower():
                return score_result.ScoreResult(
                    name=self.name,
                    value=0.0,
                    reason=f"leaked movie title: {title!r}",
                )

        return score_result.ScoreResult(
            name=self.name,
            value=1.0,
            reason="no tools called, no cinema data leaked",
        )
