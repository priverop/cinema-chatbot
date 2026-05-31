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
from evals.metrics.moderation import MODERATION_AVAILABLE, ModerationGuarded
from evals.metrics.off_topic import OffTopicRefusal
from evals.metrics.tool_selection import ToolSelection

DATASET_NAME = "cinema-eval-v1"
DATASET_RAG_NAME = "cinema-eval-v1-rag"
RAG_EXPERIMENT_NAME = "rag-context-precision-recall-v1"

# A/B prompt variants. Each experiment runs the full DATASET_NAME with one
# prompt variant. Results land in Opik under the same dataset so the UI can
# compare them side-by-side via the Experiments tab.
_PROMPT_VARIANTS = [
    ("v1", "prompt-v1-baseline"),
    ("v2", "prompt-v2-short"),
]

# Free tier: 15 RPM. Each item triggers 3 Gemini calls (task + 2 LLM judges).
# OffTopicRefusal is deterministic (no LLM call). ModerationGuarded adds 1 more
# LLM call if MODERATION_AVAILABLE. Judges add 5s each (see _JUDGE_THROTTLE_SECONDS
# in metrics). Total per item without moderation:
# 20s task gap + ~5s task call + 5s + ~5s hallucination + 5s + ~5s correctness ≈ 45s
# → ~4 RPM, well under the 15 RPM limit.
# Running 2 variants back-to-back: ~45s × dataset_size × 2 ≈ 520s minimum.
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


def make_task(prompt_variant: str = "v1"):
    chat = build_chat_for_evals(prompt_variant=prompt_variant)

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

    # A/B: run both prompt variants against the same dataset so Opik can
    # compare them side-by-side (dataset → Experiments tab → select both).
    dataset = client.get_dataset(name=DATASET_NAME)
    base_metrics = [ToolSelection(), HallucinationGuarded(), CorrectnessJudge(), OffTopicRefusal()]
    if MODERATION_AVAILABLE:
        base_metrics.append(ModerationGuarded())

    for variant, exp_name in _PROMPT_VARIANTS:
        evaluate(
            dataset=dataset,
            task=make_task(variant),
            scoring_metrics=base_metrics,
            experiment_name=exp_name,
            task_threads=1,
        )
        print(f"Experiment '{exp_name}' completed.")

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
