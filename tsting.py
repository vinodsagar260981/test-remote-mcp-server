from fastmcp import FastMCP
import os
import aiosqlite
import sqlite3
import json
import tempfile

TEMP_DIR = tempfile.gettempdir()
DB_PATH = os.path.join(TEMP_DIR, "expenses.db")  # Prefect uses /tmp

mcp = FastMCP("ExpenseTracker")

def init_db():
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

init_db()

@mcp.tool()
async def add_expense(date, amount, category, subcategory="", note=""):
    """Add a new expense entry to the database."""
    async with aiosqlite.connect(DB_PATH) as conn:
        cur = await conn.execute(
            "INSERT INTO expenses(date, amount, category, subcategory, note) VALUES (?,?,?,?,?)",
            (date, amount, category, subcategory, note)
        )
        await conn.commit()
        return {"status": "success", "id": cur.lastrowid}

@mcp.tool()
async def list_expenses():
    """List all the expenses """
    async with aiosqlite.connect(DB_PATH) as conn:
        cur = await conn.execute("""
            SELECT id, date, amount, category, subcategory, note
            FROM expenses ORDER BY date DESC, id DESC
        """)
        cols = [d[0] for d in cur.description]
        rows = await cur.fetchall()
        return [dict(zip(cols, r)) for r in rows]

@mcp.tool()
async def list_expenses_dates(start_date, end_date):
    """List the expenses between the dates range"""
    async with aiosqlite.connect(DB_PATH) as conn:
        cur = await conn.execute("""
            SELECT id, date, amount, category, subcategory, note
            FROM expenses WHERE date BETWEEN ? AND ?
            ORDER BY date DESC, id DESC
        """, (start_date, end_date))
        cols = [d[0] for d in cur.description]
        rows = await cur.fetchall()
        return [dict(zip(cols, r)) for r in rows]

@mcp.tool()
async def summarize(start_date, end_date, category=None):
    """Summarize expenses by category within an inclusive date range."""
    async with aiosqlite.connect(DB_PATH) as conn:
        query = """
            SELECT category, SUM(amount) AS total_amount, COUNT(*) AS count
            FROM expenses WHERE date BETWEEN ? AND ?
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

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)