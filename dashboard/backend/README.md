# HuaLaoWei Dashboard Backend

This is the **backend service** for the HuaLaoWei Dashboard application, built using **FastAPI**, **Async PostgreSQL**, and modular service pipelines.

---

# Project Structure

```bash
root/
├── docker-compose.yaml           # Orchestrates backend, database, and model server
├── config/
│   ├── config.yaml               # Main configuration file
│   └── config.py                 # Pydantic settings loader
├── dashboard/
│   └── backend/
│       ├── api/
│       │   └── v1/
│       │       └── endpoints/    # FastAPI routers (issues, meta, subzone, forecast)
│       ├── crud/                 # Database access layer (pure SQL)
│       ├── db/
│       │   └── database.py       # Connection pooling with AsyncConnectionPool
│       ├── services/
│       │   └── forecast/
│       │       ├── modules/      # Modular forecast services (weather, POI, socioeconomic, etc.)
│       │       └── pipeline.py   # ForecastIssueCountPipeline class
│       ├── main.py               # FastAPI app entrypoint
│       ├── pyproject.toml        # Project dependencies (Hatch)
│       ├── Dockerfile            # Docker build for backend
│       └── README.md             # Project documentation (you are reading this)
```

---

# Requirements

* Python 3.11+
* PostgreSQL database
* OneMap API Token
* Optional: Model Server for Forecasting (e.g., `your-model-server`)

---

# Getting Started

## Install Dependencies

```bash
# Inside the backend directory
cd dashboard/backend
hatch env create
hatch run python -m pip install --upgrade pip
```

## Run Development Server

```bash
# From backend folder
hatch run uvicorn dashboard.backend.main:app --reload --host 0.0.0.0 --port 8000
```

Visit [http://localhost:7000/docs](http://localhost:7000/docs) for Swagger API docs.


## Run Using Docker

```bash
cd dashboard/backend

# Build image
docker build -t municipal-backend .

# Run container
docker run -p 7000:7000 municipal-backend
```

Or using Docker Compose from project root:

```bash
docker-compose up --build
```

---

# Key Components

* **Database Pooling:** via `psycopg-pool`.
* **Async HTTP Calls:** via `aiohttp`.
* **Modular Pipelines:** Forecasting pipeline divided into logical modules.
* **Separation of Concerns:** CRUD vs Service layers.
* **Full API Documentation:** Auto-generated at `/docs`.
* **Central Configuration:** All configurations are found in `config/config.yaml` and loaded via `config/config.py` using Pydantic.

---

# Maintenance Commands

| Task                | Command                                                  |
| :------------------ | :------------------------------------------------------- |
| Format Code         | `hatch run black .`                                      |
| Lint Code           | `hatch run flake8 .`                                     |
| Install New Package | `hatch run python -m pip install package-name`           |
| Update Dependencies | `hatch run python -m pip install --upgrade package-name` |

---

# Useful Resources

* [FastAPI Documentation](https://fastapi.tiangolo.com/)
* [Hatch Documentation](https://hatch.pypa.io/latest/)
* [PostgreSQL Async Python](https://www.psycopg.org/psycopg3/docs/async.html)
* [Open-Meteo API](https://open-meteo.com/en/docs)
* [OneMap API Singapore](https://www.onemap.gov.sg/docs/)

---

# Author

Created by Fleming Siow.

