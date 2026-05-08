from pydantic import BaseModel
from fastapi import APIRouter, Depends

from analytics.performance import detect_weak_topics
from services.auth import get_current_user

router = APIRouter()


class GradeRecord(BaseModel):
    topic: str
    score: float
    max_score: float


@router.post("/weak-topics")
async def weak_topics(
    records: list[GradeRecord],
    _: dict[str, str] = Depends(get_current_user),
) -> dict[str, object]:
    normalized = [r.model_dump() for r in records]
    return {"weak_topics": detect_weak_topics(normalized)}
