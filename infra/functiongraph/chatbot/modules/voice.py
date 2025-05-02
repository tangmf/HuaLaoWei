# modules/voice.py

import os
import torch

import librosa
from transformers import WhisperProcessor, WhisperForConditionalGeneration

class WhisperTranscriber:
    def __init__(self):
        model_path = os.getenv("WHISPER_MODEL_PATH")
        self.processor = WhisperProcessor.from_pretrained(model_path, task="transcribe", local_files_only=True)
        self.model = WhisperForConditionalGeneration.from_pretrained(model_path, local_files_only=True)
        self.model.generation_config.forced_decoder_ids = None

        # Use GPU if available
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)

    def transcribe(self, audio_path):
        # Load and preprocess audio
        audio_array, sampling_rate = librosa.load(audio_path, sr=16000)  # Whisper expects 16kHz

        # Prepare input features
        inputs = self.processor(audio_array, sampling_rate=16000, return_tensors="pt")
        input_features = inputs.input_features.to(self.device)

        # Generate prediction
        predicted_ids = self.model.generate(input_features)

        # Decode transcription
        transcription = self.processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
        
        return transcription
