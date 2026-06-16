from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from database import Base
import enum
import datetime

class RoleEnum(str, enum.Enum):
    FRESHER = "Fresher Software Developer"
    EXPERIENCED = "Experienced Software Developer"
    ADVANCED = "Advanced Software Developer"
    TECH_LEAD = "Technical Lead"
    TECH_ARCHITECT = "Technical Architect"
    PROJECT_MANAGER = "Project Manager"
    PROGRAM_MANAGER = "Program Manager"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String) # Could map to RoleEnum
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    test_attempts = relationship("TestAttempt", back_populates="user")

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True) # e.g. OOPS, .Net, C#, ReactJS

    questions = relationship("Question", back_populates="category")

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"))
    role_level = Column(String) # Target difficulty based on RoleEnum
    question_text = Column(Text)
    practical_example = Column(Text, nullable=True) # Code snippet or example
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    category = relationship("Category", back_populates="questions")
    answers = relationship("Answer", back_populates="question")

class Answer(Base):
    __tablename__ = "answers"
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"))
    answer_text = Column(Text)
    is_correct = Column(Boolean, default=False)

    question = relationship("Question", back_populates="answers")

class TestAttempt(Base):
    __tablename__ = "test_attempts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    started_at = Column(DateTime, default=datetime.datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    score = Column(Integer, nullable=True)
    ai_summary = Column(Text, nullable=True) # Storing the AI generated feedback

    user = relationship("User", back_populates="test_attempts")
    responses = relationship("TestResponse", back_populates="attempt")
    assigned_questions = relationship("AttemptQuestion", back_populates="attempt", order_by="AttemptQuestion.position")

    @hybrid_property
    def total(self):
        return len(self.assigned_questions) if self.assigned_questions else 0

class TestResponse(Base):
    __tablename__ = "test_responses"
    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("test_attempts.id"))
    question_id = Column(Integer, ForeignKey("questions.id"))
    selected_answer_id = Column(Integer, ForeignKey("answers.id"), nullable=True) # Null if skipped/timeout

    attempt = relationship("TestAttempt", back_populates="responses")

class AttemptQuestion(Base):
    """Binds specific questions to a test attempt at creation time."""
    __tablename__ = "attempt_questions"
    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("test_attempts.id"))
    question_id = Column(Integer, ForeignKey("questions.id"))
    position = Column(Integer) # 0-indexed order within the test

    attempt = relationship("TestAttempt", back_populates="assigned_questions")
    question = relationship("Question")
