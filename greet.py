"""A tiny greeting utility."""


def greet(name: str = "") -> str:
    """Return a friendly greeting for the given name.

    Falls back to a generic greeting when no name is provided.
    """
    name = name.strip() if name else ""
    if not name:
        return "Hello there!"
    return f"Hello, {name}!"


if __name__ == "__main__":
    import sys

    who = " ".join(sys.argv[1:])
    print(greet(who))
