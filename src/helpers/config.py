from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    app_name: str
    app_version: str
    openai_api_key: str
    FILE_ALLOWED_TYPES: list
    FILE_MAX_SIZE: int
    FILE_DEFAULT_CHUNK_SIZE: int



    model_config = SettingsConfigDict(env_file=".env")


def get_settings() -> Settings:
    return Settings()