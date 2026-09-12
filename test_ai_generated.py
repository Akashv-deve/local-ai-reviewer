import pytest

def test_add():
    assert add(1, 2) == 3
    assert add(-1, 1) == 0
    assert add(-1, -1) == -2

def test_subtract():
    assert subtract(1, 2) == -1
    assert subtract(-1, 1) == -2
    assert subtract(-1, -1) == 0