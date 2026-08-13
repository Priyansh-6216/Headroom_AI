from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
import httpx
import json
import os
from headroom.compressors.smart_crusher import SmartCrusher
from headroom.utils.logger import logger

app = FastAPI(title="Headroom Proxy Server")

# Initialize compressor
crusher = SmartCrusher()

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_handler(request: Request, path: str):
    """
    Intercepts requests, applies headroom compression to tool outputs if it's a chat completions endpoint,
    and forwards it to the actual LLM provider.
    """
    # Determine upstream provider URL
    # By default, we use OpenAI's API base URL unless overridden by environment variables
    base_url = os.environ.get("HEADROOM_UPSTREAM_URL", "https://api.openai.com")
    
    url = f"{base_url}/{path}"
    
    # Read original request body
    body = await request.body()
    try:
        if request.method == "POST" and "chat/completions" in path:
            data = json.loads(body)
            messages = data.get("messages", [])
            
            # Compress tool responses in the messages
            compressed_count = 0
            for msg in messages:
                if msg.get("role") == "tool" and "content" in msg:
                    # Compress the tool output
                    original = msg["content"]
                    compressed = crusher.compress(original)
                    if len(str(compressed)) < len(str(original)):
                        msg["content"] = compressed
                        compressed_count += 1
            
            if compressed_count > 0:
                logger.info(f"Compressed {compressed_count} tool responses in the request payload.")
                
            body = json.dumps(data).encode("utf-8")
    except Exception as e:
        logger.error(f"Failed to compress payload: {e}. Forwarding original request.")
        
    # Forward the request
    headers = dict(request.headers)
    # Remove host header to avoid SSL/Host mismatch issues
    headers.pop("host", None)
    
    async with httpx.AsyncClient() as client:
        try:
            proxy_req = client.build_request(
                method=request.method,
                url=url,
                headers=headers,
                content=body
            )
            response = await client.send(proxy_req, stream=True)
            
            # Return response to client
            return Response(
                content=await response.aread(),
                status_code=response.status_code,
                headers=dict(response.headers)
            )
        except httpx.RequestError as e:
            return JSONResponse(
                status_code=502,
                content={"error": f"Bad Gateway: {str(e)}"}
            )

def serve(port: int = 8787):
    """Starts the proxy server."""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)
