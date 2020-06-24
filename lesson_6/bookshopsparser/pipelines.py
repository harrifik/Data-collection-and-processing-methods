# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

from pymongo import MongoClient


class BookshopsparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.books_scrapy

    def process_item(self, item, spider):

        if spider.name == 'labirint':
            self.process_labirint_item(item, spider.name)

        if spider.name == 'book24':
            self.process_book24_item(item, spider.name)

        return item


    def process_labirint_item(self, item, collection_name):
        book = {
            'url': item['url'],
            'title': item['title'],
            'author': item['author'],
            'price': item['price'],
            'discount': item['discount'],
            'rate': item['rate']
        }
        collection = self.mongo_base[collection_name]
        collection.insert_one(book)

    def process_book24_item(self, item, collection_name):
        book = {
            'url': item['url'],
            'title': item['title'],
            'author': item['author'],
            'price': item['price'],
            'discount': item['discount'],
            'rate': item['rate']
        }
        collection = self.mongo_base[collection_name]
        collection.insert_one(book)