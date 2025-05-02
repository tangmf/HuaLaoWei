from modules.voice import WhisperTranscriber
from modules.language import LanguageDetector, Translator
from modules.heuristics import HeuristicFilter
from modules.intent import IntentRouter
from modules.indexer import ChatbotIndexer
from modules.query_model import QueryModel
from modules.session_logger import ChatSessionLogger
from modules.intent_utils import is_intent, match_intent
import uuid
import logging

# Basic logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

class ChatbotPipeline:
    def __init__(self):
        logger.info("Initializing chatbot pipeline...")

        logger.info("Loading Whisper (speech-to-text)...")
        self.transcriber = WhisperTranscriber()

        logger.info("Loading language detection + NLLB translator...")
        self.lang_detector = LanguageDetector()
        self.translator = Translator()

        logger.info("Loading heuristic filters...")
        self.heuristics = HeuristicFilter()

        logger.info("Loading intent routing...")
        self.intent_router = IntentRouter()

        logger.info("Loading chat session logger...")
        self.logger = ChatSessionLogger()

        logger.info("Loading Chatbot indexer...")
        self.indexer = ChatbotIndexer()

        logger.info("Loading model query...")
        self.query_model = QueryModel()

        logger.info("Pipeline ready.")

    def run(self, input_text=None, input_audio_path=None, session_id=None, user_id=None):
        if not session_id:
            session_id = str(uuid.uuid4())

        # --------------------------------------------------------
        # VOICE INPUT
        # --------------------------------------------------------
        if input_audio_path:
            logger.info("Transcribing voice input...")
            input_text = self.transcriber.transcribe(input_audio_path)

        if not input_text:
            return "No input provided."

        # --------------------------------------------------------
        # LANGUAGE DETECTION
        # --------------------------------------------------------
        original_lang = "en"  # default fallback

        logger.info("Running language detection...")
        lang, prob = self.lang_detector.detect(input_text)
        original_lang = lang

        # --------------------------------------------------------
        # LANGUAGE TRANSLATION (To English)
        # --------------------------------------------------------
        if lang != "en":
            logger.info(f"Detected non-English ({lang}), translating to English...")
            input_text = self.translator.translate(text=input_text, lang_code=lang)

        # --------------------------------------------------------
        # SESSION RETRIEVAL: STRUCTURED CHAT HISTORY
        # --------------------------------------------------------
        chat_messages = self.logger.get_structured_messages(session_id, user_id)

        # Append current user input to the messages
        chat_messages.append({"role": "user", "content": input_text})
        # logger.info(f"Chat history: {chat_messages}")

        # --------------------------------------------------------
        # LAYER 0: FOLLOW-UP CHECK
        # --------------------------------------------------------
        is_follow_up = self.intent_router.is_follow_up(chat_messages)
        logger.info(f"Is it a followup?: {is_follow_up}")

        # --------------------------------------------------------
        # LAYER 1: HEURISTIC FILTERS
        # --------------------------------------------------------
        if self.heuristics.is_gibberish(input_text) and not is_follow_up:
            return self.translator.translate_back(
                "Sorry, I couldn't understand that input.", original_lang
            )

        # --------------------------------------------------------
        # LAYER 2: OUT OF SCOPE (Embeddings + Classifier)
        # --------------------------------------------------------
        if not self.intent_router.is_in_scope(input_text) and not is_follow_up:
            return self.translator.translate_back(
                "This question seems unrelated to municipal services.",
                original_lang
            )

        # --------------------------------------------------------
        # SESSION LOGGING: USER INPUT
        # --------------------------------------------------------
        self.logger.log_message(
            session_id=session_id,
            user_id=user_id,
            sender="user",
            message=input_text
        )

        # --------------------------------------------------------
        # LAYER 3: INTENT CLASSIFICATION (LLM Few Shot Prompting)
        # --------------------------------------------------------
        intent = self.intent_router.classify_intent(input_text)
        logger.info(f"Classified intent: {intent}")

        # Canonicalize + Match Robustly
        matched_intent = match_intent(intent)
        logger.info(f"Matched intent: {matched_intent}")

        # --------------------------------------------------------
        # MODEL QUERY
        # --------------------------------------------------------
                                                                                                                                                                                    
        # Intent: Data Driven Query (RAG)
        if is_intent(intent, "data_driven_query"):
            logger.info("Running vector search via ChatbotIndexer...")
            rag_response = self.indexer.query(input_text)

            if isinstance(rag_response, str):
                logger.warning(f"RAG response error: {rag_response}")
                return self.translator.translate_back("Sorry, I could not retrieve related information at the moment.", original_lang)

            for hit in rag_response["raw_hits"]:
                doc = hit["_source"]
                logger.info(f"[Score {hit['_score']:.2f}] Issue ID {doc.get('issue_id')} — {doc.get('issue_type')} > {doc.get('issue_subtype')}")

            rag_context = "\n\n---\n\n".join(rag_response["documents"])

            logger.info("Calling QueryModel with chat history and RAG context...")
            response = self.query_model.ask(chat_messages, context=rag_context, is_follow_up=is_follow_up)


        # Intent: Narrow Intent
        elif is_intent(intent, "narrow_intent"):
            return "[NARROW_INTENT] was classified as the intent. Input text: " + self.translator.translate_back(
                input_text,
                original_lang
            )

        # Intent: General Query 
        elif is_intent(intent, "general_query"):
            response = self.query_model.ask(chat_messages, is_follow_up=is_follow_up)

        else:
            response = "Unhandled intent."

        # --------------------------------------------------------
        # TRANSLATE BACK TO ORIGINAL LANGUAGE (If needed)
        # --------------------------------------------------------
        if original_lang != "en":
            logger.info(f"Translating response back to {original_lang}")
            response = self.translator.translate_back(response, original_lang)

        # --------------------------------------------------------
        # SESSION LOGGING: BOT RESPONSE
        # --------------------------------------------------------
        self.logger.log_message(
            session_id=session_id,
            user_id=user_id,
            sender="bot",
            message=response
        )

        return response


if __name__ == "__main__":
    pipeline = ChatbotPipeline()

    result = pipeline.run(input_text="这个垃圾桶已经满了")
    logger.info("Chatbot Reply:", result)
