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
| Frontend | React.js (Vite + TailwindCSS + Headless UI) |
| Authentication | OAuth2 + JWT Tokens |
| Database | PostgreSQL |
| State Management | Redux Toolkit |
| File Storage | Local (Dev), S3/Cloudinary (Prod) |
| Charts | Recharts or Chart.js |
| API Communication | Axios |
| Real-time (Optional) | WebSockets for live status |

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

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

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
