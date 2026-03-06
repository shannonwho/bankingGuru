from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./dev.db"
    debug: bool = True

    model_config = {"env_prefix": "BANKING_"}


settings = Settings()
