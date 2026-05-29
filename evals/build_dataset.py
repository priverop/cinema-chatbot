"""Upload dataset.yaml to Opik, replacing any existing items.

Re-running this script is safe and idempotent: it deletes the old dataset
(if it exists) and creates a fresh one from dataset.yaml, so stale entries
from previous runs never accumulate.
"""
from pathlib import Path

import yaml
from opik import Opik

from app.infrastructure.config.settings import get_settings
from app.infrastructure.observability.opik_setup import configure_opik

DATASET_NAME = "cinema-eval-v1"
DATASET_RAG_NAME = "cinema-eval-v1-rag"
YAML_PATH = Path(__file__).parent / "dataset.yaml"


def _recreate(client: Opik, name: str, description: str, items: list) -> None:
    try:
        client._rest_client.datasets.delete_dataset_by_name(dataset_name=name)
        print(f"Deleted existing dataset '{name}'")
    except Exception:
        pass
    ds = client.create_dataset(name=name, description=description)
    ds.insert(items)
    print(f"Created '{name}' with {len(items)} items")


def main() -> None:
    configure_opik(get_settings())
    items = yaml.safe_load(YAML_PATH.read_text())
    rag_items = [i for i in items if i.get("category") == "rag"]
    client = Opik()

    _recreate(client, DATASET_NAME, "Cinema-chatbot eval cases v1", items)
    _recreate(client, DATASET_RAG_NAME, "Cinema-chatbot RAG-only eval cases v1", rag_items)


if __name__ == "__main__":
    main()
