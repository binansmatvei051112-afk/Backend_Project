import requests

def get_crypto_data(coin_ids: list[str]):
    """
    Запрашивает текущие цены и изменения за 24 часа у CoinGecko.
    coin_ids: список названий монет, например ['bitcoin', 'ethereum', 'solana']
    """
    url = "https://api.coingecko.com/api/v3/simple/price"
    
    params = {
        "ids": ",".join(coin_ids),
        "vs_currencies": "rub,usd",
        "include_24hr_change": "true"
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Ошибка при обращении к API: {e}")
        return None

if __name__ == "__main__":
    test_coins = ["bitcoin", "ethereum", "dogecoin"]
    data = get_crypto_data(test_coins)
    
    if data:
        print("--- Данные получены успешно! ---")
        for coin, info in data.items():
            pricerub = info['rub']
            priceusd = info['usd']
            change = info['rub_24h_change']
            print(f"Монета: {coin.capitalize()}")
            print(f"Цена (RUB): {pricerub:,.2f} рублей")
            print(f"Цена (USD): ${priceusd:,.2f}")
            print(f"Изменение за 24ч 6: {change:.2f}%")
            print("-" * 30)
        else:
            print("Не удалось получить данные. Проверь VPN или интернет.")