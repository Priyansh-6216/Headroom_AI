from typing import Any, List, Optional
from headroom.compressors.smart_crusher import SmartCrusher

try:
    from agno.models.base import Model
    from agno.messages import Message
    AGNO_AVAILABLE = True
except ImportError:
    Model = object
    Message = object
    AGNO_AVAILABLE = False

class HeadroomAgnoModel(Model):
    """
    Wraps an Agno Model to compress tool outputs before they are processed by the LLM.
    """
    
    def __init__(self, model: Model, **kwargs):
        if not AGNO_AVAILABLE:
            raise ImportError("agno is not installed. Run `pip install agno`.")
        # We don't call super() if it interferes with the underlying model wrapping
        # A true implementation would inherit properly or use composition.
        # For this demonstration, we use composition.
        self.model = model
        self.crusher = SmartCrusher()
        # Copy basic attributes that might be expected
        self.id = getattr(model, "id", "headroom_model")
        
    def _compress_messages(self, messages: List[Message]) -> List[Message]:
        compressed_msgs = []
        for msg in messages:
            # In Agno, tool responses usually have role='tool'
            if getattr(msg, "role", "") == "tool" and hasattr(msg, "content"):
                original = msg.content
                if isinstance(original, str):
                    compressed = self.crusher.compress(original)
                    if len(str(compressed)) < len(original):
                        # Safe copy or mutate
                        # Usually it's better to create a new object, but Agno messages might vary
                        import copy
                        new_msg = copy.deepcopy(msg)
                        new_msg.content = compressed
                        compressed_msgs.append(new_msg)
                        continue
            compressed_msgs.append(msg)
        return compressed_msgs
        
    def response(self, messages: List[Message], **kwargs) -> Any:
        # Intercept and compress
        compressed = self._compress_messages(messages)
        return self.model.response(messages=compressed, **kwargs)
        
    def async_response(self, messages: List[Message], **kwargs) -> Any:
        compressed = self._compress_messages(messages)
        return self.model.async_response(messages=compressed, **kwargs)
