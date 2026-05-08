# API Architecture

## Base Principles

- Versioned REST APIs under `/api/v1`
- JWT-authenticated requests with role claims
- Strict Pydantic request/response schemas
- Traceable responses with request IDs

## Core Route Groups

- `/auth` - session validation and identity bootstrap
- `/documents` - upload, index, retrieve curriculum resources
- `/rag` - ask question, retrieve citations, semantic search
- `/analytics` - grade ingestion, weakness analysis, trend/risk reporting
- `/calendar` - exam dates, deadlines, notices, due-soon queries
- `/agents` - router endpoint and specialist-agent execution endpoints

## Representative Endpoints

- `POST /api/v1/documents/upload`
- `POST /api/v1/documents/index`
- `POST /api/v1/rag/query`
- `POST /api/v1/analytics/grades`
- `GET /api/v1/analytics/student/{student_id}/weak-topics`
- `GET /api/v1/calendar/upcoming`
- `POST /api/v1/agents/route`

## Security Model

- Role-based access control in route dependencies.
- Student scope isolation for personal data.
- Lecturer/admin elevated access with explicit module/faculty permissions.
