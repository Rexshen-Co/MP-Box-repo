def greet(name: str = "Rex") -> str:
    return f"Hello, {name}! This is second.py."


def farewell(name: str = "Rex") -> str:
    return f"Goodbye, {name}! See you next time."


if __name__ == "__main__":
    print(greet())
    print(farewell())
