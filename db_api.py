# -*- coding:utf-8 -*- 
from bs4 import BeautifulSoup

import os,sys
pkg_path = os.path.sep.join(
    (os.path.abspath(os.curdir).split(os.path.sep)[:-1]))
if pkg_path not in sys.path:
    sys.path.append(pkg_path)
    
from future_mysql.dbBase import DB_BASE
from sqlalchemy import Column, Integer, String, DateTime, Numeric, Index, Float, Boolean
from sqlalchemy import Table

class Punishment(DB_BASE):

    def __init__(self):
        db_name = 'cbrc'
        table_name = 'punishment'
        super(Punishment, self).__init__(db_name)

        self.table_obj = Table(table_name, self.meta,
                                  Column('city', String(64),index = True),
                                  Column('web_url',String(128),),
                                  Column('publication_url', String(128),index = True),
                                  Column('punishment_item_url', String(128),primary_key = True),
                                  Column('update_date',Integer),
                                  Column('index',Integer,autoincrement = True)
                                  )
        
    def create_table(self):
        self.table_struct = self.quick_map(self.table_obj)
        
html = '''
<li><a href="/sj/beijing/index.html">北京</a></li>
<li><a href="/sj/tianjin/index.html">天津</a></li>
<li><a href="/sj/hebei/index.html">河北</a></li>
<li><a href="/sj/shanxi/index.html">山西</a></li>
<li><a href="/sj/neimenggu/index.html">内蒙古</a></li>
<li><a href="/sj/liaoning/index.html">辽宁</a></li>
<li><a href="/sj/jilin/index.html">吉林</a></li>
<li><a href="/sj/heilongjiang/index.html">黑龙江</a></li>
<li><a href="/sj/shanghai/index.html">上海</a></li>
<li><a href="/sj/jiangsu/index.html">江苏</a></li>
<li><a href="/sj/zhejiang/index.html">浙江</a></li>
<li><a href="/sj/anhui/index.html">安徽</a></li>
<li><a href="/sj/fujian/index.html">福建</a></li>
<li><a href="/sj/jiangxi/index.html">江西</a></li>
<li><a href="/sj/shandong/index.html">山东</a></li>
<li><a href="/sj/henan/index.html">河南</a></li>
<li><a href="/sj/hubei/index.html">湖北</a></li>
<li><a href="/sj/hunan/index.html">湖南</a></li>
<li><a href="/sj/guangdong/index.html">广东</a></li>
<li><a href="/sj/guangxi/index.html">广西</a></li>
<li><a href="/sj/hainan/index.html">海南</a></li>
<li><a href="/sj/chongqing/index.html">重庆</a></li>
<li><a href="/sj/sichuan/index.html">四川</a></li>
<li><a href="/sj/guizhou/index.html">贵州</a></li>
<li><a href="/sj/yunnan/index.html">云南</a></li>
<li><a href="/sj/xizang/index.html">西藏</a></li>
<li><a href="/sj/shaanxi/index.html">陕西</a></li>
<li><a href="/sj/gansu/index.html">甘肃</a></li>
<li><a href="/sj/qinghai/index.html">青海</a></li>
<li><a href="/sj/ningxia/index.html">宁夏</a></li>
<li><a href="/sj/xinjiang/index.html">新疆</a></li>
<li><a href="/sj/dalian/index.html">大连</a></li>
<li><a href="/sj/ningbo/index.html">宁波</a></li>
<li><a href="/sj/xiamen/index.html">厦门</a></li>
<li><a href="/sj/qingdao/index.html">青岛</a></li>
<li><a href="/sj/shenzhen/index.html">深圳</a></li>
'''

cbrc_url = r'http://www.cbrc.gov.cn/chinese/home/docViewPage/110002.html'
root_xzcf_url = r'http://www.cbrc.gov.cn/zhuanti/xzcf/get2and3LevelXZCFDocListDividePage/{}/1.html'

def get_branch_list():
    root_url = r'http://www.cbrc.gov.cn'
    soup = BeautifulSoup(html,'lxml')
    tag_a_all = soup.find_all('a')
    with open('branch_list.txt','w') as fout:
        fout.write(cbrc_url)
        fout.write('\n')
        for tag_a in tag_a_all:
            public_page = root_xzcf_url.format(tag_a['href'].strip().split('/')[2])
            fout.write(public_page)
            fout.write('\n')

def get_cities():
    dbapi = Punishment()
    dbapi.create_table()
    ss = dbapi.get_session()
    cursor = ss.query(dbapi.table_struct.city).group_by(dbapi.table_struct.city).all()
    cities = [i.city for i in cursor]
    ss.close()
    return cities
   
if __name__ == '__main__':
    print get_cities()