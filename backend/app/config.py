from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://banking:banking_secret@localhost:5432/fintechco"
    debug: bool = True

    model_config = {"env_prefix": "BANKING_"}


settings = Settings()
