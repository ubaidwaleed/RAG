from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    app_name: str = "rag-agent"
    environment: str = "dev"
    log_level: str = "INFO"

    gemini_api_key: str
    gemini_embedding_model: str = "gemini-embedding-001"
    embedding_dimension: int = 768

    groq_api_key: str
    groq_llm_model: str = "openai/gpt-oss-120b"

    pinecone_api_key: str
    pinecone_index_name: str = "rag-agent-index"

    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k: int = 5
    max_upload_size_mb: int = 10


settings = Settings()
