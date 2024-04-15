"""Test fixtures."""

from typing import Generator

from fastapi import FastAPI
from pytest import fixture

from ueditor import app
from ueditor.settings import init_settings


@fixture
def empty_app() -> Generator[FastAPI, None, None]:
    """Yield an empty application."""
    try:
        init_settings.base_path = "tests/fixtures/empty"
        init_settings.test = True
        yield app
    finally:
        init_settings.base_path = "./"
        init_settings.test = False


@fixture
def simple_app() -> Generator[FastAPI, None, None]:
    """Yield a uEditor application for a simple uEdition."""
    try:
        init_settings.base_path = "tests/fixtures/simple"
        init_settings.test = True
        yield app
    finally:
        init_settings.base_path = "./"
        init_settings.test = False


@fixture
def tei_app() -> Generator[FastAPI, None, None]:
    """Yield a uEditor application for a uEdition with some TEI."""
    try:
        init_settings.base_path = "tests/fixtures/tei"
        init_settings.test = True
        yield app
    finally:
        init_settings.base_path = "./"
        init_settings.test = False
