"""
language.py

A core module for the HuaLaoWei municipal chatbot.
Handles language detection and translation functionalities for the chatbot.

Author: Fleming Siow
Date: 3rd May 2025
"""

# --------------------------------------------------------
# Imports
# --------------------------------------------------------

import logging
import langid
import requests
from config.config import config

# --------------------------------------------------------
# Logger Setup
# --------------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --------------------------------------------------------
# Language Module
# --------------------------------------------------------

class LanguageModule:
    """
    LanguageModule provides methods to detect language and perform
    translation between supported languages using a pre-trained NLLB model.
    """

    def __init__(self):
        self.env = config.env

        try:
            self.translate_url = config.ai_models.chatbot.translate.url
        except AttributeError:
            raise ValueError("Translation model url missing in config")

        logger.info(f"Loading translation model from: {self.translate_url}")

        # Language code mapping: langid to NLLB format
        self.lang_map = {
            "zh": "zho_Hans",   # Simplified Chinese
            "ms": "msa_Latn",   # Malay
            "ta": "tam_Taml",   # Tamil
            "en": "eng_Latn"    # English
        }

    def detect(self, query: str) -> tuple[str, float]:
        """
        Detect the language of the input query.

        Args:
            query (str): The text input to classify.

        Returns:
            tuple[str, float]: (language code, confidence score)
        """
        return langid.classify(query)

    def translate(self, query: str, lang_code: str) -> str:
        """
        Translate input text from source language to English.

        Args:
            query (str): The text to translate.
            lang_code (str): Source language code.

        Returns:
            str: Translated English text.
        """
        if lang_code not in self.lang_map:
            logger.warning(f"Unsupported source language '{lang_code}', skipping translation.")
            return query

        try:
            logger.info(f"Translating from '{lang_code}' to English...")
            payload = {"text": query, "source_lang": self.lang_map[lang_code], "target_lang": "eng_Latn"}
            response = requests.post(self.translate_url, json=payload)
            response.raise_for_status()
            translation = response.json().get("translation", "")
            return translation
        except Exception as e:
            logger.error(f"Translation to English failed: {str(e)}")
            return "[Translation Error] Unable to translate to English."

    def translate_back(self, query: str, target_lang_code: str) -> str:
        """
        Translate input text from English back to the original language.

        Args:
            query (str): The text to translate back.
            target_lang_code (str): Target language code.

        Returns:
            str: Translated text in the target language.
        """
        if target_lang_code not in self.lang_map:
            logger.warning(f"Unsupported target language '{target_lang_code}', leaving text in English.")
            return query

        try:
            tgt_lang = self.lang_map[target_lang_code]
            
            logger.info(f"Translating from English to '{target_lang_code}'...")
            payload = {"text": query, "source_lang": "eng_Latn", "target_lang": tgt_lang}
            response = requests.post(self.translate_url, json=payload)
            response.raise_for_status()
            translation = response.json().get("translation", "")
            return translation
        except Exception as e:
            logger.error(f"Translation back to '{target_lang_code}' failed: {str(e)}")
            return "[Translation Error] Unable to translate back to original language."
