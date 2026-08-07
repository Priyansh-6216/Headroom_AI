import pytest

@pytest.fixture
def dummy_message():
    return {
        "role": "user",
        "content": "Hello, world!"
    }
