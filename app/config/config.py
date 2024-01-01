"""
A module for config in the app-core package.
"""
from functools import lru_cache

from app.config.db.auth_settings import AuthSettings
from app.config.db.sql_database_settings import SQLDatabaseSettings
from app.config.init_settings import InitSettings
from app.config.settings import Settings


@lru_cache()
def get_init_settings() -> InitSettings:
    """
    Get init settings cached
    :return: The init settings instance
    :rtype: InitSettings
    """
    return init_setting


@lru_cache()
def get_settings() -> Settings:
    """
    Get settings cached
    :return: The settings instance
    :rtype: Settings
    """
    return Settings()


@lru_cache()
def get_sql_settings() -> SQLDatabaseSettings:
    """
    Get SQL db settings cached
    :return: SQL Database settings instance
    :rtype: SQLDatabaseSettings
    """
    return SQLDatabaseSettings()


@lru_cache()
def get_auth_settings() -> AuthSettings:
    """
    Get auth settings cached
    :return: Auth settings instance
    :rtype: AuthSettings
    """
    return AuthSettings()


init_setting: InitSettings = InitSettings()
setting: Settings = Settings()
sql_database_setting: SQLDatabaseSettings = SQLDatabaseSettings()
auth_setting: AuthSettings = AuthSettings()
