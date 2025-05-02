# scripts/save_cache.py

import os
import argparse
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, WhisperProcessor, WhisperForConditionalGeneration
from sentence_transformers import SentenceTransformer

MARKER_PATH = "/models/.cache_complete"

parser = argparse.ArgumentParser()
parser.add_argument("--force", action="store_true", help="Force regeneration of cached models")
args = parser.parse_args()

if os.path.exists(MARKER_PATH) and not args.force:
    print("Model cache already exists. Skipping save_cache.py. Use --force to override.")
    exit(0)

# Create model directories if they don't exist
os.makedirs("/models/nllb_model", exist_ok=True)
os.makedirs("/models/sentence_model", exist_ok=True)
os.makedirs("/models/whisper_tiny", exist_ok=True)

# --------------------------
# Save NLLB
# --------------------------
try:
    if not os.path.exists("/models/nllb_model/pytorch_model.bin") or args.force:
        print("Saving NLLB model...")
        tokenizer = AutoTokenizer.from_pretrained("facebook/nllb-200-distilled-600M")
        tokenizer.save_pretrained("/models/nllb_model")

        model = AutoModelForSeq2SeqLM.from_pretrained("facebook/nllb-200-distilled-600M")
        model.save_pretrained("/models/nllb_model")
    else:
        print("NLLB model already exists. Skipping.")
except Exception as e:
    print("Error downloading NLLB model:", e)
    exit(1)

# --------------------------
# Save SentenceTransformer
# --------------------------
try:
    if not os.path.exists("/models/sentence_model/config.json") or args.force:
        print("Saving SentenceTransformer (MiniLM)...")
        embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        embedder.save("/models/sentence_model")
    else:
        print("SentenceTransformer already exists. Skipping.")
except Exception as e:
    print("Error downloading sentence-transformer model:", e)
    exit(1)

# --------------------------
# Save Whisper
# --------------------------
try:
    if not os.path.exists("/models/whisper_tiny/preprocessor_config.json") or args.force:
        print("Saving Whisper model (tiny)...")
        processor = WhisperProcessor.from_pretrained("openai/whisper-tiny", task="transcribe")
        processor.save_pretrained("/models/whisper_tiny")

        model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-tiny")
        model.save_pretrained("/models/whisper_tiny")
    else:
        print("Whisper model already exists. Skipping.")
except Exception as e:
    print("Error downloading Whisper model:", e)
    exit(1)

# Write marker file
with open(MARKER_PATH, "w") as f:
    f.write("done")

print("Model cache saved successfully.")