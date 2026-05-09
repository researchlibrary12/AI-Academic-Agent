# AI Academic Agent

An AI-native academic platform for students that combines:
- personalized performance analytics,
- exam timetable + prep planning,
- dynamic quiz generation + auto-marking,
- retrieval-augmented academic support chat.

It is designed as a practical, submission-ready project for AI-first product/engineering roles and can be run locally with Cursor.

## What The System Does

### 1) Personalized Coach
- Auto-loads student academic profile and seeded school-record-style results.
- Shows top summary: `Course`, `Year`, and `Risk Rate`.
- Lets student filter by:
  - module,
  - assessment (test/exam/assignment),
  - all modules/all assessments.
- Produces:
  - risk analysis by topic,
  - weekly study plan,
  - actionable insights explaining why topics need focus.

### 2) Smart Practice
- Generates dynamic quizzes with:
  - module selection,
  - topic selection,
  - difficulty selection.
- Enforces 10-question flow.
- Shows submit button only after all questions are answered.
- Auto-marks quiz and returns:
  - score,
  - percentage,
  - mastery score,
  - recommendation.

### 3) Exam Timetable + Exam Prep
- Displays upcoming exams (module, date, time, venue).
- Lets student select an exam and generate a day-by-day prep plan.

### 4) Floating Academic Chat
- Bottom-right launcher icon opens full chat panel.
- Asks student name first and addresses student by name.
- Supports in-chat file upload using `+`.
- Includes typing state ("Assistant is typing...").
- Uses recent student results in chat context for more relevant responses.

### 5) Safety Guardrails
- Chat is configured with safety constraints:
  - does not provide definitive financial/legal/medical advice,
  - refuses final-exam leak requests and provides practice alternatives,
  - supports non-course questions with safe responses,
  - follows POPIA-aligned privacy principles for user data handling.

---

## Architecture Overview

### Frontend (`frontend/`)
- Next.js 15 (App Router) + TailwindCSS
- Main student workspace:
  - `PersonalizedCoach`
  - `SmartPractice`
  - `ExamPrepTimetable`
  - `FloatingChat`

### Backend (`backend/`)
- FastAPI API layer with modular routers:
  - `routers/phase2.py` for performance analytics and profile-driven planning
  - `routers/phase3.py` for quiz + exam timetable/prep
  - `routers/rag.py` for retrieval QA
  - `routers/agents.py` for chat routing
- Provider abstraction:
  - OpenAI / Anthropic via `services/model_gateway.py`
- Vector retrieval:
  - ChromaDB via `vector_db/chroma_client.py`

### Data Layer
- Profile and results flows currently use local persistent JSON-backed storage for rapid local testing.
- Results are structured with:
  - module,
  - assessment type,
  - assessment name,
  - topic,
  - score/max score,
  - date.
- This structure is compatible with migration to PostgreSQL tables later.

---

## Tech Stack

- Frontend: Next.js 15, React 18, TypeScript, TailwindCSS
- Backend: FastAPI, Pydantic, LangChain/LangGraph components
- Auth: Clerk (configured in current implementation)
- Vector Store: ChromaDB
- LLM Providers: OpenAI and Anthropic (switchable by env)

---

## Repository Structure

- `frontend/` - UI and interactive student experience
- `backend/` - API, agents, RAG, analytics, quiz/timetable logic
- `benchmarks/` - scoring and benchmark toolkit
- `docs/` - architecture and implementation documents
- `knowledge_base/` - source data directories
- `.cursorrules` - Cursor-specific project guidance

---

## Environment Variables

Create root `.env` from `.env.example` and configure:

- Backend:
  - `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`
  - `DATABASE_URL` (optional for future DB extension)
  - `CLERK_JWKS_URL`, `JWT_ISSUER` (for token verification)
- Frontend:
  - `NEXT_PUBLIC_API_BASE_URL`
  - `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`
  - `CLERK_SECRET_KEY` in `frontend/.env.local`

Recommended frontend `.env.local`:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_AUTH_PROVIDER=clerk
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=<your_clerk_publishable_key>
CLERK_SECRET_KEY=<your_clerk_secret_key>
```

---

## Local Setup

## Requirements (What to Install First)

Before running the project, install:

- **Node.js**: v20+ (includes `npm`)
- **Python**: v3.11+ (project tested on 3.13)
- **Git**: latest stable
- **Clerk account**: for authentication keys
- **LLM provider key**: OpenAI and/or Anthropic

Quick version checks:

```bash
node -v
npm -v
python3 --version
git --version
```

If you need to install tools on macOS (Homebrew):

```bash
brew install node python git
```

Then configure environment files:

```bash
cp .env.example .env
touch frontend/.env.local
```

Fill in your real values in:

- `.env` (backend secrets and provider config)
- `frontend/.env.local` (Clerk publishable/secret keys and frontend API base URL)

---

## 1) Backend

```bash
cd backend
/Library/Frameworks/Python.framework/Versions/3.13/bin/python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 2) Frontend

```bash
cd frontend
npm install
npm run dev
```

Open:
- App: `http://localhost:3000/dashboard`
- API docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

---

## Core API Surface (Current)

