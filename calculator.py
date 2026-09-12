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

def find_max(numbers):
    # Bug: Initializing to 0 causes it to fail if the list contains only negative numbers.
    # It also crashes with an error if the list is completely empty.
    max_val = 0  
    for n in numbers:
        if n > max_val:
            max_val = n
    return max_val