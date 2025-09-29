import json
from price_checker import get_top_coins, get_price

DATA_FILE = "user_data.json"


def save_store(store):
    with open(DATA_FILE, "w") as f:
        json.dump(store, f, indent=2)


def load_store():
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            if isinstance(data, dict) and "users" in data:
                return data
            if isinstance(data, dict) and "email" in data and "alerts" in data:
                return {"users": [data]}
            return {"users": []}
    except FileNotFoundError:
        return {"users": []}


def prompt_email():
    while True:
        email = input("Enter your email address for alerts: ").strip()
        if email:
            return email
        print("Email cannot be empty.")


def prompt_alerts(coins):
    alerts = []
    while True:
        print("\nTop coins:")
        for i, c in enumerate(coins, start=1):
            print(f"{i:2d}. {c['name']} ({c['symbol'].upper()}) - ${c['currentprice']:.4f}")
        coin_input = input("\nEnter the number of a coin to track (or press Enter to finish): ").strip()
        if not coin_input:
            break
        if not coin_input.isdigit() or not (1 <= int(coin_input) <= len(coins)):
            print("Invalid number. Please try again.")
            continue
        coin = coins[int(coin_input) - 1]
        crypto_id = coin["id"]
        try:
            increase = float(input("Alert if price INCREASES by % (e.g., 5): ").strip() or "0")
            decrease = float(input("Alert if price DECREASES by % (e.g., 5): ").strip() or "0")
        except ValueError:
            print("Invalid input. Please enter numbers.")
            continue
        current_price = get_price(crypto_id)
        alerts.append(
            {
                "crypto": crypto_id,
                "increasepercent": increase,
                "decreasepercent": decrease,
                "lastnotifiedprice": current_price,
                "last_notified_at": None,
            }
        )
        print(f"Added {coin['name']} with thresholds +{increase}% / -{decrease}% at ${current_price:.6f}")
    return alerts


def main():
    coins = get_top_coins()
    if not coins:
        print("Failed to fetch coins.")
        return
    email = prompt_email()
    alerts = prompt_alerts(coins)

    store = load_store()
    user = next((u for u in store["users"] if u.get("email") == email), None)
    if user is None:
        user = {"email": email, "alerts": []}
        store["users"].append(user)
    # Merge alerts by crypto
    by_id = {a["crypto"]: a for a in user["alerts"]}
    for a in alerts:
        by_id[a["crypto"]] = a
    user["alerts"] = list(by_id.values())

    save_store(store)
    print("\nSaved alerts to user_data.json")


if __name__ == "__main__":
    main()

