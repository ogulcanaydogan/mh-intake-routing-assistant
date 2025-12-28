from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class StartSessionRequest(BaseModel):
    email: Optional[str] = None
    language: str = "TR"
    country: str = "TR"
    age_band: str = "18+"
    consent: bool = False


class StartSessionResponse(BaseModel):
    session_id: str
    disclaimer: str


class MessageRequest(BaseModel):
    session_id: str
    message: str


class MessageResponse(BaseModel):
    intent: str
    user_message: str
    extracted_entities: dict
    next_action: dict


class QuestionnaireNextResponse(BaseModel):
    questionnaire: str
    question_index: int
    question: str


class QuestionnaireAnswerRequest(BaseModel):
    session_id: str
    questionnaire: str
    question_index: int
    score: int = Field(ge=0, le=3)


class RouteResponse(BaseModel):
    bucket: str
    recommendation: str
    scores: dict
    crisis: bool = False
    explanation: dict = Field(default_factory=dict)


class ResourceEntry(BaseModel):
    emergency_number: str
    crisis_lines: List[str]
    public_health: List[str]
    private_options: List[str] = []


class ExportResponse(BaseModel):
    user: dict
    sessions: List[dict]
    audit_logs: List[dict]
    messages: List[dict]
    questionnaire_responses: List[dict]


class AuditLogEntry(BaseModel):
    event: str
    detail: dict
    created_at: datetime
