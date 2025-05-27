"""
service.py

Main chatbot service entry point.

This script defines the ChatbotPipeline class for the HuaLaoWei mobile application, 
which orchestrates the full flow from user input (text or voice) to final chatbot response,
using modular components for speech-to-text, language detection and translation, 
heuristic filtering, intent classification, information retrieval, and model querying.

Author: Fleming Siow
Date: 3rd May 2025
"""

# --------------------------------------------------------
# Imports
# --------------------------------------------------------

import uuid
import logging

from fastapi import UploadFile
from typing import List, Optional

from backend.data_stores.resources import Resources
from backend.services.chatbot.modules.speech import SpeechModule
from backend.services.chatbot.modules.language import LanguageModule
from backend.services.chatbot.modules.heuristics import HeuristicFilter
from backend.services.chatbot.modules.intent import IntentRouter
from backend.services.chatbot.modules.indexer import ChatbotIndexer
from backend.services.chatbot.modules.query import QueryService
from backend.services.chatbot.modules.session import ChatSessionLogger
from backend.services.chatbot.modules.report_form import ReportFormManager

# --------------------------------------------------------
# Logger Configuration
# --------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# --------------------------------------------------------
# Chatbot Service
# --------------------------------------------------------

class ChatbotService:
    """
    ChatbotPipeline manages the end-to-end flow of processing a user's input
    (either text or voice) and generating a corresponding chatbot response.

    It uses modular components for voice transcription, language detection,
    translation, heuristics filtering, intent classification, structured chat
    history management, and model querying.
    """

    def __init__(self):
        logger.info("INITIALISING CHATBOT PIPELINE\n")

        logger.info("LOADING MODULE | Speech Service...")
        self.speech = SpeechModule()

        logger.info("LOADING MODULE | Language Detection and Translator...")
        self.language = LanguageModule()

        logger.info("LOADING MODULE | Form Manager...")
        self.report_form_manager = ReportFormManager()

        logger.info("LOADING MODULE | Heuristic Filters...")
        self.heuristics = HeuristicFilter()

        logger.info("LOADING MODULE | Intent Classifier...")
        self.intent_router = IntentRouter()

        logger.info("LOADING MODULE | Chat Session Logger...")
        self.session = ChatSessionLogger()

        logger.info("LOADING MODULE | Embedder and Indexer...")
        self.indexer = ChatbotIndexer()

        logger.info("LOADING MODULE | Model Query Engine...")
        self.query_service = QueryService()

        logger.info("\nPIPELINE INITIALISED")

    def run(self, resources: Resources, text: str = None, audio: Optional[UploadFile] = None, user_id: str = None, session_id: str = None, files: Optional[List[UploadFile]] = None):
        """
        Process user input (text or audio) through the chatbot pipeline
        and return the chatbot's response.

        Args:
            text (str, optional): Containing the user's input in text
            audio
            session_id (str, optional): Session identifier for the conversation.
            user_id (str, optional): User identifier.
            files
            
        Returns:
            str: Chatbot response.
        """
        
        if not session_id:
            session_id = str(uuid.uuid4())

        # --------------------------------------------------------
        # SPEECH TO TEXT: Converts audio to text if provided
        # --------------------------------------------------------
        if audio:
            logger.info("Transcribing voice input...")
            text = self.speech.transcribe(audio)

        if not text:
            return self._finalise_response("No input provided.", "en", session_id, user_id)

        # --------------------------------------------------------
        # LANGUAGE DETECTION & TRANSLATION: Detects the language of the input, and translate if not english
        # --------------------------------------------------------
        logger.info("Running language detection...")
        original_lang, _ = self.language.detect(text)

        if original_lang != "en":
            logger.info(f"Detected language '{original_lang}', translating to English...")
            text = self.language.translate(text=text, lang_code=original_lang)

        # --------------------------------------------------------
        # FORM FILLING STATE: Custom form filling conversation for report submission
        # --------------------------------------------------------
        if self.report_form_manager.active:
            text = text.lower()

            # If user presses the cancel button, terminate the process
            if text == "cancel":
                self.report_form_manager.cancel()
                return self._finalise_response("Okay, I have cancelled your report submission.", original_lang, session_id, user_id)
            # If user presses the manual button, direct them to the manual form instead
            if text == "manual":
                self.report_form_manager.cancel()
                return self._finalise_response("Sure, you can fill out the form manually at your convenience, by clicking the button below.", original_lang, session_id, user_id)
            # If user presses the submit button, submit their report and end the process
            if text == "submit":
                self.report_form_manager.finalise_submission(resources)
                return self._finalise_response("Thanks for the submission! Please wait patiently as we review your issue report.", original_lang, session_id, user_id)
            # If user presses the change button, redirect them to the respective stage, at which the change was requested
            if text.startswith("change"):
                field = text.replace("change ", "").strip()
                if self.report_form_manager.start_change_field(field):
                    return self._finalise_response(f"Sure! Please provide the new {field}.", original_lang, session_id, user_id)
                return self._finalise_response("Sorry, I did not understand what you want to change.", original_lang, session_id, user_id)

            # A button was not pressed (not a fixed input), so the input needs to be processed
            form_response = self.report_form_manager.receive_input(text, files)

            # If the user provides the updated data after requesting for a change
            if form_response == "updated":
                summary = self.report_form_manager.generate_summary()
                return self._finalise_response(f"Got it! Here is the updated information:\n\n{summary}\n\nYou can 'Change' a field, 'Submit' to submit, or 'Cancel' to abort.", original_lang, session_id, user_id)
            # If the user has finished the report form, but has not submitted yet
            if self.report_form_manager.is_complete():
                summary = self.report_form_manager.generate_summary()
                return self._finalise_response(f"Thanks for the information! Here is what I have gathered:\n\n{summary}\n\nWould you like to change anything? You can 'Change' a field, 'Submit' to submit, or 'Cancel' to abort.", original_lang, session_id, user_id)
            
            # Otherwise, user has not finished the form report process, so they proceed to the next question
            return self._finalise_response(self.report_form_manager.next_question(), original_lang, session_id, user_id)

        # --------------------------------------------------------
        # CHAT SESSION RETRIEVAL: Fetch existing structured chat history (based on session_id and user_id)
        # --------------------------------------------------------
        chat_messages = self.session.get_structured_messages(resources=resources, session_id=session_id, user_id=user_id)
        chat_messages.append({"role": "user", "content": text})

        # --------------------------------------------------------
        # LAYER 0 [FOLLOW-UP CHECK]: Check if the input is a follow-up query
        # --------------------------------------------------------
        is_follow_up = self.intent_router.is_follow_up(chat_messages)
        logger.info(f"Is follow-up query?: {is_follow_up}")

        # --------------------------------------------------------
        # LAYER 1 [HEURISTIC FILTER]: If not a follow-up, check for gibberish input
        # --------------------------------------------------------
        if self.heuristics.is_gibberish(text) and not is_follow_up:
            return self._finalise_response("Sorry, I could not understand that input.", original_lang, session_id, user_id)
        
        # --------------------------------------------------------
        # LAYER 2 [OUT OF SCOPE]: If not a follow-up, check if the input is out of scope (unrelated to municipal services)
        # --------------------------------------------------------
        if not self.intent_router.is_in_scope(text) and not is_follow_up:
            return self._finalise_response("This question seems unrelated to municipal services.", original_lang, session_id, user_id)
        
        # --------------------------------------------------------
        # CHAT SESSION LOGGING: If input is valid (related or a follow-up), log the user message
        # --------------------------------------------------------
        self.session.log_message(resources=resources, session_id=session_id, user_id=user_id, sender="user", message=text)

        # --------------------------------------------------------
        # LAYER 3 [INTENT CLASSIFICATION]: Classifies and routes the intent of the input text
        # --------------------------------------------------------
        intent = self.intent_router.classify_intent(text)
        logger.info(f"Classified intent: {intent}")

        # If the user requests for real-time data, or data only known to us
        if intent == "data_driven_query":
            logger.info("Running vector search with ChatbotIndexer...")
            rag_response = self.indexer.query(text)
            if isinstance(rag_response, str):
                logger.warning(f"RAG response error: {rag_response}")
                return self._finalise_response("Sorry, I could not retrieve related information at the moment.", original_lang, session_id, user_id)
            for hit in rag_response["raw_hits"]:
                doc = hit["_source"]
                logger.info(f"[Score {hit['_score']:.2f}] Issue ID {doc.get('issue_id')} — {doc.get('issue_type')} > {doc.get('issue_subtype')}")
            rag_context = "\n\n---\n\n".join(rag_response["documents"])
            response = self.query_service.ask(chat_messages, context=rag_context, is_follow_up=is_follow_up)

        # If the user asks a more broad municipal question that a general LLM would know
        elif intent == "general_query":
            logger.info("Handling general_query...")
            response = self.query_service.ask(chat_messages, is_follow_up=is_follow_up)

        # SPECIFIC: If the user specifically mentions that they want to file a report
        elif intent == "start_report":
            logger.info("Routing to custom form report conversational flow...")
            self.report_form_manager.start(session_id=session_id, user_id=user_id)
            response = "You can report any municipal issues in Singapore here. I will start the report submission process now. Would you like me to guide you through the process, or would you rather fill out the form yourself?"
        
        # FALLBACK
        else:
            logger.error("Unhandled intent encountered.")
            response = "Unhandled intent."

        # --------------------------------------------------------
        # CHAT SESSION LOGGING: Log the bot's message
        # --------------------------------------------------------
        self.session.log_message(resources=resources, session_id=session_id, user_id=user_id, sender="bot", message=response)

        return self._finalise_response(response, original_lang, session_id, user_id)

    def _finalise_response(self, response, lang, session_id, user_id):
        if lang != "en":
            logger.info(f"Translating response back to '{lang}'...")
            response = self.language.translate_back(response, lang)
        return response
