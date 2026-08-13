import json
import pytest
from fastapi.testclient import TestClient
from headroom.server.proxy import app

client = TestClient(app)

def test_proxy_health():
    # Mocking a basic request, though it will try to forward to openai by default.
    # To prevent actually calling OpenAI in tests, we can test that the proxy 
    # correctly parses and handles malformed data without crashing, or we can mock httpx.
    pass

def test_proxy_compression_logic(monkeypatch):
    import httpx
    
    # Mock the httpx client to just echo back what we sent it
    class MockResponse:
        def __init__(self, content, status_code):
            self.content = content
            self.status_code = status_code
            self.headers = {}
            
        async def aread(self):
            return self.content
            
    class MockClient:
        async def __aenter__(self):
            return self
            
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass
            
        def build_request(self, method, url, headers, content):
            self.sent_content = content
            return "mock_req"
            
        async def send(self, request, stream=False):
            # Echo back the payload we got so we can verify compression happened
            return MockResponse(self.sent_content, 200)
            
    monkeypatch.setattr("httpx.AsyncClient", MockClient)
    
    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "tool",
                "content": "This is a very very long string that should get compressed by text compressor if max length is small, or by json if it was json"
            }
        ]
    }
    
    # The default text compressor might not compress this if max_length is 1000.
    # Let's pass a massive json to trigger the json compressor.
    payload["messages"][0]["content"] = json.dumps(["LONG_STRING_" * 50 for _ in range(10)])
    
    response = client.post("/v1/chat/completions", json=payload)
    
    assert response.status_code == 200
    
    echoed_data = response.json()
    assert "messages" in echoed_data
    
    # Check if compression happened
    tool_content = echoed_data["messages"][0]["content"]
    assert "truncated" in tool_content
