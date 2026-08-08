import json
from typing import Any, Dict, List, Union

def compress_json(data: Union[Dict, List, str], max_list_items: int = 5) -> Union[Dict, List, str]:
    """
    Compresses a JSON structure by truncating long lists.
    Keeps the first few items and a placeholder for the rest.
    """
    if isinstance(data, str):
        try:
            parsed = json.loads(data)
            return json.dumps(compress_json(parsed, max_list_items))
        except json.JSONDecodeError:
            return data
            
    if isinstance(data, dict):
        return {k: compress_json(v, max_list_items) for k, v in data.items()}
        
    if isinstance(data, list):
        if len(data) <= max_list_items:
            return [compress_json(item, max_list_items) for item in data]
            
        keep = max_list_items - 1
        compressed_list = [compress_json(item, max_list_items) for item in data[:keep]]
        compressed_list.append(f"... [{len(data) - keep} more items truncated]")
        return compressed_list
        
    return data
