# -*- coding:utf-8 -*-
import os
import re
from bs4 import BeautifulSoup

from misc import valid_city,dates_trans,empty

root_path = r'/home/xudi/tmp/cbrc/punishment_source'

first_row_kw = re.compile(ur'行政处罚决定书文号')
def is_first_row(tag):
    if tag.name == 'td':
        text = empty.sub('',tag.text)
        reobj = first_row_kw.search(text)
        return True if reobj else False
    return False

def precess_htmls(include,exclude):
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
                        
if __name__ == '__main__':
    pass