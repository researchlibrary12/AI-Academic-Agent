# Benchmark Kit (Quest Requirement)

This folder helps you satisfy two quest items:

1. Create your own performance metric (1 to 10,000)
2. Compare your agent with default Cursor Claude

## Files

- `test_cases.json`: academic prompts and weighted evaluation dimensions
- `results_template.json`: example scores for both systems (replace with your real data)
- `evaluate_agent.py`: computes final score and side-by-side delta
- `live_benchmark.py`: runs real benchmark execution and rubric scoring
- `baseline_cursor_claude_template.json`: fill with real Cursor Claude outputs for fair comparison

## Scoring Formula

For each test:

`test_score = sum(dimension_score * dimension_weight) / sum(weights)`

where each `dimension_score` is from 1.0 to 5.0.

Final score:

`final_10000 = round((avg_test_score / 5.0) * 10000)`

This ensures output always lands on the required 1 to 10,000 scale.

## Run

```bash
python benchmarks/evaluate_agent.py
```

## Real (Non-Dummy) Run

This is the real execution path (not static demo numbers):

1. Ensure backend env is configured (`OPENAI_API_KEY` or `ANTHROPIC_API_KEY`).
2. Run live agent benchmark:

```bash
python benchmarks/live_benchmark.py
```

This generates `benchmarks/results_real.json` from actual agent responses and measured latency.

3. Compute the 1..10000 score from live results:

```bash
python benchmarks/evaluate_agent.py --results benchmarks/results_real.json
```

4. For baseline comparison against default Cursor Claude:
   - put real Claude outputs in `benchmarks/baseline_cursor_claude_template.json`
   - then run:

```bash
python benchmarks/live_benchmark.py --include-baseline
python benchmarks/evaluate_agent.py --results benchmarks/results_real.json
```

## How to Use with Real Data

1. Run `live_benchmark.py` to generate live scores for your agent.
2. Add real default Cursor Claude responses into baseline template.
3. Re-run `live_benchmark.py --include-baseline` for side-by-side scored data.
4. Run evaluator with `--results benchmarks/results_real.json` and copy output into your report.
