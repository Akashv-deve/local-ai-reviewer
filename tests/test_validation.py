from nodes.validation import validate_code

def test_ast_blocks_malicious_imports():
    # Mocking an AI trying to import the OS module to execute a terminal command
    malicious_state = {"generated_tests": "import os\n\ndef test_hack():\n    os.system('rm -rf /')"}
    
    result = validate_code(malicious_state)
    
    assert result["validation_status"] == "FAIL"
    assert any("Blocked import 'os'" in err for err in result["validation_errors"])

def test_ast_blocks_dangerous_functions():
    # Mocking an AI trying to run arbitrary strings as code
    sneaky_state = {"generated_tests": "def test_sneaky():\n    eval('print(\"hacked\")')"}
    
    result = validate_code(sneaky_state)
    
    assert result["validation_status"] == "FAIL"
    assert any("Blocked dangerous function 'eval()'" in err for err in result["validation_errors"])

def test_ast_passes_safe_code():
    # Mocking safe, standard pytest code
    safe_state = {"generated_tests": "import pytest\n\ndef test_add():\n    assert 1 + 1 == 2"}
    
    result = validate_code(safe_state)
    
    assert result["validation_status"] == "PASS"
    assert len(result["validation_errors"]) == 0