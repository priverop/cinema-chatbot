"""Run evals against cinema-eval-v1 dataset and record results in Opik."""
import time

from opik import Opik
from opik.evaluation import evaluate

from app.domain.errors import LLMRateLimited
from app.infrastructure.config.settings import get_settings
from app.infrastructure.observability.opik_setup import configure_opik
from evals.chat_factory import build_chat_for_evals
from evals.metrics.tool_selection import ToolSelection

DATASET_NAME = "cinema-eval-v1"
EXPERIMENT_NAME = "tool-selection-baseline"

# Free tier: 15 RPM → 1 request every 4s minimum. Use 5s to stay safe.
_THROTTLE_SECONDS = 5
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
            }
        except LLMRateLimited:
            time.sleep(_RATE_LIMIT_RETRY_SECONDS)
            response = chat(message=item["input"], history=None)
            return {
                "tools_called": list(response.tools_called),
                "output": response.reply,
            }

    return chat_task


def main() -> None:
    configure_opik(get_settings())
    client = Opik()
    dataset = client.get_dataset(name=DATASET_NAME)
    evaluate(
        dataset=dataset,
        task=make_task(),
        scoring_metrics=[ToolSelection()],
        experiment_name=EXPERIMENT_NAME,
        task_threads=1,
    )
    print(f"Experiment '{EXPERIMENT_NAME}' completed. Check Opik UI for results.")


if __name__ == "__main__":
    main()
