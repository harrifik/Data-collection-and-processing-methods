# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InstaparserItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field()
    user_id = scrapy.Field()
    subscriber = scrapy.Field()
    subscription = scrapy.Field()
    photo = scrapy.Field()
    username = scrapy.Field()
    full_name = scrapy.Field()
