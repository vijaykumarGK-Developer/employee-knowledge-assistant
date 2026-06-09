from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Employee Knowledge Assistant"
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/employee_knowledge"
    SECRET_KEY: str = "change-this-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8000
    EMBEDDINGS_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    LLM_MODEL: str = "google/flan-t5-small"
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024
    CORS_ORIGINS: str = "http://localhost:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    class Config:
        env_file = ".env"


settings = Settings()
