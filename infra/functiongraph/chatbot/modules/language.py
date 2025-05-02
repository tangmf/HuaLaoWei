# modules/language.py

import os
import langid
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM

class LanguageDetector:
    def detect(self, text):
        return langid.classify(text)

class Translator:
    def __init__(self):
        model_path = os.getenv("NLLB_MODEL_PATH")
        print(f"Loading NLLB translation model from: {model_path}")

        self.tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_path, local_files_only=True)
        self.translator = pipeline("translation", model=self.model, tokenizer=self.tokenizer)

        self.lang_map = {"zh": "zho_Hans", "ms": "msa_Latn", "ta": "tam_Taml", "en": "eng_Latn"}


    def translate(self, text, lang_code):
        if lang_code not in self.lang_map:
            return text  # fallback: skip translation
        print(f"Translating from {lang_code} to English...")
        return self.translator(text, src_lang=self.lang_map[lang_code], tgt_lang="eng_Latn")[0]["translation_text"]

    def translate_back(self, text, target_lang_code):
        if target_lang_code not in self.lang_map:
            return text  # fallback: leave in English
        tgt_lang = self.lang_map[target_lang_code]
        print(f"Translating back from English to {target_lang_code}...")
        return self.translator(text, src_lang="eng_Latn", tgt_lang=tgt_lang)[0]["translation_text"]
