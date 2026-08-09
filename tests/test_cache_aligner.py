from headroom.compressors.cache_aligner import CacheAligner

def test_cache_aligner_reordering():
    aligner = CacheAligner(provider="openai")
    messages = [
        {"role": "user", "content": "hello"},
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "assistant", "content": "Hi there"},
        {"role": "system", "content": "Always output JSON"}
    ]
    
    aligned = aligner.align_messages(messages)
    
    # Check that both system messages were moved to the front
    assert aligned[0]["role"] == "system"
    assert aligned[1]["role"] == "system"
    # Check the contents
    assert aligned[0]["content"] == "You are a helpful assistant"
    assert aligned[1]["content"] == "Always output JSON"
    # User and assistant follow
    assert aligned[2]["role"] == "user"
    assert aligned[3]["role"] == "assistant"

def test_cache_aligner_anthropic_cache_control():
    aligner = CacheAligner(provider="anthropic")
    messages = [
        {"role": "system", "content": "First system msg"},
        {"role": "system", "content": "Last system msg"},
        {"role": "user", "content": "hello"}
    ]
    
    aligned = aligner.align_messages(messages)
    
    # The last system message should have the cache_control block
    assert isinstance(aligned[1]["content"], list)
    assert aligned[1]["content"][0]["type"] == "text"
    assert aligned[1]["content"][0]["text"] == "Last system msg"
    assert "cache_control" in aligned[1]["content"][0]
    
    # First system message should be unchanged (no cache_control added)
    assert isinstance(aligned[0]["content"], str)
