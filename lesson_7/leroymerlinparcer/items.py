# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy.loader.processors import MapCompose, TakeFirst
import scrapy


def price_to_float(value):
    return float(value.replace(' ', ''))


def create_folder(url):
    return url.split('/')[-2]


class LeroymerlinparcerItem(scrapy.Item):
    _id = scrapy.Field()
    name = scrapy.Field(output_processor=TakeFirst())
    photos = scrapy.Field()
    price = scrapy.Field(input_processor=MapCompose(price_to_float), output_processor=TakeFirst())
    url = scrapy.Field(output_processor=TakeFirst())
    features = scrapy.Field()
    folder = scrapy.Field(input_processor=MapCompose(create_folder), output_processor=TakeFirst())