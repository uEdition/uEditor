# SPDX-FileCopyrightText: 2024-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""Settings for the uEditor."""

import os
from secrets import token_hex
from typing import Any, Dict, Literal, Optional, Tuple, Type

import yaml_include
from pydantic import BaseModel, EmailStr, model_validator
from pydantic.fields import FieldInfo
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)
from pygit2 import GitError, Repository
from pygit2.enums import RepositoryOpenFlag
from typing_extensions import Self
from uedition.settings import Settings as UEditonSettingsBase
from yaml import SafeLoader, add_constructor, load


class NoAuth(BaseModel):
    """Configuration model for no authentication."""

    provider: Literal["no-auth"] = "no-auth"
    email: Literal[""] = ""
    name: Literal[""] = ""


class EmailAuth(BaseModel):
    """Configuration model for password-less authentication."""

    provider: Literal["email"]
    email: EmailStr
    name: str


class EmailPasswordUser(BaseModel):
    """Configuration model for a single email/password combination."""

    email: EmailStr
    name: str
    password: str


class EmailPasswordAuth(BaseModel):
    """Configuration model for email/password authentication."""

    provider: Literal["email-password"]
    users: list[EmailPasswordUser]


class GithubOAuth2(BaseModel):
    """Configuration model for authenticating via GitHub."""

    provider: Literal["github"]
    client_id: str
    client_secret: str
    callback_base: str
    users: list[str] = []


class SessionSettings(BaseModel):
    """Session configuration."""

    key: str = token_hex(32)


class GitSettings(BaseModel):
    """Settings for Git."""

    remote_name: str = "origin"
    default_branch: str = "main"


class InitSettings(BaseSettings):
    """The initialisation settings."""

    base_path: str = "./"
    auth: NoAuth | EmailAuth | EmailPasswordAuth | GithubOAuth2 = NoAuth()
    session: SessionSettings = SessionSettings()
    git: GitSettings = GitSettings()
    test: bool = False

    @model_validator(mode="after")
    def git_auth_check(self) -> Self:
        """Check that there is no git repository for no-auth authentication."""
        if self.auth.provider == "no-auth":
            try:
                Repository(self.base_path, flags=RepositoryOpenFlag.NO_SEARCH)
                raise ValueError(
                    "You need to configure an authentication method when using a git repository."  # noqa: EM101
                )
            except GitError:
                pass
        return self

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="ueditor__",
        env_nested_delimiter="__",
        extra="ignore",
    )


init_settings = InitSettings()

