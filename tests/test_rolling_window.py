from headroom.compressors.rolling_window import RollingWindow

def test_rolling_window_token_counting():
    rw = RollingWindow(model="gpt-4o")
    # "Hello world" is typically 2 tokens
    assert rw.count_tokens("Hello world") == 2
    
    msg = {"role": "user", "content": "Hello world"}
    # 3 tokens (values) + 4 overhead = 7 tokens
    assert rw.count_message_tokens(msg) == 7

def test_rolling_window_pruning():
    # Set max_tokens to roughly fit 2 short messages (approx 12 tokens each) + system message (approx 10 tokens)
    # Total limit: 30 tokens
    rw = RollingWindow(max_tokens=30, model="gpt-4o")
    
    messages = [
        {"role": "system", "content": "System prompt"}, # ~6 tokens
        {"role": "user", "content": "Message 1"},      # ~6 tokens
        {"role": "user", "content": "Message 2"},      # ~6 tokens
        {"role": "user", "content": "Message 3"},      # ~6 tokens
        {"role": "user", "content": "Message 4"},      # ~6 tokens
    ]
    
    # 5 * 6 = 30 tokens total, so everything should theoretically fit, but we add 4 overhead per msg
    # 5 * 10 = 50 tokens total. It shouldn't all fit.
    
    result = rw.apply_window(messages)
    
    # System message should always be kept
    assert result[0]["role"] == "system"
    # Should keep the most recent messages
    assert result[-1]["content"] == "Message 4"
    assert len(result) < len(messages)

def test_rolling_window_tool_pairing():
    # Make window small enough to force pruning
    rw = RollingWindow(max_tokens=50, model="gpt-4o")
    
    messages = [
        {"role": "system", "content": "Sys"},
        {"role": "user", "content": "Old message to be pruned"},
        {"role": "assistant", "content": None, "tool_calls": [{"id": "call_1", "function": {"name": "get_weather"}}]},
        {"role": "tool", "tool_call_id": "call_1", "content": "Sunny"}
    ]
    
    result = rw.apply_window(messages)
    
    # Check if tool result is there
    has_tool = any(m.get("role") == "tool" for m in result)
    # Check if assistant call is there
    has_call = any(m.get("role") == "assistant" and m.get("tool_calls") for m in result)
    
    # Both must either be present or absent. If present, they are paired.
    assert has_tool == has_call
    
    if has_tool:
        # Assert they are adjacent
        roles = [m.get("role") for m in result]
        assert roles[-2:] == ["assistant", "tool"]
