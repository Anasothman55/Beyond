from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
  POSTGRESQL_URI: str
  SECRET_KEY: str
  ALGORITHM: str
  ACCESS_TOKEN_EXPIRE_MINUTES: int
  REFRESH_TOKEN_EXPIRE_DAYS: int
  UPSTASH_REDIS_HOST: str
  UPSTASH_REDIS_PORT: int
  UPSTASH_REDIS_PASSWORD: str
  UPSTASH_REDIS_SSL: bool | None = True
  MAIL_USERNAME : str
  MAIL_PASSWORD : str
  MAIL_FROM : str
  MAIL_SERVER : str
  MAIL_FROM_NAME : str

  DOMAIN: str

  model_config = SettingsConfigDict(
    env_file=".env",
    extra="ignore"
  )


settings = Settings()

