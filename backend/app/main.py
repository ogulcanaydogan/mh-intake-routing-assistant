from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app import schemas, safety, questionnaires, routing, resources as resource_loader
from app.database import SessionLocal, engine, Base
from app.models import User, Session as DBSession, Message, QuestionnaireResponse, AuditLog
from app.llm import get_llm_client
from app.config import DISCLAIMER
import uuid

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mental Health Intake + Routing Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_disclaimer_header(request, call_next):
    response = await call_next(request)
    response.headers["X-Disclaimer"] = DISCLAIMER
    return response


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/session/start", response_model=schemas.StartSessionResponse)
def start_session(payload: schemas.StartSessionRequest, db: Session = Depends(get_db)):
    user = None
    if payload.email:
        user = db.query(User).filter(User.email == payload.email).first()
        if not user:
            user = User(email=payload.email, consent=payload.consent)
            db.add(user)
            db.commit()
            db.refresh(user)
    session = DBSession(
        user_id=user.id if user else None,
        language=payload.language,
        country=payload.country,
        age_band=payload.age_band,
        consent=payload.consent,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    db.add(AuditLog(session_id=session.id, event="session_started", detail=payload.dict()))
    db.commit()
    return schemas.StartSessionResponse(session_id=str(session.id), disclaimer=DISCLAIMER)


@app.post("/message", response_model=schemas.MessageResponse)
def process_message(payload: schemas.MessageRequest, db: Session = Depends(get_db)):
    session = db.query(DBSession).get(uuid.UUID(payload.session_id))
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    db.add(Message(session_id=session.id, sender="user", content=payload.message))
    db.commit()

    country_resources = resource_loader.load_resources(session.country)

    if safety.detect_crisis(payload.message):
        response_text = safety.crisis_response(country_resources)
        db.add(AuditLog(session_id=session.id, event="crisis_override", detail={"message": payload.message}))
        db.commit()
        return schemas.MessageResponse(
            intent="crisis",
            user_message=response_text,
            extracted_entities={},
            next_action={"type": "stop", "payload": {}},
        )

    llm = get_llm_client()
    llm_result = llm.generate(payload.message)
    db.add(AuditLog(session_id=session.id, event="llm_called", detail=llm_result))
    db.commit()
    return schemas.MessageResponse(**llm_result)


@app.get("/questionnaire/next", response_model=schemas.QuestionnaireNextResponse)
def questionnaire_next(session_id: str, questionnaire: str, db: Session = Depends(get_db)):
    session = db.query(DBSession).get(uuid.UUID(session_id))
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    questions = questionnaires.get_questionnaire(questionnaire)
    answered_indices = {r.question_index for r in session.questionnaire_responses if r.questionnaire == questionnaire}
    for idx, question in enumerate(questions):
        if idx not in answered_indices:
            return schemas.QuestionnaireNextResponse(questionnaire=questionnaire, question_index=idx, question=question)
    raise HTTPException(status_code=404, detail="No more questions")


@app.post("/questionnaire/answer")
def questionnaire_answer(payload: schemas.QuestionnaireAnswerRequest, db: Session = Depends(get_db)):
    session = db.query(DBSession).get(uuid.UUID(payload.session_id))
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    questions = questionnaires.get_questionnaire(payload.questionnaire)
    if payload.question_index >= len(questions):
        raise HTTPException(status_code=400, detail="Invalid question index")
    db.add(
        QuestionnaireResponse(
            session_id=session.id,
            questionnaire=payload.questionnaire,
            question_index=payload.question_index,
            score=payload.score,
        )
    )
    db.commit()
    return {"status": "recorded"}


@app.get("/route", response_model=schemas.RouteResponse)
def compute_route(session_id: str, db: Session = Depends(get_db)):
    session = db.query(DBSession).get(uuid.UUID(session_id))
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    phq9_scores = [r.score for r in session.questionnaire_responses if r.questionnaire.lower() == "phq9"]
    gad7_scores = [r.score for r in session.questionnaire_responses if r.questionnaire.lower() == "gad7"]
    phq9_total = sum(phq9_scores)
    gad7_total = sum(gad7_scores)
    result = routing.route_user(phq9_total, gad7_total, session.age_band)
    db.add(AuditLog(session_id=session.id, event="routing", detail=result))
    db.commit()
    return schemas.RouteResponse(
        bucket=result["bucket"],
        recommendation=result["recommendation"],
        scores=result["scores"],
    )


@app.get("/resources", response_model=schemas.ResourceEntry)
def get_resources(country: str = "tr"):
    return resource_loader.load_resources(country)


@app.get("/export", response_model=schemas.ExportResponse)
def export_data(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    sessions = db.query(DBSession).filter(DBSession.user_id == user.id).all()
    session_ids = [s.id for s in sessions]
    messages = db.query(Message).filter(Message.session_id.in_(session_ids)).all()
    responses = db.query(QuestionnaireResponse).filter(QuestionnaireResponse.session_id.in_(session_ids)).all()
    audits = db.query(AuditLog).filter(AuditLog.session_id.in_(session_ids)).all()
    return schemas.ExportResponse(
        user={"id": str(user.id), "email": user.email, "consent": user.consent},
        sessions=[{"id": str(s.id), "country": s.country, "language": s.language, "age_band": s.age_band} for s in sessions],
        messages=[{"session_id": str(m.session_id), "sender": m.sender, "content": m.content, "created_at": m.created_at.isoformat()} for m in messages],
        questionnaire_responses=[
            {
                "session_id": str(r.session_id),
                "questionnaire": r.questionnaire,
                "question_index": r.question_index,
                "score": r.score,
            }
            for r in responses
        ],
        audit_logs=[{"session_id": str(a.session_id), "event": a.event, "detail": a.detail, "created_at": a.created_at.isoformat()} for a in audits],
    )


@app.get("/")
def root():
    return {"message": "Mental Health Intake + Routing Assistant", "disclaimer": DISCLAIMER}
