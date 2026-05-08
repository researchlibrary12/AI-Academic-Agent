import csv
import json
from typing import Literal
from io import StringIO
import random

from fastapi import APIRouter, Depends, File, UploadFile
from pydantic import BaseModel, Field

from database.assessment_store import add_results, get_results_for_user
from services.auth import get_current_user

router = APIRouter()


class LearnerProfileIn(BaseModel):
    program: str
    year: int = Field(ge=1, le=8)
    goals: list[str] = Field(default_factory=list)
    weak_topics: list[str] = Field(default_factory=list)
    study_style: Literal["visual", "reading", "practice", "mixed"] = "mixed"
    available_hours_per_week: int = Field(default=10, ge=1, le=80)
    target_gpa: float = Field(default=3.5, ge=0.0, le=5.0)
    attendance_rate: float = Field(default=85.0, ge=0.0, le=100.0)
    preferred_session_minutes: int = Field(default=45, ge=15, le=180)


class LearnerProfileOut(LearnerProfileIn):
    user_id: str


class GradeRecord(BaseModel):
    module: str
    assessment_type: Literal["test", "exam", "assignment"]
    assessment_name: str
    topic: str
    score: float
    max_score: float
    assessment_date: str | None = None


class PlannerRequest(BaseModel):
    available_hours_per_week: int = Field(default=10, ge=1, le=80)


_profiles: dict[str, LearnerProfileOut] = {}
_performance_history: dict[str, list[GradeRecord]] = {}
_demo_profiles = [
    {"program": "Computer Science", "year": 2, "study_style": "practice", "available_hours_per_week": 12},
    {"program": "Software Engineering", "year": 3, "study_style": "mixed", "available_hours_per_week": 10},
    {"program": "Information Systems", "year": 1, "study_style": "reading", "available_hours_per_week": 9},
    {"program": "Data Science", "year": 4, "study_style": "visual", "available_hours_per_week": 14},
    {"program": "Computer Engineering", "year": 2, "study_style": "practice", "available_hours_per_week": 11},
    {"program": "Business IT", "year": 3, "study_style": "mixed", "available_hours_per_week": 8},
]


def _topic_percentage(record: GradeRecord) -> float:
    denom = record.max_score if record.max_score > 0 else 1.0
    return round((record.score / denom) * 100, 2)


def _priority_for_percentage(pct: float) -> str:
    if pct < 50:
        return "high"
    if pct < 70:
        return "medium"
    return "low"


def _build_risk_summary(records: list[GradeRecord]) -> list[dict[str, object]]:
    if not records:
        return []

    by_topic: dict[str, list[float]] = {}
    for row in records:
        by_topic.setdefault(row.topic, []).append(_topic_percentage(row))

    summary: list[dict[str, object]] = []
    for topic, percentages in by_topic.items():
        avg_pct = round(sum(percentages) / len(percentages), 2)
        summary.append(
            {
                "topic": topic,
                "average_percentage": avg_pct,
                "risk_level": _priority_for_percentage(avg_pct),
                "attempts": len(percentages),
            }
        )
    return sorted(summary, key=lambda item: item["average_percentage"])  # weakest first


def _compute_overall_risk(profile: LearnerProfileOut | None, risk_summary: list[dict[str, object]]) -> dict[str, object]:
    if not risk_summary:
        return {"overall_risk": "medium", "confidence": "low", "driver": "insufficient grade data"}

    avg = sum(float(item["average_percentage"]) for item in risk_summary) / len(risk_summary)
    attendance_penalty = 0.0
    if profile:
        attendance_penalty = max(0.0, (75.0 - profile.attendance_rate) * 0.2)
    adjusted = avg - attendance_penalty
    if adjusted < 50:
        risk = "high"
    elif adjusted < 70:
        risk = "medium"
    else:
        risk = "low"
    return {"overall_risk": risk, "confidence": "medium", "driver": f"avg score {round(adjusted,2)}"}


