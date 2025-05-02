# app.py

from modules.voice import WhisperTranscriber
from modules.language import LanguageDetector, Translator
from backend_functions.chatbot.modules.heuristics import HeuristicFilter
from modules.intent import IntentRouter
from modules.indexer import ChatbotIndexer
from modules.query_model import QueryModel

class ChatbotPipeline:
    def __init__(self):
        print("Initializing chatbot pipeline...")

        print("Loading Whisper (speech-to-text)...")
        self.transcriber = WhisperTranscriber()

        print("Loading language detection + NLLB translator...")
        self.lang_detector = LanguageDetector()
        self.translator = Translator()

        print("Loading heuristic filters...")
        self.heuristics = HeuristicFilter()

        print("Loading intent routing...")
        self.intent_router = IntentRouter()

        print("Loading Chroma indexer...")
        self.indexer = ChatbotIndexer()

        print("Loading model query...")
        self.query_model = QueryModel()

        print("Pipeline ready.")

    def run(self, input_text=None, input_audio_path=None):
        original_lang = "en"  # default fallback

        # Step 1: Voice input
        if input_audio_path:
            print("Transcribing voice input...")
            input_text = self.transcriber.transcribe(input_audio_path)

        if not input_text:
            return "No input provided."

        # Step 2: Detect language
        print("Running language detection...")
        lang, prob = self.lang_detector.detect(input_text)
        original_lang = lang

        # Step 3: Translate to English if needed
        if lang != "en":
            print(f"Detected non-English ({lang}), translating to English...")
            input_text = self.translator.translate(text=input_text, lang_code=lang)

        # Step 4: Heuristic gibberish check
        if self.heuristics.is_gibberish(input_text):
            return self.translator.translate_back(
                "Sorry, I couldn't understand that input.", original_lang
            )

        # Step 5: Out-of-scope check
        if not self.intent_router.is_in_scope(input_text):
            return self.translator.translate_back(
                "This question seems unrelated to municipal services.",
                original_lang
            )

        # Step 6: Intent classification
        intent = self.intent_router.classify_intent(input_text)
        print(f"Classified intent: {intent}")

        # Step 7: Handle intent
        if "DATA_DRIVEN_QUERY" in intent:
            rag_response = self.indexer.query(input_text)
            documents = rag_response["documents"][0]
            metadatas = rag_response["metadatas"][0]
            
            rag_context = "\n\n---\n\n".join(documents)
            response = self.query_model.ask(input_text, rag_context)

        elif "NARROW_INTENT" in intent:
            response = "Opening report form..."

        elif "GENERAL_QUERY" in intent:
            response = self.query_model.ask(input_text)

        else:
            response = "Unhandled intent."

        # Step 8: Translate response back to original language (if needed)
        if original_lang != "en":
            print(f"Translating response back to {original_lang}")
            response = self.translator.translate_back(response, original_lang)

        return response


if __name__ == "__main__":
    pipeline = ChatbotPipeline()

    # For voice input: pipeline.run(input_audio_path="mic_input.wav")
    result = pipeline.run(input_text="这个垃圾桶已经满了")
    print("Chatbot Reply:", result)
