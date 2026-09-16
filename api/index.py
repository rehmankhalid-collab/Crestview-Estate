"""Vercel's Python runtime looks for a serverless function under api/.
This just re-exports the real ASGI app so there's a single source of truth.
"""

from app.main import app as app
