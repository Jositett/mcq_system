# MCQ System Backend

A FastAPI backend for facial recognition-based attendance and MCQ management.

---

## Quickstart

### 1. Install dependencies

```sh
python -m venv venv
venv\Scripts\activate  # On Windows
pip install -r requirements.txt
```

### 2. Set environment variables

Copy `.env.example` to `.env` and fill in the required values (JWT secret, DB URL, etc).

### 3. Run the backend (development)

```sh
uvicorn app.main:app --reload
```

### 4. Run the backend (production, with HTTPS & CORS)

```sh
uvicorn app.main:app --host 0.0.0.0 --port 8000 --ssl-keyfile path/to/privkey.pem --ssl-certfile path/to/fullchain.pem
```

### 5. Run tests

```sh
cd backend
pytest app/tests
```

### 6. API Docs

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- Redoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

See `API_REFERENCE.md` for a full endpoint reference.
