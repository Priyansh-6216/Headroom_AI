import tiktoken
from typing import List, Dict, Any

class RollingWindow:
    """
    Manages conversation context limits using a rolling window approach,
    ensuring that paired tool calls and tool responses are never separated.
    """
    
    def __init__(self, max_tokens: int = 4000, model: str = "gpt-4o"):
        self.max_tokens = max_tokens
        self.model = model
        try:
            self.tokenizer = tiktoken.encoding_for_model(model)
        except KeyError:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        """Counts the number of tokens in a string."""
        if not text:
            return 0
        return len(self.tokenizer.encode(str(text)))

    def count_message_tokens(self, message: Dict[str, Any]) -> int:
        """Estimates tokens for a standard message dictionary."""
        tokens = 0
        for key, value in message.items():
            if isinstance(value, str):
                tokens += self.count_tokens(value)
            elif isinstance(value, list) or isinstance(value, dict):
                import json
                tokens += self.count_tokens(json.dumps(value))
        return tokens + 4  # Baseline overhead per message

    def apply_window(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Keeps system messages, and then keeps the most recent messages 
        that fit within max_tokens, ensuring tool calls aren't orphaned.
        """
        system_msgs = [m for m in messages if m.get("role") == "system"]
        other_msgs = [m for m in messages if m.get("role") != "system"]
        
        system_tokens = sum(self.count_message_tokens(m) for m in system_msgs)
        available_tokens = max(0, self.max_tokens - system_tokens)
        
        kept_msgs = []
        current_tokens = 0
        
        # We iterate backwards to keep the most recent messages
        i = len(other_msgs) - 1
        while i >= 0:
            msg = other_msgs[i]
            msg_tokens = self.count_message_tokens(msg)
            
            # Check for tool pairs
            paired_msgs = [msg]
            paired_tokens = msg_tokens
            
            # If this is a tool result, we must include its originating tool call
            if msg.get("role") == "tool":
                tool_call_id = msg.get("tool_call_id")
                # Look backwards for the assistant message that made this tool call
                j = i - 1
                found_call = False
                while j >= 0:
                    prev_msg = other_msgs[j]
                    if prev_msg.get("role") == "assistant" and prev_msg.get("tool_calls"):
                        # Ensure it's the right call
                        calls = prev_msg.get("tool_calls", [])
                        if any(c.get("id") == tool_call_id for c in calls):
                            # Include all tool results that might be associated with this assistant message
                            # To be perfectly safe, we'll just grab the block from j to i
                            block = other_msgs[j:i+1]
                            paired_msgs = block
                            paired_tokens = sum(self.count_message_tokens(m) for m in block)
                            i = j # Skip the ones we just bundled
                            found_call = True
                            break
                    j -= 1
                if not found_call:
                    # Missing its tool call (e.g. malformed or already pruned previously), skip it entirely
                    i -= 1
                    continue

            # Check if this message (or paired block) fits
            if current_tokens + paired_tokens > available_tokens and kept_msgs:
                # Reached token limit, stop adding
                break
                
            # Prepend because we are iterating backwards
            kept_msgs = paired_msgs + kept_msgs
            current_tokens += paired_tokens
            
            # Step back
            if len(paired_msgs) == 1:
                i -= 1
            
        return system_msgs + kept_msgs
