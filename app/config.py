from pydantic import BaseSettings
import os


class Settings(BaseSettings):
    APP_KEY: str = os.getenv("APP_KEY", "YOUR_APP_KEY")
    APP_SECRET: str = os.getenv("APP_SECRET", "YOUR_APP_KEY")
    API_DOMAIN: str = os.getenv("API_DOMAIN", "YOUR_APP_DOMAIN")
    REDIRECT: str = os.getenv("REDIRECT", "/admin")


settings = Settings()
