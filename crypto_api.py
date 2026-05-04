import requests
import time
from datetime import datetime

CACHE = {}
LAST_UPDATE_TIME = 0
CACHE_EXPIRE_SECONDS = 120

def get_crypto_data(coin_ids: list[str]):
    global CACHE, LAST_UPDATE_TIME
    
    if not coin_ids:
        return {}

    current_time = time.time()
    if CACHE and (current_time - LAST_UPDATE_TIME < CACHE_EXPIRE_SECONDS):
        print("--- Использую данные из кэша (API не беспокоим) ---")
        return {coin: CACHE[coin] for coin in coin_ids if coin in CACHE}

    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": ",".join(coin_ids),
        "vs_currencies": "rub,usd",
        "include_24hr_change": "true",
        "include_last_updated_at": "true",
        "include_market_cap": "true",
        "include_24hr_vol": "true"
    }

    try:
        print("--- Запрос к API CoinGecko... ---")
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        raw_data = response.json()
        
        processed_data = {}
        for coin in raw_data:
            info = raw_data[coin]
            processed_data[coin] = {
                "usd": info.get("usd", 0),
                "rub": info.get("rub", 0),
                "change_24h": info.get("rub_24h_change", 0),
                "market_cap": info.get("rub_market_cap", 0),
                "volume_24h": info.get("rub_24h_vol", 0),
                "last_updated": datetime.fromtimestamp(info.get("last_updated_at", 0)).strftime('%H:%M:%S')
            }
        
        CACHE.update(processed_data)
        LAST_UPDATE_TIME = current_time
        
        return processed_data
    except Exception as e:
        print(f"Ошибка при обращении к API: {e}")
        return CACHE if CACHE else {}