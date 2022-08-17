from pydantic import BaseSettings


class Settings(BaseSettings):
    pg_host: str = "localhost"
    pg_database: str = "fastapi"
    pg_user: str = "postgres"
    pg_password: str
    api_key: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    api_key: str
    api_key_name: str = "API_KEY"

    class Config:
        env_file = ".env"


settings = Settings()