### Personalized Coach
- `GET /api/v1/phase2/summary`
- `GET /api/v1/phase2/modules`
- `GET /api/v1/phase2/results?module=...&assessment=...`
- `GET /api/v1/phase2/analyze?module=...&assessment=...`
- `POST /api/v1/phase2/plan?module=...&assessment=...`
- `GET /api/v1/phase2/insights?module=...&assessment=...`

### Smart Practice
- `POST /api/v1/phase3/quiz`
- `POST /api/v1/phase3/quiz/submit`

### Exam Prep
- `GET /api/v1/phase3/exam-timetable`
- `POST /api/v1/phase3/exam-prep-plan`

### Chat / Agents
- `POST /api/v1/agents/route`

### RAG / Documents
- `POST /api/v1/documents/upload`
- `POST /api/v1/rag/query`

---

## User Flow (Recommended Demo)

1. Sign in.
2. Open dashboard.
3. In Personalized Coach:
   - select module + assessment filter,
   - view results,
   - run risk analysis,
   - load insights,
   - generate weekly plan.
4. In Smart Practice:
   - generate quiz,
   - answer all 10,
   - submit and review marking.
5. In Exam Timetable:
   - select exam,
   - generate prep plan.
6. In chat:
   - provide name,
   - ask targeted questions,
   - optionally upload document with `+`.

---

## Benchmark & Submission Assets

- Requirement mapping: `docs/quest_submission.md`
- Benchmark instructions: `benchmarks/README.md`
- Evaluator script: `benchmarks/evaluate_agent.py`
- Cursor config: `.cursorrules`

Run benchmark evaluator:

```bash
python benchmarks/evaluate_agent.py
```

---

## Quest Requirement Compliance (1 to 7)

### 1) Build Your Own Agent

- This repository is the custom agent implementation (`AI Academic Agent`).
- Public sharing target: publish this repository on GitHub.
- If public publishing is delayed, provide a ZIP archive of this repository as fallback.
- After publishing, add your GitHub URL in this section before submission.

### 2) Cursor-Based Setup

- Cursor-ready configuration is included via `.cursorrules`.
- The project has clear local run instructions for backend and frontend.
- Architecture and module boundaries are documented for easy Cursor onboarding.

### 3) Security Requirements

- Secrets are externalized to environment variables.
- Root `.env` and `frontend/.env.local` are git-ignored.
- `.env.example` contains placeholder values only.
- Do not commit real API keys, tokens, credentials, or student-identifying data.

### 4) Performance Metrics (Score 1 to 10,000)

Custom scoring formula:

- `test_score = sum(dimension_score * dimension_weight) / sum(weights)`
- `final_score_1_to_10000 = round((avg_test_score / 5.0) * 10000)`

Evaluation dimensions:

- relevance
- accuracy
- actionability
- clarity
- latency

Measurement process:

1. Run the same test prompts from `benchmarks/test_cases.json`.
2. Score each system with the same weighted rubric.
3. Save results in `benchmarks/results_template.json`.
4. Run `python benchmarks/evaluate_agent.py`.

### 5) Benchmark vs Default Cursor Claude

Sample benchmark output from current template data:

- `must_academic_agent`: **8663 / 10000**
- `cursor_default_claude`: **7720 / 10000**
- Delta: **+943**
- Improvement: **+12.22%**

Side-by-side per test:

- `T1` (5-day exam plan): 4.420 vs 3.920
- `T2` (derivatives explanation): 4.350 vs 3.870
- `T3` (quiz generation): 4.305 vs 3.865
- `T4` (deadline schedule): 4.250 vs 3.785

### 6) Problem Specialization

Specialization:

- Academic performance intelligence and intervention support for students.

Why this problem:

- Students need actionable guidance (what to study, when, and why), not generic responses.
- Institutions benefit from early risk detection and measurable support pathways.

Why this is priority #1:

- Early academic underperformance compounds quickly.
- Timely intervention can improve retention, outcomes, and confidence.

### 7) Documentation

Documentation coverage:

- Setup and usage: `README.md`
- Architecture: `docs/system_architecture.md`, `docs/api_architecture.md`
- Workflow design: `docs/multi_agent_workflow.md`
- Submission mapping: `docs/quest_submission.md`
- Benchmark method: `benchmarks/README.md`

---

## Known Limitations / Next Steps

- Results store is local JSON-backed for speed; migrate to PostgreSQL for production durability and relational queries.
- Add role-based admin/lecturer dashboards with cohort analytics.
- Add quiz attempt history and richer per-question explanations.
- Add exportable student reports (PDF).
- Add integration with real institutional systems (LMS/SIS).

---

## Troubleshooting of tool

- `Missing publishableKey/secretKey`:
  - ensure values exist in `frontend/.env.local`
  - restart frontend server.
- `Failed to fetch` from frontend:
  - ensure backend is running on port 8000
  - check `NEXT_PUBLIC_API_BASE_URL`.
- Auth errors (`401/500`):
  - verify `JWT_ISSUER` and `CLERK_JWKS_URL`
  - restart backend after env changes.
- Frontend stale build errors:
  - stop dev server,
  - run `rm -rf frontend/.next`,
  - restart `npm run dev`.
