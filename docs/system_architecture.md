# System Architecture

## High-Level Components

1. **Client Applications**
   - Student dashboard (web/mobile-ready)
   - Lecturer analytics dashboard
   - Admin content and operations console
2. **API & Orchestration Layer**
   - FastAPI REST endpoints
   - Router Agent (intent and policy routing)
   - Async task layer for ingestion/analytics
3. **AI Intelligence Layer**
   - Domain agents (Tutor, Exam, Calendar, Performance, Recommendation, Quiz, Announcement)
   - RAG pipeline (retrieval + grounded response generation)
   - Prompt management and evaluation hooks
4. **Data Layer**
   - PostgreSQL for transactional/analytical records
   - ChromaDB for embeddings and semantic retrieval
   - Object storage (S3/Supabase) for documents

## Multi-Agent Control Plane

- Router Agent receives user requests and metadata (role, module, context).
- Policy rules validate role-based scope and safety constraints.
- Router dispatches to a specialist agent or a composed workflow.
- Shared memory/context store captures summarized conversation and task state.
- Agent outputs are persisted and surfaced through APIs with trace IDs.

## Clean Architecture Boundaries

- `routers/`: API adapters only
- `services/`: orchestration, business logic
- `agents/`: LLM-facing behavior and task logic
- `rag/`: retrieval/indexing workflows
- `vector_db/`: vector provider abstraction
- `database/`: ORM models, schema, migrations
- `analytics/`: performance metrics and risk scoring

## Scalability Decisions

- All AI providers behind a common model gateway interface.
- Vector database adapter supports Chroma today, Pinecone/Weaviate later.
- Async ingestion pipeline for bulk PDF processing.
- Pydantic contracts for strict request/response typing.
- Observability via structured logging and request correlation IDs.
