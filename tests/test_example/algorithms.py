
def sum(a, b):
    a = a["number"]
    b = b["number"]
    return a + b


def subtract(a, b):
    a = a["number"]
    b = b["number"]
    return a - b


def mult(a, b):
    return a * b


def divide(a, b):
    return a / b


def average(a):
    return [a.sum() / len(a)]


def return_a_number():
    return 10


def does_nothing(*args, **kwargs):
    pass
