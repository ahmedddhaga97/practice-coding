from python_scaffold.main import hello


def test_hello_default():
    assert hello() == "Hello, world!"


def test_hello_name():
    assert hello("Alice") == "Hello, Alice!"
