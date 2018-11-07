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
        driver.get("https://sellercentral.amazon.co.uk/productsearch/ref=id_catadd_dnav_xx_")
        elem_name = driver.find_element_by_id("ap_email")
        elem_password = driver.find_element_by_id("ap_password")
        elem_name.clear()
        elem_password.clear()
        elem_name.send_keys("zm15360586565@sina.com")
        elem_password.send_keys("5560rfvg")
        elem_login = driver.find_element_by_id("signInSubmit")
        elem_login.click()
        time.sleep(10)

        #二次登录
        elem_login2 = driver.find_element_by_id("auth-signin-button")
        elem_login2.click()
        #添加商品页面
        driver.get("https://sellercentral.amazon.co.uk/productsearch/ref=id_catadd_dnav_xx_")    
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
    updatesql = "update Brand20180919 set status='%s' where asin= '%s'" % (status,asin)
    
    try:
            cursor.execute(updatesql)
            db.commit()
    except Exception,e:
            logger.error("updateres error:%s",e)
            db.rollback()

#更新源数据库
def updateuse(asin):
    updatesql = "update Brand20180919 set ischeck=1 where asin= '%s'" % (asin)
    
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
        "refer":"https://sellercentral.amazon.com/productsearch?q=B0769XPJGS&ref_=xx_prodsrch_cont_prodsrch",
        'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
        }
        
        data_list = seldata()
        cookie = '__guid=148651701.1533386504589582800.1532402662324.6316; sid="NZsvirXoZaEtoP7reMQYQw==|8UMp5lfMig8L6BqjKLNGIMArGvIPTllXxE38v0fJf2A="; at-acbuk=Atza|IwEBIJEc4iV1vIqkuo15HQYs0MnlHfAAUqjLI5EMkpQZZWZsjkPUEVLFJ69j0INb-wRVKNdtv9W9mrbXaOyYYjA_Fz4CfZP73SMXw4QZq-AlfriHySJGSMREc9PThljizbs-W_wiqdoGLTpW_arVu5NTv-u7IGc5hQSUPEtOCxoIwy-a8M4FDQhsrZelnhxTdVF6IUFMqiCPGk2kWQRSUWYfuGDyROyonOjsoe7QzV0RSlcre_bmkiW7DpOq_a3-ijn_qj2w6WVqKkyI8GgT-0G4dQnd7I8IF-0pff8HIwipeLQcAWDjBQH4hY53GZFmYrewm_KR-i0wKH3kfdFpRCfwg1MhvtRTUkPJr9rNHfdUDBvBpEd8CcFUejFos8Uf8SMqUcRnmGWANyQiHQOkeXGunKvlkHWk_t-NM-oBmiw_UIqQEw; sess-at-acbuk="sMrRYrHJbGhICOkL8DPQ34uuyWaX4jlauCOK9vzpbPA="; sst-acbuk=Sst1|PQETNdCJbKTId7-6P3jHbIg1C8xF4RCCSMbCZnHaoXeLeFIOd8IchDdsWloI4S6NvPj6zT0_mKv3b6IFwVmDBD8CTw3fTervbHAyV7eSBd_YffoCx25f4_VS5CvqceDUJagXRra2ebs5JB-2IBKXoTglUipjee5XhLjkNqrbyifxdHi1PGI_Bq1V94FxP9YgNVkMputiJ2PszR_f7fmSjPq5oJD0AghWphmF5KICsikhe7pQHn1zULPoq0JbeUnjV-gGFWkJdiC3p830HDuOTDkPJoZEMxEG15cLbtMK0faGUzhbH3_2DVPo2lgkmiKW61eIJaJ_8Nr-jk1XTmWbs6kbaw; session-id=258-7504511-0460136; ubid-acbuk=257-4651174-2472549; session-token="iaRO0CN2LEX9JPQHqHnL3Q6dWdYK0Lg05Zy27LbRLLlkkmPZbh8uZd+E4GoD7UohOT9Z4S+vbed7D33J1VFz6krHuDPsVRIp3bVDDlUvU5B+9DqYXr+2SwEHVg6c+Krsx95PsemNAM669kwm/GnF6T9LxU7VfcChD0X14UombATayeEZ5w+I8eX6ROH5TMYYGM99XDIih5Prl5Sp4kwGXDQf0j7axa30OSNN2145cU0="; x-acbuk="Aex5qv4Mto8FoDYHWShbVKkFS1drdgpbF83iL1bEeZQlqm9cVe8bh11bizBDv10@"; monitor_count=3; csm-hit=s-JBMDTFDT49A39A3QHMAE|1537432764853; session-id-time=1538031600l'
        print len(data_list)
        if data_list != None:
            for i in range(0,len(data_list)):
                #second url request
                opener = urllib2.build_opener()
                opener.addheaders.append(('Cookie',cookie))
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
    sql = "select asin from Brand20180919 where ischeck=0 "
    try:
            cursor.execute(sql)
            results = cursor.fetchall()
            return results
    
    except Exception,e:
            print e
            db.rollback()
if __name__=="__main__":
    
    webscreen()