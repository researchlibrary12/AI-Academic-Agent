import json
import argparse
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
TEST_CASES_PATH = BASE_DIR / "test_cases.json"
RESULTS_PATH = BASE_DIR / "results_template.json"


def _load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _score_run(test_case: dict, scored_case: dict) -> float:
    dimensions = test_case["dimensions"]
    weighted_sum = 0.0
    total_weight = 0.0
    for dim, weight in dimensions.items():
        weighted_sum += float(scored_case[dim]) * float(weight)
        total_weight += float(weight)
    return weighted_sum / total_weight


def _final_score_10000(per_test_scores: list[float]) -> int:
    # 5-point rubric -> normalize to 0..1 -> map to 1..10000
    avg = sum(per_test_scores) / len(per_test_scores)
    normalized = avg / 5.0
    return max(1, min(10000, round(normalized * 10000)))


def evaluate(results_path: Path = RESULTS_PATH):
    test_cases = _load_json(TEST_CASES_PATH)
    raw_results = _load_json(results_path)

    summary = {}
    for system_name, system_results in raw_results.items():
        scores = []
        by_test_id = {item["test_id"]: item for item in system_results}
        for test_case in test_cases:
            score_row = by_test_id[test_case["id"]]
            scores.append(_score_run(test_case, score_row))
        summary[system_name] = {
            "avg_5pt_score": round(sum(scores) / len(scores), 3),
            "score_1_to_10000": _final_score_10000(scores),
            "per_test_scores": [round(s, 3) for s in scores],
        }

    ours = summary.get("must_academic_agent", {}).get("score_1_to_10000", 0)
    baseline = summary.get("cursor_default_claude", {}).get("score_1_to_10000", 0)
    delta = ours - baseline
    improvement_pct = round(((ours - baseline) / baseline) * 100, 2) if baseline else None

    print(json.dumps(summary, indent=2))
    print("\nComparison")
    print(f"- Delta score: {delta}")
    if improvement_pct is not None:
        print(f"- Improvement: {improvement_pct}%")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate benchmark scores to 1..10000 scale.")
    parser.add_argument(
        "--results",
        default=str(RESULTS_PATH),
        help="Path to benchmark results JSON (default: benchmarks/results_template.json)",
    )
    args = parser.parse_args()
    evaluate(Path(args.results))
