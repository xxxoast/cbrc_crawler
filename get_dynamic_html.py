# coding=utf-8
from selenium import webdriver
import os
import time

fireFoxOptions = webdriver.FirefoxOptions()
fireFoxOptions.set_headless()

download_path = '/home/xudi/tmp/cbrc/selenium_download'
try_timeout_count = 20
try_sleep_interval = 0.5

def get_profile():
    profile = webdriver.FirefoxProfile()
    profile.set_preference('browser.download.dir', download_path)
    profile.set_preference('browser.download.folderList', 2)
    profile.set_preference('browser.download.manager.showWhenStarting', False)
    profile.set_preference("plugin.disable_full_page_plugin_for_types", "application/pdf")
    profile.set_preference("pdfjs.disabled", True)
    profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 
                           "application/zip,text/plain,application/vnd.ms-excel,application/vnd.ms-word,text/csv,\
                           text/comma-separated-values,\
                           application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,\
                           application/vnd.openxmlformats-officedocument.wordprocessingml.document,\
                           application/msword,application/msexcel,\
                           application/octet-stream,\
                           application/x-xls,application/pdf,\
                           image/tiff,image/jpeg")
    return profile

profile = get_profile()
brower = webdriver.Firefox(firefox_profile= profile,firefox_options=fireFoxOptions)

def get_js_html(url):
    r = brower.get(url)
    return brower.page_source.encode('utf-8')

def download_js(url,href_text,content_type = None):
    brower.get(url)    
    button = brower.find_element_by_link_text(href_text)
    prev_files_length = len(os.listdir(download_path))
    button.click()
    try_count = 0
    while True:
        time.sleep(try_sleep_interval)
        after_files_length = len(os.listdir(download_path))
        if after_files_length > prev_files_length:
            break
        try_count += 1
        if try_count >= try_timeout_count:
            break
        
if __name__ == '__main__':
    pass
    