"""
Vercel entrypoint for FastAPI application.
This file is required by Vercel to locate the FastAPI app instance.
"""
import sys
import os

# Add parent directory to path so we can import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.api_server import app

# Export the app instance for Vercel
__all__ = ["app"]

