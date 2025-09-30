import json
from pathlib import Path

def load_schema(name: str):
    path = Path(__file__).parent.parent / "data" / "schemas" / f"{name}.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
