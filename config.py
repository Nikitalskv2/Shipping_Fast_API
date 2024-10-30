from zoneinfo import ZoneInfo

from pydantic_settings import BaseSettings, SettingsConfigDict

_project_timezone = "Europe/Moscow"


class Settings(BaseSettings):
    timezone: str
    tz: ZoneInfo

    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "postgres"
    DB_USER: str = "postgres"
    DB_PASS: str = "123456"
    DB_echo: bool = False

    DB_HOST_TEST: str = "localhost"
    DB_PORT_TEST: int = 5432
    DB_NAME_TEST: str = "postgres"
    DB_USER_TEST: str = "postgres"
    DB_PASS_TEST: str = "123456"

    @property
    def DATABASE_URL_asyncpg(self):
        return f"""postgresql+asyncpg://
{self.DB_USER}:
{self.DB_PASS}@
{self.DB_HOST}:
{self.DB_PORT}/
{self.DB_NAME}"""

    @property
    def TEST_DATABASE_asyncpg(self):
        return f"""postgresql+asyncpg://
{self.DB_USER_TEST}:
{self.DB_PASS_TEST}@
{self.DB_HOST_TEST}:
{self.DB_PORT_TEST}/
{self.DB_NAME_TEST}"""

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings(timezone=_project_timezone, tz=ZoneInfo(_project_timezone))
