from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI-Based Citizen Grievance Classification System"
    app_env: str = "development"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"

    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/grievance_db"

    secret_key: str = "change-this-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    model_name_or_path: str = "distilbert-base-uncased"
    duplicate_threshold: float = 0.82
    candidate_labels_csv: str = "Road,Water,Sanitation,Electricity,Healthcare,Education,Other"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def candidate_labels(self) -> list[str]:
        return [label.strip() for label in self.candidate_labels_csv.split(",") if label.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
