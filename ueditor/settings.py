# SPDX-FileCopyrightText: 2024-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""Settings for the uEditor."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """The main application settings."""

    local_repo_path: str

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", env_nested_delimiter=".", extra="ignore"
    )


settings = Settings()
