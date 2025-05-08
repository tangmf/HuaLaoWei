# VLM Issue Categoriser Service

FastAPI server hosting Vision-Language Model (VLM) to categorise municipal issues.
Utilises fine-tuned VLMs for multimodal classification tasks in municipal services.

Author: Jerick Cheong, Fleming Siow
Date: 5th May 2025

---

## Features

* Image + Text multimodal input
* Returns predicted categories and severity score
* Lightweight serving with HuggingFace + PEFT adapters

---

## API Endpoints

| Endpoint       | Method | Description                                  |
| -------------- | ------ | -------------------------------------------- |
| `/categorise`  | POST   | Perform issue categorisation from image/text |
| `/health`      | GET    | Health check for model readiness             |

---

## Installation (Development)

### Requirements

* Python 3.10+
* PyTorch with CUDA support
* Huggingface Transformers

### Local Setup

```bash
# Clone repo and navigate to vlm_issue_categoriser folder
cd ai_models/vlm_issue_categoriser

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install .

# Run the server
python server.py
```

---

## Docker Deployment

Build and run using Docker:

```bash
# From repo root
docker build -f ai_models/vlm_issue_categoriser/Dockerfile -t vlm-issue-categoriser .

docker run -p 8101:8101 `
  --env-file "${PWD}\.env.dev" `
  -v "${PWD}\ai_models\vlm_issue_categoriser\app.py:/app/app.py" `
  -v "${PWD}\ai_models\vlm_issue_categoriser\server.py:/app/server.py" `
  vlm-issue-categoriser

docker run -p 8101:8101 \
  --env-file "${PWD}/.env.dev" \
  -v "${PWD}/ai_models/vlm_issue_categoriser/app.py:/app/app.py" \
  -v "${PWD}/ai_models/vlm_issue_categoriser/server.py:/app/server.py" \
  vlm-issue-categoriser


docker run -p 8101:8101 vlm-issue-categoriser
```

Or run via docker-compose together with chatbot and forecast services.

---

## Project Structure

```plaintext
/app
 ├── app.py             # FastAPI app for categorising issue types and severity
 ├── server.py          # Server launcher
 ├── preload_vlm.py     # Model preloading (if needed)
 ├── models/            # Model logic
 └── pyproject.toml     # Python project settings
/config
 └── config.dev.yaml     # Global config reference
```

---

## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).

---

## Acknowledgements

* Huggingface Transformers
* SmolVLM / Idefics-3 models
* PEFT fine-tuning adapters
* FastAPI for API server
* PyTorch for model hosting