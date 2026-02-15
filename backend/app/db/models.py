from __future__ import annotations

from datetime import datetime
from typing import Optional, List

from sqlalchemy import (
    String, Integer, Boolean, DateTime, ForeignKey,
    SmallInteger, Text, UniqueConstraint, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Enum as SAEnum

from app.db.base import Base


#  Enums (simples y futuros) 
AttemptStatus = SAEnum(
    "in_progress", "completed", "abandoned",
    name="attempt_status",
)

EntitlementPlan = SAEnum(
    "free", "pro", "school",
    name="entitlement_plan",
)

SessionSource = SAEnum(
    "pwa", "whatsapp", "web",
    name="session_source",
)


#  Core catalog 
class Exam(Base):
    __tablename__ = "exams"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True)  # ej: "PAES"
    name: Mapped[str] = mapped_column(String(120))

    subjects: Mapped[List["Subject"]] = relationship(back_populates="exam", cascade="all, delete-orphan")


class Subject(Base):
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    exam_id: Mapped[int] = mapped_column(ForeignKey("exams.id", ondelete="CASCADE"), index=True)
    code: Mapped[str] = mapped_column(String(32), index=True)  # ej: "M1"
    name: Mapped[str] = mapped_column(String(120))

    exam: Mapped["Exam"] = relationship(back_populates="subjects")
    topics: Mapped[List["Topic"]] = relationship(back_populates="subject", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("exam_id", "code", name="uq_subject_exam_code"),
    )


class Topic(Base):
    __tablename__ = "topics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id", ondelete="CASCADE"), index=True)
    code: Mapped[str] = mapped_column(String(32), index=True)  # ej: "ALG"
    name: Mapped[str] = mapped_column(String(120))

    subject: Mapped["Subject"] = relationship(back_populates="topics")
    questions: Mapped[List["Question"]] = relationship(back_populates="topic", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("subject_id", "code", name="uq_topic_subject_code"),
    )


#  Users / Entitlements 
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # WhatsApp-friendly (puedes usar phone como “identifier” al inicio)
    phone: Mapped[Optional[str]] = mapped_column(String(32), unique=True, index=True, nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), unique=True, index=True, nullable=True)

    name: Mapped[str] = mapped_column(String(120))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    attempts: Mapped[List["Attempt"]] = relationship(back_populates="user")
    study_sessions: Mapped[List["StudySession"]] = relationship(back_populates="user")
    progress: Mapped[List["UserProgress"]] = relationship(back_populates="user")
    entitlements: Mapped[List["UserEntitlement"]] = relationship(back_populates="user")


class UserEntitlement(Base):
    __tablename__ = "user_entitlements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)

    plan: Mapped[str] = mapped_column(EntitlementPlan, default="free", index=True)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    ends_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    meta: Mapped[dict] = mapped_column(JSONB, default=dict)

    user: Mapped["User"] = relationship(back_populates="entitlements")

    __table_args__ = (
        Index("ix_entitlements_user_active", "user_id", "is_active"),
    )


#  Questions 
class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id", ondelete="CASCADE"), index=True)

    prompt: Mapped[str] = mapped_column(Text)
    explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reading_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # 1=facil,2=medio,3=dificil
    difficulty: Mapped[int] = mapped_column(SmallInteger, default=1, index=True)

    # futuro: "mcq", "open_text", etc.
    question_type: Mapped[str] = mapped_column(String(32), default="mcq", index=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    topic: Mapped["Topic"] = relationship(back_populates="questions")
    choices: Mapped[List["QuestionChoice"]] = relationship(back_populates="question", cascade="all, delete-orphan")


class QuestionChoice(Base):
    __tablename__ = "question_choices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id", ondelete="CASCADE"), index=True)

    # "A" "B" "C" "D"
    label: Mapped[str] = mapped_column(String(1))
    text: Mapped[str] = mapped_column(Text)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False)

    question: Mapped["Question"] = relationship(back_populates="choices")

    __table_args__ = (
        UniqueConstraint("question_id", "label", name="uq_choice_question_label"),
    )


#  Attempts / Feedback 
class Attempt(Base):
    __tablename__ = "attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    exam_id: Mapped[int] = mapped_column(ForeignKey("exams.id", ondelete="RESTRICT"), index=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id", ondelete="RESTRICT"), index=True)
    topic_id: Mapped[Optional[int]] = mapped_column(ForeignKey("topics.id", ondelete="SET NULL"), index=True, nullable=True)

    status: Mapped[str] = mapped_column(AttemptStatus, default="in_progress", index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    total_questions: Mapped[int] = mapped_column(Integer, default=0)
    correct_count: Mapped[int] = mapped_column(Integer, default=0)
    score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # futuro: puntaje PAES u otro

    user: Mapped["User"] = relationship(back_populates="attempts")
    feedback_items: Mapped[List["AttemptFeedback"]] = relationship(back_populates="attempt", cascade="all, delete-orphan")


class AttemptFeedback(Base):
    __tablename__ = "attempt_feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    attempt_id: Mapped[int] = mapped_column(ForeignKey("attempts.id", ondelete="CASCADE"), index=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id", ondelete="RESTRICT"), index=True)

    # la alternativa elegida (si fue MCQ)
    selected_choice_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("question_choices.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )

    is_correct: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    # feedback “humano”/reglas (hoy)
    feedback_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # feedback IA (futuro), guardado como JSON
    ai_payload: Mapped[dict] = mapped_column(JSONB, default=dict)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    attempt: Mapped["Attempt"] = relationship(back_populates="feedback_items")


#  Study sessions / Progress 
class StudySession(Base):
    __tablename__ = "study_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)

    source: Mapped[str] = mapped_column(SessionSource, default="pwa", index=True)

    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    meta: Mapped[dict] = mapped_column(JSONB, default=dict)

    user: Mapped["User"] = relationship(back_populates="study_sessions")


class UserProgress(Base):
    __tablename__ = "user_progress"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id", ondelete="CASCADE"), index=True)

    # métricas simples, extensibles
    accuracy: Mapped[int] = mapped_column(Integer, default=0)  # 0-100
    streak: Mapped[int] = mapped_column(Integer, default=0)

    last_activity_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="progress")

    __table_args__ = (
        UniqueConstraint("user_id", "topic_id", name="uq_progress_user_topic"),
    )
