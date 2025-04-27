# 🎯 MCQ Test & Attendance System — Full Development Guide for AI Agents

---

## 📚 Core Features

| Feature | Description |
|:--------|:------------|
| **Authentication** | Secure role-based login (Admin / Instructor / Student) with JWT + OAuth2 |
| **Instructor Isolation** | Each instructor manages only their batches, tests, and students |
| **Test Management** | MCQ, True/False, Theory questions; auto-scheduled test sessions |
| **Theory Marking** | Manual grading of theory responses by instructors |
| **Attendance System** | Daily student check-ins with calendar view reports |
| **Birthday Notifications** | Alerts for upcoming birthdays (configurable days before) |
| **Dark/Light Mode** | Accessible theme switching, saved in localStorage |
| **Profile Pictures** | Upload and manage user profile images |
| **Result Analytics** | Graphical visualization of test performance and attendance history |

---

## 🛠️ Technology Stack

| Layer | Technology |
|:-----|:------------|
| Backend | FastAPI (Python 3.11+), SQLAlchemy ORM |
| Frontend | React.js (Vite + TailwindCSS v4+ + Headless UI) |
| Authentication | OAuth2 + JWT Tokens |
| Database | PostgreSQL |
| State Management | Redux Toolkit |
| File Storage | Local (Dev), S3/Cloudinary (Prod) |
| Charts | Recharts or Chart.js |
| API Communication | Axios |
| Real-time (Optional) | WebSockets for live status |

---

## 🚀 Frontend Modernization Plan

- **UI Framework:** Fully migrated to TailwindCSS v4+ for all styling and theming. No Material UI (MUI) dependencies remain.
- **Component Library:** Headless UI is used for accessible, unstyled components (modals, dropdowns, etc), styled with Tailwind.
- **Design:** Modern, responsive layouts for all pages (auth, dashboard, admin, instructor, student views).
- **Dark/Light Mode:** Implemented with Tailwind's `dark:` classes and toggled via HTML class.
- **State Management:** Redux Toolkit for scalable state handling.
- **API:** Axios for all backend communication.
- **Testing:** Jest and React Testing Library for unit and integration tests.
- **Build Tool:** Vite for fast development and hot-reload.

### Migration Roadmap

- [x] Authentication pages (login, register) refactored to TailwindCSS.
- [x] Landing page modernized.
- [x] Core dashboard and admin components migrated from MUI to Tailwind.
- [x] All legacy MUI code removed.
- [x] Error boundaries and user feedback improved.
- [x] Tailwind v4+ and PostCSS config aligned with latest standards.
- [ ] Ongoing: UX polish, accessibility, and responsive testing.

---

## 🛠️ Backend Guide (FastAPI)

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
- **Dev Setup:**
  1. `python -m venv venv && venv\Scripts\activate`
  2. `pip install -r requirements.txt`
  3. Configure `.env` (DB url, JWT secret, etc)
  4. `uvicorn app.main:app --reload`
  5. Swagger UI: <http://localhost:8000/docs>
- **Testing:** `pytest app/tests`
- **Deployment:** Use Gunicorn/Uvicorn with HTTPS and CORS configured for production.

---

## 📂 Project Structure (Updated)

```plaintext
mcq_system/
├── backend/
│   ├── app/
│   │   ├── api/               # Routers: auth, users, instructors, students, tests, attendance
│   │   ├── core/              # Security, configuration, JWT utilities
│   │   ├── db/                # SQLAlchemy models and database session management
│   │   ├── services/          # Business logic: auth, tests, attendance, grading
│   │   ├── schemas/           # Pydantic schemas (request/response validation)
│   │   ├── utils/             # Helpers (e.g., file uploads, time utilities)
│   │   └── main.py            # FastAPI app entry point
│   └── requirements.txt
├── frontend/
│   ├── public/
│   │   └── assets/            # Static files like logos and icons
│   ├── src/
│   │   ├── components/        # Reusable UI components (all TailwindCSS, Headless UI)
│   │   ├── features/          # Redux slices for different features
│   │   ├── pages/             # Login, Dashboards, Attendance, Tests, Profile
│   │   ├── services/          # Axios API services
│   │   └── App.jsx
│   └── package.json
└── GUIDE.md (this file)
```

---

## 🔗 Useful Commands

### Frontend

```sh
cd frontend
npm install
npm run dev
```

### Backend

