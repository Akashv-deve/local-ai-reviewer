def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    return a / b

def unsafe_divide(a, b):
    return a / b

def calculate_average(numbers):
    # Bug: Doesn't check for an empty list, which will cause a ZeroDivisionError
    total = sum(numbers)
    return total / len(numbers)