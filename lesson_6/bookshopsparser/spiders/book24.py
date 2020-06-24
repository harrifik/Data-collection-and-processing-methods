import scrapy
from scrapy.http import HtmlResponse
from bookshopsparser.items import BookshopsparserItem


def book_parse(response: HtmlResponse):
    book_url = response.url
    book_title = response.css('h1.item-detail__title::text').extract_first()
    book_author = response.css('a.item-tab__chars-link::text').extract_first()
    book_price = response.css('div.item-actions__price-old::text').extract_first()
    book_price_discount = response.css('div.item-actions__price b::text').extract_first()
    book_rate = response.css('span.rating__rate-value::text').extract_first()

    yield BookshopsparserItem(title=book_title, price=book_price, author=book_author,
                              discount=book_price_discount, rate=book_rate, url=book_url)


class Book24Spider(scrapy.Spider):
    name = 'book24'
    allowed_domains = ['book24.ru']
    start_urls = ['https://book24.ru/search/?q=business']

    def parse(self, response):
        next_page = response.css('a.catalog-pagination__item:contains("Далее")::attr(href)').extract_first()
        books_links = response.css('div.book__title a.book__title-link::attr(href)').extract()

        for book in books_links:
            yield response.follow(book, callback=book_parse)

        yield response.follow(next_page, callback=self.parse)
