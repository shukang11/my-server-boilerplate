import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

config_file = f"{os.environ.get('APP_CONFIG_FILE', 'default')}.env"
env_file = Path(__file__).parent.parent.joinpath(config_file)

content = env_file.read_text()


class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ECHO_SQL: bool = False

    model_config = SettingsConfigDict(
        env_file=env_file, case_sensitive=False, extra="allow"
    )


settings = Settings.model_validate({})
