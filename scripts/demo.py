import json
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from headroom.compressors.smart_crusher import SmartCrusher
from headroom.compressors.rolling_window import RollingWindow

print("🚀 Headroom AI Quick Demo")
print("-" * 30)

# Simulate a large tool output
logs = [{"id": i, "level": "INFO", "msg": "Standard request"} for i in range(100)]
# Inject anomaly
logs[42] = {"id": 42, "level": "FATAL", "msg": "Database connection failed! Exception: Timeout"}
raw_payload = json.dumps(logs)

counter = RollingWindow(model="gpt-4o")
print(f"Original tokens: {counter.count_tokens(raw_payload)}")

# Compress
crusher = SmartCrusher(max_list_items=5)
compressed_logs = crusher.compress(logs)
compressed_payload = json.dumps(compressed_logs, indent=2)

print(f"Compressed tokens: {counter.count_tokens(compressed_payload)}")
print(f"Savings: {(1 - counter.count_tokens(compressed_payload) / counter.count_tokens(raw_payload)) * 100:.1f}%")
print("\nCompressed Data Preview:")
print(compressed_payload)
