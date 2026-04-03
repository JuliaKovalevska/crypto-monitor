import requests
import time
import hvac  
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

print("Починаємо роботу. Стукаємось у Vault за дозволами...")

vault_client = hvac.Client(url='http://vault:8200', token='my-root-token')

try:
    read_response = vault_client.secrets.kv.v2.read_secret_version(path='crypto_app')

    INFLUX_TOKEN = read_response['data']['data']['influx_token']
    print(" [+] Секрет успішно отримано з Vault!")
except Exception as e:
    print(f" [-] Помилка читання з Vault: {e}")
    INFLUX_TOKEN = "error"

INFLUX_URL = "http://influxdb:8086"
INFLUX_ORG = "my-org"
INFLUX_BUCKET = "crypto_data"

db_client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = db_client.write_api(write_options=SYNCHRONOUS)


def get_crypto_price(coin="bitcoin"):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd"
    try:
        response = requests.get(url)
        data = response.json()
        if coin in data:
            return data[coin]['usd']
        return None
    except Exception as e:
        print(f"Помилка під час запиту: {e}")
        return None


if __name__ == "__main__":
    print("Скрейпер запущено. Збираємо ціну...")
    while True:
        price = get_crypto_price()
        if price:
            print(f"Поточна ціна BTC: ${price}")
            point = Point("crypto_price").tag("coin", "BTC").field("price", float(price))
            try:
                write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)
                print(" [+] Успішно збережено в базу!")
            except Exception as e:
                print(f" [-] Помилка запису в InfluxDB: {e}")

        time.sleep(60)