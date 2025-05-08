"""
save_cache.py

Downloads and saves required models for local caching to speed up application startup.
Supports parallel downloads for improved efficiency.

Author: Fleming Siow
Date: 3rd May 2025
"""

# --------------------------------------------------------
# Imports
# --------------------------------------------------------

import os
import argparse
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, WhisperProcessor, WhisperForConditionalGeneration
from sentence_transformers import SentenceTransformer, CrossEncoder

# --------------------------------------------------------
# Logger Setup
# --------------------------------------------------------

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# --------------------------------------------------------
# Constants
# --------------------------------------------------------

MODEL_DIR = "models"
MARKER_PATH = os.path.join(MODEL_DIR, ".cache_complete")
NLLB_MODEL_DIR = os.path.join(MODEL_DIR, "nllb_model")
SENTENCE_MODEL_DIR = os.path.join(MODEL_DIR, "sentence_model")
WHISPER_MODEL_DIR = os.path.join(MODEL_DIR, "whisper_tiny")
FLASH_RERANKER_DIR = os.path.join(MODEL_DIR, "flash_reranker")

# --------------------------------------------------------
# Argument Parser
# --------------------------------------------------------

parser = argparse.ArgumentParser(description="Download and cache models locally.")
parser.add_argument("--force", action="store_true", help="Force re-download even if cache exists.")
args = parser.parse_args()

# --------------------------------------------------------
# Model Saving Functions
# --------------------------------------------------------

def save_nllb_model():
    """
    Download and save NLLB translation model.
    """
    if not os.path.exists(os.path.join(NLLB_MODEL_DIR, "pytorch_model.bin")) or args.force:
        logger.info("Saving NLLB model...")
        tokenizer = AutoTokenizer.from_pretrained("facebook/nllb-200-distilled-600M")
        tokenizer.save_pretrained(NLLB_MODEL_DIR)
        model = AutoModelForSeq2SeqLM.from_pretrained("facebook/nllb-200-distilled-600M")
        model.save_pretrained(NLLB_MODEL_DIR)
    else:
        logger.info("NLLB model already exists. Skipping.")

def save_sentence_transformer():
    """
    Download and save SentenceTransformer model.
    """
    if not os.path.exists(os.path.join(SENTENCE_MODEL_DIR, "config.json")) or args.force:
        logger.info("Saving SentenceTransformer (MiniLM)...")
        embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        embedder.save(SENTENCE_MODEL_DIR)
    else:
        logger.info("SentenceTransformer model already exists. Skipping.")

def save_whisper_model():
    """
    Download and save Whisper speech-to-text model.
    """
    if not os.path.exists(os.path.join(WHISPER_MODEL_DIR, "preprocessor_config.json")) or args.force:
        logger.info("Saving Whisper model (tiny)...")
        processor = WhisperProcessor.from_pretrained("openai/whisper-tiny", task="transcribe")
        processor.save_pretrained(WHISPER_MODEL_DIR)
        model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-tiny")
        model.save_pretrained(WHISPER_MODEL_DIR)
    else:
        logger.info("Whisper model already exists. Skipping.")

def save_flash_reranker():
    """
    Download and save FlashReranker model.
    """
    if not os.path.exists(os.path.join(FLASH_RERANKER_DIR, "config.json")) or args.force:
        logger.info("Saving Flash Reranker (cross-encoder/ms-marco-MiniLM-L-12-v2)...")
        model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-12-v2")
        model.save(FLASH_RERANKER_DIR)
    else:
        logger.info("Flash Reranker model already exists. Skipping.")


# --------------------------------------------------------
# Helper Functions
# --------------------------------------------------------

def create_directories():
    """
    Create model directories if they do not already exist.
    """
    os.makedirs(NLLB_MODEL_DIR, exist_ok=True)
    os.makedirs(SENTENCE_MODEL_DIR, exist_ok=True)
    os.makedirs(WHISPER_MODEL_DIR, exist_ok=True)
    os.makedirs(FLASH_RERANKER_DIR, exist_ok=True)

def mark_completion():
    """
    Create a marker file indicating that caching was completed successfully.
    """
    with open(MARKER_PATH, "w") as f:
        f.write("done")

# --------------------------------------------------------
# Main Process
# --------------------------------------------------------

def main():
    """
    Main entry point for caching all required models.
    """

    if os.path.exists(MARKER_PATH) and not args.force:
        logger.info("Model cache already exists. Skipping save_cache.py. Use --force to override.")
        return

    create_directories()

    save_tasks = [
        ("NLLB model", save_nllb_model),
        ("SentenceTransformer model", save_sentence_transformer),
        ("Whisper model", save_whisper_model),
        ("Flash Reranker model", save_flash_reranker),
    ]

    errors = []

    with ThreadPoolExecutor(max_workers=4) as executor:
        future_to_task = {executor.submit(task_func): task_name for task_name, task_func in save_tasks}

        for future in as_completed(future_to_task):
            task_name = future_to_task[future]
            try:
                future.result()
                logger.info(f"{task_name} cached successfully.")
            except Exception as e:
                logger.error(f"Failed to save {task_name}: {e}")
                errors.append(task_name)

    if errors:
        logger.error(f"Failed to cache the following models: {errors}")
        exit(1)

    mark_completion()
    logger.info("All models cached successfully.")

if __name__ == "__main__":
    main()
