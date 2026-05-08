# Quest Submission Guide (FDE/APO)

This document maps this repository to every quest requirement in the job post.

## 1) Build Your Own Agent

- This repository is your own academic-specialized AI agent system.
- Share this repo URL publicly or provide a ZIP.

## 2) Cursor-Based Setup

- Cursor config included via `.cursorrules`.
- Project structure and startup steps are in `README.md`.

## 3) Security Requirements

- Use `.env.example` for configuration placeholders.
- Never commit real credentials, API keys, or student data.
- Before submission, run a final secret scan and verify no sensitive data exists.

## 4) Performance Metrics (1 to 10,000)

- Metric toolkit is in `benchmarks/`.
- Formula:
  - Per test: weighted average across relevance, accuracy, actionability, clarity, latency.
  - Final: `round((avg_test_score / 5.0) * 10000)`.

## 5) Benchmark vs Default Cursor Claude

- Use `benchmarks/test_cases.json` for shared test prompts.
- Score both systems in `benchmarks/results_template.json`.
- Run:

```bash
python benchmarks/evaluate_agent.py
```

- Copy output into your application package.

## 6) Problem Specialization

Primary problem solved:
- Academic performance intelligence for students and institutions (planning, tutoring, weak-topic detection, assessments, and recommendations).

Why this problem:
- High impact on student outcomes.
- Continuous feedback loops are ideal for AI-agent orchestration.
- Institutions need actionable insights, not just generic chat.

Why it is #1 priority:
- Academic underperformance compounds over time; early intervention creates outsized value.
- This domain benefits from measurable KPIs (grades, completion rates, attendance, risk prediction).

## 7) Documentation

- Core docs:
  - `README.md`
  - `docs/system_architecture.md`
  - `docs/multi_agent_workflow.md`
  - `docs/phase1_runbook.md`
  - `benchmarks/README.md`

## Submission Checklist

- [ ] Public GitHub repo or ZIP prepared
- [ ] Loom video showing UI + terminal logs + verbal explanation
- [ ] Benchmark numbers generated and included
- [ ] Self-review written (1-page summary + full appendix)
- [ ] Secrets removed and validated
