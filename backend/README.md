# MCQ System Backend

A FastAPI backend for facial recognition-based attendance and MCQ management.

---

## Tech Stack

- **Framework:** FastAPI (Python 3.11+)
- **Database:** PostgreSQL (async SQLAlchemy ORM)
- **Authentication:** OAuth2 with JWT tokens
- **Features:**
  - User, instructor, and admin management
  - MCQ/Test management (CRUD)
  - Attendance with face recognition (API endpoints for check-in, review, and history)
  - Manual grading for theory questions
  - File uploads for profile images
  - Analytics endpoints for dashboard stats

---

## Quickstart

1. Create and activate a virtual environment:

   ```sh
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # or
   source venv/bin/activate  # On macOS/Linux
   ```

2. Install dependencies:

   ```sh
   pip install -r requirements.txt
   ```

3. Set environment variables:
   - Copy `.env.example` to `.env` and fill in the required values (JWT secret, DB URL, etc).
4. Run the backend (development):

   ```sh
   uvicorn app.main:app --reload
   ```

5. Run the backend (production, with HTTPS & CORS):

   ```sh
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --ssl-keyfile path/to/privkey.pem --ssl-certfile path/to/fullchain.pem
   ```

6. Run tests:

   ```sh
   pytest app/tests
   ```

7. API Docs:
   - Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
   - Redoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

See `GUIDE.md` for full architecture, roadmap, and project structure.
