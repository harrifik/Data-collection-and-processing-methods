
import scrapy
from scrapy.http import HtmlResponse
from leroymerlinparcer.leroymerlinparcer.items import LeroymerlinparcerItem
from scrapy.loader import ItemLoader


class LeroymerlinSpider(scrapy.Spider):
    name = 'leroymerlin'
    allowed_domains = ['leroymerlin.ru']
    start_urls = ['http://leroymerlin.ru/']

    def __init__(self, search):
        self.start_urls = [f'https://leroymerlin.ru/search/?q={search}']


    def parse(self, response):
        next_page = response.xpath('//a[@class="paginator-button next-paginator-button"]/@href').extract_first()
        links = response.xpath('//a[@class="black-link product-name-inner"]/@href').extract()

        for link in links:
            yield response.follow(link, callback=self.item_parse)

        yield response.follow(next_page, callback=self.parse)


    def item_parse(self, response: HtmlResponse):
        loader = ItemLoader(item=LeroymerlinparcerItem(), response=response)
        loader.add_xpath('photos', '//img[contains(@alt, "product image")]/@src')
        loader.add_xpath('name', '//h1[contains(@class, "header-2")]/text()')
        loader.add_xpath('price', '//uc-pdp-price-view/span[contains(@slot, "price")]/text()')
        loader.add_value('url', response.url)
        loader.add_value('folder', response.url)
        loader.add_value('features', self.feature_parser(response))
        yield loader.load_item()


    def feature_parser(self, response: HtmlResponse):
        features = []
        for feature in response.css('dt'):
            feature_dict = {}
            key = feature.css("::text").get()
            value = feature.xpath('./following-sibling::dd/text()').get()
            feature_dict[f'{key}'] = value
            features.append(feature_dict)
        return features