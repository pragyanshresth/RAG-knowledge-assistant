from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    openai_api_key: str = ""  # any OpenAI-compatible provider key (Gemini, Ollama, OpenAI...)
    openai_base_url: str = ""  # empty = OpenAI
    chat_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"
    qdrant_url: str = ""
    qdrant_path: str = "data/qdrant"
    database_url: str = "sqlite:///data/app.db"
    upload_dir: str = "data/uploads"
    chunk_size: int = 900
    chunk_overlap: int = 150
    top_k: int = 5
    min_score: float = 0.30
    max_upload_mb: int = 20
    cors_origins: str = "http://localhost:3000"


settings = Settings()
