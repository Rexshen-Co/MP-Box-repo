#!/usr/bin/env python3
"""
Simple demo program for practicing GitHub workflow
"""

def greet2(name):
    """Greet someone by name"""
    return f"Hello, {name}! Welcome to GitHub."

def calculate_sum(a, b):
    """Add two numbers"""
    return a + b

def main():
    """Main function"""
    print("=== GitHub Practice Program ===")
    print(greet("Developer"))
    
    result = calculate_sum(5, 3)
    print(f"5 + 3 = {result}")
    
    print("\nReady to practice git commands!")

if __name__ == "__main__":
    main()
