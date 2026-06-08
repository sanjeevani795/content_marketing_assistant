import re
from typing import TypedDict


class SafetyAssessment(TypedDict):
    blocked: bool
    category: str
    reason: str
    response: str


DISALLOWED_PATTERNS: dict[str, list[str]] = {
    "explosives": [
        r"\bbomb\b",
        r"\bexplosive\b",
        r"\bmolotov\b",
        r"\bdetonator\b",
        r"\bpipe bomb\b",
    ],
    "weapons": [
        r"\bghost gun\b",
        r"\bsilencer\b",
        r"\bmake a gun\b",
        r"\bbuild a weapon\b",
    ],
    "malware": [
        r"\bmalware\b",
        r"\bransomware\b",
        r"\bkeylogger\b",
        r"\bcredential stealer\b",
        r"\bvirus\b",
    ],
    "cybercrime": [
        r"\bphishing\b",
        r"\bddos\b",
        r"\bsteal passwords?\b",
        r"\bhack (?:into|an|a)\b",
    ],
}


def assess_request_safety(user_query: str) -> SafetyAssessment:
    normalized = user_query.lower().strip()

    for category, patterns in DISALLOWED_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, normalized):
                return {
                    "blocked": True,
                    "category": category,
                    "reason": f"Matched unsafe pattern `{pattern}` in category `{category}`.",
                    "response": (
                        "I can't help with instructions for weapons, explosives, malware, or other harmful activity. "
                        "If your goal is safety, I can help with prevention, legal safety guidance, emergency preparedness, "
                        "or high-level educational information that does not enable harm."
                    ),
                }

    return {
        "blocked": False,
        "category": "",
        "reason": "",
        "response": "",
    }
