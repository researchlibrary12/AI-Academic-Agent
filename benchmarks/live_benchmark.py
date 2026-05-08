import argparse
import asyncio
import json
import time
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"
TEST_CASES_PATH = ROOT_DIR / "benchmarks" / "test_cases.json"
BASELINE_PATH = ROOT_DIR / "benchmarks" / "baseline_cursor_claude_template.json"
OUTPUT_PATH = ROOT_DIR / "benchmarks" / "results_real.json"


import sys

if str(BACKEND_DIR) not in sys.path:
    sys.path.append(str(BACKEND_DIR))

from agents.router_agent import route_request  # noqa: E402  # pylint: disable=import-error
from services.model_gateway import model_gateway  # noqa: E402  # pylint: disable=import-error


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _latency_to_score(latency_ms: float) -> float:
    if latency_ms <= 800:
        return 5.0
    if latency_ms <= 1500:
        return 4.5
    if latency_ms <= 2500:
        return 4.0
    if latency_ms <= 4000:
        return 3.5
    if latency_ms <= 6000:
        return 3.0
    if latency_ms <= 9000:
        return 2.0
    return 1.0


def _extract_json_object(text: str) -> dict[str, Any]:
    raw = text.strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        raw = raw.replace("json\n", "", 1).strip()
    start = raw.find("{")
    end = raw.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found in judge output")
    return json.loads(raw[start : end + 1])


async def _judge_response(query: str, response: str, target_agent: str) -> dict[str, float]:
    prompt = (
        "You are an evaluator for an academic AI assistant.\n"
        "Score from 1.0 to 5.0 with one decimal place for:\n"
        "- relevance: Does it answer the user's request?\n"
        "- accuracy: Is it technically/curricularly correct?\n"
        "- actionability: Does it provide concrete next steps?\n"
        "- clarity: Is it clear and easy to follow?\n"
        "Return STRICT JSON only in this shape:\n"
        '{"relevance": 0.0, "accuracy": 0.0, "actionability": 0.0, "clarity": 0.0}\n'
        f"Target agent type: {target_agent}\n"
        f"User query: {query}\n"
        f"Assistant response:\n{response}\n"
    )
    judged = await model_gateway.generate(prompt)
    data = _extract_json_object(judged)
    return {
        "relevance": float(data["relevance"]),
        "accuracy": float(data["accuracy"]),
        "actionability": float(data["actionability"]),
        "clarity": float(data["clarity"]),
    }


async def _run_our_agent(test_cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for case in test_cases:
        started = time.perf_counter()
        result = await route_request(case["query"], {"user_id": "benchmark-user"})
        elapsed_ms = (time.perf_counter() - started) * 1000
        response = str(result.get("response", ""))
        scores = await _judge_response(case["query"], response, case["target_agent"])
        rows.append(
            {
                "test_id": case["id"],
                "selected_agent": result.get("agent", ""),
                "latency_ms": round(elapsed_ms, 2),
                **scores,
                "latency": _latency_to_score(elapsed_ms),
                "response_excerpt": response[:400],
            }
        )
    return rows


async def _score_baseline_entries(
    test_cases: list[dict[str, Any]], baseline_rows: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    by_test_id = {row["test_id"]: row for row in baseline_rows}
    scored: list[dict[str, Any]] = []
    for case in test_cases:
        existing = by_test_id.get(case["id"])
        if not existing:
            raise ValueError(f"Missing baseline response for test_id={case['id']}")
        response = str(existing.get("response", "")).strip()
        if not response:
            raise ValueError(f"Baseline response is empty for test_id={case['id']}")
        latency_ms = float(existing.get("latency_ms", 4000))
        scores = await _judge_response(case["query"], response, case["target_agent"])
        scored.append(
            {
                "test_id": case["id"],
                "latency_ms": round(latency_ms, 2),
                **scores,
                "latency": _latency_to_score(latency_ms),
                "response_excerpt": response[:400],
            }
        )
    return scored


async def main(include_baseline: bool) -> None:
    test_cases = _load_json(TEST_CASES_PATH)
    ours = await _run_our_agent(test_cases)
    output: dict[str, Any] = {"must_academic_agent": ours}

    if include_baseline:
        baseline_payload = _load_json(BASELINE_PATH)
        baseline_rows = baseline_payload.get("cursor_default_claude", [])
        output["cursor_default_claude"] = await _score_baseline_entries(test_cases, baseline_rows)

    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    print(f"Wrote live benchmark rows to: {OUTPUT_PATH}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run live benchmark scoring from real outputs.")
    parser.add_argument(
        "--include-baseline",
        action="store_true",
        help="Also score baseline Cursor Claude responses from baseline template file.",
    )
    args = parser.parse_args()
    asyncio.run(main(include_baseline=args.include_baseline))
