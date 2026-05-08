import uuid
import json
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from services.auth import get_current_user
from services.model_gateway import model_gateway

router = APIRouter()


class QuizRequest(BaseModel):
    module: str
    topic: str
    difficulty: str = Field(default="medium")


class QuizQuestion(BaseModel):
    id: str
    question: str
    options: list[str]


class QuizSubmission(BaseModel):
    quiz_id: str
    answers: dict[str, str]


class ExamPrepRequest(BaseModel):
    exam_id: str
    available_hours_per_day: int = Field(default=2, ge=1, le=12)


_quiz_bank: dict[str, dict[str, object]] = {}
_exam_timetable = [
    {
        "exam_id": "ds-midterm",
        "module": "Data Structures",
        "exam_name": "Midterm",
        "date": "2026-06-10",
        "time": "09:00",
        "venue": "Hall A",
        "topics": ["Arrays", "Linked Lists", "Trees", "Graphs"],
    },
    {
        "exam_id": "db-final",
        "module": "Databases",
        "exam_name": "Final Exam",
        "date": "2026-06-14",
        "time": "14:00",
        "venue": "Hall C",
        "topics": ["Normalization", "SQL Joins", "Transactions", "Indexing"],
    },
    {
        "exam_id": "algo-test",
        "module": "Algorithms",
        "exam_name": "Test 2",
        "date": "2026-06-18",
        "time": "11:00",
        "venue": "Lab 2",
        "topics": ["Sorting", "Greedy", "Dynamic Programming", "Complexity Analysis"],
    },
]


def _difficulty_multiplier(level: str) -> float:
    if level == "easy":
        return 0.8
    if level == "hard":
        return 1.2
    return 1.0


def _parse_quiz_json(raw_text: str) -> list[dict[str, object]]:
    text = raw_text.strip()
    # Support responses wrapped in markdown code fences.
    if "```" in text:
        start = text.find("```")
        end = text.rfind("```")
        if start != -1 and end != -1 and end > start:
            fenced = text[start + 3 : end].strip()
            if fenced.startswith("json"):
                fenced = fenced[4:].strip()
            text = fenced
    data = json.loads(text)
    questions = data.get("questions", []) if isinstance(data, dict) else []
    normalized: list[dict[str, object]] = []
    for row in questions:
        if not isinstance(row, dict):
            continue
        question = str(row.get("question", "")).strip()
        options = row.get("options", [])
        answer = str(row.get("answer", "")).strip().upper()
        if not question or not isinstance(options, list) or len(options) != 4:
            continue
        cleaned_options = [str(opt).strip() for opt in options]
        if answer not in {"A", "B", "C", "D"}:
            continue
        normalized.append({"question": question, "options": cleaned_options, "answer": answer})
    return normalized


@router.get("/next-actions")
async def next_actions(_: dict[str, str] = Depends(get_current_user)) -> dict[str, object]:
    return {
        "actions": [
            "Review one weak topic for 30 minutes",
            "Solve a 10-question practice set",
            "Write a 5-bullet summary of what you learned",
            "Schedule tomorrow's study block before ending the session",
        ]
    }


@router.get("/exam-timetable")
async def exam_timetable(_: dict[str, str] = Depends(get_current_user)) -> dict[str, object]:
    return {"exams": _exam_timetable}


@router.post("/exam-prep-plan")
async def exam_prep_plan(
    payload: ExamPrepRequest,
    _: dict[str, str] = Depends(get_current_user),
) -> dict[str, object]:
    selected = next((item for item in _exam_timetable if item["exam_id"] == payload.exam_id), None)
    if not selected:
        return {"detail": "Exam not found", "plan": []}

    topics = selected["topics"]
    hours = payload.available_hours_per_day
    plan = [
        {
            "day": idx + 1,
            "topic": topic,
            "hours": hours,
            "tasks": [
                f"Review key theory for {topic}",
                f"Solve 8 timed problems on {topic}",
                f"Write a short summary and common mistakes for {topic}",
            ],
        }
        for idx, topic in enumerate(topics)
    ]
    return {
        "exam": selected,
        "daily_hours": hours,
        "plan": plan,
        "advice": "Focus on weak topics first, then run one full timed mock before exam day.",
    }


