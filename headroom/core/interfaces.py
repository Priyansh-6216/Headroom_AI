from abc import ABC, abstractmethod
from typing import Any, Dict

class Compressor(ABC):
    """Base interface for all context compression strategies."""
    
    @abstractmethod
    def compress(self, data: Any, **kwargs) -> Any:
        """Compress the input data."""
        pass

class ContextManager(ABC):
    """Interface for managing the LLM conversation context."""
    
    @abstractmethod
    def add_message(self, message: Dict[str, Any]) -> None:
        pass
    
    @abstractmethod
    def get_messages(self) -> list:
        pass
    
    @abstractmethod
    def optimize(self) -> list:
        pass
