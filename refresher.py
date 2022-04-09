import requests
import time
"""import environ

env = environ.Env()
environ.Env.read_env()"""

while True:
    try:
        refresh_request = requests.request(url="https://golden-league.pro/Пляжный волейбол/Матч", method="get")

    except Exception as e:
        print(e)

    time.sleep(1)
