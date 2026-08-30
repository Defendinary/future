from future.database import Database
import pytest


def test_database_registers_and_resolves_default():
    Database._connections = {}
    Database._default = None
    sqlite = object()
    mysql = object()
    Database().set_connection_details({"default": "sqlite", "sqlite": sqlite, "mysql": mysql})
    assert Database().get_connection("default") is sqlite
    assert Database().get_connection("sqlite") is sqlite
    assert Database().get_connection("mysql") is mysql


def test_database_set_connection_details_returns_self():
    Database._connections = {}
    Database._default = None
    registry = Database()
    assert registry.set_connection_details({"default": "sqlite", "sqlite": object()}) is registry


def test_database_get_connection_requires_registration():
    Database._connections = {}
    Database._default = None
    with pytest.raises(RuntimeError, match="No database connections registered"):
        Database().get_connection("default")


def test_database_unknown_name_raises():
    Database._connections = {}
    Database._default = None
    Database().set_connection_details({"default": "sqlite", "sqlite": object()})
    with pytest.raises(RuntimeError, match="No database connections registered"):
        Database().get_connection("postgres")


def test_database_replaces_previous_map():
    Database._connections = {}
    Database._default = None
    first = object()
    second = object()
    Database().set_connection_details({"default": "a", "a": first})
    Database().set_connection_details({"default": "b", "b": second})
    assert Database().get_connection("default") is second
    with pytest.raises(RuntimeError):
        Database().get_connection("a")
