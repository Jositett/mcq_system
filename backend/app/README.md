# MCQ System Backend

## Setup

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables (optional for SQLite):
   - `DATABASE_URL` (default: `sqlite:///./test.db`)
3. Run database migrations (if using Alembic or similar).
4. Seed initial data:

   ```bash
   python -m app.seed
   ```

5. Start the server:

   ```bash
   uvicorn app.main:app --reload
   ```

## API Overview

- **User Profile Fields:** All user-related endpoints now support the following fields: `full_name`, `phone`, `department`, `bio`, `gender`. The `gender` field only accepts `male`, `female`, or `other`.
- **Auth:** `/api/auth/register`, `/api/auth/login`
- **Users:** `/api/users/` (admin only)
- **Instructors:** `/api/instructors/{instructor_id}/batches`, `/api/instructors/{instructor_id}/tests` (instructor only)
- **Students:** `/api/students/{student_id}/tests`, `/api/students/{student_id}/attendance` (student only)
- **Tests:** `/api/tests/` (instructor only)
- **Attendance:** `/api/attendance/check-in`, `/api/attendance/history/{student_id}` (student only)

## Roles

- `admin`: Full access to user management.
- `instructor`: Manage batches, tests, and view students.
- `student`: Take tests, check attendance, view results.

## Running Tests

```bash
pytest app/tests/
```
