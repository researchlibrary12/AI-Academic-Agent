from services.model_gateway import model_gateway
from vector_db.chroma_client import vector_store


def _is_small_talk(question: str) -> bool:
    lower = question.strip().lower()
    small_talk_phrases = {
        "hi",
        "hello",
        "hey",
        "good morning",
        "good afternoon",
        "good evening",
        "how are you",
        "thanks",
        "thank you",
    }
    return any(phrase in lower for phrase in small_talk_phrases)


async def answer_with_rag(question: str, metadata_filter: dict[str, str]) -> dict[str, object]:
    if _is_small_talk(question):
        answer = await model_gateway.generate(
            "You are a friendly academic assistant. "
            "Respond briefly and warmly to the user's greeting or social message.\n"
            f"User message: {question}"
        )
        return {"answer": answer, "citations": []}

    query_embedding = await model_gateway.embed_query(question)
    results = vector_store.query(query_embedding, metadata_filter=metadata_filter, top_k=5)
    docs = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    if not docs:
        fallback = await model_gateway.generate(
            "You are an academic assistant. The retrieval system found no relevant documents. "
            "Give a helpful, general answer with practical study guidance, and state that it is "
            "not based on uploaded course materials.\n"
            f"Question: {question}"
        )
        return {"answer": fallback, "citations": []}
    context = "\n\n".join(docs)
    prompt = (
        "You are an academic AI assistant. Use only the retrieved context.\n"
        "If context is insufficient, say so clearly.\n"
        f"Question: {question}\n"
        f"Context:\n{context}"
    )
    answer = await model_gateway.generate(prompt)
    citations = [
        {
            "source": md.get("source", "unknown"),
            "module": md.get("module", "unknown"),
            "topic": md.get("topic", "unknown"),
            "document_type": md.get("document_type", "unknown"),
        }
        for md in metadatas
    ]
    return {"answer": answer, "citations": citations}
