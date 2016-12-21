#qpy:3
# -*- coding:utf-8 -*-

from datetime import datetime
import re
import logging

from bs4 import BeautifulSoup as Soup
import requests

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, Date
from sqlalchemy import ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship


logging.basicConfig(level=logging.INFO)
TODAY = datetime.now().date()


# engine = create_engine('sqlite:///lianjia.db', echo=False)
# Session = sessionmaker(bind=engine)
Base = declarative_base()


class House(Base):
    __tablename__ = 'houses'

    id_ = Column(Integer, primary_key=True)
    title = Column(String, default='')
    community = Column(String, default='')
    area = Column(Float, default=0.0)
    layout = Column(String, default='')

    prices = relationship('Price')


    def __repr__(self):
        return "<House(id_='{h.id_}', community='{h.community}', title='{h.title}')>".format(h=self)

    def __str__(self):
        return '\n'.join('{}: {}'.format(k, v) for k, v in self.__dict__.items() if not k.startswith('_'))
            

class Price(Base):
    __tablename__ = 'prices'
    hid = Column(Integer, ForeignKey('houses.id_'), primary_key=True)
    date = Column(Date, primary_key=True)
    unit_price = Column(Float, default=0.0)
    total_price = Column(Float, default=0.0)

    def __repr__(self):
        return "<Price(hid='{p.hid}', date='{p.date}', unit_price={p.unit_price}, total_price={p.total_price}>".format(p=self)




total_page_pattern = re.compile(r'{"totalPage":(\d+)')


def find_next_pages(soup):
    ''' Find next pages '''

    page_box_tag = soup.find(class_='house-lst-page-box')
    page_url_template = r'http://dl.lianjia.com' + page_box_tag['page-url']

    match = total_page_pattern.match(page_box_tag['page-data'])
    if match:
        total_page = int(match.groups()[0])
    
    urls = [page_url_template.format(page=i) for i in range(2, total_page + 1)]

    return urls
        

def find_houses(soup, session):
    ''' Find houses information and store them '''

    house_tags = soup.select('.sellListContent > li')
    for htag in house_tags:

        title_tag = htag.find(class_='title')
        title = title_tag.get_text().strip()
        id_ = int(title_tag.find('a')['href'][-17:-5])
        title = htag.find(class_='title').get_text().strip().split('\n')[0]
        community, layout, area, direction, decoration, has_lift = \
                htag.find(class_='houseInfo').get_text().strip().replace(' ', '').split('|')
        area = float(area[:-2])
        
        unit_price = float(htag.find(class_='unitPrice').get_text().strip()[2:-4])
        total_price = float(htag.find(class_='totalPrice').get_text().strip()[:-1])
    
        h = session.query(House).filter(House.id_ == id_).first()
        if not h:
            h = House(id_=id_, title=title, community=community, area=area, layout=layout)
            logging.info('  New: {h.id_} - {h.area:>6.2f}平 - {p:>5.1f}万 - {h.title}'.format(h=h, p=total_price))
        else:
            h.title = title
            logging.info('  Upd: {h.id_} - {h.area:>6.2f}平 - {p:>5.1f}万 - {h.title}'.format(h=h, p=total_price))

        session.add(h)

        p = session.query(Price).filter(Price.hid == id_).filter(Price.date == TODAY).first()
        if not p:
            p = Price(hid=id_, date=TODAY, unit_price=unit_price, total_price=total_price)
        else:
            p.unit_price = unit_price
            p.total_price = total_price

        session.add(p)


def parse_lianjia(html, session):
    soup = Soup(html, 'lxml')
    find_houses(soup, session)
    return find_next_pages(soup)


URLS = ( 
         (r'http://dl.lianjia.com/ershoufang/c1311042053299/', '学子园'),
         (r'http://dl.lianjia.com/ershoufang/c1311042052472/', '老年公寓'),
         (r'http://dl.lianjia.com/ershoufang/c1311042053230/', '学清园'),
         (r'http://dl.lianjia.com/ershoufang/c1311042053235/', '知音园'),
         (r'http://dl.lianjia.com/ershoufang/c1311042053231/', '双语学校'),
         (r'http://dl.lianjia.com/ershoufang/c1311042053238/', '学院派'),
         (r'http://dl.lianjia.com/ershoufang/c1311043078176/', '软景E居'),
        )


def test():
    try:
        session = Session()
        parse_lianjia(open('test.html'), session)
        session.commit()
    finally:
        session.close()


def update_ershoufang(url, session):
    logging.info(' proc ' + url)
    resp = requests.get(url)
    return parse_lianjia(resp.content, session)


def create_tables(engine):
    Base.metadata.create_all(engine)

def do_update(echo=False):
    engine = create_engine('sqlite:///lianjia.db', echo=echo)
    create_tables(engine)

    Session = sessionmaker(bind=engine)
    session = Session()


    for url, community in URLS:
        logging.info('Updating ' + community)
        next_urls = update_ershoufang(url, session)
        for next_url in next_urls:
            update_ershoufang(next_url, session)

    session.commit()
    session.close()
    

if __name__ == '__main__':
    do_update()

