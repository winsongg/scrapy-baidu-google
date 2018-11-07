# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities,FirefoxProfile
from lxml import etree
import time,string
import random   
import MySQLdb
from selenium.webdriver.common.proxy import * 
from selenium.webdriver import DesiredCapabilities
import logging  
from cmath import asin
import urllib,urllib2,requests,cookielib
  
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
 
handler = logging.FileHandler('amazonspider.log')
handler.setLevel(logging.INFO)
 
# create a logging format 
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
 
# add the handlers to the logger
logger.addHandler(handler)
db = MySQLdb.connect("47.254.69.199", "root", "123456", "amazon")
cursor = db.cursor()

def webscreen(driver=None):
    try:
        if driver == None:
            driver = changeIP()
        
        #登录
        driver.get("https://sellercentral.amazon.com/ap/signin?openid.pape.max_auth_age=18000&openid.return_to=https%3A%2F%2Fsellercentral.amazon.com%2Fgp%2Fhomepage.html&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=sc_na_amazon_v2&_encoding=UTF8&openid.mode=checkid_setup&openid.ns.pape=http%3A%2F%2Fspecs.openid.net%2Fextensions%2Fpape%2F1.0&language=zh_CN&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&pageId=sc_na_amazon&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&ssoResponse=eyJ6aXAiOiJERUYiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiQTI1NktXIn0.IAUIhOxwtWfyerjryLNuDUY_Xzo4r5ldQ-qXauJ6_6WhESMdhrKE2A.nDXXzq7GV9ZPnWXS.WgzHehTRsXi0vaYWPMJ6amTPH5iOhexjo4ROZAfz_KLFmQ1tEwdBVI48tzgdJjNM5_snEXNcUDURjlcG1qe5Ap1U5AAz04a4iFxRoLQDG2xE40-AISJsGdDj9d3ie2m4TzPOxNlfMksN-_FDF4rwENS5a7UMrLenlmmL8ZwqOIbOu15fdzz-Z3AiDcxeuuQ2UOyu0PaWuXp7C_u8iUytOmI2Q4yRXMkBQu5ac5XlBIyKYfvkCXakYaNinsx606LoVFRY4w.1NroIVnAgkjYSMesPv3O_A")
        elem_name = driver.find_element_by_id("ap_email")
        elem_password = driver.find_element_by_id("ap_password")
        elem_name.clear()
        elem_password.clear()
        elem_name.send_keys("vupykn72515@163.com")
        elem_password.send_keys("UMWDMYIVKIR")
        elem_login = driver.find_element_by_id("signInSubmit")
        elem_login.click()
        time.sleep(10)

        #二次登录
        elem_login2 = driver.find_element_by_id("auth-signin-button")
        elem_login2.click()
        #添加商品页面
        driver.get("https://sellercentral.amazon.com/productsearch/ref=id_catadd_dnav_xx_")    
        time.sleep(3)
        data_list = seldata()
        if data_list != None:
            for i in range(0,len(data_list)):
                print data_list[i][0]
                asininput = driver.find_element_by_id("product-search") 
                asinbtn = driver.find_element_by_xpath('//*[@id="product-search-button"]/span/input')
                asininput.clear()
                asininput.send_keys(data_list[i][0])
                asinbtn.click()
                parsehtml(driver,data_list[i][0])
                updateuse(data_list[i][0])
                time.sleep(3)
        driver.close()
    except Exception,e:
        driver.close()
        logger.error('webscreen error:%s',e)

#切换IP的方法
def changeIP():
    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = (
    "Mozilla/5.0 (Linux; Android 5.1.1; Nexus 6 Build/LYZ28E) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.23 Mobile Safari/537.36"
    )
    #driver = webdriver.PhantomJS(executable_path =r"C:\phantomjs-2.1.1-windows\bin\phantomjs.exe",desired_capabilities=dcap)
    #driverOptions = webdriver.ChromeOptions()
    #driverOptions.add_argument(r"user-data-dir=C:\Users\Administrator\AppData\Local\Google\Chrome\User Data")
    #driver = webdriver.Chrome(executable_path ="c:\Python27\chromedriver.exe",chrome_options=driverOptions)
    driver = webdriver.Chrome(executable_path ="c:\Python27\chromedriver.exe")
    return driver
    
#解析要获取的元素方法
def parsehtml(driver,asin):
    try:
        if(len(driver.find_element_by_xpath('//div[@id="search-results"]').text))>0:
            try:
                btn1 = driver.find_element_by_xpath('//*[@id="a-autoid-2-announce"]').text
                btn2 = driver.find_element_by_xpath('//*[@id="a-autoid-3-announce"]').text
                print btn1+"---"+btn2
                if u"出售您的" in btn1 and u"请求批准" in btn2:
                    print u'可以销售的~~~~'
                    print asin
                    updateres(asin,"yes")
            except Exception,e1:
                logger.warn("%s",e1)

    except Exception,e:
        logger.error(e)
        logger.error("parse url:%s",driver.current_url)
 
