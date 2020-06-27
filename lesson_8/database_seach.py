from pymongo import MongoClient
from pprint import pprint

# 4) Написать запрос к базе, который вернет список подписчиков только указанного пользователя
# 5) Написать запрос к базе, который вернет список профилей, на кого подписан указанный пользователь

client = MongoClient('mongodb://127.0.0.1:27017')
db = client.instagram
objects = db.instagram.find({'subscriber': 1})          # запрос, который возвращает подписчиков
objects = db.instagram.find({'subscription': 1})        # запрос, который возвращает подписки
pprint(list(objects))
