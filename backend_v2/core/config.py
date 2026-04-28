import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Settings
    PROJECT_NAME: str = "Veridex Backend V2"
    API_VERSION: str = "v2.0.0"
    DEBUG: bool = True
    
    # Storage
    UPLOADS_DIR: str = "uploads/backend_v2"
    MODELS_DIR: str = "models/backend_v2"
    
    # Dataset Paths
    DATASET_ROOT: str = "Dataset"
    
    # Quality Gate Thresholds
    BLUR_THRESHOLD: float = 100.0  # Laplacian variance
    MIN_RESOLUTION: tuple[int, int] = (640, 480)
    
    # OCR Settings
    OCR_PRIMARY: str = "PADDLE"
    OCR_FALLBACK: str = "TROCR"
    CONFIDENCE_THRESHOLD_OCR: float = 0.85
    
    # Redis/Queue
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Postgres
    DATABASE_URL: str = "postgresql://jotex_user:Lucky%402005%2B@localhost:5432/jotex_db"

    
    # Risk Scoring Weights
    RISK_WEIGHTS: dict[str, float] = {
        "fraud": 0.40,
        "consistency": 0.20,
        "conflicts": 0.15,
        "metadata": 0.25
    }
    
    # Metadata Conservative Fallbacks (when Redis is down)
    METADATA_FALLBACK_RISK: float = 0.45
    
    class Config:
        env_file = ".env"


settings = Settings()

# Ensure directories exist
os.makedirs(settings.UPLOADS_DIR, exist_ok=True)
os.makedirs(settings.MODELS_DIR, exist_ok=True)