def _ensure_demo_profile(user_id: str) -> LearnerProfileOut:
    existing = _profiles.get(user_id)
    if existing:
        return existing
    selected = random.choice(_demo_profiles)
    profile = LearnerProfileOut(
        user_id=user_id,
        program=selected["program"],
        year=selected["year"],
        goals=[],
        weak_topics=[],
        study_style=selected["study_style"],  # type: ignore[arg-type]
        available_hours_per_week=selected["available_hours_per_week"],
        target_gpa=3.5,
        attendance_rate=85.0,
        preferred_session_minutes=45,
    )
    _profiles[user_id] = profile
    return profile


def _generate_demo_results(user_id: str) -> list[dict[str, object]]:
    rng = random.Random(user_id)
    modules = {
        "Data Structures": ["Arrays", "Linked Lists", "Trees", "Graphs"],
        "Databases": ["Normalization", "SQL Joins", "Transactions", "Indexing"],
        "Algorithms": ["Sorting", "Greedy", "Dynamic Programming", "Complexity"],
        "Calculus": ["Limits", "Derivatives", "Integrals", "Series"],
        "Operating Systems": ["Processes", "Threads", "Scheduling", "Memory"],
        "Networks": ["OSI Model", "Routing", "TCP", "Security"],
    }
    assessment_types = [("test", "Test"), ("exam", "Exam"), ("assignment", "Assignment")]
    rows: list[dict[str, object]] = []
    for module, topics in modules.items():
        for idx, topic in enumerate(topics, start=1):
            for a_type, a_name in assessment_types:
                score = max(20, min(95, int(rng.gauss(60, 15))))
                rows.append(
                    {
                        "user_id": user_id,
                        "module": module,
                        "assessment_type": a_type,
                        "assessment_name": f"{a_name} {idx}",
                        "topic": topic,
                        "score": score,
                        "max_score": 100,
                        "assessment_date": f"2026-0{rng.randint(1,6)}-{rng.randint(10,28)}",
                    }
                )
    return rows


def _ensure_demo_data(user_id: str) -> None:
    _ensure_demo_profile(user_id)
    existing = get_results_for_user(user_id)
    if existing:
        return
    add_results(_generate_demo_results(user_id))


@router.get("/profile")
async def get_profile(user: dict[str, str] = Depends(get_current_user)) -> dict[str, object]:
    user_id = user["user_id"]
    profile = _ensure_demo_profile(user_id)
    if not profile:
        return {"profile": None, "message": "Profile not set yet"}
    return {"profile": profile.model_dump()}


@router.put("/profile")
async def upsert_profile(
    payload: LearnerProfileIn,
    user: dict[str, str] = Depends(get_current_user),
) -> dict[str, object]:
    user_id = user["user_id"]
    profile = LearnerProfileOut(user_id=user_id, **payload.model_dump())
    _profiles[user_id] = profile
    return {"profile": profile.model_dump(), "message": "Profile saved"}


@router.post("/performance")
async def submit_performance(
    records: list[GradeRecord],
    user: dict[str, str] = Depends(get_current_user),
) -> dict[str, object]:
    user_id = user["user_id"]
    payload_rows = [{"user_id": user_id, **row.model_dump()} for row in records]
    total_rows = add_results(payload_rows)
    history = [GradeRecord(**row) for row in get_results_for_user(user_id)]
    _performance_history[user_id] = history
    risk_summary = _build_risk_summary(history)
    return {"risk_summary": risk_summary, "total_records": len(history), "database_rows": total_rows}


def _filter_records(
    records: list[GradeRecord],
    module: str | None,
    assessment_name: str | None,
) -> list[GradeRecord]:
    filtered = records
    if module and module.lower() != "all":
        filtered = [row for row in filtered if row.module == module]
    if assessment_name and assessment_name.lower() != "all":
        filtered = [row for row in filtered if row.assessment_name == assessment_name]
    return filtered


def _normalize_assessment_type(value: str) -> Literal["test", "exam", "assignment"]:
    lower = value.strip().lower()
    if lower in {"test", "quiz"}:
        return "test"
    if lower in {"exam", "midterm", "final"}:
        return "exam"
    return "assignment"


