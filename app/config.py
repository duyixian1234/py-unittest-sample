from pydantic import BaseSettings
import os


class Settings(BaseSettings):
    APP_KEY: str = os.getenv("APP_KEY")
    APP_SECRET: str = os.getenv("APP_SECRET")
    API_DOMAIN: str = os.getenv("API_DOMAIN")
    REDIRECT: str = "/admin"


settings = Settings()
