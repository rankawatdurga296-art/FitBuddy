from dataclasses import dataclass
import os

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "FitBuddy")

    database_url: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./fitbuddy.db"
    )

    gemini_api_key: str | None = os.getenv("GEMINI_API_KEY")

    workout_model: str = os.getenv(
        "GEMINI_WORKOUT_MODEL",
        "gemini-3.7-flash"
    )

    nutrition_model: str = os.getenv(
        "GEMINI_NUTRITION_MODEL",
        "gemini-3.8-flash"
    )

    admin_username: str = os.getenv(
        "ADMIN_USERNAME",
        "admin"
    )

    admin_password: str | None = os.getenv(
        "ADMIN_PASSWORD"
    )

    app_env: str = os.getenv(
        "APP_ENV",
        "development"
    )


settings = Settings()