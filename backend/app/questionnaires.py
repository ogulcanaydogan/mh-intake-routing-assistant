from typing import List
from app import config


def get_questionnaire(name: str) -> List[str]:
    if name.lower() == "phq9":
        return config.PHQ9_QUESTIONS
    if name.lower() == "gad7":
        return config.GAD7_QUESTIONS
    raise ValueError("Unknown questionnaire")


def score_questionnaire(responses: List[int]) -> int:
    return sum(responses)


def bucket_for_scores(phq9: int, gad7: int) -> str:
    if phq9 >= config.PHQ9_THRESHOLDS["high"] or gad7 >= config.GAD7_THRESHOLDS["high"]:
        return "high"
    if phq9 >= config.PHQ9_THRESHOLDS["moderate"] or gad7 >= config.GAD7_THRESHOLDS["moderate"]:
        return "moderate"
    return "low"
