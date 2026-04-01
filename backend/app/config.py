from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DEFAULT_FOLDER: str = "backend"
    DEFAULT_K: int = 5
    EMBED_MODEL_NAME: str = "all-MiniLM-L6-v2"
    TEST_PENALTY: float = 0.25
    ANTHROPIC_API_KEY: str = ""

    model_config = SettingsConfigDict(
        env_file="backend/.env",
        extra="allow"
    )

settings = Settings()