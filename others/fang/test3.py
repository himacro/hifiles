#qpy:3
# -*- coding:utf-8 -*-

from bs4 import BeautifulSoup
import requests

r = requests.get(u'http://dl.lianjia.com/xiaoqu/1311042052472/esf/')
print(type(r.content))
print(r.content)

soup = BeautifulSoup(r.content, 'html.parser')
