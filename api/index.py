"""Vercel entrypoint for Onchain AI.

The backend is imported lazily. This is intentional: Vercel imports the
function module during deployment/cold start, and optional configuration or
backend dependencies should not be able to crash the entire function before
we can even answer /api/health.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _json_response(send, status: int, payload: dict):
    body = json.dumps(payload).encode("utf-8")
    return send({
        "type": "http.response.start",
        "status": status,
        "headers": [
            (b"content-type", b"application/json; charset=utf-8"),
            (b"content-length", str(len(body)).encode("ascii")),
        ],
    }, body)


async def app(scope, receive, send):
    """ASGI callable exposed to Vercel.

    Health is deliberately dependency-free. All other requests lazily load
    the real FastAPI application so import/startup failures are isolated to
    application requests instead of preventing the serverless function from
    being imported.
    """
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
        body = json.dumps({
            "ok": True,
            "service": "onchain-ai",
            "version": "2.4.2",
            "runtime": "vercel-python",
            "backend": "lazy-import",
        }).encode("utf-8")
        await send({
            "type": "http.response.start",
            "status": 200,
            "headers": [
                (b"content-type", b"application/json; charset=utf-8"),
                (b"cache-control", b"no-store"),
                (b"content-length", str(len(body)).encode("ascii")),
            ],
        })
        await send({"type": "http.response.body", "body": body})
        return

    try:
        from backend.main import app as fastapi_app
    except Exception as exc:
        body = json.dumps({
            "ok": False,
            "error": "Backend startup failed",
            "detail": str(exc),
            "type": type(exc).__name__,
        }).encode("utf-8")
        await send({
            "type": "http.response.start",
            "status": 500,
            "headers": [
                (b"content-type", b"application/json; charset=utf-8"),
                (b"content-length", str(len(body)).encode("ascii")),
            ],
        })
        await send({"type": "http.response.body", "body": body})
        return

    await fastapi_app(scope, receive, send)
