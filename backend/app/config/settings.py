"""Application settings and configuration."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application configuration from environment variables."""
    
    # Database
    sql_server: str = "KOPPHPDEV006\\SQLEXPRESS"
    sql_database: str = "AG_RBAC_POC"
    sql_username: Optional[str] = None
    sql_password: Optional[str] = None
    sql_trusted_connection: bool = True
    
    # App
    debug: bool = False
    app_name: str = "A&G RBAC POC"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    @property
    def database_url(self) -> str:
        """Construct the async SQL Server database URL."""
        if self.sql_trusted_connection:
            # Windows authentication
            connection_string = (
                f"mssql+pyodbc://{self.sql_server}/{self.sql_database}"
                f"?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
            )
        else:
            # Username/password authentication
            connection_string = (
                f"mssql+pyodbc://{self.sql_username}:{self.sql_password}"
                f"@{self.sql_server}/{self.sql_database}"
                f"?driver=ODBC+Driver+17+for+SQL+Server"
            )
        return connection_string


settings = Settings()
