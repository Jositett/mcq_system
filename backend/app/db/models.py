from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date, Text, Table
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(String, nullable=False)
    profile_picture = Column(String, nullable=True)  # Path to profile picture file
    instructor = relationship('Instructor', back_populates='user', uselist=False)
    student = relationship('Student', back_populates='user', uselist=False)
    face_images = relationship('FaceImage', back_populates='user', cascade='all, delete-orphan')

class FaceImage(Base):
    __tablename__ = 'face_images'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    image_data = Column(String, nullable=False)  # Store as base64-encoded string (alternatively, use LargeBinary for BLOB)
    embedding = Column(String, nullable=True)    # Store as JSON string or comma-separated floats
    created_at = Column(Date, nullable=False)
    user = relationship('User', back_populates='face_images')


class Instructor(Base):
    __tablename__ = 'instructors'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    department = Column(String)
    user = relationship('User', back_populates='instructor')
    batches = relationship('Batch', back_populates='instructor')

class Student(Base):
    __tablename__ = 'students'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    batch_id = Column(Integer, ForeignKey('batches.id'))
    roll_number = Column(String)
    dob = Column(Date)
    user = relationship('User', back_populates='student')
    batch = relationship('Batch', back_populates='students')
    attendance = relationship('Attendance', back_populates='student')

class Batch(Base):
    __tablename__ = 'batches'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    instructor_id = Column(Integer, ForeignKey('instructors.id'))
    instructor = relationship('Instructor', back_populates='batches')
    students = relationship('Student', back_populates='batch')
    tests = relationship('Test', back_populates='batch')

class Test(Base):
    __tablename__ = 'tests'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    batch_id = Column(Integer, ForeignKey('batches.id'))
    scheduled_at = Column(String)
    batch = relationship('Batch', back_populates='tests')
    questions = relationship('Question', back_populates='test')

class Question(Base):
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey('tests.id'))
    question_text = Column(Text, nullable=False)
    question_type = Column(String, nullable=False)
    options = Column(Text)
    correct_answer = Column(Text)
    test = relationship('Test', back_populates='questions')

class Attendance(Base):
    __tablename__ = 'attendance'
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    date = Column(Date, nullable=False)
    status = Column(String, nullable=False)
    student = relationship('Student', back_populates='attendance')
