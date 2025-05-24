from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str  
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int
    MAIL_USERNAME: str
    MAIL_PASSWORD: str

    model_config = SettingsConfigDict(
    env_file=".env"
    )

Config = Settings()
