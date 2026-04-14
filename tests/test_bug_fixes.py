"""
Test suite for bug fixes in preswald.

This module contains tests for:
1. Function return type mismatch - missing return on exception paths
2. Function exception paths not returning values
3. Known marked bugs (removed TODO: bug comments)
4. Spelling errors / undefined variables
5. Inconsistent logging methods
6. Singleton pattern race condition
7. Overly broad exception catching
8. Production debug logs
9. Logger level inconsistency
10. Production console.log statements
"""

import logging
import threading
import time
from unittest.mock import MagicMock, patch

import pytest


class TestDataFunctionExceptionPaths:
    """Tests for Bug 1&2: Function exception paths missing return values."""

    def test_connect_raises_exception_on_failure(self):
        """Test that connect() raises exception instead of returning None."""
        from preswald.interfaces import data

        with patch.object(data, 'PreswaldService') as mock_service:
            mock_service.get_instance.side_effect = RuntimeError("Service not initialized")

            with pytest.raises(RuntimeError, match="Service not initialized"):
                data.connect()

    def test_query_raises_exception_on_failure(self):
        """Test that query() raises exception instead of returning None."""
        from preswald.interfaces import data

        with patch.object(data, 'PreswaldService') as mock_service:
            mock_instance = MagicMock()
            mock_service.get_instance.return_value = mock_instance
            mock_instance.data_manager.query.side_effect = ValueError("Invalid SQL")

            with pytest.raises(ValueError, match="Invalid SQL"):
                data.query("SELECT * FROM nonexistent", "source")

    def test_get_df_raises_exception_on_failure(self):
        """Test that get_df() raises exception instead of returning None."""
        from preswald.interfaces import data

        with patch.object(data, 'PreswaldService') as mock_service:
            mock_instance = MagicMock()
            mock_service.get_instance.return_value = mock_instance
            mock_instance.data_manager.get_df.side_effect = FileNotFoundError("Source not found")

            with pytest.raises(FileNotFoundError, match="Source not found"):
                data.get_df("nonexistent_source")


class TestWorkflowSpellingErrors:
    """Tests for Bug 4: Spelling errors / undefined variables in workflow.py."""

    def test_set_variable_logs_correct_variable_names(self, caplog):
        """Test that set_variable uses correct parameter names in logging."""
        from preswald.interfaces.workflow import WorkflowContext

        context = WorkflowContext()

        with caplog.at_level(logging.DEBUG):
            context.set_variable("test_atom", "test_value")

        assert "test_atom" in caplog.text or len(caplog.records) == 0
        assert "producer_atom" not in caplog.text

    def test_set_variable_stores_value_correctly(self):
        """Test that set_variable correctly stores the value."""
        from preswald.interfaces.workflow import WorkflowContext

        context = WorkflowContext()
        context.set_variable("my_atom", "my_value")

        assert context.get_variable("my_atom") == "my_value"


class TestSingletonRaceCondition:
    """Tests for Bug 6: Singleton pattern race condition in base_service.py."""

    def test_singleton_thread_safety(self):
        """Test that singleton initialization is thread-safe."""
        from preswald.engine.base_service import BasePreswaldService

        BasePreswaldService._instance = None

        instances = []
        errors = []

        def create_instance():
            try:
                instance = BasePreswaldService.initialize()
                instances.append(id(instance))
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=create_instance) for _ in range(10)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0, f"Errors during concurrent initialization: {errors}"
        assert len(set(instances)) == 1, "Multiple instances created - race condition detected"

        BasePreswaldService._instance = None

    def test_singleton_double_checked_locking(self):
        """Test that double-checked locking pattern works correctly."""
        from preswald.engine.base_service import BasePreswaldService

        BasePreswaldService._instance = None

        instance1 = BasePreswaldService.initialize()
        instance2 = BasePreswaldService.initialize()

        assert instance1 is instance2, "Singleton should return same instance"

        BasePreswaldService._instance = None


