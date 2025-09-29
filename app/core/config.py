from typing import Literal
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "abc-airlines"
    env: Literal["dev", "test", "prod"] = "dev"

    database_url: str = Field(
        default="sqlite+aiosqlite:///./abc-airlines.db", alias="DATABASE_URL"
    )
    jwt_secret: str = Field(default="change-me", alias="JWT_SECRET")
    jwt_alg: str = Field(default="HS256", alias="JWT_ALG")
    access_token_expire_minutes: int = Field(
        default=60, alias="ACCESS_TOKEN_EXPIRE_MINUTES"
    )

    admin_email: str = Field(default="admin@abcairlines.com", alias="ADMIN_EMAIL")
    admin_password: SecretStr = Field(alias="ADMIN_PASSWORD") 

    admin_session_secret: str = Field(alias="ADMIN_SESSION_SECRET")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_ignore_empty=True,
    )


settings = Settings()
