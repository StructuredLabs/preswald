"""
Simple test cases for bug fixes - no external dependencies
"""
import os
import sys
import ast
import tempfile
import threading

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_read_port_from_config_fixed():
    """Test 1: read_port_from_config returns port value on exception"""
    print("Testing: read_port_from_config returns port value on exception...")
    
    utils_path = os.path.join(BASE_DIR, 'preswald', 'utils.py')
    
    with open(utils_path, encoding='utf-8') as f:
        content = f.read()
    
    tree = ast.parse(content)
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == 'read_port_from_config':
            has_return_in_except = False
            has_logger_warning = False
            
            for subnode in ast.walk(node):
                if isinstance(subnode, ast.ExceptHandler):
                    for stmt in subnode.body:
                        if isinstance(stmt, ast.Return):
                            has_return_in_except = True
                        if (isinstance(stmt, ast.Expr) and 
                            isinstance(stmt.value, ast.Call) and
                            isinstance(stmt.value.func, ast.Attribute) and
                            stmt.value.func.attr == 'warning'):
                            has_logger_warning = True
            
            assert has_return_in_except, "Missing return statement in except block"
            assert has_logger_warning, "Should use logger.warning, not print"
            print("  [OK] return statement present in exception handler")
            print("  [OK] using logger.warning instead of print")
            break
    
    print("  [OK] PASSED\n")


def test_data_functions_have_raise():
    """Test 2: data interface functions have raise after logging"""
    print("Testing: data interface functions re-raise exceptions...")
    
    data_path = os.path.join(BASE_DIR, 'preswald', 'interfaces', 'data.py')
    
    with open(data_path, encoding='utf-8') as f:
        content = f.read()
    
    tree = ast.parse(content)
    
    functions_to_check = ['connect', 'query', 'get_df']
    for func_name in functions_to_check:
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == func_name:
                has_raise = False
                for subnode in ast.walk(node):
                    if isinstance(subnode, ast.ExceptHandler):
                        for stmt in subnode.body:
                            if isinstance(stmt, ast.Raise):
                                has_raise = True
                                break
                
                assert has_raise, f"Function {func_name} should re-raise after logging"
                print(f"  [OK] {func_name}() re-raises exceptions")
                break
    
    print("  [OK] PASSED\n")


def test_singleton_has_locking():
    """Test 3: singleton pattern has proper locking"""
    print("Testing: singleton has proper double-checked locking...")
    
    base_service_path = os.path.join(BASE_DIR, 'preswald', 'engine', 'base_service.py')
    
    with open(base_service_path, encoding='utf-8') as f:
        content = f.read()
    
    tree = ast.parse(content)
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == 'BasePreswaldService':
            has_lock_class_var = False
            has_instance_class_var = False
            has_with_lock = False
            
            for item in node.body:
                if isinstance(item, ast.Assign):
                    for target in item.targets:
                        if isinstance(target, ast.Name):
                            if target.id == '_lock':
                                has_lock_class_var = True
                            if target.id == '_instance':
                                has_instance_class_var = True
            
            for subnode in ast.walk(node):
                if isinstance(subnode, ast.With):
                    if (isinstance(subnode.items[0].context_expr, ast.Attribute) and
                        subnode.items[0].context_expr.attr == '_lock'):
                        has_with_lock = True
            
            assert has_lock_class_var, "Missing _lock class variable"
            assert has_instance_class_var, "Missing _instance class variable"
            assert has_with_lock, "Missing with cls._lock in initialize"
            
            print("  [OK] _lock class variable present")
            print("  [OK] _instance class variable present")  
            print("  [OK] using double-checked locking pattern")
            break
    
    print("  [OK] PASSED\n")


def test_spelling_error_fixed():
    """Test 4: spelling error fixed"""
    print("Testing: spelling error 'upate' -> 'update'...")
    
    runtime_path = os.path.join(
        BASE_DIR, 'preswald', 'engine', 'transformers', 'reactive_runtime.py'
    )
    
    with open(runtime_path, encoding='utf-8') as f:
        content = f.read()
    
    assert 'upate' not in content, "Spelling error 'upate' should be fixed"
    assert 'update this to default' in content, "Correct 'update' spelling should be present"
    
    print("  [OK] spelling 'upate' fixed to 'update'")
    print("  [OK] PASSED\n")