#更新源数据库
def updateres(asin,status):
    updatesql = "update tb_unavaliable_google set status='%s' where asin= '%s'" % (status,asin)
    
    try:
            cursor.execute(updatesql)
            db.commit()
    except Exception,e:
            logger.error("updateres error:%s",e)
            db.rollback()

#更新源数据库
def updateuse(asin):
    updatesql = "update tb_unavaliable_google set ischeck=1 where asin= '%s'" % (asin)
    
    try:
            cursor.execute(updatesql)
            db.commit()
    except Exception,e:
            logger.error("updateuse error:%s",e)
            db.rollback()
            



#---------------------------------直接后台添加cookie去无界面查询数据
def webscreen2():
    try:
        AMAZON_HEADERS = {
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding':'gzip, deflate, br',
        'Accept-Language':'zh-CN,zh;q=0.9',
        'Connection':'keep-alive',
        "upgrade-insecure-requests":1,
        "refer":"https://sellercentral.amazon.com/ap/signin",
        'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
        }
        
        data_list = seldata()
        print len(data_list)
        
        cj = cookielib.CookieJar() 
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        urllib2.install_opener(opener)
        
        #一次登录
        request2 = urllib2.Request("https://sellercentral.amazon.com/ap/signin?openid.pape.max_auth_age=18000&openid.return_to=https%3A%2F%2Fsellercentral.amazon.com%2Fproductsearch%3Fq%3DB008R51338%26ref_%3Dxx_prodsrch_cont_prodsrch&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=sc_na_amazon_v2&openid.mode=checkid_setup&language=zh_CN&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&pageId=sc_na_amazon_v2&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&ssoResponse=eyJ6aXAiOiJERUYiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiQTI1NktXIn0.DCqE7Lc_tzIQkSUGJTU-NKj5ibgdPNQMhDBtPWPa3j3sUnQ1oSF3pQ.RZG4DU06QAyvEBae.hgFnE6GZD781ZLIk6Y4DO1_apKfaXgxOcvuiYI0tJqDCUDb1qSl1oi6sA-TYSc4HYfhy4oveCSd9wjn5_jJvRJZCEqKpJoK9fAZqc_R7021OjfHcTQi0hBD-LDsqAaLZccymNvlvJJrINJTNwImj7SdIj8zriR55S5PoDzX9hxmpgTCkzH6F-kgWCdwgtRgadml3Ds4xXKtNXK_gqt9UYsj-NrkUv7Gg5XA8BI_97hCR95oBhynm6uqbLy5bKg8UmueR.Qb6WLq-7ihB7cXfvBaQfTA", headers=AMAZON_HEADERS)
        form_data = []
        request2.add_header('User-Agent', ua) 
        response = urllib2.urlopen(request2)
        
        if data_list != None:
            for i in range(0,len(data_list)):
                url = "https://sellercentral.amazon.com/productsearch?q=B008R51338&ref_=xx_prodsrch_cont_prodsrch"
                print data_list[i][0]
                request2 = urllib2.Request(url, headers=AMAZON_HEADERS)
                response = urllib2.urlopen(request2)
                
                parsehtml2(response.read(),data_list[i][0])
                #updateuse(data_list[i][0])
                break
            
    except Exception,e:
        logger.error('webscreen2 error:%s',e)


#解析要获取的元素方法
def parsehtml2(html,asin):
    try:
        #print html
            logger.info(html)
            selector = etree.HTML(html)
            print selector.xpath('//div[@id="search-results"]')
            try:
                btn1 = selector.xpath('//*[@id="a-autoid-2-announce"]/text()')[0]
                print btn1
                btn2 = selector.xpath('//*[@id="a-autoid-3-announce"]/text()')[0]
                print btn2
                if u"出售您的" in btn1 and u"请求批准" in btn2:
                    print u'可以销售的~~~~'
                    print asin
                    updateres(asin,"yes")
            except Exception,e1:
                logger.warn("%s",e1)

    except Exception,e:
        logger.error(e)


#查询数据库
def seldata():
    sql = "select asin from tb_unavaliable_google where ischeck=0 "
    try:
            cursor.execute(sql)
            results = cursor.fetchall()
            return results
    
    except Exception,e:
            print e
            db.rollback()
if __name__=="__main__":
    
    webscreen()