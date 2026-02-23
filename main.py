from fastmcp import FastMCP
import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), 'expenses.db')
CATEGORIES_PATH = os.path.join(os.path.dirname(__file__), "categories.json")

mcp = FastMCP("ExpenseTracker")

def init_db():
    with sqlite3.connect(DB_PATH) as cursor:
        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS expenses(
                           id INTEGER PRIMARY KEY AUTOINCREMENT,
                           date TEXT NOT NULL,
                           amount REAL NOT NULL,
                           category TEXT NOT NULL,
                           subcategory TEXT DEFAULT '',
                           note TEXT DEFAULT '')
                           """)

init_db()

# mcp.tool()
# def add_expense(date, amount, category, subcategory="", note=""):
#     """Add a new expense entry to the database"""
#     with sqlite3.connect(DB_PATH) as cursor:
#         cursor = cursor.execute(
#             "INSERT INTO expenses(date, amount, category, subcategory, note) VALUES (?, ?, ?, ?, ?)", (date, amount, category, subcategory, note)
#         )
#         return {"status": "ok", "id": cursor.lastrowid}
    
@mcp.tool()
def add_expense(date, amount, category, subcategory="", note=""):
    '''Add a new expense entry to the database.'''
    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute(
            "INSERT INTO expenses(date, amount, category, subcategory, note) VALUES (?,?,?,?,?)",
            (date, amount, category, subcategory, note)
        )
        return {"status": "ok", "id": cur.lastrowid}


@mcp.tool()
def list_expenses():
    """List all the expenses """
    with sqlite3.connect(DB_PATH) as cursor:
        cursor = cursor.execute("SELECT id, date, amount, category, subcategory, note FROM expenses ORDER BY id ASC")
        cols = [d[0] for d in cursor.description]#gives column name
        return [dict(zip(cols, r)) for r in cursor.fetchall()]
    

@mcp.tool()
def list_expenses_dates(start_date, end_date):
    '''List the expenses between the dates range'''
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            """
            SELECT * FROM expenses
            where date BETWEEN ? AND ?
            ORDER BY id ASC
            """, (start_date, end_date)
        )
        cols = [d[0] for d in cursor.description]#gives column name
        return [dict(zip(cols, r)) for r in cursor.fetchall()]

@mcp.tool()
def summarize(start_date, end_date, category=None):
    '''Summarize expenses by category within an inclusive date range.'''
    with sqlite3.connect(DB_PATH) as c:
        query = (
            """
            SELECT category, SUM(amount) AS total_amount
            FROM expenses
            WHERE date BETWEEN ? AND ?
            """
        )
        params = [start_date, end_date]

        if category:
            query += " AND category = ?"
            params.append(category)

        query += " GROUP BY category ORDER BY category ASC"

        cur = c.execute(query, params)
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]
    
@mcp.resource("expense://categories", mime_type="application/json")
def categories():
    # Read fresh each time so you can edit the file without restarting
    with open(CATEGORIES_PATH, "r", encoding="utf-8") as f:
        return f.read()
    
if __name__ == "__main__":
    # mcp.run()
    mcp.run(transport='http', host="0.0.0.0", port=8000)