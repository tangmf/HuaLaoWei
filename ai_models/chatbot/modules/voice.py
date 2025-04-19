# modules/voice.py

from transformers import WhisperProcessor, WhisperForConditionalGeneration
from config import MODEL_PATHS
import librosa

class WhisperTranscriber:
    def __init__(self):
        self.processor = WhisperProcessor.from_pretrained(MODEL_PATHS["whisper"], task="transcribe", local_files_only=True)
        self.model = WhisperForConditionalGeneration.from_pretrained(MODEL_PATHS["whisper"], local_files_only=True)

        self.model.generation_config.forced_decoder_ids = None

        # Use GPU if available
        # self.device = "cuda" if torch.cuda.is_available() else "cpu"
        # model.to(device)

    def transcribe(self, audio_path):
        # Load and preprocess audio
        audio_array, sampling_rate = librosa.load(audio_path, sr=16000)  # Whisper expects 16kHz

        # Prepare input features
        inputs = self.processor(audio_array, sampling_rate=16000, return_tensors="pt")
        # input_features = inputs.input_features.to(device)

        # Generate prediction
        predicted_ids = self.model.generate(inputs["input_features"])

        # Decode transcription
        transcription = self.processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
        
        return transcription