def test_logger_level_consistency():
    """Test 5: debug messages use correct logger level"""
    print("Testing: debug messages use logger.debug not logger.info...")
    
    workflow_path = os.path.join(BASE_DIR, 'preswald', 'interfaces', 'workflow.py')
    
    with open(workflow_path, encoding='utf-8') as f:
        content = f.read()
    
    assert "logger.info('[DEBUG]'" not in content, "Should not use logger.info() with [DEBUG] prefix"
    assert "logger.info('[DEBUG]" not in content, "Should not use logger.info() with [DEBUG] prefix"
    print("  [OK] no logger.info with [DEBUG] prefix in workflow.py")
    
    registry_path = os.path.join(BASE_DIR, 'preswald', 'interfaces', 'render', 'registry.py')
    
    with open(registry_path, encoding='utf-8') as f:
        content = f.read()
    
    assert "logger.info('[DEBUG]'" not in content, "Should not use logger.info() with [DEBUG] prefix"
    assert "logger.info('[DEBUG]" not in content, "Should not use logger.info() with [DEBUG] prefix"
    print("  [OK] no logger.info with [DEBUG] prefix in registry.py")
    
    print("  [OK] PASSED\n")


def test_no_print_in_logging_config():
    """Test 6: no print in configure_logging, uses logging.warning"""
    print("Testing: no print() in configure_logging...")
    
    utils_path = os.path.join(BASE_DIR, 'preswald', 'utils.py')
    
    with open(utils_path, encoding='utf-8') as f:
        content = f.read()
    
    tree = ast.parse(content)
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == 'configure_logging':
            for subnode in ast.walk(node):
                if isinstance(subnode, ast.Call):
                    if isinstance(subnode.func, ast.Name) and subnode.func.id == 'print':
                        pytest.fail("print() found in configure_logging function")
    
    print("  [OK] no print() in configure_logging function")
    print("  [OK] PASSED\n")


def test_frontend_debug_mechanism():
    """Test 7: frontend has proper debug mechanism"""
    print("Testing: frontend has proper DEBUG mechanism...")
    
    websocket_path = os.path.join(BASE_DIR, 'frontend', 'src', 'utils', 'websocket.js')
    
    with open(websocket_path, encoding='utf-8') as f:
        content = f.read()
    
    assert 'const DEBUG = import.meta.env?.DEV ?? false;' in content, "Should have DEBUG flag definition"
    assert 'const debugLog = DEBUG' in content, "Should have debugLog function"
    
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if i > 10 and 'console.log' in line and '.bind' not in line:
            pytest.fail(f"Found raw console.log at line {i+1}: {line}")
    
    print("  [OK] DEBUG flag using import.meta.env.DEV")
    print("  [OK] debugLog wrapper function present")
    print("  [OK] no raw console.log calls found")
    print("  [OK] PASSED\n")


def test_boot_js_clean():
    """Test 8: boot.js has no debug console.log"""
    print("Testing: boot.js has no debug console.log...")
    
    boot_path = os.path.join(BASE_DIR, 'preswald', 'browser', 'boot.js')
    
    with open(boot_path, encoding='utf-8') as f:
        content = f.read()
    
    debug_messages = [
        'Starting boot process',
        'Waiting for PRESWALD_COMM',
        'PRESWALD_COMM found',
        'Project copied into',
        'Files in /project',
        'Running initial script',
        'Processing'
    ]
    
    for msg in debug_messages:
        assert msg not in content, f"Should not have debug message: {msg}"
    
    assert 'console.error' in content, "Should keep console.error for actual errors"
    
    print("  [OK] debug console.log messages removed")
    print("  [OK] console.error kept for actual errors")
    print("  [OK] PASSED\n")


def test_virtual_service_singleton_integrity():
    """Test 9: VirtualPreswaldService does not redefine _instance"""
    print("Testing: VirtualPreswaldService singleton integrity...")
    
    virtual_path = os.path.join(BASE_DIR, 'preswald', 'browser', 'virtual_service.py')
    
    with open(virtual_path, encoding='utf-8') as f:
        content = f.read()
    
    tree = ast.parse(content)
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == 'VirtualPreswaldService':
            for item in node.body:
                if isinstance(item, ast.Assign):
                    for target in item.targets:
                        if isinstance(target, ast.Name) and target.id == '_instance':
                            pytest.fail("VirtualPreswaldService should not redefine _instance, should inherit from BasePreswaldService")
    
    print("  [OK] VirtualPreswaldService uses inherited _instance")
    print("  [OK] PASSED\n")


def test_workflow_no_print_in_exception():
    """Test 10: workflow.py exception handlers use logger, not print"""
    print("Testing: workflow.py exception handlers use logger.error not print...")
    
    workflow_path = os.path.join(BASE_DIR, 'preswald', 'interfaces', 'workflow.py')
    
    with open(workflow_path, encoding='utf-8') as f:
        content = f.read()
    
    assert 'print(f"Error finding critical path:' not in content, "critical path exception should use logger.error"
    assert 'print(f"Error finding parallel groups:' not in content, "parallel groups exception should use logger.error"
    assert 'logger.error(f"Error finding critical path:' in content, "critical path exception should use logger.error"
    assert 'logger.error(f"Error finding parallel groups:' in content, "parallel groups exception should use logger.error"
    
    print("  [OK] exception handlers in workflow.py use logger.error")
    print("  [OK] PASSED\n")