```sh
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

---

## 📢 Notes

- All new UI and features should use TailwindCSS and Headless UI only.
- No Material UI code should remain in any component.
- For theming, use Tailwind's dark mode strategy.

---

## 📝 Next Steps & TODOs

### Backend (Tasks)

- [ ] **Enhance Test Coverage:**
  - Write and improve unit/integration tests for all async services and API endpoints
  - Ensure database, authentication, and edge cases are covered
- [ ] **Add Rate Limiting:**
  - Implement rate limiting middleware to prevent abuse of API endpoints
- [ ] **CI/CD Setup:**
  - Configure GitHub Actions or similar for automated testing and deployment
- [ ] **Production Caching:**
  - Integrate Redis for distributed caching (optional, for scaling)
- [ ] **File Storage Service:**
  - Abstract and implement file storage (local for dev, S3/Cloudinary for prod)
- [ ] **API Documentation:**
  - Continue refining OpenAPI docs and usage examples
- [ ] **Database Migrations:**
  - Finalize and document Alembic migration workflow
- [ ] **Performance Optimization:**
  - Profile and optimize async DB queries, caching, and bottlenecks
- [ ] **Security Review:**
  - Pen-test endpoints, review JWT handling, and RBAC enforcement
- [ ] **Convert Services to async/await:**
  - Convert all business logic and service functions to async/await for full async support
- [ ] **API Versioning:**
  - Implement version prefixes and strategy (e.g., v1) for all endpoints
- [ ] **Health Checks:**
  - Add liveness/readiness endpoints and monitoring middleware

### Frontend (Tasks)

- [x] **UX Polish & Accessibility:**
  - Finalize responsive layouts, keyboard navigation, and ARIA labels
- [x] **Test Coverage:**
  - Add/expand Jest and React Testing Library tests for all core components
- [x] **API Error Handling:**
  - Improve user feedback on API/network errors
- [ ] **Dashboard Analytics:**
  - Enhance charts/graphs for results and attendance analytics
- [ ] **Profile & File Uploads:**
  - Integrate with backend file storage endpoints
- [ ] **Real-time Features:**
  - Add WebSocket support for live test/attendance updates (optional)
- [ ] **Deployment:**
  - Prepare Vite build for production, configure environment variables

---

**For details on development, see the relevant backend and frontend sections above.**

### _Last updated: 2025-04-21_

- Keep backend and frontend `.env` files up to date with API URLs and secrets.
- See README.md in each subfolder for quickstart and troubleshooting.

---

## 🏗️ Project Structure

```plaintext
mcq_system/
├── backend/
│   ├── app/
│   │   ├── api/               # Routers: auth, users, instructors, students, tests, attendance
│   │   ├── core/              # Security, configuration, JWT utilities
│   │   ├── db/                # SQLAlchemy models and database session management
│   │   ├── services/          # Business logic: auth, tests, attendance, grading
│   │   ├── schemas/           # Pydantic schemas (request/response validation)
│   │   ├── utils/             # Helpers (e.g., file uploads, time utilities)
│   │   └── main.py            # FastAPI app entry point
│   └── requirements.txt
├── frontend/
│   ├── public/
│   │   └── assets/            # Static files like logos and icons
│   ├── src/
│   │   ├── components/        # Reusable UI components
│   │   ├── features/          # Redux slices for different features
│   │   ├── pages/             # Login, Dashboards, Attendance, Tests, Profile
│   │   ├── services/          # Axios API services
│   │   └── App.jsx
│   └── package.json
└── README.md
```

---

## 🛢️ Expanded Database Schema (PostgreSQL)

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    role VARCHAR(50) NOT NULL,
    birthday DATE,
    hashed_password TEXT NOT NULL,
    profile_picture TEXT
);

CREATE TABLE courses (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    description TEXT
);

CREATE TABLE batches (
    id SERIAL PRIMARY KEY,
    course_id INT REFERENCES courses(id),
    instructor_id INT REFERENCES users(id),
    name VARCHAR(255),
    start_date DATE,
    end_date DATE
);

CREATE TABLE enrollments (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    batch_id INT REFERENCES batches(id)
);

CREATE TABLE tests (
    id SERIAL PRIMARY KEY,
    batch_id INT REFERENCES batches(id),
    title VARCHAR(255),
    duration INT,
    difficulty VARCHAR(50),
    start_time TIMESTAMP,
    end_time TIMESTAMP
);

CREATE TABLE questions (
    id SERIAL PRIMARY KEY,
    test_id INT REFERENCES tests(id),
    question_text TEXT,
    question_type VARCHAR(50), -- MCQ, TrueFalse, Theory
    correct_answer TEXT,
    options JSONB
);

CREATE TABLE responses (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    question_id INT REFERENCES questions(id),
    selected_answer TEXT,
    is_theory BOOLEAN DEFAULT FALSE,
    graded_score FLOAT DEFAULT NULL -- NULL if not graded yet
);

CREATE TABLE attendance (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    date DATE,
    status VARCHAR(50)
);
```

