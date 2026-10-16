from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "PantryPal API"
    database_url: str = "postgresql+psycopg://pantrypal:pantrypal@localhost:5432/pantrypal"
    expiring_soon_days: int = 3


settings = Settings()
