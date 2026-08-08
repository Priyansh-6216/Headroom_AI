import json
from headroom.compressors.smart_crusher import SmartCrusher

def test_smart_crusher_with_text():
    crusher = SmartCrusher(max_text_length=15)
    text = "This is a very long string that should be truncated."
    result = crusher.compress(text)
    assert len(result) == 15
    assert "TRUNCATED" in result

def test_smart_crusher_with_json_string():
    crusher = SmartCrusher(max_list_items=2)
    data = json.dumps([1, 2, 3, 4, 5])
    result = crusher.compress(data)
    parsed = json.loads(result)
    assert len(parsed) == 2
    assert "truncated" in parsed[1]

def test_smart_crusher_with_dict():
    crusher = SmartCrusher(max_list_items=2)
    data = {"items": [1, 2, 3, 4]}
    result = crusher.compress(data)
    assert len(result["items"]) == 2
    assert "truncated" in result["items"][1]
