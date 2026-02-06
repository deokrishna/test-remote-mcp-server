import sqlite3
import os
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastmcp import FastMCP

# 1. Create a standard FastAPI app
app = FastAPI()

# 2. Add CORS middleware to the FastAPI app (Fixes Inspector error)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["mcp-session-id"],  # Important for MCP sessions
)

# 3. Initialize FastMCP
mcp = FastMCP("Expense Tracker")

# ... (Keep your init_db and @mcp.tool functions exactly as they were) ...


@mcp.tool()
def add_expense(amount: float, category: str, description: str = "") -> str:
    """Add a new expense to the tracker"""
    # Your existing code...
    return f"Successfully added ${amount}."


# 4. Integrate FastMCP into the FastAPI app
# This mounts the MCP protocol endpoints onto your FastAPI app
app.mount("/mcp", mcp.http_app())

if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8080))
    # Run the FastAPI app directly
    uvicorn.run(app, host="0.0.0.0", port=port)
