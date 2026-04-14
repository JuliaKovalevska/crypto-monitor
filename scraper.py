import requests
import time
import hvac
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS


def get_crypto_price(coin="bitcoin"):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd"
    try:
        response = requests.get(url)
        data = response.json()
        if coin in data:
            return data[coin]['usd']
        return None
    except Exception as e:
        print(f"Помилка API: {e}")
        return None


if __name__ == "__main__":
    print("Починаємо роботу. Стукаємось у Vault...")

    try:
        vault_client = hvac.Client(url='http://vault:8200', token='my-root-token')
        read_response = vault_client.secrets.kv.v2.read_secret_version(path='crypto_app')
        INFLUX_TOKEN = read_response['data']['data']['influx_token']
        print(" [+] Секрет отримано!")
    except Exception as e:
        print(f" [-] Помилка Vault: {e}")
        exit(1)

    print("Налаштовуємо InfluxDB...")
    try:
        db_client = InfluxDBClient(url="http://influxdb:8086", token=INFLUX_TOKEN, org="my-org")
        write_api = db_client.write_api(write_options=SYNCHRONOUS)
        print(" [+] Клієнт InfluxDB готовий!")
    except Exception as e:
        print(f" [-] Помилка клієнта InfluxDB: {e}")
        exit(1)

    print("Скрейпер запущено. Починаємо цикл...")
    while True:
        price = get_crypto_price()
        if price:
            print(f"Поточна ціна BTC: ${price}")
            point = Point("crypto_price").tag("coin", "BTC").field("price", float(price))
            try:
                write_api.write(bucket="crypto_data", org="my-org", record=point)
                print(" [+] Дані в базі!")
            except Exception as e:
                print(f" [-] Помилка запису: {e}")
        else:
            print(" [-] Не вдалося отримати ціну.")

        time.sleep(60)