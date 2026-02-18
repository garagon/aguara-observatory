"""Shared test fixtures for Aguara Observatory tests."""

import pytest
import libsql_experimental as libsql

from crawlers.db import init_schema


@pytest.fixture
def db():
    """Create an in-memory database with schema applied."""
    conn = libsql.connect("file::memory:")
    init_schema(conn)
    return conn
