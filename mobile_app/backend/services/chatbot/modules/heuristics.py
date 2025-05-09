"""
heuristics.py

A core module for the HuaLaoWei municipal chatbot.
Provides basic heuristic filters to detect and reject gibberish or malformed inputs.

Author: Fleming Siow
Date: 3rd May 2025
"""

# --------------------------------------------------------
# Imports
# --------------------------------------------------------

import re

# --------------------------------------------------------
# Heuristic Filter
# --------------------------------------------------------

class HeuristicFilter:
    """
    HeuristicFilter applies lightweight rules to identify nonsensical or invalid text inputs.

    Methods include checks for:
    - Extreme consonant-to-vowel ratio
    - Repeated character sequences
    - High non-alphabetic character ratio
    """

    def is_gibberish(self, text: str) -> bool:
        """
        Determine whether the input text is likely to be gibberish.

        Args:
            text (str): Input text to evaluate.

        Returns:
            bool: True if the text is detected as gibberish, False otherwise.
        """
        text = text.strip()
        return (
            not text
            or len(re.findall(r"\w", text)) < 2
            or re.fullmatch(r"[\W_]+", text)
            or self.has_extreme_consonant_ratio(text)
            or self.has_repeated_sequences(text)
            or self.has_high_nonalpha_ratio(text)
        )

    def has_extreme_consonant_ratio(self, text: str) -> bool:
        """
        Check if the consonant-to-vowel ratio is abnormally high.

        Args:
            text (str): Input text.

        Returns:
            bool: True if ratio is extreme, False otherwise.
        """
        vowels = len(re.findall(r"[aeiouAEIOU]", text))
        consonants = len(re.findall(r"[bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ]", text))
        return vowels == 0 or (consonants / max(vowels, 1)) > 7

    def has_repeated_sequences(self, text: str) -> bool:
        """
        Check if the text contains repeated character sequences (2 to 4 characters).

        Args:
            text (str): Input text.

        Returns:
            bool: True if repeated patterns are detected, False otherwise.
        """
        return bool(re.search(r"(.{2,4})\1{2,}", text))

    def has_high_nonalpha_ratio(self, text: str) -> bool:
        """
        Check if the proportion of non-alphabetic characters is too high.

        Args:
            text (str): Input text.

        Returns:
            bool: True if non-alphabetic characters exceed 50%, False otherwise.
        """
        if not text:
            return False
        non_alpha_count = sum(1 for ch in text if not ch.isalpha())
        return (non_alpha_count / len(text)) > 0.5
