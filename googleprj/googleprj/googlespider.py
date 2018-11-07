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
        driver = checkstatus(driver)
        if nexturl != "":
            rm.updateRedis(keyword,nexturl)
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
    #使用代理
    proxy = Proxy({  
    'proxyType': ProxyType.MANUAL,  
    'httpProxy': thisip["ipaddr"],  
    'ftpProxy': thisip["ipaddr"],  
    'sslProxy': thisip["ipaddr"],  
    'noProxy': ''   
    })  
    driver = webdriver.Firefox(executable_path ="D:\Python27\geckodriver.exe",proxy=proxy)#,firefox_profile=profile)
    driver.implicitly_wait(10)
    return driver
    
#解析要获取的元素方法
def parsehtml(driver):
    global keyword
    #获取下一页
    flag = True
    nexturl = ""
    try:
        nexturl = driver.find_element_by_id("pnnext").get_attribute("href")
    except Exception,e:
        flag = False
    
    #获取google的url数据
    try:
        
        datalist = driver.find_elements_by_xpath('//*[@id="rso"]/div[@class="bkWMgd"]/div[@class="srg"]/div[@class="g"]') 

        for one in datalist:
            url = one.find_element_by_tag_name("a").get_attribute("href")
            if "https://amazon.com" in url or "https://www.amazon.com" in url :
                insertdata(url,keyword)
    except Exception,e:
        logger.error('parse error:%s',e)
    
    return nexturl
#需要换IP的判断
def checkstatus(driver):
    try:
        global count
        body = driver.find_element_by_tag_name("body").text
        title = driver.find_element_by_tag_name("title").text
        flag = False
        #meet the dog,robot换
        if body != None and ("._TTD_.jpg" in body or "503" in body):
            flag = True
            logger.info('进503 和反扒') 
        elif title != None and "Robot Check" in title:
            flag = True
            logger.info('进robot')
        '''elif count == 3:
            #计数换IP
            count =0
            flag = True
        '''
        if flag == True:
            driver.quit()
            sleeptime = random.randint(3,5)
            logger.info(sleeptime)
            time.sleep(sleeptime)
            driver = changeIP()
        
        return driver
    except Exception,e:
        logger.error('checkstatus error:%s',e)
        return changeIP()
        
#写入数据库
def insertdata(url,keyword):
    sql = "replace  INTO tb_tempurl (url,keyword,isvalid) VALUES ('%s', '%s','%s')" % (url,keyword,1)
    try:
            cursor.execute(sql)
            db.commit()
    except Exception,e:
            logger.error('mysql error:%s',e)
            db.rollback()

#初始化
def initdriver(keyword):
    driver = changeIP()
    last = "https://www.google.com.hk/search?q=site:amazon.com+Amazon+Devices+%26+Accessories+currently+unavailable&newwindow=1&safe=strict&ei=eNc9W4zgCsSO0wKHz7q4CA&start=130&sa=N&biw=1366&bih=662"
    if last == None:
        driver.get("https://www.google.com")
        elem_name = driver.find_element_by_id("lst-ib")
        elem_name.clear()
        elem_name.send_keys(keyword)
        elem_search = driver.find_element_by_name("btnK")
        elem_search.click()
        webscreen(driver.current_url, driver)  
    else:
        webscreen(last, driver)

if __name__=="__main__":
    
    keyword_list = ["Amazon Devices & Accessories"]
    for key in keyword_list:
        keyword = key
        initdriver("site:amazon.com "+ key +" currently unavailable")
        time.sleep(200)
    #time.sleep(1800)