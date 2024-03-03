"""Test fixtures."""

import os
from typing import Generator

from fastapi import FastAPI
from pytest import fixture

from ueditor import app


def app_generator(root: str) -> Generator[FastAPI, None, None]:
    cwd = os.getcwd()
    try:
        os.chdir(root)
        yield app
    finally:
        os.chdir(cwd)


@fixture
def empty_app() -> Generator[FastAPI, None, None]:
    yield from app_generator("tests/fixtures/empty")


@fixture
def simple_app() -> Generator[FastAPI, None, None]:
    """Yield a uEditor application for a simple uEdition."""
    yield from app_generator("tests/fixtures/simple")


@fixture
def tei_app() -> Generator[FastAPI, None, None]:
    """Yield a uEditor application for a uEdition with some TEI."""
    yield from app_generator("tests/fixtures/tei")
