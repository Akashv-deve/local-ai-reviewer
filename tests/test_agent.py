from nodes.validation import validate_code
from nodes.generation import generate_tests
import re

def test_ast_blocks_malicious_imports():
    state = {"generated_tests": "import os\nos.system('rm -rf /')"}
    result = validate_code(state)
    assert result["validation_status"] == "FAIL"
    assert any("Blocked import 'os'" in err for err in result["validation_errors"])

def test_ast_blocks_dangerous_attributes():
    # Tests Point 5 from our critique (catching os.system)
    state = {"generated_tests": "import subprocess\nsubprocess.run(['ls'])"}
    result = validate_code(state)
    assert result["validation_status"] == "FAIL"
    assert any("Blocked attribute access 'subprocess.run'" in err for err in result["validation_errors"])

def test_ast_blocks_file_operations():
    state = {"generated_tests": "f = open('.gitignore', 'w')"}
    result = validate_code(state)
    assert result["validation_status"] == "FAIL"
    assert any("Blocked dangerous function 'open()'" in err for err in result["validation_errors"])

def test_regex_cleans_markdown():
    # Simulates the LLM returning code wrapped in markdown backticks
    raw_llm_output = "Here is the code:\n```python\nimport pytest\nassert 1==1\n```\nEnjoy!"
    match = re.search(r'```python(.*?)```', raw_llm_output, re.DOTALL)
    clean_code = match.group(1).strip() if match else raw_llm_output.replace('```python', '').replace('```', '').strip()
    
    assert clean_code == "import pytest\nassert 1==1"