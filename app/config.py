from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
  POSTGRESQL_URI: str

  model_config = SettingsConfigDict(
    env_file=".env",
    extra="ignore"
  )


settings = Settings()




