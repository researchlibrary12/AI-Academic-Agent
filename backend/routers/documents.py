from fastapi import APIRouter, Depends, Form, UploadFile

from rag.ingest import ingest_document
from services.auth import get_current_user

router = APIRouter()


@router.post("/upload")
async def upload_document(
    file: UploadFile,
    faculty: str = Form(default="unknown"),
    course: str = Form(default="unknown"),
    module: str = Form(default="unknown"),
    topic: str = Form(default="unknown"),
    year: str = Form(default="unknown"),
    document_type: str = Form(default="Uploaded Note"),
    _: dict[str, str] = Depends(get_current_user),
) -> dict[str, str]:
    metadata = {
        "faculty": faculty,
        "course": course,
        "module": module,
        "topic": topic,
        "year": year,
        "document_type": document_type,
    }
    return await ingest_document(file, metadata)
