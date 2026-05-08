from io import BytesIO
import uuid

from fastapi import UploadFile
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

from services.model_gateway import model_gateway
from vector_db.chroma_client import vector_store


def _extract_text(file_name: str, file_bytes: bytes) -> str:
    if file_name.lower().endswith(".pdf"):
        reader = PdfReader(BytesIO(file_bytes))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    return file_bytes.decode("utf-8", errors="ignore")


async def ingest_document(file: UploadFile, metadata: dict[str, str]) -> dict[str, str]:
    file_bytes = await file.read()
    content = _extract_text(file.filename or "unknown", file_bytes)
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = [c.strip() for c in splitter.split_text(content) if c.strip()]
    ids = [str(uuid.uuid4()) for _ in chunks]
    chunk_metadata = [
        {
            "source": file.filename or "unknown",
            "document_type": metadata.get("document_type", "Uploaded Note"),
            "faculty": metadata.get("faculty", "unknown"),
            "course": metadata.get("course", "unknown"),
            "module": metadata.get("module", "unknown"),
            "topic": metadata.get("topic", "unknown"),
            "year": metadata.get("year", "unknown"),
        }
        for _ in chunks
    ]
    if chunks:
        embeddings = await model_gateway.embed_texts(chunks)
        vector_store.add_chunks(ids=ids, texts=chunks, embeddings=embeddings, metadatas=chunk_metadata)
    return {"status": "indexed", "chunks": str(len(chunks)), "source": file.filename or "unknown"}
