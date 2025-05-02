import os
import torch
from typing import Dict, Tuple, Type
from config import MODEL_FOLDER, DEVICE

# Import model classes
from classes.tcn_forecast_class import TCN

# Mapping: subfolder name -> (ModelClass, DefaultConstructorParams)
MODEL_CLASS_MAPPING: Dict[str, Tuple[Type[torch.nn.Module], dict]] = {
    "tcn": (TCN, {
        "num_channels": [32, 64, 128],
        "kernel_size": 3,
        "dropout": 0.3
    }),
    # "cnn": (CNN, {
    #     "num_channels": [64, 128, 256],
    #     "kernel_size": 5,
    #     "dropout": 0.4
    # }),
    # "lstm": (LSTM, {
    #     "hidden_size": 128,
    #     "num_layers": 2,
    #     "dropout": 0.2
    # }), 
}

model_cache: Dict[str, Tuple[torch.nn.Module, int]] = {}

def preload_all_models():
    print("Preloading models...")

    for root, dirs, files in os.walk(MODEL_FOLDER):
        for filename in files:
            if filename.endswith("_model.pth"):
                full_path = os.path.join(root, filename)

                # Extract subfolder
                relative_path = os.path.relpath(full_path, MODEL_FOLDER)
                subfolder = relative_path.split(os.sep)[0]  # "tcn", "cnn", etc

                entry = MODEL_CLASS_MAPPING.get(subfolder.lower())

                if entry is None:
                    print(f"Skipping {full_path}: Unknown model type '{subfolder}'")
                    continue

                ModelClass, default_params = entry

                issue_type = filename.replace("_model.pth", "")
                input_size_hint = detect_input_size_from_model_file(full_path)

                print(f"Loading: {full_path} (Type: {subfolder}, Input Size: {input_size_hint})")

                # Build model dynamically with parameters
                model = ModelClass(
                    input_size=input_size_hint,
                    output_size=1,
                    **default_params
                )

                model.load_state_dict(torch.load(full_path, map_location=DEVICE))
                model.to(DEVICE)
                model.eval()

                model_cache[issue_type] = (model, input_size_hint)
                print(f"Preloaded model '{issue_type}' as {ModelClass.__name__}")

    print(f"Finished preloading {len(model_cache)} models.")

def detect_input_size_from_model_file(model_path):
    return 13
