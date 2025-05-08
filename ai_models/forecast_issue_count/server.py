"""
server.py

Launches the FastAPI server for issue count forecasting using preloaded TCN models.

Author: Fleming Siow
Date: 5th May 2025
"""

# --------------------------------------------------------
# Imports
# --------------------------------------------------------

import uvicorn

# --------------------------------------------------------
# Server Startup
# --------------------------------------------------------

if __name__ == "__main__":
    uvicorn.run(
        "app:app", 
        host="0.0.0.0", 
        port=8102,  # assuming 8102 based on your ports earlier
        reload=True
    )