def test_no_logger_info_with_debug_prefix():
    """Test 11: No logger.info with [DEBUG] prefix"""
    print("Testing: no logger.info with [DEBUG] prefix...")
    
    preswald_dir = os.path.join(BASE_DIR, 'preswald')
    
    for root, _dirs, files in os.walk(preswald_dir):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                with open(filepath, encoding='utf-8') as f:
                    content = f.read()
                    assert "logger.info('[DEBUG]'" not in content, f"Found logger.info('[DEBUG]' in {filepath}"
                    assert 'logger.info("[DEBUG]"' not in content, f"Found logger.info('[DEBUG]' in {filepath}"
    
    print("  [OK] no logger.info with [DEBUG] prefix found")
    print("  [OK] PASSED\n")


def test_websocket_debug_mechanism_correct():
    """Test 12: websocket.js has correct debug mechanism"""
    print("Testing: websocket.js debug mechanism correct...")
    
    websocket_path = os.path.join(BASE_DIR, 'frontend', 'src', 'utils', 'websocket.js')
    
    with open(websocket_path, encoding='utf-8') as f:
        content = f.read()
    
    assert 'const debugLog = DEBUG ? console.log.bind(console)' in content, "debugLog binding incorrect"
    assert 'const debugError = DEBUG ? console.error.bind(console)' in content, "Should have debugError"
    assert 'debugError.bind' not in content, "Should not have self-referential binding bug for debugError"
    assert 'debugWarn.bind' not in content, "Should not have self-referential binding bug for debugWarn"
    assert 'debugLog.bind' not in content, "Should not have self-referential binding bug for debugLog"
    
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if i > 10 and 'console.log' in line and '.bind' not in line:
            pytest.fail(f"Found raw console.log at line {i+1}: {line}")
    
    print("  [OK] debug mechanism has no self-referential bugs")
    print("  [OK] debugError function exists and properly bound")
    print("  [OK] no raw console.log calls found")
    print("  [OK] PASSED\n")


def test_dynamic_components_use_debug_utils():
    """Test 13: DynamicComponents uses debug utils"""
    print("Testing: DynamicComponents uses debug utils...")
    
    dc_path = os.path.join(BASE_DIR, 'frontend', 'src', 'components', 'DynamicComponents.jsx')
    
    with open(dc_path, encoding='utf-8') as f:
        content = f.read()
    
    assert "from '@/utils/debug'" in content, "Should import debug utils"
    assert 'console.log' not in content, "All console.log should be replaced with debugLog"
    
    print("  [OK] imports debug utils")
    print("  [OK] no raw console.log found")
    print("  [OK] PASSED\n")


def test_spelling_gaurd_fixed():
    """Test 14: spelling 'gaurd' -> 'guard' fixed"""
    print("Testing: spelling 'gaurd' -> 'guard' fixed...")
    
    runtime_path = os.path.join(
        BASE_DIR, 'preswald', 'engine', 'transformers', 'reactive_runtime.py'
    )
    
    with open(runtime_path, encoding='utf-8') as f:
        content = f.read()
    
    assert 'gaurd' not in content, "Spelling error 'gaurd' should be fixed"
    assert 'register_display_dependency_resolver guard' in content, "Correct 'guard' spelling should be present"
    
    print("  [OK] spelling 'gaurd' -> 'guard' fixed")
    print("  [OK] PASSED\n")


def main():
    print("\n" + "="*60)
    print("Running bug fix validation tests (no dependencies)")
    print("="*60 + "\n")
    
    tests = [
        test_read_port_from_config_fixed,
        test_data_functions_have_raise,
        test_singleton_has_locking,
        test_spelling_error_fixed,
        test_logger_level_consistency,
        test_no_print_in_logging_config,
        test_frontend_debug_mechanism,
        test_boot_js_clean,
        test_virtual_service_singleton_integrity,
        test_workflow_no_print_in_exception,
        test_no_logger_info_with_debug_prefix,
        test_websocket_debug_mechanism_correct,
        test_dynamic_components_use_debug_utils,
        test_spelling_gaurd_fixed,
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"  [FAIL] FAILED: {e}\n")
            failed += 1
    
    print("="*60)
    print(f"Results: {passed} PASSED, {failed} FAILED")
    print("="*60)
    
    if failed > 0:
        sys.exit(1)
    else:
        print("\n[OK] ALL TESTS PASSED!")


if __name__ == '__main__':
    main()
