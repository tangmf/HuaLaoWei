"""
server.py

Uvicorn server launcher for HuaLaoWei VLM Issue Categoriser.

Author: Jerick Cheong
Date: 5th May 2025
"""

import uvicorn
from app import app

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8101,
        reload=True
    )
