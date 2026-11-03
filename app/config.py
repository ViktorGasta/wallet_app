from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = (
        "postgresql+asyncpg://postgres:postgres@db:5432/wallet_db"
    )

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
