# modules/heuristics.py

import re

class HeuristicFilter:
    def is_gibberish(self, text):
        text = text.strip()
        return (
            not text or
            len(re.findall(r"\w", text)) < 2 or
            re.fullmatch(r"[\W_]+", text)
        )
