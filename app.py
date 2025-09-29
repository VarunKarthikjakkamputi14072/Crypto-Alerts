import os
import json
from flask import Flask, render_template, request, redirect, url_for, flash
from price_checker import get_top_coins, get_price

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "change-me")
DATA_FILE = "user_data.json"

# Helper functions for loading/saving alerts

def load_users():
    if not os.path.exists(DATA_FILE):
        return {"users": []}
    with open(DATA_FILE, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return {"users": []}
    if isinstance(data, dict) and "users" in data:
        return data
    return {"users": []}

def save_users(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

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
    symbol = request.form.get("cryptoid", "").upper().strip()  # Use symbol, e.g. 'BTC'
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
    store = load_users()
    user = next((u for u in store["users"] if u.get("email") == email), None)
    if user is None:
        user = {"email": email, "alerts": []}
        store["users"].append(user)
    existing = next((a for a in user["alerts"] if a.get("crypto") == symbol), None)
    payload = {
        "crypto": symbol,  # Store symbol, e.g. 'BTC'
        "increasepercent": increase,
        "decreasepercent": decrease,
        "lastnotifiedprice": current_price,
        "last_notified_at": None,
    }
    if existing:
        existing.update(payload)
    else:
        user["alerts"].append(payload)
    save_users(store)
    flash(
        f"Alert set for {symbol}. Notify if price increases by {increase}% or decreases by {decrease}%. Current price: {current_price:.4f}",
        "success",
    )
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)

