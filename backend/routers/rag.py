from pydantic import BaseModel
from fastapi import APIRouter, Depends

from rag.pipeline import answer_with_rag
from services.auth import get_current_user

router = APIRouter()


class RagQuery(BaseModel):
    question: str
    metadata_filter: dict[str, str] | None = None


@router.post("/query")
async def query_rag(
    payload: RagQuery,
    _: dict[str, str] = Depends(get_current_user),
) -> dict[str, object]:
    try:
        return await answer_with_rag(payload.question, payload.metadata_filter or {})
    except Exception as exc:  # pragma: no cover
        # Keep the API responsive during provider/config issues and surface
        # a user-safe message instead of a generic 500.
        return {
            "answer": f"RAG temporarily unavailable: {exc}",
            "citations": [],
        }
