# -*- coding:utf-8 -*-
import re
unicode2utf8 = lambda x: x.encode('utf8') if isinstance(x,unicode) else x

def valid_city(city,include,exclude):
    if len(include) > 0:
        return True if city in include else False
    if len(exclude) > 0:
        return True if city not in exclude else False
    return True

empty = re.compile(ur'[\s\xa0]*')
public_table_kw = re.compile(ur'^行政处罚依据')
date_kw = re.compile(ur'[\u4e00-\u9fa5/\\.-]')

def dates_trans(x):
    x = date_kw.sub('',x)
    x = empty.sub('',x)
    print x
    try:
        if len(x) > 6:
            year,month,day = int(x[:4]),int(x[4:-2]),int(x[-2:])
        else:
            year,month,day = int(x[:4]),int(x[4:-1]),int(x[-1:])
        return 10000 * int(year) + 100 * int(month) + int(day)
    except:
        return None 
    

def is_table_td(tag):
    if tag.name == 'td':
        text = empty.sub('',tag.text)
        reobj = public_table_kw.search(text)
        return True if reobj else False
    return False