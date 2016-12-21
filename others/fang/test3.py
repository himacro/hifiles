#qpy:3
# -*- coding:utf-8 -*-

from bs4 import BeautifulSoup as Soup

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///lianjia.db', echo=True)
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


class House(Base):
    __tablename__ = 'houses'

    id_ = Column(Integer, primary_key=True)
    title = Column(String, default='')
    community = Column(String, default='')
    area = Column(Float, default=0.0)
    layout = Column(String, default='')


    def __repr__(self):
        return "<House(id_='{h.id_}', community='{h.community}', title='{h.title}')>".format(h=self)

    def __str__(self):
        return '\n'.join('{}: {}'.format(k, v) for k, v in self.__dict__.items() if not k.startswith('_'))
            

if not engine.has_table('houses'):
    Base.metadata.create_all(engine)
    

def parse_lianjia(html):
    soup = Soup(html, 'lxml')

    house_tags = soup.select('.sellListContent > li')

    houses = []
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

        print(h)
        houses.append(h)

    return houses


if __name__ == '__main__':
    session.add_all(parse_lianjia(open('test.html')))
    session.commit()



