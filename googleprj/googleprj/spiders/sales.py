# -*- coding: utf-8 -*-
import scrapy
from googleprj.items import DmozItem,gurl
from lxml import etree
import re,time
import urllib
import requests
from googleprj.settings import *
from googleprj.redisM import RedisM
import MySQLdb
import logging  

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
 
handler = logging.FileHandler('sales.log')
handler.setLevel(logging.INFO)
 
# create a logging format 
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
count = 0
rm = RedisM()
db = MySQLdb.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB)
cursor = db.cursor()

class amazon(scrapy.Spider):
    
    name = "sales"
    allowed_domains = ["amazon.com"]
    
    def start_requests(self):

        return [scrapy.Request("https://sellercentral.amazon.com/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fsellercentral.amazon.com%2Fhome&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=sc_na_amazon_v2&openid.mode=checkid_setup&language=zh_CN&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&pageId=sc_na_amazon_v2&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&ssoResponse=eyJ6aXAiOiJERUYiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiQTI1NktXIn0.aeRI-LZLhqgHn_Alc2C_zgS7j8NcG6u-hceqR-O0QIQqhx8BdxxQEA.Aq6PJjbrqEk2IbRS.M_7W-lcp8LNhdVrCFQqsSbuwAXAvjigQ_HMJhDdhNE6qAKif2OzTyrNfl14xSVd9lZO91Ap-YdGD7DrXlgTy-lDEimga7Wq0tvxPZD7MhpYndx0OxbqKOxULzAF6uWnYQniOXPWSvQwrYDe_YwUYjTl9QarA_bwNicezXfh-TCnXCR7Liwk6qxsjd_QiywLBbIcNROXexG7Krcnt2rvfOPxq4keYuuJ0HB09P9By6EnVkvi_gwTqwMtL0KKZ1HKtZ-q5.UkjxDTqyWcZjNqQ0V1cjvw",meta={'cookiejar':1},headers=AMAZON_HEADERS, callback=self.post_login)]

    def post_login(self, response):
        logger.info('1111111111111')
        appActionToken = response.xpath('//*[@name="appActionToken"]/@value')[0].extract()  
        max_auth_age = response.xpath('//*[@name="openid.pape.max_auth_age"]/@value')[0].extract()  
        identity = response.xpath('//*[@name="openid.identity"]/@value')[0].extract()  
        ssoResponse = response.xpath('//*[@name="ssoResponse"]/@value')[0].extract()  
        language = response.xpath('//*[@name="language"]/@value')[0].extract()  
        pageId = response.xpath('//*[@name="pageId"]/@value')[0].extract()  
        return_to = response.xpath('//*[@name="openid.return_to"]/@value')[0].extract()  
        prevRID = response.xpath('//*[@name="prevRID"]/@value')[0].extract()  
        assoc_handle = response.xpath('//*[@name="openid.assoc_handle"]/@value')[0].extract() 
        openidmode = response.xpath('//*[@name="openid.mode"]/@value')[0].extract()  
        prepopulatedLoginId = response.xpath('//*[@name="prepopulatedLoginId"]/@value')[0].extract()  
        failedSignInCount = response.xpath('//*[@name="failedSignInCount"]/@value')[0].extract()  
        claimed_id = response.xpath('//*[@name="openid.claimed_id"]/@value')[0].extract()  
        openidns = response.xpath('//*[@name="openid.ns"]/@value')[0].extract()  
        
        return [scrapy.FormRequest.from_response(response,method="POST",
                                          headers=AMAZON_HEADERS,  # 注意此处的headers
                                          formdata={
                                              'email': 'vupykn72515@163.com',
                                              'password': 'UMWDMYIVKIR',
                                              'create':'0',
                                              'appActionToken':appActionToken,
                                              'openid.pape.max_auth_age':max_auth_age,
                                              'openid.identity':identity,
                                              'ssoResponse':ssoResponse,
                                              'language':language,
                                              'pageId':pageId,
                                              'openid.return_to':return_to,
                                              'prevRID':prevRID,
                                              'openid.assoc_handle':assoc_handle,
                                              'openid.mode':openidmode,
                                              'prepopulatedLoginId':prepopulatedLoginId,
                                              'failedSignInCount':failedSignInCount,
                                              'openid.claimed_id':claimed_id,
                                              'openid.ns':openidns
                                          },
                                          meta={'cookiejar': response.meta['cookiejar']},
                                          callback=self.second_login,
                                          dont_filter=True
                                          )]
    
    def second_login(self, response):
        logger.info('22222222222222')
        logger.info(response.request.url)
        logger.info(response.body) 
    
    def parse(self, response):
        print '33333333333333'