import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from price_checker import get_top_coins, get_price
from db import get_connection, init_db
from main import run_alerts

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "change-me")

init_db()

@app.route("/", methods=["GET"])
def home():
    try:
        coins = get_top_coins()
    except Exception as e:
        flash(f"Error fetching coins: {e}", "error")
        coins = []
    return render_template("index.html", coins=coins)

@app.route("/submit", methods=["POST"])
def submit():
    symbol = request.form.get("cryptoid", "").upper().strip()
    increase_str = request.form.get("increasepercent", "").strip()
    decrease_str = request.form.get("decreasepercent", "").strip()
    email = request.form.get("email", "").strip()

    if not symbol:
        flash("No cryptocurrency selected.", "error")
        return redirect(url_for("home"))
    if not email:
        flash("Email is required.", "error")
        return redirect(url_for("home"))

    try:
        increase = float(increase_str) if increase_str else 0.0
        decrease = float(decrease_str) if decrease_str else 0.0
    except ValueError:
        flash("Invalid input for increase or decrease percentage.", "error")
        return redirect(url_for("home"))

    try:
        current_price = get_price(symbol)
    except Exception as e:
        flash(f"Error fetching price: {e}", "error")
        return redirect(url_for("home"))

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT id FROM alerts WHERE email = ? AND crypto = ?",
        (email, symbol),
    )
    row = cur.fetchone()

    if row:
        cur.execute(
            """
            UPDATE alerts
            SET increase_percent = ?, decrease_percent = ?, last_notified_price = ?, last_notified_at = NULL
            WHERE id = ?
            """,
            (increase, decrease, current_price, row[0]),
        )
    else:
        cur.execute(
            """
            INSERT INTO alerts (email, crypto, increase_percent, decrease_percent, last_notified_price, last_notified_at)
            VALUES (?, ?, ?, ?, ?, NULL)
            """,
            (email, symbol, increase, decrease, current_price),
        )

    conn.commit()
    conn.close()

    flash(
        f"Alert set for {symbol}. Increase {increase}% / Decrease {decrease}%. Current price: {current_price:.4f}",
        "success",
    )

    return redirect(url_for("home"))

@app.route("/run-checker", methods=["POST"])
def run_checker():
    run_alerts()
    return jsonify({"status": "alerts checked"}), 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)

