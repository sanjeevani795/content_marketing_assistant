from dataclasses import dataclass
import os


@dataclass
class AppConfig:
    app_env: str = os.getenv("APP_ENV", "development")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    default_llm_provider: str = os.getenv("DEFAULT_LLM_PROVIDER", "openai")
    default_image_provider: str = os.getenv("DEFAULT_IMAGE_PROVIDER", "openai")
    default_research_provider: str = os.getenv("DEFAULT_RESEARCH_PROVIDER", "serpapi")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    temperature: float = float(os.getenv("MODEL_TEMPERATURE", "0.4"))


config = AppConfig()
