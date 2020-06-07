from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
import re

search_text = 'разработчик'
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
        'name': [],
        'min_salary': [],
        'max_salary': [],
        'currency':[],
        'link': [],
        'site':[]
    }
    for tag in tags:
        _name = bs(str(tag)).get_text()
        _min_salary, _max_salary, _currency = get_salary(tag['href'], headers)
        _link = tag['href']

        vacancies['name'].append(_name)
        vacancies['min_salary'].append(_min_salary)
        vacancies['max_salary'].append(_max_salary)
        vacancies['currency'].append(_currency)
        vacancies['link'].append(_link)
        vacancies['site'].append(main_link)

    df = pd.concat([df, pd.DataFrame(vacancies)]).reset_index(drop=True)

    if (i+1) < num_of_page:
        next_page = soup.find('a', class_='bloko-button HH-Pager-Controls-Next HH-Pager-Control')
    else:
        next_page = None

    if next_page is not None:
        next_page_link = main_link + next_page['href']
        response = requests.get(next_page_link, headers=headers)
    else:
        break

df.to_csv('hh_vacancies.csv')

pass

