"""Test fixtures."""

import os

from typing import Generator

from fastapi import FastAPI
from pytest import fixture

from ueditor import app
from ueditor.settings import settings


@fixture
def simple_app() -> Generator[FastAPI, None, None]:
    """Yield a uEditor application for a simple uEdition."""
    cwd = os.getcwd()
    try:
        os.chdir("tests/fixtures/simple")
        yield app
    finally:
        os.chdir(cwd)


@fixture
def tei_app() -> Generator[FastAPI, None, None]:
    """Yield a uEditor application for a uEdition with some TEI."""
    cwd = os.getcwd()
    try:
        os.chdir("tests/fixtures/tei")
        yield app
    finally:
        os.chdir(cwd)
