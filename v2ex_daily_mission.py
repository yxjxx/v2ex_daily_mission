#!/usr/bin/python
# -*- coding : utf-8 -*-
from bs4 import BeautifulSoup
import requests


username = ''   # your v2ex username
password = ''    # your v2ex password
login_url = 'https://v2ex.com/signin'
home_page = 'https://www.v2ex.com'
mission_url = 'https://www.v2ex.com/mission/daily'

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.152 Safari/537.36"

headers = {
        "User-Agent": UA,
        "Host": "www.v2ex.com",
        "Referer": "https://www.v2ex.com/signin",
        "Origin": "https://www.v2ex.com"
        }

v2ex_session = requests.Session()


def make_soup(url, tag, name):
    page = v2ex_session.get(url, headers=headers, verify=True).text
    soup = BeautifulSoup(page)
    soup_result = soup.find(attrs={tag: name})
    # print soup_result
    return soup_result

once_vaule = make_soup(login_url, 'name', 'once')['value']
print(once_vaule)

post_info = {
    'u': username,
    'p': password,
    'once': once_vaule,
    'next': '/'
}

resp = v2ex_session.post(login_url, data=post_info,
                         headers=headers, verify=True)

short_url = make_soup(mission_url, 'class', 'super normal button')['onclick']


first_quote = short_url.find("'")
last_quote = short_url.find("'", first_quote+1)
final_url = home_page + short_url[first_quote+1:last_quote]

page = v2ex_session.get(final_url, headers=headers, verify=True).content

successful = make_soup(mission_url, 'class', 'fa fa-ok-sign')
if successful:
    print ("Successful.")
else:
    print ("Something wrong.")
