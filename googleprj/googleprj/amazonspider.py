# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver import DesiredCapabilities,FirefoxProfile
import time,string
import random   
from settings import *
import MySQLdb
from selenium.webdriver.common.proxy import * 
import logging  
  
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.FileHandler('amazonspider.log')
handler.setLevel(logging.INFO)

# create a logging format 
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)
keyword = ""
count = 0
db = MySQLdb.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB)
cursor = db.cursor()
contactlist = {"Home & Kitchen":"search-alias=garden"}

def webscreen(driver=None):
    global contactlist
    try:
        if driver == None:
            driver = changeIP()
            
        data_list = seldata()
        logger.info("spider:%s----%s",0,len(data_list))
        if data_list != None:
            for i in range(0,len(data_list)):
                starturl =  "https://www.amazon.com/s/ref=nb_sb_noss_2?url="+contactlist[data_list[i][0]]+"&field-keywords="+data_list[i][1]+""
                driver.get(starturl)
                
                stocks = driver.find_elements_by_xpath("//span[@class='a-size-small a-color-base s-ref-text-link s-ref-link-cursor']") 
                flag = False
                stock_name = ""
                star = ""
                for stock in stocks:
                    if stock.text == "Include Out of Stock":
                        print "找到了Include Out of Stock"
                        flag = True
                        stock_name = stock.find_elements_by_xpath("../../..")[0].get_attribute("data-a-input-name")
                        
                        driver.find_elements_by_name(stock_name)[0].click()
                
                if flag == False:
                    continue
                
                #找星级的标识
                tempul = 0
                time.sleep(3)
                star = driver.find_element_by_xpath('//i[@class="a-icon a-icon-star-medium a-star-medium-4"]/..')
                star.click()
                time.sleep(3)
                parsehtml(driver,data_list[i][1])
                try:
                    next = driver.find_element_by_id("pagnNextString")
                    curl = driver.current_url
                    while next != None:
                        next.click()
                        
                        if curl == driver.current_url:
                            break
                        else:
                            curl = driver.current_url
                            
                        time.sleep(3)
                        parsehtml(driver,data_list[i][1])
                        next = driver.find_element_by_id("pagnNextString")
                        
                except Exception,e:
                    print e
                    pass        
                
                updateurl(data_list[i][1])
                driver = checkstatus(driver)
	
    except Exception,e:
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
    driver = webdriver.Firefox(executable_path ="D:\Python27\geckodriver.exe",proxy=proxy)
    return driver
    
#解析要获取的元素方法
def parsehtml(driver,keyword):
    try:
        if(driver.find_elements_by_xpath('//ul[@id="s-results-list-atf"]'))!= None:
            lis = driver.find_elements_by_xpath('//ul[@id="s-results-list-atf"]/li')
            for li in lis:
                flag = False
                check = li.find_element_by_xpath("//span[@class='a-size-small a-color-secondary']")
                
                if "Currently unavailable" in li.get_attribute('outerHTML'):
                    flag = True
                
                if flag == True:
                    url = li.find_element_by_xpath("div/div[3]/div[1]/a").get_attribute("href")
                    insertdata(url,keyword)
        else:
            if len(driver.find_element_by_xpath('body').text)<300:
                logger.error('被反扒了~~~~~')
                logger.info(driver.find_element_by_tag_name("body").text)
            else:
                logger.info('aiiiiiiiiiiiiiiiiii')
    except Exception,e:
        logger.error(e)
        logger.error("parse url:%s",driver.current_url)

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
            logger.warn('进503 和反扒')
        elif title != None and "Robot Check" in title:
            flag = True
            logger.warn('进robot')
        #elif count == 30:
            #计数换IP
        #    count =0
        #    flag = True
        elif len(body)<1000:
            flag = True
            logger.warn('验证码')
        if flag ==True:
            driver.quit()
            time.sleep(random.randint(15,20))
            driver = changeIP()
        
        return driver
    except Exception,e:
            logger.error("checkstatus error:%s",e)
            return changeIP()
        
#写入数据库
def insertdata(url,keyword):
    sql = "replace  INTO tb_tempurl (url,keyword,isvalid) VALUES ('%s', '%s','%s')" % (url,keyword,1)
    
    try:
            cursor.execute(sql)
            
            db.commit()
    except Exception,e:
            logger.error("mysql error:%s",e)
            db.rollback()
            
#更新源数据库
def updateurl(keyword):
    updatesql = "update tb_keywords set isvalid=0 where keyword= '%s'" % (keyword)
    
    try:
            cursor.execute(updatesql)
            db.commit()
    except Exception,e:
            logger.error("mysql error:%s",e)
            db.rollback()
            

#查询数据库
def seldata():
    sql = "select bigname,keyword from tb_keywords where isvalid=1 limit 1"
    try:
            cursor.execute(sql)
            results = cursor.fetchall()
            return results
    
    except Exception,e:
            print e
            db.rollback()
if __name__=="__main__":
    
    webscreen()
    

