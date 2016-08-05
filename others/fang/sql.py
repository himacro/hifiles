create_table_house = '''
create table house (
    hid text primary key not null,
    community text not null,
    area double not null,
    layout text,
    school text,
    floor text,
    href text,
    title text
)
'''

insert_into_house = '''
insert into house (hid, community, area, layout, school, floor, href, title) 
    values('{h.hid}', '{h.community}', {h.area}, '{h.layout}', '{h.school}', '{h.floor}', '{h.href}', '{h.title}')
'''

create_table_date = '''
create table date (
    date text primary key not null
)
'''

insert_into_date = '''
insert into date (date) values ('{}')
'''

create_table_prices = '''
create table price (
    hid text not null,
    date text not null,
    total double,
    unit double,
    constraint pid primary key (hid, date)
    )
'''

insert_into_price = '''
insert into price (hid, date, total, unit) values ('{}', '{}', {}, {})
'''
