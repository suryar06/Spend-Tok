import sqlite3, datetime, os
from flask import Flask, render_template, request, jsonify

DB_FILE = os.path.join(os.path.dirname(__file__), "expenses.db")

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        amount REAL NOT NULL,
        category TEXT NOT NULL)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL)""")
    for cat in ["toiletries","vegetables","snacks","food","travel","bills","shopping","loans","emi","fees","charity","savings","general"]:
        cur.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (cat,))
    conn.commit(); conn.close()

def insert_expense(amount, category):
    conn = sqlite3.connect(DB_FILE); cur = conn.cursor()
    cur.execute("SELECT name FROM categories WHERE name=?", (category,))
    if not cur.fetchone(): category="other"
    cur.execute("INSERT INTO expenses (timestamp, amount, category) VALUES (?,?,?)",
        (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), amount, category))
    conn.commit(); conn.close()

def delete_expense(expense_id):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
    conn.commit()
    conn.close()

def get_expenses():
    conn = sqlite3.connect(DB_FILE); cur = conn.cursor()
    cur.execute("SELECT * FROM expenses"); rows=cur.fetchall(); conn.close(); return rows

def get_categories():
    conn = sqlite3.connect(DB_FILE); cur = conn.cursor()
    cur.execute("SELECT name FROM categories"); cats=[r[0] for r in cur.fetchall()]
    conn.close(); return cats

app = Flask(__name__); init_db()

@app.route("/") 
def index(): return render_template("index.html")

@app.route("/get_categories") 
def categories_route(): return jsonify(get_categories())

@app.route("/get_expenses") 
def expenses_route(): return jsonify([
    {"id":r[0],"timestamp":r[1],"amount":r[2],"category":r[3]} for r in get_expenses()
])

@app.route("/add_expense", methods=["POST"])

def add_expense_route():
    data=request.json; amt=data.get("amount"); cat=data.get("category","other")
    try: insert_expense(float(amt), cat); return jsonify({"status":"success"})
    except: return jsonify({"status":"error"})

@app.route("/delete_expense/<int:expense_id>", methods=["DELETE"])

def delete_expense_route(expense_id):
    try:
        delete_expense(expense_id)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

