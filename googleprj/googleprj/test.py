# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities,FirefoxProfile
import time,string
import random   
from settings import *
import MySQLdb
from selenium.webdriver.common.proxy import * 
from gevent import monkey; monkey.patch_socket()
import gevent
import logging  
from selenium.webdriver.support.wait import WebDriverWait
from redisM import RedisM

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.FileHandler('google.log')
handler.setLevel(logging.INFO)
 
# create a logging format 
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
 
# add the handlers to the logger
logger.addHandler(handler)
rm = RedisM()

keyword = ""
count = 0
db = MySQLdb.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB)
cursor = db.cursor()

def webscreen(url,driver):
    global count
    try:
        driver.get(url)
        
        nexturl = parsehtml(driver)
        count += 1
        #driver = checkstatus(driver)
        if nexturl != "https://www.baidu.com":
            webscreen(nexturl,driver)
    except Exception,e:
        logger.debug("111111111")
        logger.error('webscreen error:%s',e)

#切换IP的方法
def changeIP():
    thisip=random.choice(IPPOOL)  
    profile = webdriver.FirefoxProfile()  
    #禁止加载图片
    profile.set_preference('permissions.default.image', 2)
    
    driver = webdriver.Firefox(executable_path ="D:\Python27\geckodriver.exe")#,firefox_profile=profile)
    driver.implicitly_wait(10)
    return driver
    
#解析要获取的元素方法
def parsehtml(driver):
    
    #获取下一页
    flag = True
    nexturl = "https://www.baidu.com"
    try:
        hrefs = driver.find_elements_by_xpath('//*[@id="page"]/a')
        for one in hrefs:
                realnext = one.text
                if(u"下一页" in realnext):
                    nexturl = one.get_attribute("href")
                    print nexturl
    except Exception,e:
        flag = False
        print e
    return nexturl
    
#初始化
def initdriver(keyword):
    driver = changeIP()
    last = None
    if last == None:
        driver.get("https://www.baidu.com")
        elem_name = driver.find_element_by_id("kw")
        elem_name.clear()
        elem_name.send_keys(keyword)
        elem_search = driver.find_element_by_id("su")
        elem_search.click()
        webscreen(driver.current_url, driver)  
    else:
        webscreen(last, driver)

if __name__=="__main__":
    
    keyword_list = ["beauty","Electoric","Baby"]
    for key in keyword_list:
        keyword = key
        initdriver("site:amazon.com "+ key +" currently unavailable")
        #time.sleep(200)
    #time.sleep(1800)