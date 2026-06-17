"""
Tests for data interface bug fixes
"""
import unittest
from unittest.mock import Mock, patch
import pandas as pd


class TestDataInterfaceReturnValues(unittest.TestCase):
    """Test that data interface functions return proper values in all paths."""

    def test_query_exception_returns_empty_dataframe(self):
        """Test that query() returns empty DataFrame on exception."""
        from preswald.interfaces.data import query

        # Mock PreswaldService to raise exception
        with patch('preswald.interfaces.data.PreswaldService') as mock_service:
            mock_instance = Mock()
            mock_instance.data_manager.query.side_effect = Exception("Connection error")
            mock_service.get_instance.return_value = mock_instance

            # Call query and verify it returns empty DataFrame on exception
            result = query("SELECT * FROM test", "test_source")

            # Should return empty DataFrame, not None
            self.assertIsInstance(result, pd.DataFrame)
            self.assertTrue(result.empty)

    def test_get_df_exception_returns_empty_dataframe(self):
        """Test that get_df() returns empty DataFrame on exception."""
        from preswald.interfaces.data import get_df

        # Mock PreswaldService to raise exception
        with patch('preswald.interfaces.data.PreswaldService') as mock_service:
            mock_instance = Mock()
            mock_instance.data_manager.get_df.side_effect = Exception("Connection error")
            mock_service.get_instance.return_value = mock_instance

            # Call get_df and verify it returns empty DataFrame on exception
            result = get_df("test_source")

            # Should return empty DataFrame, not None
            self.assertIsInstance(result, pd.DataFrame)
            self.assertTrue(result.empty)

    def test_query_success_returns_dataframe(self):
        """Test that query() returns DataFrame on success."""
        from preswald.interfaces.data import query

        expected_df = pd.DataFrame({'col1': [1, 2], 'col2': ['a', 'b']})

        with patch('preswald.interfaces.data.PreswaldService') as mock_service:
            mock_instance = Mock()
            mock_instance.data_manager.query.return_value = expected_df
            mock_service.get_instance.return_value = mock_instance

            result = query("SELECT * FROM test", "test_source")

            self.assertIsInstance(result, pd.DataFrame)
            pd.testing.assert_frame_equal(result, expected_df)

    def test_get_df_success_returns_dataframe(self):
        """Test that get_df() returns DataFrame on success."""
        from preswald.interfaces.data import get_df

        expected_df = pd.DataFrame({'col1': [1, 2], 'col2': ['a', 'b']})

        with patch('preswald.interfaces.data.PreswaldService') as mock_service:
            mock_instance = Mock()
            mock_instance.data_manager.get_df.return_value = expected_df
            mock_service.get_instance.return_value = mock_instance

            result = get_df("test_source")

            self.assertIsInstance(result, pd.DataFrame)
            pd.testing.assert_frame_equal(result, expected_df)


if __name__ == '__main__':
    unittest.main()
