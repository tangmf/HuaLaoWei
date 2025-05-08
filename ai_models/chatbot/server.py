"""
server.py

Launches the FastAPI HuaLaoWei Chatbot model hosting server with Uvicorn.

Author: Fleming Siow
Date: 3rd May 2025
"""

import uvicorn
from app import app

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8100,
        reload=True  
    )