@router.post("/quiz")
async def generate_quiz(
    payload: QuizRequest,
    user: dict[str, str] = Depends(get_current_user),
) -> dict[str, object]:
    prompt = (
        "Generate an academic multiple-choice quiz and return STRICT JSON only.\n"
        "Output format:\n"
        "{\n"
        '  "questions": [\n'
        '    {"question": "...", "options": ["A) ...", "B) ...", "C) ...", "D) ..."], "answer": "A"}\n'
        "  ]\n"
        "}\n"
        "Rules:\n"
        "- Exactly 10 questions\n"
        "- Module and topic specific\n"
        "- Difficulty must match requested level\n"
        "- answer must be one of A/B/C/D\n"
        f"Module: {payload.module}\n"
        f"Topic: {payload.topic}\n"
        f"Difficulty: {payload.difficulty}\n"
    )

    parsed_questions: list[dict[str, object]] = []
    try:
        llm_output = await model_gateway.generate(prompt)
        parsed_questions = _parse_quiz_json(llm_output)
    except Exception:
        parsed_questions = []

    # Safe fallback if parsing/provider fails.
    if len(parsed_questions) < 10:
        parsed_questions = []
        for idx in range(10):
            parsed_questions.append(
                {
                    "question": f"{payload.topic}: Concept check {idx + 1}",
                    "options": [
                        f"A) Correct concept for {payload.topic} #{idx + 1}",
                        f"B) Misconception for {payload.topic} #{idx + 1}",
                        f"C) Partial concept for {payload.topic} #{idx + 1}",
                        f"D) Unrelated concept for {payload.topic} #{idx + 1}",
                    ],
                    "answer": "A",
                }
            )

    questions: list[dict[str, object]] = []
    answer_key: dict[str, str] = {}
    for row in parsed_questions[:10]:
        qid = str(uuid.uuid4())
        questions.append({"id": qid, "question": row["question"], "options": row["options"]})
        answer_key[qid] = str(row["answer"])

    quiz_id = str(uuid.uuid4())
    _quiz_bank[quiz_id] = {
        "user_id": user["user_id"],
        "module": payload.module,
        "topic": payload.topic,
        "difficulty": payload.difficulty,
        "answer_key": answer_key,
    }
    return {"quiz_id": quiz_id, "module": payload.module, "topic": payload.topic, "questions": questions}


@router.post("/quiz/submit")
async def submit_quiz(
    payload: QuizSubmission,
    user: dict[str, str] = Depends(get_current_user),
) -> dict[str, object]:
    quiz = _quiz_bank.get(payload.quiz_id)
    if not quiz or quiz.get("user_id") != user["user_id"]:
        return {"detail": "Quiz not found", "score": 0, "total": 0, "percentage": 0}

    answer_key = quiz["answer_key"]
    total = len(answer_key)
    correct = 0
    feedback: list[dict[str, object]] = []
    for qid, expected in answer_key.items():
        selected = payload.answers.get(qid, "").upper()
        is_correct = selected == expected
        if is_correct:
            correct += 1
        feedback.append(
            {
                "question_id": qid,
                "selected": selected or "N/A",
                "correct_answer": expected,
                "is_correct": is_correct,
            }
        )

    percentage = round((correct / total) * 100, 2) if total else 0
    mastery_score = round(min(100, percentage * _difficulty_multiplier(str(quiz["difficulty"]))), 2)
    recommendation = (
        "Strong performance. Move to higher difficulty."
        if percentage >= 80
        else "Review weak questions and retry with focused practice."
    )

    return {
        "module": quiz["module"],
        "topic": quiz["topic"],
        "score": correct,
        "total": total,
        "percentage": percentage,
        "mastery_score": mastery_score,
        "recommendation": recommendation,
        "feedback": feedback,
    }
