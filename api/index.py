"""Vercel ASGI entrypoint for the Onchain AI FastAPI application."""
from backend.main import app

# Vercel discovers the FastAPI/ASGI application exported as `app`.
