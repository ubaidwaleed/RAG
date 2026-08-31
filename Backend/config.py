from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    app_name: str = "rag-agent"
    environment: str = "dev"
    log_level: str = "INFO"

    gemini_api_key: str
    gemini_llm_model: str = "gemini-3.6-flash"
    gemini_embedding_model: str = "gemini-embedding-001"
    embedding_dimension: int = 768

    pinecone_api_key: str
    pinecone_index_name: str = "rag-agent-index"

    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k: int = 5


settings = Settings()
