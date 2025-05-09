"""
save_cache.py

Downloads and saves required embedding model for local caching to speed up application startup.
Supports parallel downloads for improved efficiency if ever needed.

Author: Fleming Siow
Date: 5th May 2025
"""

# --------------------------------------------------------
# Imports
# --------------------------------------------------------

import os
import argparse
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, WhisperProcessor, WhisperForConditionalGeneration
from sentence_transformers import SentenceTransformer

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
SENTENCE_MODEL_DIR = os.path.join(MODEL_DIR, "sentence_model")

# --------------------------------------------------------
# Argument Parser
# --------------------------------------------------------

parser = argparse.ArgumentParser(description="Download and cache models locally.")
parser.add_argument("--force", action="store_true", help="Force re-download even if cache exists.")
args = parser.parse_args()

# --------------------------------------------------------
# Model Saving Functions
# --------------------------------------------------------

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

# --------------------------------------------------------
# Helper Functions
# --------------------------------------------------------

def create_directories():
    """
    Create model directories if they do not already exist.
    """
    os.makedirs(SENTENCE_MODEL_DIR, exist_ok=True)

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
        ("SentenceTransformer model", save_sentence_transformer),
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