def _parse_result_rows(raw_text: str) -> list[GradeRecord]:
    text = raw_text.strip()
    if not text:
        return []

    rows: list[dict[str, object]] = []
    if text.startswith("["):
        data = json.loads(text)
        if isinstance(data, list):
            rows = [r for r in data if isinstance(r, dict)]
    else:
        reader = csv.DictReader(StringIO(text))
        rows = [dict(r) for r in reader]

    parsed: list[GradeRecord] = []
    for row in rows:
        try:
            parsed.append(
                GradeRecord(
                    module=str(row.get("module", "General")),
                    assessment_type=_normalize_assessment_type(str(row.get("assessment_type", "test"))),
                    assessment_name=str(row.get("assessment_name", "Assessment")),
                    topic=str(row.get("topic", "General")),
                    score=float(row.get("score", 0)),
                    max_score=float(row.get("max_score", 100)),
                    assessment_date=str(row.get("assessment_date", "")) or None,
                )
            )
        except Exception:
            continue
    return parsed


@router.get("/modules")
async def list_modules(user: dict[str, str] = Depends(get_current_user)) -> dict[str, object]:
    user_id = user["user_id"]
    _ensure_demo_data(user_id)
    rows = [GradeRecord(**row) for row in get_results_for_user(user_id)]
    modules = sorted({row.module for row in rows})
    by_module: dict[str, list[str]] = {}
    for module in modules:
        assessments = sorted(
            {
                f"{row.assessment_name} ({row.assessment_type})"
                for row in rows
                if row.module == module
            }
        )
        by_module[module] = assessments
    return {"modules": modules, "assessments_by_module": by_module}


@router.get("/results")
async def list_results(
    module: str = "all",
    assessment: str = "all",
    user: dict[str, str] = Depends(get_current_user),
) -> dict[str, object]:
    user_id = user["user_id"]
    _ensure_demo_data(user_id)
    rows = [GradeRecord(**row) for row in get_results_for_user(user_id)]
    assessment_name = assessment.split(" (")[0] if assessment.lower() != "all" else "all"
    filtered = _filter_records(rows, module, assessment_name)
    return {"results": [row.model_dump() for row in filtered], "count": len(filtered)}


@router.post("/seed-sample-results")
async def seed_sample_results(user: dict[str, str] = Depends(get_current_user)) -> dict[str, object]:
    user_id = user["user_id"]
    existing = get_results_for_user(user_id)
    if existing:
        return {"message": "Sample already exists", "inserted": 0}
    sample = [
        {
            "user_id": user_id,
            "module": "Data Structures",
            "assessment_type": "test",
            "assessment_name": "Test 1",
            "topic": "Arrays",
            "score": 42,
            "max_score": 100,
            "assessment_date": "2026-05-01",
        },
        {
            "user_id": user_id,
            "module": "Data Structures",
            "assessment_type": "assignment",
            "assessment_name": "Assignment 1",
            "topic": "Trees",
            "score": 58,
            "max_score": 100,
            "assessment_date": "2026-05-03",
        },
        {
            "user_id": user_id,
            "module": "Databases",
            "assessment_type": "exam",
            "assessment_name": "Midterm",
            "topic": "Normalization",
            "score": 37,
            "max_score": 100,
            "assessment_date": "2026-05-05",
        },
        {
            "user_id": user_id,
            "module": "Databases",
            "assessment_type": "test",
            "assessment_name": "Quiz 2",
            "topic": "SQL Joins",
            "score": 49,
            "max_score": 100,
            "assessment_date": "2026-05-06",
        },
    ]
    add_results(sample)
    return {"message": "Sample results inserted", "inserted": len(sample)}


@router.get("/analyze")
async def analyze_results(
    module: str = "all",
    assessment: str = "all",
    user: dict[str, str] = Depends(get_current_user),
) -> dict[str, object]:
    user_id = user["user_id"]
    _ensure_demo_data(user_id)
    rows = [GradeRecord(**row) for row in get_results_for_user(user_id)]
    assessment_name = assessment.split(" (")[0] if assessment.lower() != "all" else "all"
    filtered = _filter_records(rows, module, assessment_name)
    summary = _build_risk_summary(filtered)
    why = [
        {
            "topic": row["topic"],
            "why": f"Average score is {row['average_percentage']}%, which is {row['risk_level']} risk."
        }
        for row in summary
    ]
    return {"risk_summary": summary, "why_topics_need_focus": why, "count": len(filtered)}


