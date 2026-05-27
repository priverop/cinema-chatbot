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
YAML_PATH = Path(__file__).parent / "dataset.yaml"


def main() -> None:
    configure_opik(get_settings())
    items = yaml.safe_load(YAML_PATH.read_text())
    client = Opik()

    try:
        client._rest_client.datasets.delete_dataset_by_name(dataset_name=DATASET_NAME)
        print(f"Deleted existing dataset '{DATASET_NAME}'")
    except Exception:
        pass

    dataset = client.create_dataset(name=DATASET_NAME, description="Cinema-chatbot eval cases v1")
    dataset.insert(items)
    print(f"Created '{DATASET_NAME}' with {len(items)} items")


if __name__ == "__main__":
    main()