---

## ⚙️ Backend API Endpoints (Key)

| URL | Method | Description |
|:----|:-------|:------------|
| `/api/auth/login` | POST | Login, returns JWT token |
| `/api/auth/register` | POST | Register user |
| `/api/users/profile-picture` | POST | Upload profile picture |
| `/api/users/me` | GET | Fetch current user profile |
| `/api/instructor/batches` | CRUD | Manage own batches |
| `/api/instructor/tests` | CRUD | Manage own tests |
| `/api/instructor/questions` | CRUD | Add/edit/delete questions |
| `/api/instructor/grade-theory` | POST | Grade theory answers |
| `/api/student/available-tests` | GET | List of active tests |
| `/api/student/submit-test` | POST | Submit test |
| `/api/attendance/check-in` | POST | Daily attendance check-in |
| `/api/attendance/history` | GET | View past attendance |
| `/api/admin/users` | CRUD | Manage all users |

---

## 💻 Frontend Pages

| Page | Features |
|:-----|:---------|
| `/login` | Email/password login |
| `/register` | Role-based signup |
| `/dashboard/student` | Upcoming tests, results, attendance summary |
| `/dashboard/instructor` | Manage batches, tests, grade theory |
| `/dashboard/admin` | Manage all users and system settings |
| `/profile` | Edit profile, upload/change photo |
| `/test/start/:id` | Test UI with countdown and auto-submit |
| `/attendance` | Daily check-in form and history calendar |

---

## 🚀 Development Setup

### Backend (DEV)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend (DEV)

```bash
cd frontend
npm install
npm run dev
```

---

## 📝 `.env` Sample

```env
DATABASE_URL=postgresql://postgres:swe@localhost/mcq_db
SECRET_KEY=yourverysecuresecret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
FRONTEND_URL=http://localhost:5173
```

---

## ✅ Testing Checklist

| Area | Task | Status |
|:-----|:-----|:------|
| Authentication | Registration/Login | [ ] |
| Authentication | JWT Security | [ ] |
| User | Profile Management | [ ] |
| Instructor | Batch/Test Management | [ ] |
| Test Management | MCQ, True/False, Theory | [ ] |
| Test Management | Auto-generate Tests | [ ] |
| Test Management | Auto-submit on timeout | [ ] |
| Attendance | Daily Check-in/Reporting | [ ] |
| Birthday Notification | Notification system | [ ] |
| Result Analytics | Graphical Reports | [ ] |
| UI/UX | Dark/Light Mode | [ ] |
| Security | Password Hashing (bcrypt) | [ ] |
| Admin | User Management | [ ] |
| File Upload | Profile Pictures | [ ] |

---

## 🔮 Future Enhancements (Post-Launch)

- **Email notifications** for tests, birthdays
- **SMS notifications** (Twilio or local provider)
- **WebSocket live test monitoring** for instructors
- **Offline attendance check-ins** (for mobile-first support)
- **Push Notifications** (via PWA)
- **Audit Logging** (Security events, Admin logs)

---

## 📈 Development Phases (Recommended)

1. **Backend Foundation:** Auth, User, Attendance, Tests
2. **Frontend Core:** Login, Dashboards, Attendance UI, Test UI
3. **Advanced Features:** Theory marking, Birthday reminders, Profile Pictures
4. **CI/CD:** Dockerize backend & frontend ➔ Setup GitHub Actions ➔ Deploy (Render/VPS)
5. **Beta Launch:** Collect feedback, fix bugs, polish

---

> **Goal:**  
> Build a **production-grade**, **user-centric**, and **scalable** MCQ and Attendance system ready for real-world educational or corporate deployment with **robust backend**, **responsive frontend**, and **secure data handling**.

---

## 🏁 End of Full Guide for AI Agents
