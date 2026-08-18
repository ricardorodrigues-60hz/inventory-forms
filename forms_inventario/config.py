from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = 'sqlite+aiosqlite:///./inventario.db'
    secret_key: str = 'troque-por-uma-chave-segura-de-32-chars'
    access_token_expire_minutes: int = 480
    cors_origins: str = 'http://localhost:5173'

    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8', extra='ignore'
    )


settings = Settings()
