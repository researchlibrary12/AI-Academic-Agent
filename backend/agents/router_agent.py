from services.model_gateway import model_gateway
from database.assessment_store import get_results_for_user

AGENT_HINTS = {
    "exam": "exam_preparation_agent",
    "quiz": "quiz_generation_agent",
    "calendar": "academic_calendar_agent",
    "deadline": "academic_calendar_agent",
    "announcement": "announcement_agent",
    "weak": "performance_analysis_agent",
    "recommend": "recommendation_agent",
}


def _resolve_agent(query: str) -> str:
    lower = query.lower()
    for keyword, agent_name in AGENT_HINTS.items():
        if keyword in lower:
            return agent_name
    return "tutor_agent"


async def route_request(query: str, context: dict[str, object]) -> dict[str, object]:
    selected_agent = _resolve_agent(query)
    user_id = str(context.get("user_id", "")) if isinstance(context, dict) else ""
    results_context = []
    if user_id:
        user_results = get_results_for_user(user_id)
        results_context = user_results[-10:]
    response = await model_gateway.generate(
        "You are a safe academic assistant with POPIA-aligned privacy behavior.\n"
        "Guardrails:\n"
        "- Never provide financial, legal, or medical advice as definitive instructions.\n"
        "- If asked for final exam leaks/questions, refuse and provide practice-style alternatives.\n"
        "- You may answer non-course questions briefly, but keep responses safe and non-harmful.\n"
        "- Do not expose sensitive personal data from context.\n"
        "- If student_name exists in context, address the student by name.\n"
        f"Agent={selected_agent}\nContext={context}\nRecentResults={results_context}\nQuery={query}"
    )
    return {"agent": selected_agent, "response": response}
