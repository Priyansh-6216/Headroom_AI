import pytest
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from headroom.integrations.langchain import HeadroomChatModel
from headroom.compressors.text import TextCompressor

received_messages_store = []

class MockChatModel(BaseChatModel):
    # Minimal mock implementation
    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        # Return the messages it received for verification
        received_messages_store.clear()
        received_messages_store.extend(messages)
        from langchain_core.outputs import ChatResult, ChatGeneration
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content="Mock"))])
        
    @property
    def _llm_type(self) -> str:
        return "mock"

def test_langchain_integration():
    mock_model = MockChatModel()
    
    # We will override the crusher to make it predictable
    headroom_model = HeadroomChatModel(model=mock_model)
    headroom_model.crusher = TextCompressor(max_length=15, suffix="[T]")
    
    long_tool_output = "This is a very long tool output that should be truncated."
    
    messages = [
        HumanMessage(content="Hello"),
        ToolMessage(content=long_tool_output, tool_call_id="123")
    ]
    
    headroom_model.invoke(messages)
    
    # Check what the underlying model received
    received = received_messages_store
    assert len(received) == 2
    assert isinstance(received[0], HumanMessage)
    assert isinstance(received[1], ToolMessage)
    
    # Tool message should be compressed
    compressed_content = received[1].content
    assert compressed_content != long_tool_output
    assert len(compressed_content) == 15
    assert "[T]" in compressed_content
