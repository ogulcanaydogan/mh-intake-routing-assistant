from datetime import datetime
from typing import Dict, List

from app import config
from app.questionnaires import bucket_for_scores


def _evaluate_thresholds(score: int, thresholds: Dict[str, int]) -> Dict:
    """Return a per-threshold comparison for transparency."""

    def sort_key(item):
        # Ensure deterministic order low -> moderate -> high
        return item[1]

    comparisons: List[Dict] = []
    for level, cutoff in sorted(thresholds.items(), key=sort_key):
        comparisons.append({
            "threshold": level,
            "cutoff": cutoff,
            "met": score >= cutoff,
        })

    highest_met = next((c["threshold"] for c in reversed(comparisons) if c["met"]), "low")
    return {
        "score": score,
        "comparisons": comparisons,
        "highest_met": highest_met,
    }


def route_user(phq9_score: int, gad7_score: int, age_band: str) -> dict:
    bucket = bucket_for_scores(phq9_score, gad7_score)
    recommendation = ""
    if bucket == "low":
        recommendation = (
            "Based on what you shared, here are some self-help options and public resources that may be supportive."
        )
    elif bucket == "moderate":
        recommendation = (
            "We suggest speaking with a licensed professional or trusted clinician. Here are referral options."
        )
    else:
        recommendation = (
            "We recommend connecting with professional support as soon as possible. If you feel unsafe, please use crisis resources."
        )

    if age_band.lower() == "under 18":
        recommendation += " As you are under 18, please involve a trusted guardian or appropriate youth service."
        bucket = f"{bucket}_minor"

    phq9_explanation = _evaluate_thresholds(phq9_score, config.PHQ9_THRESHOLDS)
    gad7_explanation = _evaluate_thresholds(gad7_score, config.GAD7_THRESHOLDS)

    decision_basis = "phq9"
    if bucket.startswith("high"):
        decision_basis = "phq9" if phq9_explanation["highest_met"] == "high" else "gad7"
    elif bucket.startswith("moderate"):
        decision_basis = "phq9" if phq9_explanation["highest_met"] == "moderate" else "gad7"

    return {
        "bucket": bucket,
        "recommendation": recommendation,
        "scores": {"phq9": phq9_score, "gad7": gad7_score},
        "timestamp": datetime.utcnow().isoformat(),
        "explanation": {
            "decision": {
                "selected_bucket": bucket,
                "basis": decision_basis,
                "phq9_bucket": phq9_explanation["highest_met"],
                "gad7_bucket": gad7_explanation["highest_met"],
            },
            "phq9": phq9_explanation,
            "gad7": gad7_explanation,
        },
    }
