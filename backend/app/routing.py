from datetime import datetime
from app.questionnaires import bucket_for_scores


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

    return {
        "bucket": bucket,
        "recommendation": recommendation,
        "scores": {"phq9": phq9_score, "gad7": gad7_score},
        "timestamp": datetime.utcnow().isoformat(),
    }
