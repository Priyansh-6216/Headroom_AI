import pytest
from headroom.integrations.agno import HeadroomAgnoModel
from headroom.compressors.text import TextCompressor

class MockAgnoMessage:
    def __init__(self, role, content):
        self.role = role
        self.content = content

class MockAgnoModel:
    def __init__(self):
        self.id = "mock"
        
    def response(self, messages, **kwargs):
        self.received_messages = messages
        return "mock_response"

def test_agno_integration(monkeypatch):
    import headroom.integrations.agno
    monkeypatch.setattr(headroom.integrations.agno, "AGNO_AVAILABLE", True)
    
    mock_model = MockAgnoModel()
    
    # We will override the crusher
    headroom_model = HeadroomAgnoModel(model=mock_model)
    headroom_model.crusher = TextCompressor(max_length=15, suffix="[T]")
    
    long_tool_output = "This is a very long tool output that should be truncated by the agno wrapper."
    
    messages = [
        MockAgnoMessage(role="user", content="Hello"),
        MockAgnoMessage(role="tool", content=long_tool_output)
    ]
    
    headroom_model.response(messages)
    
    received = mock_model.received_messages
    assert len(received) == 2
    assert received[0].content == "Hello"
    
    # Tool message should be compressed
    compressed_content = received[1].content
    assert compressed_content != long_tool_output
    assert len(compressed_content) == 15
    assert "[T]" in compressed_content
