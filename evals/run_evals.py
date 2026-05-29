"""Run evals against cinema-eval-v1 dataset and record results in Opik."""
import json
import time

from opik import Opik
from opik.evaluation import evaluate

from app.domain.errors import LLMRateLimited
from app.infrastructure.config.settings import get_settings
from app.infrastructure.observability.opik_setup import configure_opik
from evals.chat_factory import build_chat_for_evals
from evals.metrics.context_metrics import ContextPrecisionThrottled, ContextRecallThrottled
from evals.metrics.correctness import CorrectnessJudge
from evals.metrics.hallucination import HallucinationGuarded
from evals.metrics.tool_selection import ToolSelection

DATASET_NAME = "cinema-eval-v1"
DATASET_RAG_NAME = "cinema-eval-v1-rag"
GENERAL_EXPERIMENT_NAME = "tool-selection+hallucination+correctness-v1"
RAG_EXPERIMENT_NAME = "rag-context-precision-recall-v1"

# Free tier: 15 RPM. Each item triggers 3 Gemini calls (task + 2 judges).
# Judges add 5s each (see _JUDGE_THROTTLE_SECONDS in metrics). Total per item:
# 20s task gap + ~5s task call + 5s + ~5s hallucination + 5s + ~5s correctness ≈ 45s
# → ~4 RPM, well under the 15 RPM limit.
_THROTTLE_SECONDS = 20
_RATE_LIMIT_RETRY_SECONDS = 61


def _parse_retrieved_chunks(tool_outputs: list) -> list[str]:
    """Extract chunk content strings from search_knowledge JSON tool outputs."""
    chunks = []
    for raw in tool_outputs:
        try:
            parsed = json.loads(raw)
            for entry in parsed.get("results", []):
                content = entry.get("content")
                if content:
                    chunks.append(content)
        except (json.JSONDecodeError, AttributeError):
            pass
    return chunks


def make_task():
    chat = build_chat_for_evals()

    def chat_task(item: dict) -> dict:
        time.sleep(_THROTTLE_SECONDS)
        try:
            response = chat(message=item["input"], history=None)
        except LLMRateLimited:
            time.sleep(_RATE_LIMIT_RETRY_SECONDS)
            response = chat(message=item["input"], history=None)

        tool_outputs = list(response.tool_outputs)
        return {
            "tools_called": list(response.tools_called),
            "output": response.reply,
            "context": tool_outputs,
            "retrieved_chunks": _parse_retrieved_chunks(tool_outputs),
            "input": item["input"],
            "expected_output": item.get("expected_output"),
        }

    return chat_task


def main() -> None:
    configure_opik(get_settings())
    client = Opik()

    # Run 1: all cases — tool selection, hallucination, correctness
    dataset = client.get_dataset(name=DATASET_NAME)
    evaluate(
        dataset=dataset,
        task=make_task(),
        scoring_metrics=[ToolSelection(), HallucinationGuarded(), CorrectnessJudge()],
        experiment_name=GENERAL_EXPERIMENT_NAME,
        task_threads=1,
    )
    print(f"Experiment '{GENERAL_EXPERIMENT_NAME}' completed.")

    # Run 2: RAG cases only — context precision and recall
    rag_dataset = client.get_dataset(name=DATASET_RAG_NAME)
    evaluate(
        dataset=rag_dataset,
        task=make_task(),
        scoring_metrics=[ContextPrecisionThrottled(), ContextRecallThrottled()],
        experiment_name=RAG_EXPERIMENT_NAME,
        task_threads=1,
    )
    print(f"Experiment '{RAG_EXPERIMENT_NAME}' completed.")

    print("Both experiments done. Check Opik UI for results.")


if __name__ == "__main__":
    main()
