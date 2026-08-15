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
            
        # Extract anomalies (items containing error keywords)
        anomalies = []
        regular = []
        
        for item in data:
            item_str = str(item).lower()
            if any(keyword in item_str for keyword in ["error", "fatal", "exception", "fail", "critical", "pg-"]):
                anomalies.append(item)
            else:
                regular.append(item)
                
        # Keep anomalies + first few regular items
        keep = max(0, max_list_items - len(anomalies) - 1)
        compressed_list = [compress_json(item, max_list_items) for item in regular[:keep]]
        
        # Add truncated message
        truncated_count = len(regular) - keep
        if truncated_count > 0:
            compressed_list.append(f"... [{truncated_count} more items truncated]")
            
        # Add anomalies back
        compressed_list.extend([compress_json(item, max_list_items) for item in anomalies])
        return compressed_list
        
    return data
