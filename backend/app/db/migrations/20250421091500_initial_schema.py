"""
Migration: initial_schema
Version: 20250421091500
"""

from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text


async def upgrade_async(session: AsyncSession) -> None:
    """Apply the initial schema migration using async SQLAlchemy."""
    await session.execute(text("""
        -- Users table
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            full_name VARCHAR(255),
            hashed_password VARCHAR(255) NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            role VARCHAR(50) NOT NULL,
            profile_picture TEXT
        );

        -- Face images table
        CREATE TABLE IF NOT EXISTS face_images (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            image_data TEXT NOT NULL,
            embedding TEXT,
            created_at DATE NOT NULL
        );

        -- Instructors table
        CREATE TABLE IF NOT EXISTS instructors (
            id SERIAL PRIMARY KEY,
            user_id INTEGER UNIQUE REFERENCES users(id) ON DELETE CASCADE,
            department VARCHAR(255)
        );

        -- Batches table
        CREATE TABLE IF NOT EXISTS batches (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            instructor_id INTEGER REFERENCES instructors(id) ON DELETE SET NULL
        );

        -- Students table
        CREATE TABLE IF NOT EXISTS students (
            id SERIAL PRIMARY KEY,
            user_id INTEGER UNIQUE REFERENCES users(id) ON DELETE CASCADE,
            batch_id INTEGER REFERENCES batches(id) ON DELETE SET NULL,
            roll_number VARCHAR(255),
            dob DATE
        );

        -- Tests table
        CREATE TABLE IF NOT EXISTS tests (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            batch_id INTEGER REFERENCES batches(id) ON DELETE CASCADE,
            scheduled_at VARCHAR(255)
        );

        -- Questions table
        CREATE TABLE IF NOT EXISTS questions (
            id SERIAL PRIMARY KEY,
            test_id INTEGER REFERENCES tests(id) ON DELETE CASCADE,
            question_text TEXT NOT NULL,
            question_type VARCHAR(50) NOT NULL,
            options TEXT,
            correct_answer TEXT
        );

        -- Attendance table
        CREATE TABLE IF NOT EXISTS attendance (
            id SERIAL PRIMARY KEY,
            student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
            date DATE NOT NULL,
            status VARCHAR(50) NOT NULL
        );
        
        -- Create indexes for performance
        CREATE INDEX IF NOT EXISTS idx_face_images_user_id ON face_images(user_id);
        CREATE INDEX IF NOT EXISTS idx_students_batch_id ON students(batch_id);
        CREATE INDEX IF NOT EXISTS idx_tests_batch_id ON tests(batch_id);
        CREATE INDEX IF NOT EXISTS idx_questions_test_id ON questions(test_id);
        CREATE INDEX IF NOT EXISTS idx_attendance_student_id ON attendance(student_id);
        CREATE INDEX IF NOT EXISTS idx_attendance_date ON attendance(date);
    """))


def upgrade(session: Session) -> None:
    """Apply the initial schema migration using sync SQLAlchemy."""
    session.execute(text("""
        -- Users table
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            full_name VARCHAR(255),
            hashed_password VARCHAR(255) NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            role VARCHAR(50) NOT NULL,
            profile_picture TEXT
        );

        -- Face images table
        CREATE TABLE IF NOT EXISTS face_images (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            image_data TEXT NOT NULL,
            embedding TEXT,
            created_at DATE NOT NULL
        );

        -- Instructors table
        CREATE TABLE IF NOT EXISTS instructors (
            id SERIAL PRIMARY KEY,
            user_id INTEGER UNIQUE REFERENCES users(id) ON DELETE CASCADE,
            department VARCHAR(255)
        );

        -- Batches table
        CREATE TABLE IF NOT EXISTS batches (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            instructor_id INTEGER REFERENCES instructors(id) ON DELETE SET NULL
        );

        -- Students table
        CREATE TABLE IF NOT EXISTS students (
            id SERIAL PRIMARY KEY,
            user_id INTEGER UNIQUE REFERENCES users(id) ON DELETE CASCADE,
            batch_id INTEGER REFERENCES batches(id) ON DELETE SET NULL,
            roll_number VARCHAR(255),
            dob DATE
        );

        -- Tests table
        CREATE TABLE IF NOT EXISTS tests (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            batch_id INTEGER REFERENCES batches(id) ON DELETE CASCADE,
            scheduled_at VARCHAR(255)
        );

        -- Questions table
        CREATE TABLE IF NOT EXISTS questions (
            id SERIAL PRIMARY KEY,
            test_id INTEGER REFERENCES tests(id) ON DELETE CASCADE,
            question_text TEXT NOT NULL,
            question_type VARCHAR(50) NOT NULL,
            options TEXT,
            correct_answer TEXT
        );

        -- Attendance table
        CREATE TABLE IF NOT EXISTS attendance (
            id SERIAL PRIMARY KEY,
            student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
            date DATE NOT NULL,
            status VARCHAR(50) NOT NULL
        );
        
        -- Create indexes for performance
        CREATE INDEX IF NOT EXISTS idx_face_images_user_id ON face_images(user_id);
        CREATE INDEX IF NOT EXISTS idx_students_batch_id ON students(batch_id);
        CREATE INDEX IF NOT EXISTS idx_tests_batch_id ON tests(batch_id);
        CREATE INDEX IF NOT EXISTS idx_questions_test_id ON questions(test_id);
        CREATE INDEX IF NOT EXISTS idx_attendance_student_id ON attendance(student_id);
        CREATE INDEX IF NOT EXISTS idx_attendance_date ON attendance(date);
    """))


async def downgrade_async(session: AsyncSession) -> None:
    """Revert the initial schema migration using async SQLAlchemy."""
    await session.execute(text("""
        DROP TABLE IF EXISTS attendance;
        DROP TABLE IF EXISTS questions;
        DROP TABLE IF EXISTS tests;
        DROP TABLE IF EXISTS students;
        DROP TABLE IF EXISTS batches;
        DROP TABLE IF EXISTS instructors;
        DROP TABLE IF EXISTS face_images;
        DROP TABLE IF EXISTS users;
    """))


def downgrade(session: Session) -> None:
    """Revert the initial schema migration using sync SQLAlchemy."""
    session.execute(text("""
        DROP TABLE IF EXISTS attendance;
        DROP TABLE IF EXISTS questions;
        DROP TABLE IF EXISTS tests;
        DROP TABLE IF EXISTS students;
        DROP TABLE IF EXISTS batches;
        DROP TABLE IF EXISTS instructors;
        DROP TABLE IF EXISTS face_images;
        DROP TABLE IF EXISTS users;
    """))
