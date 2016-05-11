from bs4 import BeautifulSoup
import requests
import os
from datetime import datetime


class House:
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

    def __str__(self):
        return '{:<20} - {:<10} {} {:>5}万 - {} - {}'.format(self.community, self.area, self.layout, self.total_price, self.title, self.href)

    def update_price(self, date, total_price, unit_price):
        if type(date) is datetime:
            date = date.strftime('%Y-%m-%d')

        self.prices[date] = {
                'total_price': total_price,
                'unit_price': unit_price
                }


def lj_houses(url=None, houses=None):
    if not houses:
        houses = {}

    if not url:
        return houses

    resp = requests.get(url) 
    soup = BeautifulSoup(resp.content.decode('utf-8'), 'lxml')
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

        if hid not in houses:
            house = House(title, community, area, layout, floor, school, hid, href)
            houses[hid] = house
        else:
            house = houses[hid]

        house.update_price(datetime.now(), total_price, unit_price)

    return houses

def hwj_houses(url=None, houses=None):
    if not houses:
        houses = {}

    if not url:
        return houses

    resp = requests.get(url) 
    soup = BeautifulSoup(resp.content.decode('utf-8'), 'lxml')

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

        if hid not in houses:
            house = House(title, community, area, layout, floor, school, hid, href)
            houses[hid] = house
        else:
            house = houses[hid]

        house.update_price(datetime.now(), total_price, unit_price)

    return houses


def test_lj_houses():
    houses = lj_houses(url='http://dl.lianjia.com/xiaoqu/1311042053231/esf')
    for h in houses:
        print(h)

    return houses

def test_hwj_houses():
    houses = hwj_houses(url='http://dl.hwj.com/search/ershou?project=老年公寓')
    for h in houses:
        print(h)

    return houses

def get_houses():

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

    houses = {}
    for url in lj_community_urls:
        houses = lj_houses(url, houses)

    for url in hwj_community_urls:
        houses = hwj_houses(url, houses)

    for h in houses:
        print(h)

    json_fn = datetime.now().strftime('%Y-%m-%d')+'.json'
    with open(json_fn, 'w') as f:
        json.dump(houses, f, indent=4, ensure_ascii=False, default=lambda obj: vars(obj))



if __name__ == '__main__':
    pass

