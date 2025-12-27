import re
from typing import List

CRISIS_PATTERNS = [
    r"suicide",
    r"kill myself",
    r"hurt myself",
    r"end my life",
    r"kendime zarar",
    r"intihar",
    r"ölmek istiyorum",
    r"kendimi öldürmek",
]

DISCLAIMER = (
    "Not a medical professional. Not a diagnosis. If you are in immediate danger call local emergency services."
)


def detect_crisis(text: str) -> bool:
    lower = text.lower()
    for pattern in CRISIS_PATTERNS:
        if re.search(pattern, lower):
            return True
    return False


def crisis_response(country_resources: dict) -> str:
    emergency = country_resources.get("emergency_number", "112")
    crisis_lines = country_resources.get("crisis_lines", [])
    lines = [
        DISCLAIMER,
        "We detected language about being unsafe. Please contact emergency services immediately.",
        f"Emergency number: {emergency}",
    ]
    if crisis_lines:
        lines.append("Crisis hotlines:")
        lines.extend([f"- {line}" for line in crisis_lines])
    lines.append("You can also reach out to someone you trust nearby right now.")
    return "\n".join(lines)
