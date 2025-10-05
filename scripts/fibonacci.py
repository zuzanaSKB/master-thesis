#!/usr/bin/env python3
import sys

# compute n-th fibonacci number F(0) = 0, F(1) = 1, F(n) = F(n-1) + F(n-2)
def fibonacci(n):
    if n == 0:
        return 0
    if n == 1:
        return 1
    
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    
    return b

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 fibonacci.py <n>", file=sys.stderr)
        sys.exit(1)
    
    try:
        n = int(sys.argv[1])
        result = fibonacci(n)
        #print(f"F({n}) = {result}")
    except ValueError as e:
        if "invalid literal" in str(e):
            print(f"Error: '{sys.argv[1]}' is not a valid integer", file=sys.stderr)
        else:
            print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()