@router.post("/plan")
async def generate_personalized_plan(
    payload: PlannerRequest,
    user: dict[str, str] = Depends(get_current_user),
    module: str = "all",
    assessment: str = "all",
) -> dict[str, object]:
    user_id = user["user_id"]
    _ensure_demo_data(user_id)
    profile = _profiles.get(user_id)
    history = [GradeRecord(**row) for row in get_results_for_user(user_id)]
    assessment_name = assessment.split(" (")[0] if assessment.lower() != "all" else "all"
    history = _filter_records(history, module, assessment_name)
    risk_summary = _build_risk_summary(history)

    weak_topics = [row["topic"] for row in risk_summary if row["risk_level"] in {"high", "medium"}][:3]
    if not weak_topics and profile:
        weak_topics = profile.weak_topics[:3]
    if not weak_topics:
        weak_topics = ["Revision"]

    total_hours = payload.available_hours_per_week
    per_topic_hours = max(1, total_hours // len(weak_topics))

    weekly_plan = [
        {
            "topic": topic,
            "hours": per_topic_hours,
            "tasks": [
                f"Review core concepts in {topic}",
                f"Solve 10 focused practice questions for {topic}",
                f"Self-check and summarize mistakes in {topic}",
            ],
        }
        for topic in weak_topics
    ]

    return {
        "study_style": profile.study_style if profile else "mixed",
        "session_minutes": profile.preferred_session_minutes if profile else 45,
        "focus_topics": weak_topics,
        "total_hours": total_hours,
        "weekly_plan": weekly_plan,
    }


@router.get("/insights")
async def personalized_insights(
    user: dict[str, str] = Depends(get_current_user),
    module: str = "all",
    assessment: str = "all",
) -> dict[str, object]:
    user_id = user["user_id"]
    _ensure_demo_data(user_id)
    profile = _profiles.get(user_id)
    history = [GradeRecord(**row) for row in get_results_for_user(user_id)]
    assessment_name = assessment.split(" (")[0] if assessment.lower() != "all" else "all"
    history = _filter_records(history, module, assessment_name)
    risk_summary = _build_risk_summary(history)
    risk_state = _compute_overall_risk(profile, risk_summary)
    return {
        "profile": profile.model_dump() if profile else None,
        "risk": risk_state,
        "risk_summary": risk_summary[:5],
        "next_best_actions": [
            "Start with the weakest topic first for your next session",
            "Use active recall for 15 minutes before practice questions",
            "Track one measurable outcome after each study block",
        ],
    }


@router.get("/summary")
async def summary(user: dict[str, str] = Depends(get_current_user)) -> dict[str, object]:
    user_id = user["user_id"]
    _ensure_demo_data(user_id)
    profile = _profiles.get(user_id)
    rows = [GradeRecord(**row) for row in get_results_for_user(user_id)]
    risk_summary = _build_risk_summary(rows)
    avg_score = sum(float(item["average_percentage"]) for item in risk_summary) / len(risk_summary) if risk_summary else 50.0
    risk_rate = round(max(0.0, min(100.0, 100.0 - avg_score)), 2)
    return {
        "course": profile.program if profile else "Unknown",
        "year": profile.year if profile else 1,
        "risk_rate": risk_rate,
        "overall_risk": _compute_overall_risk(profile, risk_summary)["overall_risk"],
    }


@router.post("/upload-results")
async def upload_results_file(
    file: UploadFile = File(...),
    user: dict[str, str] = Depends(get_current_user),
) -> dict[str, object]:
    user_id = user["user_id"]
    raw = (await file.read()).decode("utf-8", errors="ignore")
    parsed = _parse_result_rows(raw)
    rows = [{"user_id": user_id, **record.model_dump()} for record in parsed]
    total = add_results(rows) if rows else len(get_results_for_user(user_id))
    return {"inserted": len(rows), "database_rows": total}
