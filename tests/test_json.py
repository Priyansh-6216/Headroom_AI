import json
from headroom.utils.json_parser import compress_json

def test_compress_json_list():
    data = [1, 2, 3, 4, 5, 6, 7]
    result = compress_json(data, max_list_items=3)
    assert len(result) == 3
    assert result[0] == 1
    assert result[1] == 2
    assert isinstance(result[2], str)
    assert "truncated" in result[2]

def test_compress_json_dict():
    data = {"a": [1, 2, 3, 4], "b": "value"}
    result = compress_json(data, max_list_items=2)
    assert result["b"] == "value"
    assert len(result["a"]) == 2
    assert "truncated" in result["a"][1]

def test_compress_json_string():
    data = json.dumps([1, 2, 3, 4, 5, 6])
    result = compress_json(data, max_list_items=3)
    parsed = json.loads(result)
    assert len(parsed) == 3
    assert "truncated" in parsed[2]
