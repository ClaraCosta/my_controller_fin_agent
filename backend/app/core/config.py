from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "MY CONTROLLER FINANCE"
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 60
    database_url: str = "postgresql+psycopg://app_user:app_password@db:5432/ai_ops"
    ollama_base_url: str = "http://ollama:11434"
    ollama_model: str = "llama3.2"
    tesseract_cmd: str = "/usr/bin/tesseract"
    default_admin_email: str = "admin@example.com"
    default_admin_password: str = "admin123"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

