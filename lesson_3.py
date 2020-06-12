from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
import re
import hashlib
from pymongo import MongoClient
from pprint import pprint

search_text = 'разработчик python'
num_of_page = 1

main_link = 'https://tula.hh.ru'


def get_salary(link, headers):

    _min_salary, _max_salary, _currency = None, None, None

    with requests.session() as s:
        resp = s.get(link, headers=headers).text

    soup = bs(resp, 'html.parser')
    tags = soup.find_all('p', class_='vacancy-salary')
    _text = re.sub(r'\s', '', bs(str(tags[0])).get_text())
    _salary = re.findall(r'\d+', _text)
    if len(_salary) == 0:
        pass
    elif len(_salary) == 1:
        _min_salary = _max_salary = _salary[0]
        _currency = re.findall(r'руб|USD|EUR', _text)
    elif len(_salary) == 2:
        _min_salary,  _max_salary = _salary
        _currency = re.findall(r'руб|USD|EUR', _text)
    else:
        pass
    return _min_salary, _max_salary, _currency

parameters = {
    'clusters':'true',
    'enable_snippets':'true',
    'text':search_text,
    'L_save_area':'true',
    'area':'113',
    'from':'cluster_area',
    'showClusters':'true'
}

headers = {
    'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'
}

df = pd.DataFrame()

response = requests.get(main_link + '/search/vacancy', params=parameters, headers=headers)

for i in range(num_of_page):

    soup = bs(response.text, 'html.parser')
    tags = soup.find_all('a', class_='bloko-link HH-LinkModifier')
    vacancies = {
        'id': [],
        'name': [],
        'min_salary': [],
        'max_salary': [],
        'currency':[],
        'link': [],
        'site':[]
    }
    for tag in tags:
        _id = 'hh' + re.findall(r'(\d+)\??', tag['href'])[0]
        _name = bs(str(tag)).get_text()
        _min_salary, _max_salary, _currency = get_salary(tag['href'], headers)
        _link = tag['href']

        vacancies['id'].append(hashlib.sha256(_id.encode('utf-8')).hexdigest())
        vacancies['name'].append(_name)
        vacancies['min_salary'].append(_min_salary)
        vacancies['max_salary'].append(_max_salary)
        vacancies['currency'].append(_currency)
        vacancies['link'].append(_link)
        vacancies['site'].append(main_link)

    df = pd.concat([df, pd.DataFrame(vacancies)]).drop_duplicates(subset='id').reset_index(drop=True)

    next_page = None

    if (i+1) < num_of_page:
        next_page = soup.find('a', class_='bloko-button HH-Pager-Controls-Next HH-Pager-Control')

    if next_page:
        next_page_link = main_link + next_page['href']
        response = requests.get(next_page_link, headers=headers)
    else:
        break


# 1) Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB и реализовать функцию,
# записывающую собранные вакансии в созданную БД

def save_to_db(data_frame, db_name):
    client = MongoClient('mongodb://127.0.0.1:27017')
    db = client[db_name]

    data = data_frame.to_dict('records')

    for item in data:
        objects = db.hh_vacancy_db.find({'id': item['id']})
        if len(list(objects)) == 0:
            db.hh_vacancy_db.insert_one(item.copy())

    return f'Vacancy saved to: {db_name}'


db_name = 'hh_vacancy_db'

client = MongoClient('mongodb://127.0.0.1:27017')
db = client[db_name]
db.hh_vacancy_db.create_index('id', unique=True)

save_to_db(data_frame=df, db_name=db_name)

# 2) Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой больше введенной суммы

def search_salary_gt(db_name, min_value):
    client = MongoClient('mongodb://127.0.0.1:27017')
    db = client[db_name]
    objects = db.vacancydb.find({'min_salary': {'$gt': min_value}})
    return list(objects)

pprint(search_salary_gt(db_name='hh_vacancy_db', min_value=100000))



