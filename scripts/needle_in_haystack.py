import json
import os
import sys

# Ensure headroom is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from headroom.compressors.smart_crusher import SmartCrusher
from headroom.compressors.rolling_window import RollingWindow

def generate_haystack():
    """Generates 100 log entries with one critical error."""
    logs = []
    for i in range(100):
        if i == 67:
            logs.append({"timestamp": f"2026-08-15T12:{i:02d}:00Z", "level": "FATAL", "service": "payment-gateway", "message": "error PG-5523, fix: Increase max_connections to 500, 1,847 transactions affected"})
        else:
            logs.append({"timestamp": f"2026-08-15T12:{i:02d}:00Z", "level": "INFO", "service": "auth-service", "message": "User login successful"})
    return logs

def run_test():
    print("🔬 Running Needle in Haystack Test...")
    logs = generate_haystack()
    raw_json = json.dumps(logs)
    
    # We use a token counter from RollingWindow just to measure
    counter = RollingWindow(model="gpt-4o")
    raw_tokens = counter.count_tokens(raw_json)
    print(f"Original tokens: {raw_tokens}")
    
    # Since our SmartCrusher currently just truncates lists, we need it to be anomaly-aware
    # For now, let's just compress
    crusher = SmartCrusher(max_list_items=10)
    compressed = crusher.compress(logs)
    compressed_json = json.dumps(compressed)
    
    compressed_tokens = counter.count_tokens(compressed_json)
    print(f"Compressed tokens: {compressed_tokens}")
    
    reduction = (raw_tokens - compressed_tokens) / raw_tokens * 100
    print(f"Token reduction: {reduction:.1f}%")
    
    # Verify needle is still there. Wait, does our current simple logic keep it?
    # Our Day 2 logic just kept first N items. So it would lose the needle at position 67.
    # To pass the needle in haystack test, we MUST implement anomaly detection.
    
    has_needle = "PG-5523" in compressed_json
    if has_needle:
        print("✅ Success! Needle was preserved.")
    else:
        print("❌ Failed! Needle was lost during compression.")

if __name__ == "__main__":
    run_test()
