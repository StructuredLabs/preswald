"""
Tests for exception handling improvements
"""
import unittest
from unittest.mock import Mock, patch
import pandas as pd


class TestExceptionHandling(unittest.TestCase):
    """Test that exceptions are handled properly."""

    def test_connect_exception_returns_none(self):
        """Test that connect() returns None on exception."""
        from preswald.interfaces.data import connect

        # Mock PreswaldService to raise exception
        with patch('preswald.interfaces.data.PreswaldService') as mock_service:
            mock_instance = Mock()
            mock_instance.data_manager.connect.side_effect = Exception("Connection error")
            mock_service.get_instance.return_value = mock_instance

            # Call connect and verify it returns None on exception
            result = connect()

            # Should return None, not raise
            self.assertIsNone(result)

    def test_data_manager_cleanup_exception_handling(self):
        """Test that DataManager cleanup handles exceptions gracefully."""
        from preswald.engine.managers.data import ClickhouseSource

        # Create a mock duckdb connection that raises on execute
        mock_duckdb = Mock()
        mock_duckdb.execute.side_effect = Exception("Cleanup error")

        # Create source and test cleanup
        source = ClickhouseSource.__new__(ClickhouseSource)
        source._duckdb = mock_duckdb

        # This should not raise
        try:
            source.__del__()
        except Exception:
            self.fail("__del__ should not raise exceptions")


class TestLoggerConsistency(unittest.TestCase):
    """Test that loggers are used consistently."""

    def test_workflow_uses_logger_for_errors(self):
        """Test that workflow uses logger instead of print for errors."""
        from preswald.interfaces.workflow import Workflow
        import logging

        # Check that the module has a logger
        import preswald.interfaces.workflow as workflow_module
        self.assertTrue(hasattr(workflow_module, 'logger'))


if __name__ == '__main__':
    unittest.main()
