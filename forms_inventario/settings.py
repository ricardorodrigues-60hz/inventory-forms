from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8', extra='ignore'
    )
    
    DATABASE_URL: str = Field(init=False)
    SECRET_KEY: str = Field(init=False)
    ACCESS_TOKEN_EXPITE_MINUTES: str  = Field(init=False)
    CORS_ORIGINS: str = 'http://localhost:5173'

