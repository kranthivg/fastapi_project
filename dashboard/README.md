# FastAPI Studio

Interactive posts/voting dashboard plus a modernized Python backend from kranthivg/fastapi_project.

The Sites deployment runs a JavaScript Worker + D1 sandbox scoped to the signed-in ChatGPT user. Author and Reader are explicitly simulated personas within that private workspace, not password accounts. Posts and votes are persisted in D1. The UI also connects directly to a separately deployed FastAPI backend through HTTPS and OAuth2 bearer tokens held in memory.

- `app/page.tsx`: dashboard, CRUD, votes, request inspector, backend connection.
- `app/api/sandbox/[[...path]]/route.ts`: sandbox endpoints.
- `drizzle/0000_studio.sql`: D1 schema.
- `backend/`: modernized FastAPI, SQLAlchemy, Pydantic, Docker and tests. See its README for deployment.

Frontend: `npm ci`, `npm run build`. Hosted sandbox API requires a trusted Sites identity header. It intentionally does not trust a client-supplied workspace key. A new sandbox starts empty; Add sample post is optional. The interface shows actual API responses and client-measured round-trip time. Login tokens are redacted from the inspector.
