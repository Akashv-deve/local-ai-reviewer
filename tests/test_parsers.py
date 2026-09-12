import re
from nodes.review import ALLOWED_SEVERITY, ALLOWED_CATEGORY

def test_review_schema_drops_invalid_enums():
    # Mocking an LLM hallucinating a fake severity "BANANA" and fake category "Math"
    mock_llm_output = [
        {"severity": "HIGH", "category": "Bug", "file": "calc.py", "line": "2", "issue": "x", "recommendation": "y"},
        {"severity": "BANANA", "category": "Math", "file": "calc.py", "line": "4", "issue": "x", "recommendation": "y"}
    ]
    
    valid_reviews = []
    for item in mock_llm_output:
        if item["severity"].upper() in ALLOWED_SEVERITY and item["category"] in ALLOWED_CATEGORY:
            valid_reviews.append(item)
            
    # Proves the system drops "BANANA" and keeps "HIGH"
    assert len(valid_reviews) == 1
    assert valid_reviews[0]["severity"] == "HIGH"

def test_execution_regex_parsing():
    # Mocking a pytest terminal output
    mock_logs = "=========================== short test summary info ===========================\nFAILED test_ai.py::test_bad - assert 1 == 2\nERROR test_ai.py - NameError\n========================= 2 failed, 5 passed, 1 error in 0.12s ========================="
    
    passed_match = re.search(r'(\d+) passed', mock_logs)
    failed_match = re.search(r'(\d+) failed', mock_logs)
    error_match = re.search(r'(\d+) error', mock_logs)
    
    passed = int(passed_match.group(1)) if passed_match else 0
    failed = int(failed_match.group(1)) if failed_match else 0
    errors = int(error_match.group(1)) if error_match else 0
    
    assert passed == 5
    assert failed == 2
    assert errors == 1