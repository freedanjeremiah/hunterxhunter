"""
Another sample Python code for comparison
"""

def fib(num):
    """Fibonacci function with different implementation."""
    a, b = 0, 1
    for _ in range(num):
        a, b = b, a + b
    return a

class SimpleCalc:
    """Basic calculator."""
    
    def __init__(self):
        self.results = []
    
    def add_numbers(self, x, y):
        total = x + y
        self.results.append(total)
        return total
    
    def multiply_numbers(self, x, y):
        product = x * y
        self.results.append(product)
        return product

def main():
    calculator = SimpleCalc()
    print(calculator.add_numbers(5, 3))
    print(calculator.multiply_numbers(4, 6))
    print(fib(10))

if __name__ == "__main__":
    main()