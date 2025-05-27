import os
from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import BaseModel
import yaml
from dotenv import load_dotenv

# --------------------------------------------------------
# Load Environment Variables
# --------------------------------------------------------

dotenv_path = Path(__file__).parent.parent / ".env.dev"
if dotenv_path.exists():
    load_dotenv(dotenv_path)

# --------------------------------------------------------
# Load YAML Configuration
# --------------------------------------------------------

env = os.getenv("ENV", "dev")
yaml_path = Path(__file__).parent / f"config.{env}.yaml"
if not yaml_path.exists():
    raise FileNotFoundError(f"Config YAML file not found: {yaml_path}")

with open(yaml_path, "r") as file:
    yaml_config = yaml.safe_load(file)

# --------------------------------------------------------
# Helper: Recursively Replace ${VAR} with os.getenv(VAR)
# --------------------------------------------------------

def inject_env_variables(config: Any) -> Any:
    if isinstance(config, dict):
        return {k: inject_env_variables(v) for k, v in config.items()}
    elif isinstance(config, list):
        return [inject_env_variables(i) for i in config]
    elif isinstance(config, str) and config.startswith("${") and config.endswith("}"):
        env_var = config[2:-1]
        value = os.getenv(env_var)
        if value is None:
            raise EnvironmentError(f"Missing required environment variable: {env_var}")
        if value == "":
            raise EnvironmentError(f"Environment variable '{env_var}' is empty. Please set it properly in .env.dev.")
        return value
    else:
        return config

yaml_config = inject_env_variables(yaml_config)

# --------------------------------------------------------
# Convert fields to correct types
# --------------------------------------------------------

yaml_config["data_stores"]["relational_db"]["port"] = int(yaml_config["data_stores"]["relational_db"]["port"])
yaml_config["backend"]["port"] = int(yaml_config["backend"]["port"])

# --------------------------------------------------------
# Define Pydantic Models
# --------------------------------------------------------

class URLServiceConfig(BaseModel):
    url: str

class STTModelConfig(BaseModel):
    url: str

class TTSModelConfig(BaseModel):
    url: str

class SpeechModelConfig(BaseModel):
    stt: STTModelConfig
    tts: Optional[TTSModelConfig] = None

class ChatbotServicesConfig(BaseModel):
    ollama: URLServiceConfig
    speech: SpeechModelConfig
    translate: URLServiceConfig
    embed: URLServiceConfig
    rerank: URLServiceConfig

class VLMServiceConfig(BaseModel):
    model: str
    adapter: str
    url: str

class ForecastModelConfig(BaseModel):
    url: str

class AIModelsConfig(BaseModel):
    chatbot: ChatbotServicesConfig
    vlm_issue_categoriser: VLMServiceConfig
    forecast_model_issue_count: URLServiceConfig

class RelationalDBConfig(BaseModel):
    host: str
    port: int
    database: str
    user: str
    password: str

class ObjectStorageConfig(BaseModel):
    endpoint: str
    access_key: str
    secret_key: str
    bucket_name: str
    url: str

class VectorstoreCollectionConfig(BaseModel):
    name: str

class VectorstoreConfig(BaseModel):
    url: str
    webhook_url: str
    collection: Dict[str, VectorstoreCollectionConfig]

class DataStoresConfig(BaseModel):
    relational_db: RelationalDBConfig
    object_storage: ObjectStorageConfig
    vectorstore: VectorstoreConfig

class BackendConfig(BaseModel):
    port: int
    secret_key: str

class Config(BaseModel):
    env: str
    ai_models: AIModelsConfig
    data_stores: DataStoresConfig
    backend: BackendConfig

# --------------------------------------------------------
# Build Final Config Object
# --------------------------------------------------------

config = Config(**yaml_config)
