import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    consent = Column(Boolean, default=False)

    sessions = relationship("Session", back_populates="user")


class Session(Base):
    __tablename__ = "sessions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    language = Column(String, default="TR")
    country = Column(String, default="TR")
    age_band = Column(String, default="18+")
    created_at = Column(DateTime, default=datetime.utcnow)
    consent = Column(Boolean, default=False)

    user = relationship("User", back_populates="sessions")
    messages = relationship("Message", back_populates="session")
    questionnaire_responses = relationship("QuestionnaireResponse", back_populates="session")
    audit_logs = relationship("AuditLog", back_populates="session")


class Message(Base):
    __tablename__ = "messages"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id"))
    sender = Column(String)
    content = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("Session", back_populates="messages")


class QuestionnaireResponse(Base):
    __tablename__ = "questionnaire_responses"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id"))
    questionnaire = Column(String)
    question_index = Column(Integer)
    score = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("Session", back_populates="questionnaire_responses")


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id"))
    event = Column(String)
    detail = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("Session", back_populates="audit_logs")
