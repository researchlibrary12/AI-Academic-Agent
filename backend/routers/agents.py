from pydantic import BaseModel
from fastapi import APIRouter, Depends

from agents.router_agent import route_request
from services.auth import get_current_user

router = APIRouter()


class AgentRequest(BaseModel):
    query: str
    context: dict[str, object] = {}


@router.post("/route")
async def route(
    payload: AgentRequest,
    user: dict[str, str] = Depends(get_current_user),
) -> dict[str, object]:
    enriched_context = {**payload.context, "user_id": user.get("user_id", "")}
    return await route_request(payload.query, enriched_context)
