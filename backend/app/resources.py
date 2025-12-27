import json
from pathlib import Path

RESOURCE_DIR = Path(__file__).resolve().parent.parent / "resources"


def load_resources(country: str) -> dict:
    path = RESOURCE_DIR / f"{country.lower()}.json"
    if not path.exists():
        path = RESOURCE_DIR / "default.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
