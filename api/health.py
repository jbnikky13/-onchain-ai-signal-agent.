"""Minimal Vercel health function.

This endpoint deliberately avoids importing the application stack so deployment
problems can be separated from application/runtime problems.
"""
from __future__ import annotations


def handler(request):
    return {
        "statusCode": 200,
        "headers": {"content-type": "application/json", "cache-control": "no-store"},
        "body": '{"ok":true,"service":"onchain-ai","runtime":"vercel-python"}',
    }
