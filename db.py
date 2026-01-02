import sqlite3

DB_NAME = "alerts.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            crypto TEXT NOT NULL,
            increase_percent REAL,
            decrease_percent REAL,
            last_notified_price REAL,
            last_notified_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def fetch_alerts():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, email, crypto, increase_percent, decrease_percent, last_notified_price
        FROM alerts
    """)
    rows = cur.fetchall()
    conn.close()
    return rows

def update_alert(alert_id, new_price):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE alerts
        SET last_notified_price = ?, last_notified_at = datetime('now')
        WHERE id = ?
    """, (new_price, alert_id))
    conn.commit()
    conn.close()

