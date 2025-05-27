"""
speech.py

A core module for the HuaLaoWei municipal chatbot.
Handles audio transcription using a locally loaded Whisper model.

Author: Fleming Siow
Date: 3rd May 2025
"""

# --------------------------------------------------------
# Imports
# --------------------------------------------------------

import logging
import requests
from config.config import config

# --------------------------------------------------------
# Logger Setup
# --------------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --------------------------------------------------------
# Speech Module
# --------------------------------------------------------

class SpeechModule:
    """
    SpeechModule handles speech-to-text transcription using a pre-trained Whisper model.
    """

    def __init__(self):
        self.env = config.env

        try:
            self.stt_url = config.ai_models.chatbot.speech.stt.url
        except AttributeError:
            raise ValueError("Speech to Text model url missing in config")

        logger.info(f"Loading Speech to Text model from: {self.stt_url}")

    def transcribe(self, audio_path: str) -> str:
        """
        Transcribe an audio file into text.

        Args:
            audio_path (str): Path to the audio file to be transcribed.

        Returns:
            str: The transcribed text output.
        """
        logger.info(f"Transcribing audio file: {audio_path}")

        try:
            with open(audio_path, "rb") as audio_file:
                response = requests.post(self.stt_url, file=audio_file)
                response.raise_for_status()
                transcription = response.json().get("transcription", "")
                logger.info(f"Transcription result: {transcription}")
                return transcription

        except Exception as e:
            logger.error(f"Failed to transcribe audio: {str(e)}")
            return "[Transcription Error] Unable to process the audio file."
