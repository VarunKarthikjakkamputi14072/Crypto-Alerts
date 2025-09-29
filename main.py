import json
import os
from datetime import datetime, timedelta
from time import sleep
from typing import Optional, Dict

from price_checker import get_price, get_prices_multi
from emailer import send_email

DATA_FILE = "user_data.json"


def load_store():
    if not os.path.exists(DATA_FILE):
        return {"users": []}
    with open(DATA_FILE, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return {"users": []}
    if isinstance(data, dict) and "users" in data:
        return data
    if isinstance(data, dict) and "email" in data and "alerts" in data:
        return {"users": [data]}
    return {"users": []}


def save_store(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def should_notify(change_pct: float, inc_threshold: float, dec_threshold: float) -> Optional[str]:
    # Returns "up", "down" or None
    if dec_threshold and change_pct <= -abs(dec_threshold):
        return "down"
    if inc_threshold and change_pct >= abs(inc_threshold):
        return "up"
    return None


def _collect_all_coins(store) -> list[str]:
    ids = []
    for user in store.get("users", []):
        for alert in user.get("alerts", []):
            cid = alert.get("crypto")
            if cid:
                ids.append(cid)
    # Deduplicate while preserving order
    seen = set()
    out = []
    for cid in ids:
        if cid not in seen:
            out.append(cid)
            seen.add(cid)
    return out


def check_alerts():
    store = load_store()
    changed = False

    # Batch fetch once per run to reduce API calls
    all_ids = _collect_all_coins(store)
    price_cache: Dict[str, float] = {}
    try:
        if all_ids:
            price_cache = get_prices_multi(all_ids)
    except Exception as e:
        print(f"[WARN] Batch price fetch failed, will fallback to single fetches: {e}")
        price_cache = {}

    for user in store["users"]:
        email = user.get("email")
        alerts = user.get("alerts", [])
        for alert in alerts:
            crypto = alert.get("crypto")
            last_price = alert.get("lastnotifiedprice", 0.0) or 0.0
            inc = float(alert.get("increasepercent", 0.0) or 0.0)
            dec = float(alert.get("decreasepercent", 0.0) or 0.0)
            last_notified_at = alert.get("last_notified_at")

            if not crypto or not email:
                continue

            try:
                if crypto in price_cache:
                    current_price = price_cache[crypto]
                else:
                    current_price = get_price(crypto)
                    price_cache[crypto] = current_price
                    sleep(0.5)  # be polite to free tier
            except Exception as e:
                print(f"[WARN] Failed to fetch price for {crypto}: {e}")
                continue

            change_pct = ((current_price - last_price) / last_price) * 100 if last_price else 0.0
            direction = should_notify(change_pct, inc, dec)

            # Debounce: skip if notified within last 15 minutes
            if direction and last_notified_at:
                try:
                    ts = datetime.fromisoformat(last_notified_at)
                    if ts > datetime.utcnow() - timedelta(minutes=15):
                        direction = None
                except Exception:
                    pass

            if direction:
                if direction == "up":
                    subject = f"{crypto.capitalize()} price increased by {change_pct:.2f}%!"
                    body = (
                        f"Price is now {current_price:.6f}, up from {last_price:.6f}.\n"
                        f"Threshold: +{inc:.2f}%"
                    )
                else:
                    subject = f"{crypto.capitalize()} price dropped by {abs(change_pct):.2f}%!"
                    body = (
                        f"Price is now {current_price:.6f}, down from {last_price:.6f}.\n"
                        f"Threshold: -{abs(dec):.2f}%"
                    )

                try:
                    send_email(email, subject, body)
                    alert["lastnotifiedprice"] = current_price
                    alert["last_notified_at"] = datetime.utcnow().isoformat(timespec="seconds")
                    changed = True
                    print(f"[INFO] Notified {email} for {crypto} ({direction}).")
                except Exception as e:
                    print(f"[ERROR] Failed to send email to {email}: {e}")

    if changed:
        save_store(store)
        print("[INFO] Alerts updated and saved.")
    else:
        print("[INFO] No alerts triggered this run.")


if __name__ == "__main__":
    check_alerts()

