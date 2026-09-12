import pytest

# Critical: Import the correct module based on the modified file path
from calculator import subtract, multiply, divide

def test_subtract():
    assert subtract(2, 3) == -1
    assert subtract(-1, 1) == -2
    assert subtract(0, 0) == 0

def test_multiply():
    assert multiply(4, 3) == 12
    assert multiply(-4, 3) == -12
    assert multiply(-4, -3) == 12
    assert multiply(0, 5) == 0

def test_divide():
    assert divide(10, 2) == 5
    assert divide(-10, 2) == -5
    assert divide(10, -2) == -5
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)