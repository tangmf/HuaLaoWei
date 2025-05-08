"""
pipeline.py

Main chatbot pipeline entry point.

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

from modules.speech import SpeechModule
from modules.language import LanguageModule
from modules.heuristics import HeuristicFilter
from modules.intent import IntentRouter
from modules.indexer import ChatbotIndexer
from modules.query import QueryService
from modules.session import ChatSessionLogger
from modules.report_form import ReportFormManager

# --------------------------------------------------------
# Logger Configuration
# --------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# --------------------------------------------------------
# Chatbot Pipeline
# --------------------------------------------------------

class ChatbotPipeline:
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

    def run(self, input=None, session_id=None, user_id=None):
        """
        Process user input (text or audio) through the chatbot pipeline
        and return the chatbot's response.

        Args:
            input (dict, optional): Dict containing the user's input in text, voice or/and any added documents.
            session_id (str, optional): Session identifier for the conversation.
            user_id (str, optional): User identifier.

        Returns:
            str: Chatbot response.
        """

        if not session_id:
            session_id = str(uuid.uuid4())

        # Extract user input
        input_text, input_audio, input_documents = self._extract_input(input)

        # VOICE INPUT: Convert audio to text if provided
        if input_audio:
            input_text = self._handle_audio_input(input_audio)

        if not input_text:  
            return self._finalise_response("No input provided.", "en", session_id, user_id)

        # LANGUAGE DETECTION: Detect the language of the input
        original_lang = self._detect_language(input_text)

        # LANGUAGE TRANSLATION: Translate to English if not already in English
        if original_lang != "en":
            input_text = self._translate_to_english(input_text, original_lang)

        # FORM FILLING STATE: Custiom form filling conversation for report submission
        if self.report_form_manager.active:
            return self._finalise_response(
                self._handle_form_flow(input_text, input_documents),
                original_lang, session_id, user_id
            )

        # CHAT SESSION RETRIEVAL: Fetch existing structured chat history (based on session_id and user_id)
        chat_messages = self._retrieve_chat_history(session_id, user_id, input_text)

        # LAYER 0 [FOLLOW-UP CHECK]: Check if the input is a follow-up query
        is_follow_up = self._check_follow_up(chat_messages)

        # LAYER 1 [HEURISTIC FILTER]: If not a follow-up, check for gibberish input
        if self._apply_heuristics(input_text, is_follow_up, original_lang):
            return self._finalise_response(
                "Sorry, I could not understand that input.",
                original_lang, session_id, user_id
            )

        # LAYER 2 [OUT OF SCOPE]: If not a follow-up, check if the input is out of scope (unrelated to municipal services)
        if not self.intent_router.is_in_scope(input_text) and not is_follow_up:
            return self._finalise_response(
                "This question seems unrelated to municipal services.",
                original_lang, session_id, user_id
            )

        # CHAT SESSION LOGGING: If input is valid (related or a follow-up), log the user message
        self._log_user_message(session_id, user_id, input_text)

        # LAYER 3 [INTENT CLASSIFICATION]: Classifies and routes the intent of the input text
        intent = self._classify_intent(input_text)

        # QUERY LLM: Retrieve response from the chatbot based on classified intent
        response = self._generate_response_by_intent(intent, input_text, chat_messages, is_follow_up, session_id, user_id)

        return self._finalise_response(response, original_lang, session_id, user_id)

    def _extract_input(self, input):
        return (
            input.get("text") if isinstance(input, dict) else None,
            input.get("audio") if isinstance(input, dict) else None,
            input.get("documents") if isinstance(input, dict) else None
        )

    def _handle_audio_input(self, audio):
        logger.info("Transcribing voice input...")
        return self.speech.transcribe(audio)

    def _detect_language(self, text):
        logger.info("Running language detection...")
        lang, _ = self.language.detect(text)
        return lang

    def _translate_to_english(self, text, lang):
        logger.info(f"Detected language '{lang}', translating to English...")
        return self.language.translate(text=text, lang_code=lang)

    def _handle_form_flow(self, text, documents):
        if text.lower() == "cancel":
            self.report_form_manager.cancel()
            return "Okay, I have cancelled your report submission."
        if text.lower() == "manual":
            self.report_form_manager.cancel()
            return "Sure, you can fill out the form manually at your convenience, by clicking the button below."
        if text.lower() == "submit":
            self.report_form_manager.finalise_submission()
            return "Thanks for the submission! Please wait patiently as we review your issue report."
        if text.lower().startswith("change"):
            field = text.lower().replace("change ", "").strip()
            if self.report_form_manager.start_change_field(field):
                return f"Sure! Please provide the new {field}."
            return "Sorry, I did not understand what you want to change."

        form_response = self.report_form_manager.receive_input(text, documents)
        if form_response == "updated":
            summary = self.report_form_manager.generate_summary()
            return f"Got it! Here is the updated information:\n\n{summary}\n\nYou can 'Change' a field, 'Submit' to submit, or 'Cancel' to abort."
        if self.report_form_manager.is_complete():
            summary = self.report_form_manager.generate_summary()
            return f"Thanks for the information! Here is what I have gathered:\n\n{summary}\n\nWould you like to change anything? You can 'Change' a field, 'Submit' to submit, or 'Cancel' to abort."
        return self.report_form_manager.next_question()

    def _retrieve_chat_history(self, session_id, user_id, text):
        chat = self.session.get_structured_messages(session_id, user_id)
        chat.append({"role": "user", "content": text})
        return chat

    def _check_follow_up(self, chat_messages):
        is_follow_up = self.intent_router.is_follow_up(chat_messages)
        logger.info(f"Is follow-up query?: {is_follow_up}")
        return is_follow_up

    def _apply_heuristics(self, text, is_follow_up, lang):
        return self.heuristics.is_gibberish(text) and not is_follow_up

    def _classify_intent(self, text):
        intent = self.intent_router.classify_intent(text)
        logger.info(f"Classified intent: {intent}")
        return intent

    def _generate_response_by_intent(self, intent, text, chat_messages, is_follow_up, session_id, user_id):
        if intent == "data_driven_query":
            logger.info("Running vector search with ChatbotIndexer...")
            rag_response = self.indexer.query(text)
            if isinstance(rag_response, str):
                logger.warning(f"RAG response error: {rag_response}")
                return "Sorry, I could not retrieve related information at the moment."
            for hit in rag_response["raw_hits"]:
                doc = hit["_source"]
                logger.info(f"[Score {hit['_score']:.2f}] Issue ID {doc.get('issue_id')} — {doc.get('issue_type')} > {doc.get('issue_subtype')}")
            rag_context = "\n\n---\n\n".join(rag_response["documents"])
            return self.query_service.ask(chat_messages, context=rag_context, is_follow_up=is_follow_up)

        if intent == "general_query":
            logger.info("Handling general_query...")
            return self.query_service.ask(chat_messages, is_follow_up=is_follow_up)

        if intent == "start_report":
            logger.info("Routing to custom form report conversational flow...")
            self.report_form_manager.start(session_id=session_id, user_id=user_id)
            return "You can report any municipal issues in Singapore here. I will start the report submission process now. Would you like me to guide you through the process, or would you rather fill out the form yourself?"

        logger.error("Unhandled intent encountered.")
        return "Unhandled intent."

    def _finalise_response(self, response, lang, session_id, user_id):
        if lang != "en":
            logger.info(f"Translating response back to '{lang}'...")
            response = self.language.translate_back(response, lang)
        self._log_bot_response(session_id, user_id, response)
        return response

    def _log_user_message(self, session_id, user_id, text):
        self.session.log_message(session_id=session_id, user_id=user_id, sender="user", message=text)

    def _log_bot_response(self, session_id, user_id, text):
        self.session.log_message(session_id=session_id, user_id=user_id, sender="bot", message=text)

# --------------------------------------------------------
# Entry Point
# --------------------------------------------------------

if __name__ == "__main__":
    pipeline = ChatbotPipeline()
    result = pipeline.run(input_text="这个垃圾桶已经满了")
    logger.info(f"Chatbot Reply: {result}")
