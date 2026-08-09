from typing import List, Dict, Any

class CacheAligner:
    """
    Reorders conversation context to maximize prefix consistency for LLM caching.
    Supports provider-specific cache control annotations.
    """
    
    def __init__(self, provider: str = "openai"):
        self.provider = provider

    def align_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Moves system messages and static instructions to the beginning of the context.
        This maximizes the static prefix length, leading to better cache hits.
        """
        system_messages = []
        other_messages = []
        
        for msg in messages:
            if msg.get("role") == "system":
                system_messages.append(msg)
            else:
                other_messages.append(msg)
                
        aligned_messages = system_messages + other_messages
        return self._apply_provider_caching(aligned_messages)
        
    def _apply_provider_caching(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Applies provider-specific caching configurations."""
        if not messages:
            return messages
            
        if self.provider == "anthropic":
            # Anthropic recommends putting cache_control blocks on the last system message
            # and potentially the last few human messages.
            # Here we just mark the last system message for simplicity.
            last_system_idx = -1
            for i, msg in enumerate(messages):
                if msg.get("role") == "system":
                    last_system_idx = i
                    
            if last_system_idx != -1:
                # Need to convert string content to a list of content blocks for Anthropic
                content = messages[last_system_idx].get("content", "")
                if isinstance(content, str):
                    messages[last_system_idx]["content"] = [
                        {
                            "type": "text", 
                            "text": content,
                            "cache_control": {"type": "ephemeral"}
                        }
                    ]
        
        # OpenAI and Google automatically use prefix caching based on the content matching,
        # so simply reordering the system messages is sufficient for them.
        return messages
