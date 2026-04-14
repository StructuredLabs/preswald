"""
Test cases for bug fixes:
1. Function return type mismatch - missing return value in exception path
2. Singleton pattern race condition
3. Inconsistent logging
4. Spelling errors
"""
import os
import sys
import tempfile
import threading
import time
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_read_port_from_config_exception_returns_value():
    """Bug 1: read_port_from_config should return original port value on exception, not None"""
    from preswald.utils import read_port_from_config
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
        f.write('this is not valid toml!!!')
        temp_path = f.name
    
    try:
        result = read_port_from_config(temp_path, 8000)
        assert result == 8000, f"Expected port 8000, got {result}"
        assert result is not None, "Result should not be None even on exception"
    finally:
        os.unlink(temp_path)
    
    print("✓ test_read_port_from_config_exception_returns_value PASSED")


def test_read_port_from_config_nonexistent_file_returns_port():
    """Test that read_port_from_config returns default port for non-existent file"""
    from preswald.utils import read_port_from_config
    
    result = read_port_from_config('nonexistent_file_1234.toml', 9000)
    assert result == 9000, f"Expected port 9000, got {result}"
    
    print("✓ test_read_port_from_config_nonexistent_file_returns_port PASSED")


def test_singleton_thread_safety():
    """Bug 2: Test singleton pattern thread safety"""
    from preswald.engine.base_service import BasePreswaldService
    
    BasePreswaldService._instance = None
    instances = []
    errors = []
    
    def create_instance():
        try:
            instance = BasePreswaldService.initialize()
            instances.append(instance)
        except Exception as e:
            errors.append(e)
    
    threads = [threading.Thread(target=create_instance) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    assert len(errors) == 0, f"Thread safety errors: {errors}"
    assert len(instances) == 10, f"Expected 10 instance references, got {len(instances)}"
    
    first_instance = instances[0]
    for instance in instances[1:]:
        assert instance is first_instance, "All threads should get the same instance"
    
    print("✓ test_singleton_thread_safety PASSED")


def test_singleton_get_instance_raises_when_not_initialized():
    """Test that get_instance raises RuntimeError when not initialized"""
    from preswald.engine.base_service import BasePreswaldService
    
    BasePreswaldService._instance = None
    
    with pytest.raises(RuntimeError):
        BasePreswaldService.get_instance()
    
    print("✓ test_singleton_get_instance_raises_when_not_initialized PASSED")


def test_logging_consistency_no_print_in_configure_logging():
    """Bug 3: Test that configure_logging uses logging.warning instead of print"""
    import ast
    
    utils_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'preswald', 'utils.py')
    with open(utils_path) as f:
        content = f.read()
    
    tree = ast.parse(content)
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == 'configure_logging':
            for subnode in ast.walk(node):
                if isinstance(subnode, ast.Call):
                    if isinstance(subnode.func, ast.Name) and subnode.func.id == 'print':
                        pytest.fail("print() found in configure_logging function - should use logging")
    
    print("✓ test_logging_consistency_no_print_in_configure_logging PASSED")


def test_spelling_fixed_upate_to_update():
    """Bug 4: Test that spelling error is fixed"""
    import ast
    
    runtime_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
        'preswald', 'engine', 'transformers', 'reactive_runtime.py'
    )
    
    with open(runtime_path, encoding='utf-8') as f:
        content = f.read()
    
    assert 'upate' not in content, "Spelling error 'upate' should be fixed to 'update'"
    assert 'update this to default' in content, "Correct spelling 'update' should be present"
    
    print("✓ test_spelling_fixed_upate_to_update PASSED")


def test_workflow_debug_log_level_correct():
    """Bug 5: Test that [DEBUG] logs use logger.debug instead of logger.info"""
    import ast
    
    workflow_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
        'preswald', 'interfaces', 'workflow.py'
    )
    
    with open(workflow_path, encoding='utf-8') as f:
        content = f.read()
    
    assert "logger.info('[DEBUG]'" not in content, "Should not use logger.info() with [DEBUG] prefix"
    
    tree = ast.parse(content)
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if (isinstance(node.func, ast.Attribute) and 
                node.func.attr == 'debug' and 
                isinstance(node.func.value, ast.Name) and 
                node.func.value.id == 'logger'):
                for arg in node.args:
                    if isinstance(arg, ast.Constant) and 'register_component_producer' in str(arg.value):
                        break
                else:
                    continue
                break
    else:
        pytest.fail("register_component_producer messages should use logger.debug()")
    
    print("✓ test_workflow_debug_log_level_correct PASSED")


def test_data_functions_raise_on_exception():
    """Bug 6: Test that data interface functions re-raise exceptions after logging"""
    import importlib
    
    import preswald.interfaces.data as data_module
    importlib.reload(data_module)
    
    import inspect
    
    connect_source = inspect.getsource(data_module.connect)
    query_source = inspect.getsource(data_module.query)
    get_df_source = inspect.getsource(data_module.get_df)
    
    assert 'raise' in connect_source, "connect() should re-raise after logging"
    assert 'raise' in query_source, "query() should re-raise after logging"
    assert 'raise' in get_df_source, "get_df() should re-raise after logging"
    
    print("✓ test_data_functions_raise_on_exception PASSED")


def test_frontend_debug_mechanism_exists():
    """Bug 7: Test that frontend has DEBUG mechanism in place"""
    websocket_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
        'frontend', 'src', 'utils', 'websocket.js'
    )
    
    with open(websocket_path, encoding='utf-8') as f:
        content = f.read()
    
    assert 'const DEBUG = import.meta.env?.DEV ?? false;' in content, "Should have DEBUG flag definition"
    assert 'const debugLog = DEBUG' in content, "Should have debugLog function"
    assert 'console.log' not in content, "console.log should be replaced with debugLog"
    
    print("✓ test_frontend_debug_mechanism_exists PASSED")


def test_boot_js_no_debug_console_log():
    """Bug 8: Test that boot.js has no debug console.log"""
    boot_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
        'preswald', 'browser', 'boot.js'
    )
    
    with open(boot_path, encoding='utf-8') as f:
        content = f.read()
    
    debug_messages = [
        '[Boot] Starting boot process',
        '[Boot] Waiting for PRESWALD_COMM',
        '[Boot] PRESWALD_COMM found',
        '[HTML-export] Project copied into',
        '[HTML-export] Files in /project',
        '[Client] Running initial script',
        '[Client] Processing'
    ]
    
    for msg in debug_messages:
        assert msg not in content, f"Should not have debug message: {msg}"
    
    assert 'console.error' in content, "Should keep console.error for actual errors"
    
    print("✓ test_boot_js_no_debug_console_log PASSED")


if __name__ == '__main__':
    print("\n" + "="*60)
    print("Running bug fix validation tests...")
    print("="*60 + "\n")
    
    test_read_port_from_config_exception_returns_value()
    test_read_port_from_config_nonexistent_file_returns_port()
    test_singleton_thread_safety()
    test_singleton_get_instance_raises_when_not_initialized()
    test_logging_consistency_no_print_in_configure_logging()
    test_spelling_fixed_upate_to_update()
    test_workflow_debug_log_level_correct()
    test_data_functions_raise_on_exception()
    test_frontend_debug_mechanism_exists()
    test_boot_js_no_debug_console_log()
    
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60)
