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

    # Python Program to find the L.C.M. of two input number

def compute_lcm(a, b):

   # choose the greater number
   if a > b:
       greater = a
   else:
       greater = b