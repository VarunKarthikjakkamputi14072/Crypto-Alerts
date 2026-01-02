from price_checker import get_price
from emailer import send_email
from db import fetch_alerts, update_alert, init_db

def run_alerts():
    init_db()
    alerts = fetch_alerts()

    for alert_id, email, crypto, increase_percent, decrease_percent, last_price in alerts:
        try:
            current_price = get_price(crypto)
        except Exception as e:
            print(f"[WARN] Failed to fetch price for {crypto}: {e}")
            continue

        if last_price is None:
            update_alert(alert_id, current_price)
            continue

        if increase_percent and increase_percent > 0:
            up_threshold = last_price * (1 + increase_percent / 100)
            if current_price >= up_threshold:
                send_email(email, crypto, "up")
                update_alert(alert_id, current_price)
                continue

        if decrease_percent and decrease_percent > 0:
            down_threshold = last_price * (1 - decrease_percent / 100)
            if current_price <= down_threshold:
                send_email(email, crypto, "down")
                update_alert(alert_id, current_price)

if __name__ == "__main__":
    run_alerts()

