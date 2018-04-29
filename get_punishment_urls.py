# -*- coding:utf-8 -*- 
from bs4 import BeautifulSoup
from get_dynamic_html import get_js_html
from misc import valid_city,dates_trans
from sqlalchemy.sql import func
from get_dynamic_html import get_js_html
from urlparse import urljoin
import re

last_page_kw = re.compile(ur'[尾|末]页')
punishment_item_kw = re.compile(ur'行政处罚信息公开表')
date_kw  = re.compile(ur'^20[0-9]{2}[/\-][0-9]{1,2}[\-/][0-9]{1,2}$')
empty_kw = re.compile(ur'[\s\xa0]*')

root_url = 'http://www.cbrc.gov.cn'

def is_td_date(tag):
    if tag.name == 'td':
        text = empty_kw.sub('',tag.text)
        reobj = date_kw.search(text)
        return True if reobj else False
    return False

def find_public_page(url,update_date = None):
    html = get_js_html(url)
    soup = BeautifulSoup(html,'lxml')
    page_length_tag = soup.find('a',text = last_page_kw)
    format_base = '/'.join(url.split('/')[:-1])
    if page_length_tag:
        page_length = int(page_length_tag['href'].split('=')[-1]) 
        page_format = '/'.join((format_base,page_length_tag['href'].split('=')[0].split('/')[-1]))
        all_pages = [ '='.join((page_format,str(i))) for i in range(1,page_length+1)]
        print 'page_length = ',page_length
    else:
        all_pages = [url,]
    punish_pages,punish_urls,punish_dates = [],[],[]
    for ipage in all_pages:
        punish_url = get_js_html(ipage)
        soup = BeautifulSoup(punish_url,'lxml')
        item_tags = soup.find_all('a',text = punishment_item_kw)
        date_tags = [ i.find_parent('td').find_next_sibling(is_td_date) for i in item_tags]
        punish_pages.extend([ipage,] * len(item_tags))
        punish_urls.extend([urljoin(root_url, i['href']) for i in item_tags])
        punish_dates.extend([i.text.strip() for i in date_tags])
#     print punish_pages
#     print punish_urls
#     print punish_dates
    return zip(punish_pages,punish_urls,punish_dates)
        
def crawler(include = [],exclude = []):
    from db_api import Punishment
    dbapi = Punishment()
    dbapi.create_table()
    new_items = {}
    with open('branch_list.txt','r') as fin:
        for url in fin:
            city = url.split(r'/')[-2]
            city = 'cbrc' if city == 'docViewPage' else city
            if not valid_city(city,include,exclude):
                continue
            print city
            new_items[city] = []
            ss = dbapi.session()
            max_count = ss.query(func.max(dbapi.table_struct.index)).filter_by(city = city).scalar()
            max_count = max_count + 1 if max_count is not None else 0
            print 'current max index = ',max_count
            record = ss.query(dbapi.table_struct.update_date).filter_by(city = city).order_by(dbapi.table_struct.update_date.desc()).first()
            update_date = record.update_date if record is not None else None
            download_urls = find_public_page(url,update_date)
            for (punish_page,punish_url,punish_date) in download_urls:
                used_to = ss.query(dbapi.table_struct).filter_by(punishment_item_url = punish_url.strip()).scalar()
                if used_to is None:
                    new_record = (city,url.strip(),punish_page.strip(),punish_url.strip(),dates_trans(punish_date),max_count)
                    dbapi.insert_listlike(dbapi.table_struct,new_record)
                    new_items[city].append(new_record)
                    max_count += 1 
            ss.close()
            print 'dump = ',max_count
    return new_items
            
if __name__ == '__main__':
    print '--->>> start get punishment urls'
    crawler()
#     find_public_page(r'http://www.cbrc.gov.cn/zhuanti/xzcf/get2and3LevelXZCFDocListDividePage/jiangsu/1.html',update_date = None)
    print 'done'
    