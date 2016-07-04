#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
from datetime import datetime
import json
import collections
import heapq

from bs4 import BeautifulSoup
import requests




class House():
    def __init__(
            self,
            title,
            community,
            area,
            layout,
            floor,
            school,
            hid,
            href,
            ):

        self.title = title
        self.community = community
        self.area = area
        self.layout = layout
        self.floor = floor
        self.school = school
        self.href = href
        self.hid = hid
        self.prices = {}


    def update_prices(self, total_price, unit_price, date):
        if type(date) is datetime:
            date = date.strftime('%Y/%m/%d')

        self.prices[date] = {
                'total_price': total_price,
                'unit_price': unit_price
                }

    def update(self, other):
        if other.hid != self.hid:
            return

        self.title = other.title
        self.community = other.community
        self.area = other.area
        self.layout = other.layout
        self.floor = other.floor
        self.school = other.school
        self.href = other.href
        self.prices.update(other.prices)

    def price_changed(self, days=2):
        if len(self.prices) < days:
            return True

        prices_set = {price['total_price'] for price in self.latest_prices(days).values()}
        if len(prices_set) == 1:
            return False
        else:
            return True

    def latest_dates(self, days=2):
        days = min(days, len(self.prices))
        return heapq.nlargest(days, self.prices.keys())
        

    def latest_prices(self, days=2):
        return {date: self.prices[date] for date in self.latest_dates(days)}


    def __str__(self):
       # return '{hid}'.format(self)
        return '{h.hid}: {h.community} - {h.area}平|{h.layout} - {h.title} - {h.href}'.format(h=self)


class Houses():
    def __init__(self):
        self.data = {}
        self.update_dates = []

    def update(self, parse, urls):
        if not urls:
            return

        today = datetime.now().strftime('%Y/%m/%d')

        for url in urls:
            soup = BeautifulSoup(requests.get(url).content.decode('utf-8'), 'lxml')

            house_list = parse(soup, today)

            for (title, community, 
                    area, layout, floor, school, 
                    hid, href, 
                    total_price, unit_price) in house_list:

                house = House(title, community, area, layout, floor, school, hid, href)
                house.update_prices(total_price, unit_price, today)

                if hid in self.data:
                    self.data[hid].update(house)
                else:
                    self.data[hid] = house

        if today not in self.update_dates:
            self.update_dates.append(today)


    @staticmethod
    def dump_json(obj, fn):
        with open(fn, 'w') as f:
            json.dump(obj, f, indent=4, ensure_ascii=False, default=serialize)

    @staticmethod
    def load_json(fn):
        with open(fn, 'r') as f:
            return json.load(f, object_hook=unserialize)

    def report(self):
        new, removed, price_changed = self.get_changes()

        table = ( 
                    ('新增房源', new),
                    ('下架房源', removed),
                    ('价格变动', price_changed)
                )

        for title, lst in table:
            print('==========')
            print(title)
            print('==========')
            if lst:
                for house in lst:
                    print('{h.hid}: {h.community} - {h.area}平|{h.layout} - {h.title} - {h.href}'.format(h=house))
                    for date, price in house.latest_prices(2).items():
#                   for date in house.latest_dates(days=2):
#                       if date in house.prices:
                        print('  {}:  {p[total_price]}万 / {p[unit_price]}'.format(date, p=price))
            else:
                print('无')

            print('')


    def get_changes(self):
        new = set()
        removed = set()
        price_changed = set()

        if not self.update_dates:
            print('没有任何更新日期')
        elif len(self.update_dates) == 1:
            new = set(self.data.values())
        else:
                last, latest = self.update_dates[-2:]

                for date, info in self.data.items():
                    prices = info.prices

                    if latest not in prices:
                        if last in prices:
                            removed.add(info)
                    elif len(prices) == 1:
                        new.add(info)
                    elif info.price_changed(days=2):
                        price_changed.add(info)

        return new, removed, price_changed



