import re
import difflib

KNOWN_INTENTS = [
    "data_driven_query",
    "narrow_intent",
    "general_query"
]

def canonicalize(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = text.strip()
    if "_" in text or "-" in text or " " in text:
        words = re.split(r"[_\-\s]+", text)
    else:
        words = re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)', text)
    return "_".join(word.lower() for word in words if word).strip("_")

def match_intent(intent: str) -> str:
    normalized = canonicalize(intent)
    
    # Check for substring match (robustly)
    for known in KNOWN_INTENTS:
        if known in normalized:
            return known

    # Fuzzy match if substring not found
    best = difflib.get_close_matches(normalized, KNOWN_INTENTS, n=1, cutoff=0.75)
    return best[0] if best else None

def is_intent(intent: str, target: str) -> bool:
    return match_intent(intent) == canonicalize(target)
