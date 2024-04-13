# SPDX-FileCopyrightText: 2024-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""Settings for the uEditor."""
import os
from typing import Any, Dict, Literal, Tuple, Type

from pydantic import BaseModel
from pydantic.fields import FieldInfo
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict
from yaml import safe_load


class YAMLConfigSettingsSource(PydanticBaseSettingsSource):
    """Loads the configuration settings from a YAML file."""

    def get_field_value(
        self: "YAMLConfigSettingsSource", field: FieldInfo, field_name: str  # noqa: ARG002
    ) -> Tuple[Any, str, bool]:
        """Get the value of a specific field."""
        encoding = self.config.get("env_file_encoding")
        file_content_json = None
        for filename in ["uEditor.yaml", "uEditor.yml"]:
            if os.path.exists(filename):
                with open(filename, encoding=encoding) as in_f:
                    file_content_json = safe_load(in_f)
                    break
        if file_content_json is not None:
            field_value = file_content_json.get(field_name)
        else:
            field_value = None
        return field_value, field_name, False

    def prepare_field_value(
        self: "YAMLConfigSettingsSource",
        field_name: str,  # noqa: ARG002
        field: FieldInfo,  # noqa: ARG002
        value: Any,
        value_is_complex: bool,  # noqa: ARG002, FBT001
    ) -> Any:
        """Just return the value."""
        return value

    def __call__(self: "YAMLConfigSettingsSource") -> Dict[str, Any]:
        """Call the loader."""
        d: Dict[str, Any] = {}

        for field_name, field in self.settings_cls.model_fields.items():
            field_value, field_key, value_is_complex = self.get_field_value(field, field_name)
            field_value = self.prepare_field_value(field_name, field, field_value, value_is_complex)
            if field_value is not None:
                d[field_key] = field_value

        return d


class TEINodeAttribute(BaseModel):
    """Single attribute for a TEINode."""

    name: str
    """The name of the attribute."""
    value: str | None = None
    """A fixed value to use for the attribute."""
    type: Literal["string"] | Literal["static"] | Literal["id-ref"] = "string"
    """The type of attribute this is."""
    default: str = ""
    """The default value to use if none is set."""


class TEINode(BaseModel):
    """A single node in a TEI document."""

    name: str
    """The name to use to address this node."""
    selector: str
    """The selector to identify this node."""
    attributes: list[TEINodeAttribute] = []
    """A list of attributes that are used on this node."""


class TEIMetadataSection(BaseModel):
    """A metadata section in the TEI document."""

    name: str
    """The name of the section."""
    title: str
    """The title to show in the UI."""
    type: Literal["metadata"]
    """The type must be set to metadata."""
    selector: str
    """The XPath selector to retrieve this section."""


class TEITextSection(BaseModel):
    """A section in the TEI document containing a single text."""

    name: str
    """The name of the section."""
    title: str
    """The title to show in the UI."""
    type: Literal["text"]
    """The type must be set to text."""
    selector: str
    """The XPath selector to retrieve this section."""


class TEITextListSection(BaseModel):
    """A section in the TEI document containing multiple texts."""

    name: str
    """The name of the section."""
    title: str
    """The title to show in the UI."""
    type: Literal["textlist"]
    """The type must be set to textlist."""
    selector: str
    """The XPath selector to retrieve this section."""


class TEISettings(BaseModel):
    """Settings for the TEI processing"""

    blocks: list[TEINode] = []
    """List of blocks supported in the TEI document."""
    marks: list[TEINode] = []
    """List of inline marks supported in the TEI document."""
    sections: list[TEIMetadataSection | TEITextSection | TEITextListSection] = []
    """List of sections within the TEI document."""


class Settings(BaseSettings):
    """The main application settings."""

    tei: TEISettings = TEISettings()

    @classmethod
    def settings_customise_sources(
        cls: Type["Settings"],
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        """Customise the settings sources."""
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
            YAMLConfigSettingsSource(settings_cls),
        )


class InitSettings(BaseSettings):
    """The initialisation settings."""

    local_repo_path: str = "./"
    test: bool = False

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


init_settings = InitSettings()


def settings() -> Settings:
    return Settings()
