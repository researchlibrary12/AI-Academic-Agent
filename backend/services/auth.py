import time
from typing import Any

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt

from config import settings

security = HTTPBearer(auto_error=False)
_jwks_cache: dict[str, Any] = {}
_jwks_cache_exp: float = 0


async def _get_jwks() -> dict[str, Any]:
    global _jwks_cache, _jwks_cache_exp
    if _jwks_cache and time.time() < _jwks_cache_exp:
        return _jwks_cache
    if not settings.clerk_jwks_url:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="CLERK_JWKS_URL not set")
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(settings.clerk_jwks_url)
        response.raise_for_status()
        _jwks_cache = response.json()
        _jwks_cache_exp = time.time() + 900
        return _jwks_cache


async def _decode_token(token: str) -> dict[str, Any]:
    jwks = await _get_jwks()
    try:
        return jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            issuer=settings.jwt_issuer,
            audience=settings.jwt_audience,
            options={"verify_aud": settings.jwt_audience is not None, "verify_iss": settings.jwt_issuer is not None},
        )
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc


async def get_current_user(creds: HTTPAuthorizationCredentials | None = Depends(security)) -> dict[str, str]:
    if not creds or creds.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    claims = await _decode_token(creds.credentials)
    user_id = str(claims.get("sub", ""))
    role = str(claims.get("role", "student"))
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject")
    return {"user_id": user_id, "role": role}
