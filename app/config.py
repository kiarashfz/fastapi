from pydantic import BaseSettings


class Settings(BaseSettings):
    pg_host: str
    pg_database: str
    pg_user: str
    pg_password: str
    api_key: str

    class Config:
        env_file = "app/.env"


settings = Settings()
