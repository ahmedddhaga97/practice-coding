def hello(name: str = "world") -> str:
    """Return a greeting for `name`."""
    return f"Hello, {name}!"


if __name__ == "__main__":
    print(hello())
    print(hello())
    print(hello("Alice"))
    print(hello("Bob"))