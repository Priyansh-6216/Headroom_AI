from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import uuid

class MemoryStore(ABC):
    """Interface for storage backends to hold uncompressed original data."""
    
    @abstractmethod
    def store(self, data: Any) -> str:
        """Stores data and returns a unique reference ID."""
        pass
        
    @abstractmethod
    def retrieve(self, ref_id: str) -> Optional[Any]:
        """Retrieves data using a reference ID. Returns None if not found."""
        pass


class InMemoryStore(MemoryStore):
    """A simple dictionary-based memory store. Not persistent across runs."""
    
    def __init__(self):
        self._store: Dict[str, Any] = {}
        
    def store(self, data: Any) -> str:
        ref_id = f"ref_{uuid.uuid4().hex[:8]}"
        self._store[ref_id] = data
        return ref_id
        
    def retrieve(self, ref_id: str) -> Optional[Any]:
        return self._store.get(ref_id)
