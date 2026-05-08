from fastapi import APIRouter, Depends

from services.auth import get_current_user

router = APIRouter()


@router.get("/me")
async def me(user: dict[str, str] = Depends(get_current_user)) -> dict[str, str]:
    return user
