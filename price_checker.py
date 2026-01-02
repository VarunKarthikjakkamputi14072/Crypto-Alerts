import os
import requests
import time

CMC_BASE = "https://pro-api.coinmarketcap.com/v1"
CMC_API_KEY = os.environ.get("CMC_API_KEY")

if not CMC_API_KEY:
    raise RuntimeError("CMC_API_KEY not found in environment. Set it in .env and export before running.")

HEADERS = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': CMC_API_KEY,
}

def get_top_coins(limit=50):
    url = f"{CMC_BASE}/cryptocurrency/listings/latest"
    params = {
        'start': 1,
        'limit': limit,
        'convert': 'USD',
    }
    resp = requests.get(url, headers=HEADERS, params=params, timeout=15)
    if resp.status_code != 200:
        raise RuntimeError(f"CMC API error {resp.status_code}: {resp.text}")
    data = resp.json()
    coins = []
    for item in data['data']:
        coins.append({
            "id": item["id"],
            "symbol": item["symbol"],
            "name": item["name"],
            "slug": item["slug"],
            "currentprice": item["quote"]["USD"]["price"],
        })
    return coins

def get_price(symbol):
    url = f"{CMC_BASE}/cryptocurrency/quotes/latest"
    params = {
        'symbol': symbol.upper(),
        'convert': 'USD',
    }
    resp = requests.get(url, headers=HEADERS, params=params, timeout=15)
    if resp.status_code != 200:
        raise RuntimeError(f"CMC API error {resp.status_code}: {resp.text}")
    data = resp.json()
    price = data['data'][symbol.upper()]['quote']['USD']['price']
    return float(price)

def get_prices_multi(symbols):
    url = f"{CMC_BASE}/cryptocurrency/quotes/latest"
    params = {
        'symbol': ','.join([s.upper() for s in symbols]),
        'convert': 'USD',
    }
    resp = requests.get(url, headers=HEADERS, params=params, timeout=15)
    if resp.status_code != 200:
        raise RuntimeError(f"CMC API error {resp.status_code}: {resp.text}")
    data = resp.json()
    prices = {}
    for sym in symbols:
        try:
            prices[sym.upper()] = float(data['data'][sym.upper()]['quote']['USD']['price'])
        except Exception:
            pass
    return prices

