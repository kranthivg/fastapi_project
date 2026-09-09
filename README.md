# FastAPI Studio backend

Modernized from kranthivg/fastapi_project. Existing users, posts and votes tables and original endpoint paths are retained. Python 3.11+; Python 3.13 recommended for this build. Dependencies are bounded by compatible major versions; requirements.lock.txt captures the tested environment.

## Quick start (SQLite)

Create and activate a virtual environment, then `pip install -r requirements.txt`. Set `SECRET_KEY` to a random value with at least 32 characters (generate with `python -c "import secrets; print(secrets.token_hex(32))"`). Run `python -m app.init_db`, then `uvicorn app.main:app --reload`. Open http://localhost:8000/docs. SQLite initialization is for a fresh development database only.

## PostgreSQL / Docker

Copy `.env.example` to `.env`, set a random SECRET_KEY and POSTGRES_PASSWORD (use a URL-safe random value), and set CORS_ORIGINS to the exact dashboard origin as a JSON array. Run `docker compose up --build`. Compose runs the existing Alembic migration chain before starting the API. PostgreSQL data uses a named volume. For an existing database, back it up first, set DATABASE_URL to its psycopg connection URL, and run `alembic upgrade head`. The pre-existing migration history is preserved.

Deploy this container to a Python/container-capable host with managed PostgreSQL, HTTPS, and environment secrets. Sites hosts the JavaScript dashboard and a Worker sandbox; it does **not** execute this Python backend. No external Python hosting account has been provisioned. Once deployed, enter your API HTTPS URL in the dashboard's Connect FastAPI dialog. Browser requests go directly to that API; there is no backend proxy. Add the dashboard's exact origin to CORS_ORIGINS. JWTs stay in browser memory and are cleared on refresh.

## Behavior and compatibility

Pydantic 2 replaces v1 schemas/settings. SQLAlchemy 2 uses typed models and select statements. New hashes use Argon2; existing bcrypt hashes are upgraded after successful login. PyJWT replaces python-jose and uses an explicit HS256 allowlist, required expiration and subject claims. Old JWTs must be replaced by signing in again. Configuration now uses DATABASE_URL rather than individual database fields; ALGORITHM is fixed to HS256. Preserve the existing secret in your deployment if appropriate, but existing legacy tokens are not accepted.

Drafts are now private to their author. Account lookup requires authentication and returns only the current account. Posts still include their author's email as in the original API; consider pseudonymous author profiles before a public social deployment. Duplicate emails/votes return 409; invalid input returns 422; missing/invalid credentials return 401. Passwords must be 12–128 characters for new accounts. List limits are 1–100, search 200 characters, titles 200 and content 20,000. PostOut retains the original `Post` and `votes` properties and adds `voted`. `mine=true` filters by current author. `GET /users/me` and `GET /health` are new.

This is a learning/playground application, not a completed public identity service. Before a public launch add host-level authentication rate limits, email verification/recovery, monitoring, backups, and a defined token revocation strategy. Password reset and refresh tokens are not implemented.

## Validation

`pip install -r requirements-dev.txt`, then `pytest -q` and `ruff check app tests`. Tests exercise registration, login, CRUD, draft privacy, ownership, voting conflicts, and validation with SQLite. PostgreSQL migration execution and external HTTPS connectivity require a deployed PostgreSQL/Python environment; do not treat SQLite tests as verification of those environments.

References: https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/ and https://docs.pydantic.dev/latest/migration/.
