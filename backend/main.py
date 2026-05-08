from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.v1 import api_router
from utils.logging import configure_logging

configure_logging()

app = FastAPI(title="AI Academic Agent API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
