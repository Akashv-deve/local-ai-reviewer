import pytest

@pytest.mark.parametrize(
    "test_case",
    [
        pytest.param(
            {
                "severity": "HIGH",
                "category": "Bug",
                "file": "calculator.py",
                "line": "10",
                "issue": "The division operation lacks input validation and could result in a ZeroDivisionError.",
                "recommendation": "Add a check to ensure both 'a' and 'b' are non-zero before performing the division operation."
            },
            id="divide_with_zero"
        ),
        pytest.param(
            {
                "severity": "HIGH",
                "category": "Bug",
                "file": "calculator.py",
                "line": "14",
                "issue": "The 'calculate_average' function does not handle an empty list gracefully and could raise a ZeroDivisionError.",
                "recommendation": "Add a check to ensure the list is not empty before performing the division operation."
            },
            id="calculate_average_empty_list"
        )
    ]
)
def test_calculator(test_case):
    pass