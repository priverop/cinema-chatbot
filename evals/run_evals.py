"""Run evals against cinema-eval-v1 dataset and record results in Opik."""
import time

from opik import Opik
from opik.evaluation import evaluate

from app.domain.errors import LLMRateLimited
from app.infrastructure.config.settings import get_settings
from app.infrastructure.observability.opik_setup import configure_opik
from evals.chat_factory import build_chat_for_evals
from evals.metrics.correctness import CorrectnessJudge
from evals.metrics.hallucination import HallucinationGuarded
from evals.metrics.tool_selection import ToolSelection

DATASET_NAME = "cinema-eval-v1"
EXPERIMENT_NAME = "tool-selection+hallucination+correctness-v1"

# Free tier: 15 RPM. Each item triggers 3 Gemini calls (task + 2 judges).
# Judges add 5s each (see _JUDGE_THROTTLE_SECONDS in metrics). Total per item:
# 20s task gap + ~5s task call + 5s + ~5s hallucination + 5s + ~5s correctness ≈ 45s
# → ~4 RPM, well under the 15 RPM limit.
_THROTTLE_SECONDS = 20
_RATE_LIMIT_RETRY_SECONDS = 61


def make_task():
    chat = build_chat_for_evals()

    def chat_task(item: dict) -> dict:
        time.sleep(_THROTTLE_SECONDS)
        try:
            response = chat(message=item["input"], history=None)
            return {
                "tools_called": list(response.tools_called),
                "output": response.reply,
                "context": list(response.tool_outputs),
                "input": item["input"],
                "expected_output": item.get("expected_output"),
            }
        except LLMRateLimited:
            time.sleep(_RATE_LIMIT_RETRY_SECONDS)
            response = chat(message=item["input"], history=None)
            return {
                "tools_called": list(response.tools_called),
                "output": response.reply,
                "context": list(response.tool_outputs),
                "input": item["input"],
                "expected_output": item.get("expected_output"),
            }

    return chat_task


def main() -> None:
    configure_opik(get_settings())
    client = Opik()
    dataset = client.get_dataset(name=DATASET_NAME)
    evaluate(
        dataset=dataset,
        task=make_task(),
        scoring_metrics=[ToolSelection(), HallucinationGuarded(), CorrectnessJudge()],
        experiment_name=EXPERIMENT_NAME,
        task_threads=1,
    )
    print(f"Experiment '{EXPERIMENT_NAME}' completed. Check Opik UI for results.")


if __name__ == "__main__":
    main()
