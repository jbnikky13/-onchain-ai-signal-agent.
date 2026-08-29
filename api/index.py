"""Vercel ASGI entrypoint for Onchain AI.

The application stack is imported lazily so a configuration/dependency error
cannot prevent Vercel from importing the function. A lightweight health path
is handled without importing FastAPI or any backend services.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

_fastapi_app = None
_backend_error = None


def _send_json(send, status: int, payload: dict):
    body = json.dumps(payload).encode("utf-8")
    return send(
        {
            "type": "http.response.start",
            "status": status,
            "headers": [
                (b"content-type", b"application/json; charset=utf-8"),
                (b"cache-control", b"no-store"),
                (b"content-length", str(len(body)).encode("ascii")),
            ],
        },
        body,
    )


async def app(scope, receive, send):
    """ASGI callable exposed as the Vercel Python function."""
    global _fastapi_app, _backend_error

    if scope.get("type") == "lifespan":
        while True:
            message = await receive()
            if message["type"] == "lifespan.startup":
                await send({"type": "lifespan.startup.complete"})
            elif message["type"] == "lifespan.shutdown":
                await send({"type": "lifespan.shutdown.complete"})
                return
        
    if scope.get("type") != "http":
        return

    path = scope.get("path", "")
    if path in {"/api/health", "/health"}:
        await _send_json(send, 200, {
            "ok": True,
            "service": "onchain-ai",
            "version": "2.4.2",
            "runtime": "vercel-python",
            "backend": "lazy-import",
        })
        return

    if _fastapi_app is None and _backend_error is None:
        try:
            from backend.main import app as imported_app
            _fastapi_app = imported_app
        except Exception as exc:
            _backend_error = exc

    if _fastapi_app is None:
        await _send_json(send, 500, {
            "ok": False,
            "error": "Backend startup failed",
            "detail": str(_backend_error),
            "type": type(_backend_error).__name__ if _backend_error else "UnknownError",
        })
        return

    await _fastapi_app(scope, receive, send)
