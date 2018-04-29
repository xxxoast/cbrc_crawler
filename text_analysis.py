# -*- coding:utf-8 -*-
import os
import re
import pandas as pd
from bs4 import BeautifulSoup

from misc import valid_city,dates_trans,empty
from db_api import Publication

is_replaceble = lambda x: isinstance(x,str) or isinstance(x,unicode)
root_path = r'/home/xudi/tmp/cbrc/punishment_source'

first_row_kw = re.compile(ur'(行政)?处罚决定书文号')
def is_first_row(tag):
    if tag.name == 'td':
        text = empty.sub('',tag.text)
        reobj = first_row_kw.search(text)
        return True if reobj else False
    return False

def htmlpath2txt(htmlpath):
    rows = []
    with open(htmlpath) as fin:
        for line in fin:
            rows.append(line)
    return ''.join(rows)

def flatten(l):    
    for el in l:    
        if hasattr(el, "__iter__") and not isinstance(el, basestring):    
            for sub in flatten(el):    
                yield sub    
        else:    
            yield el

amount_kw  = re.compile(ur'(?:(?:([1-9][0-9，,.]*万?)元)|(?:罚款(?:人民币)?([1-9][0-9，,.]*万?)元?))')
sum_amount_kw = re.compile(ur'[合总共]计[\u4e00-\u9fa5]*([1-9][0-9，,.]*万?)元')
tenk_kw    = re.compile(ur'万')
comma_kw   = re.compile(ur'[,，]')
def str2float(text):
    no_comma = comma_kw.sub('',text)
    multiply = 1
    if tenk_kw.search(text):
        no_comma = tenk_kw.sub('',no_comma)
        multiply = 10000
    return multiply * float(no_comma)

def get_punishment_amount(text):
    total = [ i for i in sum_amount_kw.findall(text) if len(i) > 0]
    if len(total) > 0:
        total = str2float(total[-1])
        return total
    else:
        each = [ i for i in flatten(amount_kw.findall(text)) if len(i) > 0]
        return sum([str2float(i) for i in each])
               
def precess_htmls(include = [],exclude = []):
    for root, dirs, files in os.walk(root_path):
        city = root.split('/')[-1]
        if not valid_city(city,include,exclude):
            continue
        print city
        #去头
        for ifile in filter(lambda x: (not x.startswith('.')) and x.endswith('.html'),files):
            infile = os.path.join(root,ifile)
            if infile.endswith('.html'):
                soup,rewrite = None,False
                with open(infile,'r') as fin:
                    buffer = ''.join(fin.readlines())
                    soup = BeautifulSoup(buffer,'lxml')
                    first_row_tags = soup.find_all(is_first_row)
                    if len(first_row_tags) > 0:
                        td_tag = first_row_tags[0]
                    else:
                        continue
                    tr_tag = td_tag.find_parent('tr')
                    previous_trs = tr_tag.find_previous_siblings('tr') 
                    if len(previous_trs) > 0:
                        rewrite = True
                        for tr in previous_trs:
                            tr.extract()
                if rewrite:
                    with open(infile,'w') as fout:
                        fout.write(soup.prettify(encoding='utf-8'))
                        
def parse_html(infile,dbapi,ss):
    city,index,publish_date = infile.split('/')[-2],infile.split('/')[-1].split('_')[0],int(infile.split('/')[-1].split('_')[1].split('.')[0])  
    sub_index = int(infile.split('/')[-1].split('.')[0].split('_')[1])
    sub_index = 0 if sub_index > 20000000 else sub_index
    has_stored = ss.query(dbapi.table_struct.index).filter_by(city = city,index = index,sub_index = sub_index).first()
    if has_stored:
        return 
    print city,index
    htmltxt = htmlpath2txt(infile)
    soup = BeautifulSoup(htmltxt,'lxml')
#     print soup.prettify()                     
    dfs = pd.read_html(soup.prettify())
    df = dfs[0]
    df = df.dropna(axis = 1,how = 'all')
    df = df.applymap(lambda x:empty.sub('',x) if is_replaceble(x) else x)
    if len(df.columns) > 2:
        replaced_rows = df[df.columns[-1]].apply(pd.notnull)
        df.loc[replaced_rows,1] = df.loc[replaced_rows,df.columns[-1]]
        df.drop(df.columns[-1],axis = 1,inplace = True)
    df.fillna('',inplace = True)
    print df.head()
    pubnumber = df.iloc[0,1]
    violatype,reason,punish_content,whodid,update_date = df.iloc[-5:,1]
    punish_who = [None,None,None]
    residual_length = len(df) - 1 - 5
    residual_length = residual_length if residual_length <= 3 else 3 
    punish_who[:residual_length] = df.iloc[1:residual_length+1,1]
    dollar = get_punishment_amount(df.iloc[len(df)-3,1])
    record_values = flatten((city,index,sub_index,pubnumber,punish_who,violatype,reason,punish_content,whodid,dates_trans(update_date),dollar))
    db_table_columns = dbapi.get_column_names(dbapi.table_struct)
    argdict = dict(zip(db_table_columns,record_values))
    ss.merge(dbapi.table_struct(**argdict))
    ss.commit()
        
def dumpdb(include = [], exclude = []):
    dbapi = Publication()
    dbapi.create_table()
    ss = dbapi.get_session()
    for root, dirs, files in os.walk(root_path):
        city = root.split('/')[-1]
        if not valid_city(city,include,exclude):
            continue
        for ifile in filter(lambda x: (not x.startswith('.')) and x.endswith('.html'),files):
            infile = os.path.join(root,ifile)
            if infile.endswith('.html'):
                parse_html(infile,dbapi,ss)
    ss.close()

def update():
    precess_htmls()
    dumpdb()
    
if __name__ == '__main__':
    update()
    