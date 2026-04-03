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
    INF