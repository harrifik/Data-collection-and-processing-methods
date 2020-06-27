# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import scrapy
import os
from urllib.parse import urlparse
from pymongo import MongoClient
from scrapy.pipelines.images import ImagesPipeline


class InstaparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.instagram

    def process_item(self, item, spider):
        collection = self.mongo_base[spider.name]
        collection.insert_one(item)
        return item


class InstaparserPhotosPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photo']:
            try:
                yield scrapy.Request(item['photo'], meta=item)
            except Exception as e:
                print(e)

    def file_path(self, request, response=None, info=None):
        item = request.meta
        return f'{item["_id"]}'

