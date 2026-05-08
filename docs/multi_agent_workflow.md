# Multi-Agent Workflow

## Router Agent

Input:
- user query
- role
- profile context
- recent performance summary

Process:
1. Classify intent and domain.
2. Select one or more specialist agents.
3. Build execution graph (LangGraph state transitions).
4. Aggregate and rank final response with citations/actions.

## Specialist Agents

1. Tutor Agent - concept explanation and adaptive teaching.
2. Exam Preparation Agent - past paper pattern analysis, mock exams.
3. Academic Calendar Agent - date/deadline/notice retrieval.
4. Performance Analysis Agent - trend and weak-topic diagnostics.
5. Recommendation Agent - study plans and prioritized actions.
6. Quiz Generation Agent - weak-topic question generation.
7. Announcement Agent - relevance-ranked academic notices.

## Shared State

- `conversation_context`
- `student_profile`
- `recent_grades`
- `retrieved_chunks`
- `citations`
- `recommended_actions`

## Guardrails

- Verify source grounding for factual responses.
- Enforce role permissions before data retrieval.
- Apply confidence scoring and fallback response policy.
