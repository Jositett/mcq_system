# MCQ Test & Attendance System

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

## 🛠 Technology Stack

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

## 🏗 Project Structure

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

## 🚀 Development Setup

### Backend

bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

### Frontend

bash
cd frontend
npm install
npm run dev

## 📝 .env Sample

DATABASE_URL=postgresql://postgres:swe@localhost/mcq_db
SECRET_KEY=yourverysecuresecret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
FRONTEND_URL=<http://localhost:5173>

## ✅ Testing Checklist

| Area | Task | Status |
|:-----|:-----|:------|
| Authentication | Registration/Login | [x] |
| Authentication | JWT Security | [x] |
| User | Profile Management | [ ] |
| Instructor | Batch/Test Management | [x] |
| Test Management | MCQ, True/False, Theory | [ ] |
| Test Management | Auto-generate Tests | [x] |
| Test Management | Auto-submit on timeout | [ ] |
| Attendance | Daily Check-in/Reporting | [ ] |
| Birthday Notification | Notification system | [ ] |
| Result Analytics | Graphical Reports | [ ] |
| UI/UX | Dark/Light Mode | [ ] |
| Security | Password Hashing (bcrypt) | [x] |
| Admin | User Management | [ ] |
| File Upload | Profile Pictures | [ ] |

## 🔮 Future Enhancements (Post-Launch)

- **Email notifications** for tests, birthdays
- **SMS notifications** (Twilio or local provider)
- **WebSocket live test monitoring** for instructors
- **Offline attendance check-ins** (for mobile-first support)
- **Push Notifications** (via PWA)
- **Audit Logging** (Security events, Admin logs)

## 📈 Development Phases (Recommended)

1. **Backend Foundation:** Auth, User, Attendance, Tests
2. **Frontend Core:** Login, Dashboards, Attendance UI, Test UI
3. **Advanced Features:** Theory marking, Birthday reminders, Profile Pictures
4. **CI/CD:** Dockerize backend & frontend ➔ Setup GitHub Actions ➔ Deploy (Render/VPS)
5. **Beta Launch:** Collect feedback, fix bugs, polish

> **Goal:**  
> Build a **production-grade**, **user-centric**, and **scalable** MCQ and Attendance system ready for real-world educational or corporate deployment with **robust backend**, **responsive frontend**, and **secure data handling**.
