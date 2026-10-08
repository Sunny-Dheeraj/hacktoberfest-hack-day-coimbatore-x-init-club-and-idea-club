"""Vercel standard serverless function entrypoint for FastAPI."""

import os
import sys
import traceback

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
backend_dir = os.path.join(root_dir, "backend")
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

try:
    try:
        from backend.app.main import app
    except ImportError:
        from app.main import app
except Exception as exc:
    import json
    err_msg = f"{type(exc).__name__}: {str(exc)}\n{traceback.format_exc()}"
    print("FATAL APP IMPORT ERROR:", err_msg, file=sys.stderr)
    
    # Fallback ASGI application that surfaces the initialization error in JSON
    async def app(scope, receive, send):
        if scope["type"] == "http":
            body = json.dumps({"error": "Failed to load FastAPI app", "detail": err_msg}).encode("utf-8")
            await send({
                "type": "http.response.start",
                "status": 500,
                "headers": [
                    [b"content-type", b"application/json"],
                    [b"content-length", str(len(body)).encode("utf-8")]
                ]
            })
            await send({
                "type": "http.response.body",
                "body": body
            })

__all__ = ["app"]
