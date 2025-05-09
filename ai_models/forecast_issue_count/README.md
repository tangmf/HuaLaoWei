# Forecast Issue Count Service

FastAPI server hosting Time Series forecasting models for predicting municipal issue counts.

Author: Fleming Siow
Date: 5th May 2025

---

## Features

* Forecasts issue counts using pre-trained TCN models
* Models preloaded into memory for fast serving
* Accepts structured feature inputs
* Lightweight, GPU-accelerated (optional)

---

## API Endpoints

| Endpoint                 | Method | Description                                 |
| ------------------------ | ------ | ------------------------------------------- |
| `/forecast_issue_counts` | POST   | Forecast issue counts for provided features |
| `/health`                | GET    | Health check for model readiness            |

---

## Installation (Development)

### Requirements

* Python 3.9+
* PyTorch (with or without CUDA)

### Local Setup

```bash
# Clone repo and navigate to forecast_issue_count folder
cd ai_models/forecast_issue_count

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
docker build -f ai_models/forecast_issue_count/Dockerfile -t forecast-issue-service .

docker run -p 8102:8102 -v ${PWD}/ai_models/forecast_issue_count:/app forecast-issue-service
docker run -p 8102:8102 forecast-issue-service
```

Or orchestrate via docker-compose.

---

## Project Structure

```plaintext
/app
 ├── app.py             # FastAPI app for forecasting issue counts
 ├── server.py          # Server launcher
 ├── models/            # TCN model definition
 └── pyproject.toml     # Python project settings
/config
 └── config.dev.yaml     # Global config reference
```

---

## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).

---
