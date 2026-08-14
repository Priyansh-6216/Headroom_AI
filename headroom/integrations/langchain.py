from typing import Any, List, Optional
import json
from headroom.compressors.smart_crusher import SmartCrusher

try:
    from langchain_core.language_models.chat_models import BaseChatModel
    from langchain_core.messages import BaseMessage, ToolMessage
    from langchain_core.outputs import ChatResult
    LANGCHAIN_AVAILABLE = True
except ImportError:
    # Create mock classes if langchain-core isn't installed
    BaseChatModel = object
    BaseMessage = object
    ToolMessage = object
    ChatResult = object
    LANGCHAIN_AVAILABLE = False

class HeadroomChatModel(BaseChatModel):
    """
    Wraps any LangChain BaseChatModel to apply Headroom compression
    to tool messages automatically before they are sent to the LLM.
    """
    
    # Define standard LangChain fields as private attributes or Pydantic fields
    # LangChain v0.1+ uses pydantic v1 or v2 depending on core version.
    # To keep it simple, we wrap the model directly and delegate.
    
    model: Any
    crusher: Any

    def __init__(self, model: BaseChatModel, **kwargs):
        if not LANGCHAIN_AVAILABLE:
            raise ImportError("langchain-core is not installed. Run `pip install langchain-core`.")
        # Pydantic v1 vs v2 compatibility for LangChain
        super().__init__(model=model, crusher=SmartCrusher(), **kwargs)

    @property
    def _llm_type(self) -> str:
        return f"headroom_{self.model._llm_type}"

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any,
    ) -> ChatResult:
        
        # Compress tool messages before passing to the underlying model
        compressed_messages = []
        for msg in messages:
            if isinstance(msg, ToolMessage):
                original_content = msg.content
                if isinstance(original_content, str):
                    compressed = self.crusher.compress(original_content)
                    if len(str(compressed)) < len(original_content):
                        # Create a new ToolMessage with compressed content
                        compressed_msg = ToolMessage(
                            content=compressed,
                            tool_call_id=msg.tool_call_id,
                            name=msg.name
                        )
                        compressed_messages.append(compressed_msg)
                        continue
            
            # If not a tool message or compression wasn't smaller, keep original
            compressed_messages.append(msg)
            
        # Forward to underlying model
        return self.model._generate(
            messages=compressed_messages, 
            stop=stop, 
            run_manager=run_manager, 
            **kwargs
        )