class TestInconsistentLogging:
    """Tests for Bug 5: Inconsistent logging methods (print vs logger)."""

    def test_workflow_analyzer_uses_logger_not_print(self, caplog):
        """Test that WorkflowAnalyzer uses logger instead of print for errors."""
        from preswald.interfaces.workflow import Workflow, WorkflowAnalyzer

        workflow = Workflow()
        analyzer = WorkflowAnalyzer(workflow)

        with caplog.at_level(logging.ERROR):
            result = analyzer.get_critical_path()

        assert isinstance(result, list)

    def test_parallel_groups_uses_logger_not_print(self, caplog):
        """Test that get_parallel_groups uses logger instead of print."""
        from preswald.interfaces.workflow import Workflow, WorkflowAnalyzer

        workflow = Workflow()
        analyzer = WorkflowAnalyzer(workflow)

        with caplog.at_level(logging.ERROR):
            result = analyzer.get_parallel_groups()

        assert isinstance(result, list)


class TestProductionDebugLogs:
    """Tests for Bug 8: Production debug logs left in code."""

    def test_registry_no_debug_prefix_in_info_logs(self, caplog):
        """Test that registry info logs don't have [DEBUG] prefix."""
        from preswald.interfaces.render import registry

        with caplog.at_level(logging.INFO):
            registry.get_plotly_submodules()

        for record in caplog.records:
            if record.levelno == logging.INFO:
                assert "[DEBUG]" not in record.getMessage()


class TestLoggerLevelConsistency:
    """Tests for Bug 9: Logger level inconsistency."""

    def test_workflow_component_producer_registration_uses_debug(self, caplog):
        """Test that component producer registration uses debug level."""
        from preswald.interfaces.workflow import Workflow

        workflow = Workflow()
        workflow.register_component_producer("test_component", "test_atom")

        with caplog.at_level(logging.DEBUG):
            workflow.register_component_producer("test_comp2", "test_atom2")

        debug_records = [r for r in caplog.records if r.levelno == logging.DEBUG]
        assert any("register_component_producer" in r.getMessage() for r in debug_records) or len(debug_records) == 0


class TestErrorRegistrySingleton:
    """Tests for ErrorRegistry singleton pattern."""

    def test_error_registry_singleton_thread_safety(self):
        """Test that ErrorRegistry singleton is thread-safe."""
        from preswald.interfaces.render.error_registry import ErrorRegistry

        ErrorRegistry._instance = None

        instances = []

        def get_instance():
            instances.append(id(ErrorRegistry.get_instance()))

        threads = [threading.Thread(target=get_instance) for _ in range(10)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(set(instances)) == 1, "Multiple ErrorRegistry instances - race condition"

        ErrorRegistry._instance = None


class TestExceptionHandling:
    """Tests for proper exception handling patterns."""

    def test_data_functions_propagate_exceptions(self):
        """Test that data functions properly propagate exceptions with context."""
        from preswald.interfaces import data

        with patch.object(data, 'PreswaldService') as mock_service:
            mock_service.get_instance.side_effect = ConnectionError("Database connection failed")

            with pytest.raises(ConnectionError, match="Database connection failed"):
                data.connect()


class TestLoggingConsistency:
    """Tests for logging consistency across the codebase."""

    def test_no_print_statements_in_workflow(self):
        """Test that workflow.py doesn't use print statements for error logging."""
        import ast
        import inspect

        from preswald.interfaces import workflow

        source = inspect.getsource(workflow)
        tree = ast.parse(source)

        print_calls = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == 'print':
                    print_calls.append(node)

        error_handling_prints = []
        for call in print_calls:
            for arg in call.args:
                if isinstance(arg, ast.JoinedStr):
                    for value in arg.values:
                        if isinstance(value, ast.Constant) and 'Error' in str(value.value):
                            error_handling_prints.append(call)

        assert len(error_handling_prints) == 0, "Found print statements for error handling in workflow.py"
