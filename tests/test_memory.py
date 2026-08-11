from headroom.memory.store import InMemoryStore
from headroom.memory.ccr import CCRManager
from headroom.compressors.text import TextCompressor

def test_in_memory_store():
    store = InMemoryStore()
    original_data = {"key": "very long data here"}
    
    ref_id = store.store(original_data)
    assert ref_id.startswith("ref_")
    
    retrieved = store.retrieve(ref_id)
    assert retrieved == original_data
    
    assert store.retrieve("invalid_id") is None

def test_ccr_manager_with_text():
    store = InMemoryStore()
    # A compressor that truncates aggressively to 5 characters
    compressor = TextCompressor(max_length=5, suffix="...") 
    manager = CCRManager(compressor=compressor, store=store)
    
    long_text = "This is a very long text that needs compression"
    result = manager.process(long_text)
    
    # Check that it compressed it
    assert result.startswith("Th...")
    # Check that it injected the retrieval ID
    assert "[Original data available via CCR" in result
    
    # Extract ID
    # Format: [Original data available via CCR. Use retrieval tool with ID: ref_XXX]
    ref_id = result.split("ID: ")[1].split("]")[0]
    
    # Check retrieval
    retrieved = manager.retrieve(ref_id)
    assert retrieved == long_text

def test_ccr_manager_with_dict():
    store = InMemoryStore()
    compressor = TextCompressor(max_length=100) # won't really do anything to dict, just mock
    
    # Mocking compressor to just return dict
    class MockDictCompressor:
        def compress(self, data):
            return {"compressed": "yes"}
            
    manager = CCRManager(compressor=MockDictCompressor(), store=store)
    
    data = {"massive": "payload"}
    result = manager.process(data)
    
    assert result["compressed"] == "yes"
    assert "_ccr_ref" in result
    
    retrieved = manager.retrieve(result["_ccr_ref"])
    assert retrieved == data
