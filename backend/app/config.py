import os
from datetime import timedelta

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")
RETENTION_DAYS = int(os.getenv("RETENTION_DAYS", "30"))

PHQ9_QUESTIONS = [
    "Little interest or pleasure in doing things",
    "Feeling down, depressed, or hopeless",
    "Trouble falling or staying asleep, or sleeping too much",
    "Feeling tired or having little energy",
    "Poor appetite or overeating",
    "Feeling bad about yourself — or that you are a failure or have let yourself or your family down",
    "Trouble concentrating on things, such as reading the newspaper or watching television",
    "Moving or speaking so slowly that other people could have noticed? Or the opposite — being so fidgety or restless that you have been moving around a lot more than usual",
    "Thoughts that you would be better off dead or of hurting yourself in some way",
]

GAD7_QUESTIONS = [
    "Feeling nervous, anxious, or on edge",
    "Not being able to stop or control worrying",
    "Worrying too much about different things",
    "Trouble relaxing",
    "Being so restless that it is hard to sit still",
    "Becoming easily annoyed or irritable",
    "Feeling afraid as if something awful might happen",
]

PHQ9_THRESHOLDS = {
    "low": 0,
    "moderate": 10,
    "high": 15,
}

GAD7_THRESHOLDS = {
    "low": 0,
    "moderate": 10,
    "high": 15,
}

RETENTION_DELTA = timedelta(days=RETENTION_DAYS)

MOCK_LLM_ENABLED = os.getenv("MOCK_LLM", "true").lower() == "true"

