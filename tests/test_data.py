"""Tests for preswald.interfaces.data module.

Covers connect(), query(), and get_df() with mocked PreswaldService and DataManager.
"""

import pytest
from unittest.mock import MagicMock, patch

import preswald.interfaces.data as data_mod


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _reset_connected_flag():
    """Reset the module-level _connected flag before every test."""
    data_mod._connected = False
    yield
    data_mod._connected = False


def _make_mock_service(*, already_connected: bool = False):
    """Return a mock PreswaldService with a stubbed DataManager."""
    service = MagicMock()
    dm = MagicMock()
    dm.duckdb_conn = MagicMock(name="duckdb_connection")
    dm.connect.return_value = (["source_a", "source_b"], dm.duckdb_conn)

    if already_connected:
        dm.sources = {"source_a": MagicMock()}
    else:
        dm.sources = {}

    service.data_manager = dm
    return service


# ---------------------------------------------------------------------------
# connect()
# ---------------------------------------------------------------------------

class TestConnect:

    def test_returns_duckdb_connection(self):
        service = _make_mock_service()
        with patch.object(
            data_mod.PreswaldService, "get_instance", return_value=service
        ):
            conn = data_mod.connect()

        assert conn is service.data_manager.duckdb_conn

    def test_calls_data_manager_connect(self):
        service = _make_mock_service()
        with patch.object(
            data_mod.PreswaldService, "get_instance", return_value=service
        ):
            data_mod.connect()

        service.data_manager.connect.assert_called_once()

    def test_idempotent_skips_reconnect(self):
        """Calling connect() twice should only invoke data_manager.connect() once."""
        service = _make_mock_service()
        # After the first connect(), sources will be populated
        def _simulate_connect():
            service.data_manager.sources = {"source_a": MagicMock()}
            return (["source_a"], service.data_manager.duckdb_conn)

        service.data_manager.connect.side_effect = _simulate_connect

        with patch.object(
            data_mod.PreswaldService, "get_instance", return_value=service
        ):
            first = data_mod.connect()
            second = data_mod.connect()

        # data_manager.connect() should have been called only on the first invocation
        service.data_manager.connect.assert_called_once()
        # Both calls should return the duckdb connection
        assert first is service.data_manager.duckdb_conn
        assert second is service.data_manager.duckdb_conn

    def test_connect_error_returns_none(self):
        service = _make_mock_service()
        service.data_manager.connect.side_effect = RuntimeError("boom")
        with patch.object(
            data_mod.PreswaldService, "get_instance", return_value=service
        ):
            result = data_mod.connect()

        assert result is None


# ---------------------------------------------------------------------------
# query()
# ---------------------------------------------------------------------------

class TestQuery:

    def test_delegates_to_data_manager(self):
        service = _make_mock_service()
        expected_df = MagicMock(name="dataframe")
        service.data_manager.query.return_value = expected_df

        with patch.object(
            data_mod.PreswaldService, "get_instance", return_value=service
        ):
            result = data_mod.query("SELECT 1", "source_a")

        service.data_manager.query.assert_called_once_with("SELECT 1", "source_a")
        assert result is expected_df

    def test_query_error_returns_none(self):
        service = _make_mock_service()
        service.data_manager.query.side_effect = RuntimeError("bad sql")

        with patch.object(
            data_mod.PreswaldService, "get_instance", return_value=service
        ):
            result = data_mod.query("BAD SQL", "source_a")

        assert result is None


# ---------------------------------------------------------------------------
# get_df()
# ---------------------------------------------------------------------------

class TestGetDf:

    def test_delegates_to_data_manager(self):
        service = _make_mock_service()
        expected_df = MagicMock(name="dataframe")
        service.data_manager.get_df.return_value = expected_df

        with patch.object(
            data_mod.PreswaldService, "get_instance", return_value=service
        ):
            result = data_mod.get_df("source_a")

        service.data_manager.get_df.assert_called_once_with("source_a", None)
        assert result is expected_df

    def test_passes_table_name(self):
        service = _make_mock_service()
        service.data_manager.get_df.return_value = MagicMock()

        with patch.object(
            data_mod.PreswaldService, "get_instance", return_value=service
        ):
            data_mod.get_df("source_a", table_name="my_table")

        service.data_manager.get_df.assert_called_once_with("source_a", "my_table")

    def test_get_df_error_returns_none(self):
        service = _make_mock_service()
        service.data_manager.get_df.side_effect = RuntimeError("no such source")

        with patch.object(
            data_mod.PreswaldService, "get_instance", return_value=service
        ):
            result = data_mod.get_df("missing_source")

        assert result is None
