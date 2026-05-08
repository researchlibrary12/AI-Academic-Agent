import json
from pathlib import Path
from typing import Any


STORE_PATH = Path(__file__).resolve().parents[1] / "data" / "assessment_results.json"


def _ensure_store() -> None:
    STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not STORE_PATH.exists():
        STORE_PATH.write_text("[]", encoding="utf-8")


def _read() -> list[dict[str, Any]]:
    _ensure_store()
    raw = STORE_PATH.read_text(encoding="utf-8")
    try:
        data = json.loads(raw)
        if isinstance(data, list):
            return data
    except json.JSONDecodeError:
        pass
    return []


def _write(rows: list[dict[str, Any]]) -> None:
    _ensure_store()
    STORE_PATH.write_text(json.dumps(rows, indent=2), encoding="utf-8")


def add_results(records: list[dict[str, Any]]) -> int:
    rows = _read()
    rows.extend(records)
    _write(rows)
    return len(rows)


def get_results_for_user(user_id: str) -> list[dict[str, Any]]:
    return [row for row in _read() if str(row.get("user_id", "")) == user_id]
