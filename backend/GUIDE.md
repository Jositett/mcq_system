# MCQ System Backend Guide

This guide provides a step-by-step approach to modernizing and enhancing the MCQ System backend (FastAPI).

## Requirements

**Install dependencies:**

```bash
pip install -r requirements.txt
```

**requirements.txt:**

```text
# Core dependencies
fastapi>=0.108.0
uvicorn[standard]>=0.25.0
gunicorn>=21.2.0

# Database
sqlalchemy>=2.0.25
sqlalchemy[asyncio]>=2.0.25
aiosqlite>=0.19.0
psycopg2-binary>=2.9.9
alembic>=1.13.1

# Authentication and security
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.6

# Environment and configuration
python-dotenv>=1.0.0
pydantic>=2.5.3
pydantic-settings>=2.1.0
email-validator>=2.1.0

# Face recognition
face_recognition>=1.3.0
numpy>=1.26.3
pillow>=10.1.0

# Testing
pytest>=7.4.3
pytest-asyncio>=0.23.2
httpx>=0.25.2
pytest-cov>=4.0.0

# Utilities
python-dateutil>=2.8.2
tenacity>=8.2.3
starlette>=0.27.0
psutil>=5.9.0

# Caching & Rate Limiting
redis>=4.5.5
aioredis>=2.0.1
slowapi>=0.1.4

# File Storage (AWS S3)
boto3>=1.28.0

# Utilities
fastapi-utils>=0.2.1
```

## Task 1: Environment & Configuration

- Initialize a Python virtual environment and install dependencies.
- Configure environment variables via Pydantic Settings (.env, JWT secrets, database URL, Redis URL).
- Setup async SQLAlchemy engine and configure Alembic.

## Task 2: Database Migrations

- Initialize Alembic in the `alembic/` directory.
- Update `env.py` for async migrations.
- Create initial migration for user, test, attendance tables.
- Run `alembic upgrade head` and verify schema.

## Task 3: Authentication & Authorization

- Implement JWT auth with access & refresh tokens.
- Create `/auth/login`, `/auth/refresh`, `/auth/logout` endpoints.
- Define user roles (admin, instructor, student) and permissions.
- Secure routes using FastAPI dependencies and scopes.

## Task 4: Async Refactoring

- Identify synchronous service functions.
- Convert to `async def` and add `await` for DB calls.
- Update routers and dependencies to handle async services.

## Task 5: API Versioning & Documentation

- Prefix routes with `/v1` for versioning.
- Add OpenAPI tags, summaries, and detailed descriptions.
- Verify Swagger UI and ReDoc at `/docs` and `/redoc`.

## API Endpoints Reference

- **POST /v1/auth/login**: Request body `{ username: str, password: str }`. Response `{ access_token: str, refresh_token: str, token_type: str }`.
- **POST /v1/auth/refresh**: Request body `{ refresh_token: str }`. Response `{ access_token: str, refresh_token: str }`.
- **POST /v1/auth/logout**: Invalidates refresh token. No body.

- **GET /v1/users**: List users. Response `[{ id, username, role, created_at }]`.
- **GET /v1/users/{id}**: Get user detail.
- **POST /v1/users**: Create user `{ username, password, role }`.
- **PUT /v1/users/{id}**: Update user.
- **DELETE /v1/users/{id}**: Remove user.

- **GET /v1/tests**: List tests. Response `[{ id, title, description, created_at }]`.
- **POST /v1/tests**: Create test `{ title: str, description: str, questions: Array }`.
- **GET /v1/tests/{id}**: Get test with questions.
- **PUT /v1/tests/{id}**: Update test.
- **DELETE /v1/tests/{id}**: Delete test.
- **POST /v1/tests/{test_id}/submit**: Submit answers `{ answers: { question_id: selected_option } }`. Response `{ score: int, details: Object }`.

- **GET /v1/attendance**: List attendance. Response `[{ id, test_id, user_id, status, timestamp }]`.
- **POST /v1/attendance**: Record attendance `{ test_id: int, user_id: int, status: str }`.
- **GET /v1/attendance/{id}**: Get record.
- **PUT /v1/attendance/{id}**: Update record.
- **DELETE /v1/attendance/{id}**: Delete record.

- **POST /v1/files/upload**: Upload file via form-data key `file`. Response `{ filename: str, url: str }`.
- **GET /v1/files/{filename}**: Download file.

## Task 6: Caching & Rate Limiting

- Integrate Redis via `aioredis` or `redis-py` async client.
- Implement caching decorator for frequent GET endpoints.
- Add rate limiting middleware (e.g., `slowapi`) to protect against abuse.

## Task 7: File Storage Service

- Implement an abstract storage interface (local filesystem vs S3).
- Create upload/download endpoints with validation (size, type).
- Secure file access and serve with signed URLs if needed.

## Task 8: Testing

- Write `pytest` tests with `pytest-asyncio` for routers and services.
- Configure a test database fixture and seed data.
- Cover edge cases: auth failures, DB errors, invalid payloads.

## Task 9: Monitoring & Health Checks

- Add `/health` endpoint to check DB, Redis, and storage.
- Integrate Prometheus metrics and structured logging middleware.

## Task 10: CI/CD

- Configure GitHub Actions or other CI for linting, tests, and build.
- Publish Docker image and/or deploy to cloud provider.
- Add pre-commit hooks (black, isort, flake8).

## Future Enhancements

- Implement GraphQL layer for complex queries.
- Add WebSocket support for real-time attendance updates.
- Integrate advanced caching invalidation strategies.
