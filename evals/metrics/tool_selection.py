from opik.evaluation.metrics import base_metric, score_result


class ToolSelection(base_metric.BaseMetric):
    """Score 1.0 when the set of called tools matches expected_tools exactly."""

    def __init__(self) -> None:
        super().__init__(name="tool_selection")

    def score(self, tools_called: list, expected_tools: list, **_ignored) -> score_result.ScoreResult:
        called = set(tools_called or [])
        expected = set(expected_tools or [])
        match = called == expected
        return score_result.ScoreResult(
            name=self.name,
            value=1.0 if match else 0.0,
            reason=f"called={sorted(called)} expected={sorted(expected)}",
        )
