import requests
import time

def get_crypto_price(coin="bitcoin"):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd"
    try:
        response = requests.get(url)
        data = response.json()
        return data[coin]['usd']
    except Exception as e:
        print(f"Помилка під час запиту: {e}")
        return None

if __name__ == "__main__":
    print("Скрейпер запущено. Натисни Ctrl+C для зупинки.")
    while True:
        price = get_crypto_price()
        if price:
            print(f"Поточна ціна BTC: ${price}")
        time.sleep(10)