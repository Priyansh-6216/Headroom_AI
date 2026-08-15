import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from headroom.compressors.smart_crusher import SmartCrusher
from headroom.compressors.text import TextCompressor
from headroom.compressors.rolling_window import RollingWindow

def run_benchmarks():
    print("📊 Running Headroom Benchmarks...\n")
    
    counter = RollingWindow(model="gpt-4o")
    
    # Test 1: JSON List
    json_list = [{"id": i, "val": "data " * 20} for i in range(50)]
    raw_json = json.dumps(json_list)
    raw_tok_1 = counter.count_tokens(raw_json)
    
    crusher = SmartCrusher(max_list_items=5)
    comp_json = json.dumps(crusher.compress(json_list))
    comp_tok_1 = counter.count_tokens(comp_json)
    
    # Test 2: Long Text
    long_text = "This is a redundant boilerplate text that we don't care about. " * 500
    raw_tok_2 = counter.count_tokens(long_text)
    
    text_comp = TextCompressor(max_length=100)
    comp_text = text_comp.compress(long_text)
    comp_tok_2 = counter.count_tokens(comp_text)
    
    # Results
    print("| Data Type | Original Tokens | Compressed Tokens | Savings |")
    print("|-----------|-----------------|-------------------|---------|")
    print(f"| JSON List | {raw_tok_1:<15} | {comp_tok_1:<17} | {(raw_tok_1 - comp_tok_1)/raw_tok_1*100:.1f}% |")
    print(f"| Long Text | {raw_tok_2:<15} | {comp_tok_2:<17} | {(raw_tok_2 - comp_tok_2)/raw_tok_2*100:.1f}% |")
    
if __name__ == "__main__":
    run_benchmarks()
