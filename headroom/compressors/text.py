from typing import Any
from headroom.core.interfaces import Compressor

class TextCompressor(Compressor):
    """Compresses text by truncating it to a maximum length."""
    
    def __init__(self, max_length: int = 1000, suffix: str = "... [TRUNCATED]"):
        self.max_length = max_length
        self.suffix = suffix

    def compress(self, data: Any, **kwargs) -> str:
        """Truncates text if it exceeds the max length."""
        text = str(data)
        if len(text) <= self.max_length:
            return text
            
        keep_length = self.max_length - len(self.suffix)
        if keep_length <= 0:
            return self.suffix
            
        return text[:keep_length] + self.suffix
