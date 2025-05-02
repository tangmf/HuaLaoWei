import os
import torch

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_FOLDER = os.path.join(BASE_DIR, "./models")
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")