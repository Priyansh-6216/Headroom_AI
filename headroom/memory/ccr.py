from typing import Any, Dict
from headroom.memory.store import MemoryStore
from headroom.core.interfaces import Compressor

class CCRManager:
    """
    Compress-Cache-Retrieve Manager.
    Works as a wrapper around a compressor to store the original data
    and inject a retrieval reference into the compressed output.
    """
    
    def __init__(self, compressor: Compressor, store: MemoryStore):
        self.compressor = compressor
        self.store = store

    def process(self, data: Any) -> Any:
        """
        Compresses data, stores the original in memory, 
        and returns the compressed data along with a retrieval ID.
        """
        # Compress the data
        compressed = self.compressor.compress(data)
        
        # If no significant compression happened, we might not need to store it
        # But for simplicity, we'll store everything that passes through CCR
        ref_id = self.store.store(data)
        
        # Inject the reference ID.
        # If it's a string, we append it. If it's a dict, we add a key.
        # We try to keep it non-intrusive.
        if isinstance(compressed, str):
            return f"{compressed}\n\n[Original data available via CCR. Use retrieval tool with ID: {ref_id}]"
        
        if isinstance(compressed, dict):
            compressed["_ccr_ref"] = ref_id
            return compressed
            
        if isinstance(compressed, list):
            # Just append a string to the list to notify the LLM
            compressed.append(f"[Original data available via CCR. ID: {ref_id}]")
            return compressed
            
        return compressed
        
    def retrieve(self, ref_id: str) -> Any:
        """Retrieves original data from store."""
        return self.store.retrieve(ref_id)
