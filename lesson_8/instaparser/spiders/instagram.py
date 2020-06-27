# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from instaparser.instaparser.items import InstaparserItem
import re
import json
from urllib.parse import urlencode
from copy import deepcopy


class InstagramSpider(scrapy.Spider):
    # атрибуты класса
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://instagram.com/']
    insta_login = 'harrifik2020'
    insta_pwd = '#PWD_INSTAGRAM_BROWSER:10:1593267590:AX1QADb1xbXN1WbRasidH2B/hvZg3i2TBxQF4QxX7SvR//lR0DnTynE0i74mgRtWNvkU8I3V1sJETy7dl74saswv22w28YQOxynHWmcV6w9+h1WRnTIh2T5fMgVMbZaxm3C7U1gnIwwQdhS08FIVBA=='  #
    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    parse_users = ['cnc_skill', 'proiplana']  # Пользователь, у которого собираем посты. Можно указать список

    graphql_url = 'https://www.instagram.com/graphql/query/?'
    posts_hash = 'eddbde960fed6bde675388aac39a3657'  # hash для получения данных по постах с главной страницы
    subscribers_hash = 'c76146de99bb02f6415203be841dd25a'
    subscriptions_hash = 'd04b0a864b4b54837c0d870b0e77e076'

    def parse(self, response: HtmlResponse):  # Первый запрос на стартовую страницу
        csrf_token = self.fetch_csrf_token(response.text)  # csrf token забираем из html
        yield scrapy.FormRequest(  # заполняем форму для авторизации
            self.inst_login_link,
            method='POST',
            callback=self.user_parse,
            formdata={'username': self.insta_login, 'enc_password': self.insta_pwd},
            headers={'X-CSRFToken': csrf_token}
        )

    def user_parse(self, response: HtmlResponse):
        j_body = json.loads(response.text)
        if j_body['authenticated']:
            for user in self.parse_users:
                yield response.follow(
                    f'/{user}',
                    callback=self.user_data_parse,
                    cb_kwargs={'username': user}
                )

    def user_data_parse(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)
        variables = {'id': user_id,
                     'include_reel': True,
                     'fetch_mutual': False,
                     'first': 24}

        url_subscribers = f'{self.graphql_url}query_hash={self.subscribers_hash}&{urlencode(variables)}'
        url_subscriptions = f'{self.graphql_url}query_hash={self.subscriptions_hash}&{urlencode(variables)}'

        yield response.follow(
            url_subscribers,
            callback=self.user_subscribers_parse,
            cb_kwargs={'username': username,
                       'user_id': user_id,
                       'variables': deepcopy(variables)}
        )

        yield response.follow(
            url_subscriptions,
            callback=self.user_subscriptions_parse,
            cb_kwargs={'username': username,
                       'user_id': user_id,
                       'variables': deepcopy(variables)}
        )

    def user_subscribers_parse(self, response: HtmlResponse, username, user_id, variables):
        j_data = json.loads(response.text)
        page_info = j_data.get('data').get('user').get('edge_followed_by').get('page_info')
        if page_info.get('has_next_page'):
            variables['after'] = page_info['end_cursor']
            url = f'{self.graphql_url}query_hash={self.subscribers_hash}&{urlencode(variables)}'
            yield response.follow(
                url,
                callback=self.user_subscribers_parse,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables': deepcopy(variables)}
            )

        subscribers = j_data.get('data').get('user').get('edge_followed_by').get('edges')
        for subscriber in subscribers:
            item = InstaparserItem(
                subs_id=subscriber['node']['id'],
                user_id=user_id,
                user_name=username,
                subscriber=1,
                subscription=0,
                photo=subscriber['node']['profile_pic_url'],
                username=subscriber['node']['username'],
                full_name=subscriber['node']['full_name']
            )
        yield item

    def user_subscriptions_parse(self, response: HtmlResponse, username, user_id, variables):
        j_data = json.loads(response.text)
        page_info = j_data.get('data').get('user').get('edge_follow').get('page_info')
        if page_info.get('has_next_page'):
            variables['after'] = page_info['end_cursor']
            url = f'{self.graphql_url}query_hash={self.subscriptions_hash}&{urlencode(variables)}'
            yield response.follow(
                url,
                callback=self.user_subscriptions_parse,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables': deepcopy(variables)}
            )

        subscriptions = j_data.get('data').get('user').get('edge_follow').get('edges')
        for subscription in subscriptions:
            item = InstaparserItem(
                subs_id=subscription['node']['id'],
                user_id=user_id,
                user_name=username,
                subscriber=0,
                subscription=1,
                photo=subscription['node']['profile_pic_url'],
                username=subscription['node']['username'],
                full_name=subscription['node']['full_name']
            )
        yield item


    # Получаем токен для авторизации
    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    # Получаем id желаемого пользователя
    def fetch_user_id(self, text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')
