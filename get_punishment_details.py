# -*- coding:utf-8 -*- 
import os

from sqlalchemy import func
from bs4 import BeautifulSoup
import re

from get_dynamic_html import get_js_html
from misc import unicode2utf8,is_table_td
from db_api import Punishment

root_path = r'/home/xudi/tmp/cbrc/punishment_source'
download_path = r'/home/xudi/tmp/cbrc/selenium_download'
log_path = r'/home/xudi/tmp/cbrc/log'


def strip_tags(soup,invalid_tags):
    for tag in invalid_tags: 
        for match in soup.find_all(tag):
            match.replaceWithChildren()
    return soup

def create_punishment_files(dbapi,city,des_path):
    session = dbapi.get_session()
    cursor  = session.query(dbapi.table_struct).filter_by(city = city)
    count = session.query(func.count(dbapi.table_struct.index)).filter_by(city = city).scalar()
    session.close()
    print city,count
    if count <= 0:
        return 
    print 'publication url = ',cursor.first().publication_url
    has_download = set([ int(i.split('.')[0].split('_')[0])  for i in  \
                            filter(lambda x: not x.startswith('.'),os.listdir(os.path.join(root_path,city))) ])
    cnt = 0
    for record in cursor.all():
        if int(record.index) in has_download:
                continue
        print 'cnt = ',cnt,', index = ',record.index
        cnt += 1
        public_html = get_js_html(record.punishment_item_url)
        soup = BeautifulSoup(public_html,'html.parser')
        table_tag = None
        table_td_tag = soup.find(is_table_td)
        if table_td_tag:
            table_tag = table_td_tag.find_parent('table')
        if table_tag is None:
            print '[Warning] Invalid Page = ',record.punishment_item_url
            continue
        else:
            table_tag = strip_tags(table_tag, ['span','p'])
            outfile_name = '.'.join(('_'.join((str(record.index),str(record.update_date))),'html'))
            outfile_path = os.path.join(des_path,outfile_name)
            if not os.path.exists(outfile_path):
                with open(outfile_path, 'ab') as fout:
                    fout.write(table_tag.prettify().encode('utf-8'))
        
def get_punish_table():
    dbapi = Punishment()
    dbapi.create_table()
    ss = dbapi.get_session()
    cursor = ss.query(dbapi.table_struct.city).group_by(dbapi.table_struct.city).all()
    cities = [i.city for i in cursor]
    ss.close()
    print cities
    for city in cities:
        des_path = os.path.join(root_path,city)
        if not os.path.exists(des_path):
            os.makedirs(des_path)
        create_punishment_files(dbapi,city,des_path)
  
if __name__ == '__main__':
    print '--->>> start get punishment details'
    get_punish_table()
    