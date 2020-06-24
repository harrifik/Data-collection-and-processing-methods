import scrapy
from scrapy.http import HtmlResponse
from bookshopsparser.items import BookshopsparserItem


def book_parse(response: HtmlResponse):
    book_url = response.url
    book_title = response.css('div.prodtitle h1::text').extract_first()
    book_author = response.css('div.product-description div.authors a.analytics-click-js::text').extract_first()
    book_rate = float(response.css('div[id="product-voting-body"] div[id="rate"]::text').extract_first())
    book_price = response.css('div.buying span.buying-priceold-val-number::text').extract_first()
    book_price_discount = response.css('div.buying span.buying-pricenew-val-number::text').extract_first()

    yield BookshopsparserItem(title=book_title, price=book_price, author=book_author,
                              discount=book_price_discount, rate=book_rate, url=book_url)


class LabirintSpider(scrapy.Spider):
    name = 'labirint'
    allowed_domains = ['labirint.ru']
    start_urls = ['https://www.labirint.ru/search/programming/?stype=0']

    def parse(self, response: HtmlResponse):
        next_page = response.css('div.pagination-next a.pagination-next__text::attr(href)').extract_first()
        books_links = response.css('div.card-column a.cover::attr(href)').extract()

        for book in books_links:
            yield response.follow(book, callback=book_parse)

        yield response.follow(next_page, callback=self.parse)
