from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    database_driver: str
    database_dialect: str
    secret_key: str
    algorithm: str
    access_token_expiration_minutes: int
    max_login_attempts: int
    login_attempt_cooldown_window: int

    model_config = SettingsConfigDict(
        env_file = ".env",
        env_file_encoding = "utf-8",
        case_sensitive=False,
        extra="ignore"
    )

settings = Settings()