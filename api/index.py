"""Vercel ASGI entrypoint for the Onchain AI FastAPI application."""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Vercel builds api/index.py as the function entrypoint. Explicitly add the
# repository root so imports such as `backend.main` work regardless of the
# function's current working directory.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Vercel's Python runtime exposes the ASGI application as `app`.
from backend.main import app  # noqa: E402

# Keep this module import side-effect free: database initialization happens
# lazily on the first request inside backend.main rather than at import time.
