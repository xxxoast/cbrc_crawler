# -*- coding:utf-8 -*- 
from bs4 import BeautifulSoup
from get_dynamic_html import get_js_html
from misc import is_table_td

url = r'http://www.cbrc.gov.cn/chinese/home/docView/007EAB47BE7B4343BAD1861EF4CFA5E3.html'
html = get_js_html(url)
soup = BeautifulSoup(html,'html.parser')
print soup.prettify()


