from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Telusko Workflow Engine"
    database_url: str = "sqlite+aiosqlite:///./telusko.db"
    port: int = 8000

    # JWT — env vars use JWT_ prefix (set in .env)
    secret_key: str = Field(
        default="change-me-in-production",
        validation_alias="jwt_secret_key",
    )
    algorithm: str = Field(
        default="HS256",
        validation_alias="jwt_algorithm",
    )
    access_token_expire_minutes: int = Field(
        default=60,
        validation_alias="jwt_access_token_expire_minutes",
    )


settings = Settings()
