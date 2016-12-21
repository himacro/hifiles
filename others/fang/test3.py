#qpy:3
# -*- coding:utf-8 -*-

from datetime import datetime
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


engine = create_engine('sqlite:///lianjia.db', echo=True)
Session = sessionmaker(bind=engine)
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


def create_tables():
    Base.metadata.create_all(engine)

create_tables()


def parse_lianjia(html, session):
    soup = Soup(html, 'lxml')

    house_tags = soup.select('.sellListContent > li')

    for htag in house_tags:

        title_tag = htag.find(class_='title')
        title = title_tag.get_text().strip()
        id_ = int(title_tag.find('a')['href'][-17:-5])
        title = htag.find(class_='title').get_text().strip()
        community, layout, area, direction, decoration, has_lift = \
                htag.find(class_='houseInfo').get_text().strip().replace(' ', '').split('|')
        area = float(area[:-2])
        
        unit_price = float(htag.find(class_='unitPrice').get_text().strip()[2:-4])
        total_price = float(htag.find(class_='totalPrice').get_text().strip()[:-1])
    
        h = session.query(House).filter(House.id_ == id_).first()
        if not h:
            h = House(id_=id_, title=title, community=community, area=area, layout=layout)
        h.title = title

        session.add(h)

        p = session.query(Price).filter(Price.hid == id_).filter(Price.date == TODAY).first()
        if not p:
            p = Price(hid=id_, date=TODAY, unit_price=unit_price, total_price=total_price)
        else:
            p.unit_price = unit_price
            p.total_price = total_price

        session.add(p)


URLS = ( 
        r'http://dl.lianjia.com/ershoufang/c1311042053238/',
#       r'http://dl.lianjia.com/ershoufang/c1311043078176/',
        )


def test():
    try:
        session = Session()
        parse_lianjia(open('test.html'), session)
        session.commit()
    finally:
        session.close()


def update_ershoufang(url):
    session = Session()

    resp = requests.get(url)
    next_urls = parse_lianjia(resp.content(), session)

    for url in next_urls:
        resp = requests.get(url)
        parse_lianjia(resp.content(), session)

    session.commit()
    session.close()




if __name__ == '__main__':
    for url in URLS:
        update_ershoufang(url)