def parse_hwj(soup, date):
    houses = []

    house_lis = soup.find(id='houses_list').find_all(class_='houseList_cycle')
    for hl in house_lis:
        tag_title = hl.find(class_='fontHouse_title')
        tag_a1 = hl.find(class_='fontHouse_txt')

        title = str(tag_title.a.string)
        path = tag_title.a['href']
        hid = 'HWJ_' + os.path.basename(path)
        href = 'http://dl.hwj.com'+path

        community = str(tag_a1.find(class_='m_r1_lou').string.strip())
        area = float(tag_a1.find(class_='m_r1_mj').string.strip()[:-1])
        layout = str(tag_a1.find(class_='m_r1_hx').string.strip())
        floor = ""

        total_price = float(tag_a1.find(class_='m_r1_price').string.strip()[:-1])
        unit_price = float(tag_a1.find(class_='m_r1_dj').string.strip()[:-3])

        school = ""

        houses.append((title, community, area, layout, floor, school, hid, href, total_price, unit_price))

#       house = House(title, community, area, layout, floor, school, hid, href)
#       house.update_prices(total_price, unit_price, date)

#       houses.append(house)

    return houses


def parse_lj(soup, date):
    houses = []

    house_lis = soup.find('ul', id='house-lst').find_all('li')

    for hl in house_lis:
        h2 = hl.find('h2')
        col1 = hl.find(class_='col-1')
        col2 = hl.find(class_='col-2')
        col3 = hl.find(class_='col-3')
        
        title = h2.a['title']
        href = h2.a['href']
        hid = 'LJ_' + hl['data-id']

        community = str(col1.find(class_='region').string.strip())
        area = float(col1.find(class_='meters').string.strip()[:-2])
        layout = str(col1.find(class_='zone').string.strip())
        floor = str(next(col1.find(class_='con').strings).strip())

        total_price = float(col3.find(class_='price').find('span').string.strip())
        unit_price = float(col3.find(class_='price-pre').string.strip()[:-4])

        tag = col1.find(class_='fang05-ex')
        school = str(tag.string.strip()) if tag else ""

        houses.append((title, community, area, layout, floor, school, hid, href, total_price, unit_price))

#       house = House(title, community, area, layout, floor, school, hid, href)
#       house.update_prices(total_price, unit_price, date)

#       houses.append(house)

    return houses



def update_houses(json_fn):
    lj_community_urls = (
        'http://dl.lianjia.com/xiaoqu/1311042052472/esf/',
        'http://dl.lianjia.com/xiaoqu/1311042053235/esf/',
        'http://dl.lianjia.com/xiaoqu/1311042053299/esf/',
        'http://dl.lianjia.com/xiaoqu/1311042053230/esf/',
        'http://dl.lianjia.com/xiaoqu/1311042053238/esf/',
        'http://dl.lianjia.com/xiaoqu/1311042053231/esf/'
        )

    hwj_community_urls = (
        'http://dl.hwj.com/search/ershou?project=老年公寓',
        'http://dl.hwj.com/search/ershou?project=学清园',
        'http://dl.hwj.com/search/ershou?project=学子园',
        'http://dl.hwj.com/search/ershou?project=知音园',
        'http://dl.hwj.com/search/ershou?project=双语学校',
        'http://dl.hwj.com/search/ershou?project=学院派'
        )

    if os.path.isfile(json_fn):
        houses = Houses.load_json(json_fn)
        Houses.dump_json(houses, 'backup.json')
    else:
        houses = Houses()

    houses.update(parse_lj, lj_community_urls)
    houses.update(parse_hwj, hwj_community_urls)

    Houses.dump_json(houses, json_fn)
    
    houses.report()


classes = {
        'Houses': Houses,
        'House': House
        }


def serialize(obj):
    d = { '__classname__' : type(obj).__name__}
    d.update(vars(obj))
    return d


def unserialize(d):
    clsname = d.pop('__classname__', '')
    if clsname in classes:
        cls = classes[clsname]
        obj = cls.__new__(cls)
        for key, value in d.items():
            setattr(obj, key, value)

        return obj

    else:
        return d


def dump_houses(houses):
    pass
    


if __name__ == '__main__': #and __file__ in globals():
    update_houses('fang.json')
#   pass


