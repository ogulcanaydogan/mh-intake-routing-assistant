# Mental Health Intake + Routing Assistant

This project is a safety-forward intake and routing assistant for mental health support. It prioritizes Turkey first, then the UK, then global fallback. The assistant does **not** provide diagnosis or treatment; it collects user-reported information, scores PHQ-9 and GAD-7 deterministically, and routes to appropriate resources with crisis overrides.

## Safety guardrails
- Always display: **“Not a medical professional. Not a diagnosis. If you are in immediate danger call local emergency services.”**
- Deterministic crisis detection with multilingual keywords; bypasses LLM and serves static crisis guidance with local resources.
- No diagnostic labels; neutral summaries only.

## Architecture
- Backend: FastAPI + SQLAlchemy (PostgreSQL; SQLite fallback for local tests)
- Frontend: Static HTML/JS chat UI served via nginx
- Storage: PostgreSQL (docker-compose), minimal PII separation (email on user, conversation in sessions/messages)
- LLM: pluggable interface with mock implementation by default
- Resources: Local JSON registry per country (see `backend/resources/`)

## Running locally
```bash
# backend deps
pip install -r backend/requirements.txt
uvicorn app.main:app --reload --app-dir backend
```

With Docker Compose:
```bash
docker-compose up --build
```
Backend: http://localhost:8000
Frontend: http://localhost:3000

## Key endpoints
- `POST /session/start` – start chat session (captures country, language, age band, consent, optional email)
- `POST /message` – process a chat message (crisis override or mock LLM summary)
- `GET /questionnaire/next` – fetch next PHQ-9/GAD-7 question
- `POST /questionnaire/answer` – record a score (0-3)
- `GET /route` – compute routing bucket using deterministic thresholds
- `GET /resources` – country resources
- `GET /export` – export user data by email

## Crisis detection
Deterministic keyword/regex detection for Turkish and English phrases (e.g., “kendime zarar”, “intihar”, “suicide”, “kill myself”). Crisis flow is non-LLM and returns emergency contacts.

## Questionnaires and routing
- PHQ-9 and GAD-7 questions stored in code for determinism.
- Scores summed in code, thresholds configurable in `app/config.py`.
- Routing buckets: low (self-help), moderate (professional recommended), high (urgent professional). Under 18 routes to minor-safe messaging.

## Adding countries/resources
Add a new JSON file under `backend/resources/<country>.json` with:
```json
{
  "emergency_number": "112",
  "crisis_lines": ["..."],
  "public_health": ["..."],
  "private_options": ["..."]
}
```
Then call `/resources?country=<code>`.

## Tests
Unit tests cover crisis detection, scoring, and routing logic:
```bash
cd backend
pytest
```

## Data handling
- Treats messages as sensitive; minimal PII stored separately from conversations.
- Audit logs capture routing decisions and crisis overrides.
- Export endpoint returns JSON bundle for a user email.
