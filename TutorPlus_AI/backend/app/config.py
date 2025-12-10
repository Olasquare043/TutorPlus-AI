from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # ngrok settings
    ngrok_api: str
    port: int = 8000
    
    # database settings
    database_url: str
    db_name: str
    db_user: str
    db_password: str
    db_host: str
    db_port: int = 5432

    # jwt settings
    jwt_secret_key: str
    jwt_algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int

    # app settings
    app_env: str
    debug: bool
    log_level: str

    # huggingface settings
    huggingface_api_key: str

    # ai model settings
    model_name: str
    use_4bit_quantization: bool
    device_map: str

    # chroma settings
    chroma_persist_dir: str


@lru_cache()
def get_settings():
    return Settings()