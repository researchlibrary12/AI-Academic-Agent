from fastapi import APIRouter

from routers import agents, analytics, auth, documents, phase2, phase3, rag

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(rag.router, prefix="/rag", tags=["rag"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(phase2.router, prefix="/phase2", tags=["phase2"])
api_router.include_router(phase3.router, prefix="/phase3", tags=["phase3"])
