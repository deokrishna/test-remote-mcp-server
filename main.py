import sqlite3
from datetime import datetime
from fastmcp import FastMCP
from fastapi.middleware.cors import CORSMiddleware
import os

# Initialize FastMCP

mcp = FastMCP("Expense Tracker")
fastapi_app = mcp.get_fastapi_app()
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
DB_PATH = os.path.join(os.path.dirname(__file__), "expenses.db")


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                date TEXT NOT NULL
            )
        """
        )


init_db()


@mcp.tool()
def add_expense(amount: float, category: str, description: str = "") -> str:
    """Add a new expense to the tracker"""
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO expenses (amount, category, description, date) VALUES (?, ?, ?, ?)",
            (amount, category, description, date),
        )
    return f"Successfully added ${amount} under '{category}'."


@mcp.tool()
def list_expenses(limit: int = 10) -> str:
    """List the most recent expenses."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            "SELECT * FROM expenses ORDER BY date DESC LIMIT ?", (limit,)
        )
        rows = cursor.fetchall()

    if not rows:
        return "No expenses found."

    output = "ID | Amount | Category | Description | Date\n"
    output += "-" * 50 + "\n"
    for row in rows:
        output += f"{row[0]} | ${row[1]} | {row[2]} | {row[3]} | {row[4]}\n"
    return output


@mcp.tool()
def get_monthly_summary() -> str:
    """Get a summary of spending grouped by category for the current month."""
    month = datetime.now().strftime("%Y-%m")
    query = """
        SELECT category, SUM(amount) 
        FROM expenses 
        WHERE date LIKE ? 
        GROUP BY category
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(query, (f"{month}%",))
        rows = cursor.fetchall()

    if not rows:
        return "No data for this month."

    summary = f"Summary for {month}:\n"
    total = 0
    for cat, amt in rows:
        summary += f"- {cat}: ${amt:.2f}\n"
        total += amt
    summary += f"**Total: ${total:.2f}**"
    return summary


if __name__ == "__main__":
    mcp.run()
