#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
from datetime import datetime
import json
import collections
import heapq
from queue import Queue
from threading import Thread
import logging

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

        prices_set = {price['total_price']
                      for price in self.latest_prices(days).values()}
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

    @staticmethod
    def _get_from_url(urlq, respq):
        logging.debug("Started a new thread")
        while True:
            item = urlq.get()
            if item is None:
                logging.debug("Exiting thread...")
                urlq.put(None)
                break

            url, xiaoqu, parse = item

            print("正从链家获取{}的信息({})".format(xiaoqu, url))
            resp = requests.get(url)
            if resp.status_code != requests.codes.ok:
                print('{}信息获取失败: {}'.fomrat(xiaoqu, str(resp.status_code)))
                continue
                urlq.task_done()

            print('{}信息获取成功.'.format(xiaoqu))
            respq.put((xiaoqu, resp))

            urlq.task_done()
            logging.debug("Task done")

    def update(self, parse, urls):
        if not urls:
            return

        urlq = Queue()
        respq = Queue()
        thrds = []
        today = datetime.now().strftime('%Y/%m/%d')

        for n in range(6):
            t = Thread(target=self._get_from_url, args=(urlq, respq))
            t.daemon = True
            t.start()
            thrds.append(t)


        for url in urls:
            url = list(url)
            url.append(parse)
            urlq.put(url)

        urlq.join()
        urlq.put(None)

        for t in thrds:
            t.join()

        while not respq.empty():
            xiaoqu, resp = respq.get()
            print('{}信息分析中...'.format(xiaoqu))
            soup = BeautifulSoup(resp.content.decode('utf-8'), 'html.parser')
            if not soup:
                print('发现分析错误')
                continue

            house_list = parse(soup)
            print("{}二手房信息: {}条".format(xiaoqu, len(house_list)))
            for (title, community,
                    area, layout, floor, school,
                    hid, href,
                    total_price, unit_price) in house_list:

                house = House(title, community, area, layout,
                              floor, school, hid, href)
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
                    print(
                        '{h.hid}: {h.community} - {h.area:.2f}平|{h.layout} - {h.title} - {h.href}'.format(h=house))
                    for date, price in house.latest_prices(2).items():
                        print(
                            '  {}:  {p[total_price]:.2f}万 / {p[unit_price]:.2f}'.format(date, p=price))
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


def parse_hwj(soup):
    houses = []

    house_lis = soup.find(id='houses_list').find_all(class_='houseList_cycle')
    for hl in house_lis:
        tag_title = hl.find(class_='fontHouse_title')
        tag_a1 = hl.find(class_='fontHouse_txt')

        title = str(tag_title.a.string)
        path = tag_title.a['href']
        hid = 'HWJ_' + os.path.basename(path)
        href = 'http://dl.hwj.com' + path

        community = str(tag_a1.find(class_='m_r1_lou').string.strip())
        area = float(tag_a1.find(class_='m_r1_mj').string.strip()[:-1])
        layout = str(tag_a1.find(class_='m_r1_hx').string.strip())
        floor = ""

        total_price = float(tag_a1.find(
            class_='m_r1_price').string.strip()[:-1])
        unit_price = float(tag_a1.find(class_='m_r1_dj').string.strip()[:-3])

        school = ""

        houses.append((title, community, area, layout, floor,
                       school, hid, href, total_price, unit_price))


    return houses


def parse_lj(soup):
    houses = []

    # print(soup.find_all('ul')[4])
    # print(soup.find_all('ul')[5])
    # print(len(soup.find_all('ul')))


    # house_lis = soup.find('ul', class_='listContent').find_all('li')

    def _find(tag, class_, name='div'):
        for div in tag.find_all(name):
            if div.has_attr('class') and class_ in div['class']:
                return div

        return None

    house_ul = _find(soup, 'listContent', 'ul')
    for hl in house_ul.find_all('li'):
        title_tag = _find(hl, 'title')

        href = title_tag.a["href"]
        title = next(title_tag.stripped_strings)

        total_price = float(_find(hl, "totalPrice").find("span").string)
        unit_price_tag = _find(hl, "unitPrice")
        unit_price = float(unit_price_tag.find('span').string[2:-4])
        hid = 'LJ_' + unit_price_tag["data-hid"]

        basic_infos = "".join(_find(hl, "houseInfo").stripped_strings).split('|')
        community = basic_infos[0]
        layout = basic_infos[1].strip()
        area = float(basic_infos[2][:-3])
        floor = next(_find(hl, "positionInfo").strings)

        school_tag = hl.find("span", class_="school")
        school = str(school_tag.string) if school_tag else ""

        houses.append((title, community, area, layout, floor,
                       school, hid, href, total_price, unit_price))

    return houses


def update_houses(json_fn):
    lj_community_urls = (
         ('http://dl.lianjia.com/ershoufang/c1311042053299/', '学子园'),
         ('http://dl.lianjia.com/ershoufang/c1311042052472/', '老年公寓'),
         ('http://dl.lianjia.com/ershoufang/c1311042053230/', '学清园'),
         ('http://dl.lianjia.com/ershoufang/c1311042053235/', '知音园'),
         ('http://dl.lianjia.com/ershoufang/c1311042053231/', '双语学校'),
         ('http://dl.lianjia.com/ershoufang/c1311042053238/', '学院派'),
        )

    # hwj_community_urls = (
    #     'http://dl.hwj.com/search/ershou?project=老年公寓',
    #     'http://dl.hwj.com/search/ershou?project=学清园',
    #     'http://dl.hwj.com/search/ershou?project=学子园',
    #     'http://dl.hwj.com/search/ershou?project=知音园',
    #     'http://dl.hwj.com/search/ershou?project=双语学校',
    #     'http://dl.hwj.com/search/ershou?project=学院派'
    # )

    if os.path.isfile(json_fn):
        houses = Houses.load_json(json_fn)
    else:
        houses = Houses()

    houses.update(parse_lj, lj_community_urls)
####houses.update(parse_hwj, hwj_community_urls)

    Houses.dump_json(houses, json_fn)

    houses.report()


classes = {
    'Houses': Houses,
    'House': House
}


def serialize(obj):
    d = {'__classname__': type(obj).__name__}
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


if __name__ == '__main__':  # and __file__ in globals():
    #ogging.basicConfig(level=logging.DEBUG)
    data_fn = os.path.join(os.path.split(__file__)[0], 'fang.json')
    print(data_fn)
    update_houses(data_fn)
