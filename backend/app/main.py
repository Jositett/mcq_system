import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, users, instructors, students, tests, attendance, face

app = FastAPI(
    title="MCQ Test & Attendance System API",
    description="Backend API for MCQ-based test management and attendance tracking, supporting role-based access control for admins, instructors, and students.",
    version="1.0.0",
    contact={
        "name": "Your Team",
        "email": "support@example.com"
    },
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.get("/", tags=["Info"])
def root():
    return {
        "message": "Welcome to the MCQ Test & Attendance System Backend API!",
        "docs_url": "/docs",
        "openapi_url": "/openapi.json"
    }

# CORS middleware (allow all for MVP/dev)

origins = os.getenv("CORS_ORIGINS", "").split(",") if os.getenv("CORS_ORIGINS") else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(instructors.router, prefix="/api/instructors", tags=["instructors"])
app.include_router(students.router, prefix="/api/students", tags=["students"])
app.include_router(face.router, prefix="/api/face", tags=["face"])
app.include_router(tests.router, prefix="/api/tests", tags=["tests"])
app.include_router(attendance.router, prefix="/api/attendance", tags=["attendance"])

@app.get("/health")
def health_check():
    return {"status": "ok"}
