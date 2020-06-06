import requests
import json

# 1. Посмотреть документацию к API GitHub, разобраться как вывести список репозиториев для конкретного пользователя,
# сохранить JSON-вывод в файле *.json.

url = 'https://api.github.com/users/harrifik/repos'

repos = requests.get(url)

with open('repos.json', 'w') as f:
    json.dump(repos.json(), f)

# 2. Изучить список открытых API. Найти среди них любое, требующее авторизацию (любого типа).
# Выполнить запросы к нему, пройдя авторизацию. Ответ сервера записать в файл.

# Используя сайт coinmarketcap.com получим котировки 10 певрых по капитализации криптовалют в $.

url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'

parameters = {
  'start':'1',
  'limit':'10',
  'convert':'USD'
}

headers = {
  'Accepts': 'application/json',
  'X-CMC_PRO_API_KEY': '4907088a-9d97-4d69-ae9c-3dfe7bd087e3',
}

response = requests.get(url, params=parameters, headers=headers)

with open('crypto.json', 'w') as f:
    json.dump(response.json(), f)