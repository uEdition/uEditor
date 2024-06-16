# SPDX-FileCopyrightText: 2024-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""Settings for the uEditor."""
import os
from typing import Any, Dict, Literal, Optional, Tuple, Type

from pydantic import BaseModel
from pydantic.fields import FieldInfo
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict
from uedition.settings import Settings as UEditonSettingsBase
from yaml import safe_load


class InitSettings(BaseSettings):
    """The initialisation settings."""

    base_path: str = "./"
    test: bool = False

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", env_prefix="ueditor_", extra="ignore")


init_settings = InitSettings()


class YAMLConfigSettingsSource(PydanticBaseSettingsSource):
    """Loads the configuration settings from a YAML file."""

    def __init__(self, settings_cls: Type[BaseSettings], source_files: list[str]):
        """Initialise and load the data."""
        super().__init__(settings_cls)
        self._file_content = None
        encoding = self.config.get("env_file_encoding")
        for filename in source_files:
            if os.path.exists(os.path.join(init_settings.base_path, filename)):
                with open(os.path.join(init_settings.base_path, filename), encoding=encoding) as in_f:
                    self._file_content = safe_load(in_f)
                    break

    def get_field_value(
        self: "YAMLConfigSettingsSource", field: FieldInfo, field_name: str  # noqa: ARG002
    ) -> Tuple[Any, str, bool]:
        """Get the value of a specific field."""
        if self._file_content is not None:
            field_value = self._file_content.get(field_name)
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


class ValueTitlePair(BaseModel):
    """A simple pair of value and title."""

    value: str
    """The value for the pair."""
    title: str
    """The title to show for the pair."""


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
    tag: Optional[str] = None
    """The HTML tag to use to render the node."""


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


class TEIMenuCondition(BaseModel):
    """A UI condition check."""

    block: str
    """The name of the block to be current."""


class TEIMenuItemSetBlock(BaseModel):
    """A TEI menu item to set the current block."""

    type: Literal["set-block"]
    """The menu item type."""
    block: str
    """The block to set the current node to."""
    title: str
    """The title for the button."""
    icon: Optional[str] = None
    """The optional icon to show."""


class TEIMenuItemToggleMark(BaseModel):
    """A TEI menu item to toggle a mark."""

    type: Literal["toggle-mark"]
    """The menu item type."""
    mark: str
    """The mark to toggle."""
    title: str
    """The title for the button."""
    icon: Optional[str] = None
    """The optional icon to show."""


class TEIMenuItemSelectAttribute(BaseModel):
    """A TEI menu item to select an attribute."""

    type: Literal["select-attribute"]
    """The menu item type."""
    block: str
    """The block to apply the attribute to."""
    name: str
    """The name of the attribute."""
    values: list[ValueTitlePair]
    """The available values to select from."""


class TEITextSidebarBlock(BaseModel):
    """A TEI editor sidebar block."""

    title: str
    """The title for the block."""
    items: list[TEIMenuItemSetBlock | TEIMenuItemToggleMark | TEIMenuItemSelectAttribute]
    """The list of menu items to show."""
    condition: Optional[TEIMenuCondition] = None
    """An optional condition for showing the block."""


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
    sidebar: Optional[list[TEITextSidebarBlock]] = None


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
    """Settings for the TEI processing."""

    blocks: list[TEINode] = []
    """List of blocks supported in the TEI document."""
    marks: list[TEINode] = []
    """List of inline marks supported in the TEI document."""
    sections: list[TEIMetadataSection | TEITextSection | TEITextListSection] = []
    """List of sections within the TEI document."""


class UEditorSettings(BaseSettings):
    """The uEditor settings."""

    tei: TEISettings = TEISettings()

    @classmethod
    def settings_customise_sources(
        cls: Type["UEditorSettings"],
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
            YAMLConfigSettingsSource(settings_cls, ["uEditor.yaml", "uEditor.yml"]),
        )


class UEditonSettings(UEditonSettingsBase):
    """The uEdition settings."""

    @classmethod
    def settings_customise_sources(
        cls: Type["UEditorSettings"],
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
            YAMLConfigSettingsSource(settings_cls, ["uEdition.yaml", "uEdition.yml"]),
        )


def get_ueditor_settings() -> UEditorSettings:
    """Load the current UEditorSettings."""
    return UEditorSettings()


def get_uedition_settings() -> UEditonSettings:
    """Load the current UEditionSettings."""
    return UEditonSettings()