add_constructor("!include", yaml_include.Constructor(base_dir=init_settings.base_path), SafeLoader)


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
                    self._file_content = load(in_f, SafeLoader)
                    break

    def get_field_value(
        self: "YAMLConfigSettingsSource",
        field: FieldInfo,  # noqa: ARG002
        field_name: str,
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
    type: Literal["string"] | Literal["static"] | Literal["id-ref"] | Literal["text"] | Literal["html-attribute"] = (
        "string"
    )
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
    text: Optional[str] = None
    """Where to get the text from."""
    content: Optional[str] = None
    """Allowed child nodes. Only relevant for block nodes."""


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

    node: str
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


class TEIMenuItemToggleWrapBlock(BaseModel):
    """A TEI menu item to set the current block."""

    type: Literal["toggle-wrap-block"]
    """The menu item type."""
    block: str
    """The block to toggle wrapping."""
    title: str
    """The title for the button."""
    icon: Optional[str] = None
    """The optional icon to show."""


class TEIMenuItemSetBlockAttribute(BaseModel):
    """A TEI menu item to set the current block."""

    type: Literal["set-block-attribute"]
    """The menu item type."""
    block: str
    """The block to set the attribute on."""
    name: str
    """The name of the attribute to set."""
    value: str
    """The value of the attribute to set."""
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


class TEIMenuItemSeparator(BaseModel):
    """A separator in a toolbar."""

    type: Literal["separator"]


class TEITextToolbarBlock(BaseModel):
    """A TEI editor toolbar block."""

    title: str
    """The title for the block."""
    type: Literal["toolbar"]
    """The type is set to toolbar."""
    items: list[
        TEIMenuItemSetBlock
        | TEIMenuItemToggleWrapBlock
        | TEIMenuItemSetBlockAttribute
        | TEIMenuItemToggleMark
        | TEIMenuItemSeparator
    ]
    """The list of menu items to show."""
    condition: Optional[TEIMenuCondition] = None
    """An optional condition for showing the block."""


class TEISelectBlockAttribute(BaseModel):
    """A TEI form element to select an attribute."""

    type: Literal["select-block-attribute"]
    """The form element type."""
    block: str
    """The block to apply the attribute to."""
    name: str
    """The name of the attribute."""
    title: str
    """The label for the entry."""
    values: list[ValueTitlePair]
    """The available values to select from."""


class TEISelectCrossReferenceMarkAttribute(BaseModel):
    """A TEI form element to select an attribute for a cross-reference."""

    type: Literal["select-cross-reference-attribute"]
    """The form element type."""
    mark: str
    """The mark to apply the attribute to."""
    name: str
    """The name of the attribute."""
    title: str
    """The label for the entry."""
    section: str
    """The section containing the texts to cross-reference to."""


class TEIInputMarkAttribute(BaseModel):
    """A TEI form element to input a mark attribute value."""

    type: Literal["input-mark-attribute"]
    """The form element type."""
    mark: str
    """The mark to apply the attribute to."""
    name: str
    """The name of the attribute."""
    title: str
    """The label for the entry."""


class TEISelectMarkAttribute(BaseModel):
    """A TEI form element to select a mark attribute."""

    type: Literal["select-mark-attribute"]
    """The form element type."""
    mark: str
    """The mark to apply the attribute to."""
    name: str
    """The name of the attribute."""
    title: str
    """The label for the entry."""
    values: list
    """The available selection values."""


class TEIInputBlockAttribute(BaseModel):
    """A TEI form element to input a block attribute value."""

    type: Literal["input-block-attribute"]
    """The form element type."""
    block: str
    """The block to apply the attribute to."""
    name: str
    """The name of the attribute."""
    title: str
    """The label for the entry."""


class TEITextFormBlock(BaseModel):
    """A TEI editor toolbar block."""

    title: str
    """The title for the block."""
    type: Literal["form"]
    """The type is set to form."""
    items: list[
        TEISelectBlockAttribute
        | TEISelectCrossReferenceMarkAttribute
        | TEIInputMarkAttribute
        | TEIInputBlockAttribute
        | TEISelectMarkAttribute
    ]
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
    sidebar: list[TEITextToolbarBlock | TEITextFormBlock] | None = None
    """Sidebar configuration for this section."""


class TEITextListSection(BaseModel):
    """A section in the TEI document containing multiple texts."""

    name: str
    """The name of the section."""
    title: str
    """The title to show in the UI."""
    type: Literal["textlist"]
    """The type must be set to textlist."""
    selector: str
    """The XPath selector to retrieve the texts in this section."""
    sidebar: list[TEITextToolbarBlock | TEITextFormBlock] | None = None
    """Sidebar configuration for this section."""


class TEISettings(BaseModel):
    """Settings for the TEI processing."""

    blocks: list[TEINode] = []
    """List of blocks supported in the TEI document."""
    marks: list[TEINode] = []
    """List of inline marks supported in the TEI document."""
    sections: list[TEIMetadataSection | TEITextSection | TEITextListSection] = []
    """List of sections within the TEI document."""


class UISettings(BaseModel):
    """Settings for the UI."""

    css_files: list[str] = []


class UEditorSettings(BaseSettings):
    """The uEditor settings."""

    tei: TEISettings = TEISettings()
    ui: UISettings = UISettings()

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


class UEditionSettings(UEditonSettingsBase):
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


def get_uedition_settings() -> UEditionSettings:
    """Load the current UEditionSettings."""
    return UEditionSettings()
