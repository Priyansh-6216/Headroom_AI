import json
from typing import Any
from headroom.core.interfaces import Compressor
from headroom.compressors.text import TextCompressor
from headroom.utils.json_parser import compress_json

class SmartCrusher(Compressor):
    """
    Intelligently compresses data by detecting its type (JSON, dict, list, text)
    and applying the appropriate compression strategy.
    """
    
    def __init__(self, max_text_length: int = 1000, max_list_items: int = 5):
        self.text_compressor = TextCompressor(max_length=max_text_length)
        self.max_list_items = max_list_items

    def compress(self, data: Any, **kwargs) -> Any:
        """Compress data based on its structural type."""
        # Try JSON parsing if it's a string
        if isinstance(data, str):
            try:
                parsed = json.loads(data)
                # It's JSON, compress structure then dump back
                compressed = compress_json(parsed, self.max_list_items)
                return json.dumps(compressed)
            except json.JSONDecodeError:
                # Fallback to pure text compression
                return self.text_compressor.compress(data)
                
        # If it's already a dict or list
        if isinstance(data, (dict, list)):
            return compress_json(data, self.max_list_items)
            
        # Fallback for other types
        return self.text_compressor.compress(str(data))
