from fastmcp import FastMCP
import os
import aiosqlite
import sqlite3
import tempfile
import json

# Use temp directory to avoid permission issues
TEMP_DIR = tempfile.gettempdir()
DB_PATH = os.path.join(TEMP_DIR, "expenses.db")

CATEGORIES_PATH = os.path.join(os.path.dirname(__file__), "categories.json")

mcp = FastMCP("ExpenseTracker")


# -----------------------------
# DATABASE INITIALIZATION
# -----------------------------
def init_db():
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS expenses(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    amount REAL NOT NULL,
                    category TEXT NOT NULL,
                    subcategory TEXT DEFAULT '',
                    note TEXT DEFAULT ''
                )
            """)
    except Exception as e:
        raise RuntimeError(f"Database initialization failed: {e}")


init_db()


# -----------------------------
# ADD EXPENSE
# -----------------------------
@mcp.tool()
async def add_expense(date, amount, category, subcategory="", note=""):
    """Add a new expense entry to the database."""
    try:
        async with aiosqlite.connect(DB_PATH) as conn:
            cur = await conn.execute(
                "INSERT INTO expenses(date, amount, category, subcategory, note) VALUES (?,?,?,?,?)",
                (date, amount, category, subcategory, note)
            )
            await conn.commit()
            return {
                "status": "success",
                "id": cur.lastrowid
            }
    except Exception as e:
        return {"status": "error", "message": str(e)}


# -----------------------------
# LIST EXPENSES (DATE RANGE)
# -----------------------------
@mcp.tool()
async def list_expenses(start_date, end_date):
    """List expenses within an inclusive date range."""
    try:
        async with aiosqlite.connect(DB_PATH) as conn:
            cur = await conn.execute("""
                SELECT id, date, amount, category, subcategory, note
                FROM expenses
                WHERE date BETWEEN ? AND ?
                ORDER BY date DESC, id DESC
            """, (start_date, end_date))

            cols = [d[0] for d in cur.description]
            rows = await cur.fetchall()
            return [dict(zip(cols, r)) for r in rows]

    except Exception as e:
        return {"status": "error", "message": str(e)}


# -----------------------------
# SUMMARIZE
# -----------------------------
@mcp.tool()
async def summarize(start_date, end_date, category=None):
    """Summarize expenses by category within date range."""
    try:
        async with aiosqlite.connect(DB_PATH) as conn:

            query = """
                SELECT category,
                       SUM(amount) AS total_amount,
                       COUNT(*) AS count
                FROM expenses
                WHERE date BETWEEN ? AND ?
            """

            params = [start_date, end_date]

            if category:
                query += " AND category = ?"
                params.append(category)

            query += " GROUP BY category ORDER BY total_amount DESC"

            cur = await conn.execute(query, params)
            cols = [d[0] for d in cur.description]
            rows = await cur.fetchall()

            return [dict(zip(cols, r)) for r in rows]

    except Exception as e:
        return {"status": "error", "message": str(e)}


# -----------------------------
# RESOURCE: CATEGORIES
# -----------------------------
@mcp.resource("expense:///categories", mime_type="application/json")
def categories():
    default_categories = {
        "categories": [
            "Food & Dining",
            "Transportation",
            "Shopping",
            "Entertainment",
            "Bills & Utilities",
            "Healthcare",
            "Travel",
            "Education",
            "Business",
            "Other"
        ]
    }

    try:
        if os.path.exists(CATEGORIES_PATH):
            with open(CATEGORIES_PATH, "r", encoding="utf-8") as f:
                return f.read()
        return json.dumps(default_categories, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e)})


# -----------------------------
# START SERVER
# -----------------------------
if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)