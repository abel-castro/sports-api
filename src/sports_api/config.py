from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///:memory:"

    api_footbal_key: str = ""
    api_footbal_host: str = "api-football-v1.p.rapidapi.com"

    import_token: str = ""

    debug: bool = False

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
