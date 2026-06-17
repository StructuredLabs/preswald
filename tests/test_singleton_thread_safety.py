"""
Tests for singleton thread safety
"""
import unittest
import threading
import time
from unittest.mock import patch


class TestSingletonThreadSafety(unittest.TestCase):
    """Test that singleton pattern is thread-safe."""

    def test_base_service_singleton_lock_exists(self):
        """Test that BasePreswaldService has _instance_lock."""
        from preswald.engine.base_service import BasePreswaldService

        self.assertTrue(hasattr(BasePreswaldService, '_instance_lock'))
        self.assertIsNotNone(BasePreswaldService._instance_lock)

    def test_singleton_instance_is_shared(self):
        """Test that singleton instance is shared across calls."""
        from preswald.engine.base_service import BasePreswaldService

        # Reset instance for test
        BasePreswaldService._instance = None

        # Create two instances
        instance1 = BasePreswaldService.initialize()
        instance2 = BasePreswaldService.get_instance()

        # They should be the same object
        self.assertIs(instance1, instance2)

        # Clean up
        BasePreswaldService._instance = None


class TestErrorRegistrySingleton(unittest.TestCase):
    """Test ErrorRegistry singleton pattern."""

    def test_error_registry_is_singleton(self):
        """Test that ErrorRegistry is a singleton."""
        from preswald.interfaces.render.error_registry import ErrorRegistry

        # Get two instances
        instance1 = ErrorRegistry.get_instance()
        instance2 = ErrorRegistry.get_instance()

        # They should be the same object
        self.assertIs(instance1, instance2)

    def test_error_registry_thread_safety(self):
        """Test that ErrorRegistry get_instance is thread-safe."""
        from preswald.interfaces.render.error_registry import ErrorRegistry

        instances = []
        errors = []

        def get_instance():
            try:
                instance = ErrorRegistry.get_instance()
                instances.append(instance)
            except Exception as e:
                errors.append(e)

        # Create multiple threads
        threads = [threading.Thread(target=get_instance) for _ in range(10)]

        # Start all threads
        for t in threads:
            t.start()

        # Wait for all to complete
        for t in threads:
            t.join()

        # All instances should be the same
        self.assertEqual(len(instances), 10)
        self.assertTrue(all(i is instances[0] for i in instances))
        self.assertEqual(len(errors), 0)


if __name__ == '__main__':
    unittest.main()
